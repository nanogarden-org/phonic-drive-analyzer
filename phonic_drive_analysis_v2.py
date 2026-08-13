#!/usr/bin/env python3
"""
Phonic Drive Hybrid Analyzer v2

Batch-capable acoustic analyzer for one or many audio inputs.

Measured layer
--------------
- waveform / STFT spectrum
- RMS energy
- spectral centroid, bandwidth, rolloff, zero-crossing rate
- normalized spectral flux + onset candidates
- tempo proxy from flux autocorrelation
- per-frame stereo correlation and mid/side width
- multi-feature transition speed / acceleration
- 3D export coordinates: brightness, energy, stereo space

Interpretive layer
------------------
Optional user-authored song_lens YAML/TXT annotations are attached to results,
but are kept distinct from measured features. Declared resonance anchors can be
checked for spectral energy near their stated frequencies without treating that
as proof of a cognitive or physical resonance claim.

Dependencies:
    pip install numpy scipy matplotlib pydub pyyaml

pydub also requires ffmpeg on PATH.
"""

from __future__ import annotations

import argparse
import csv
import glob
import hashlib
import json
import math
import re
import sys
import traceback
from pathlib import Path
from typing import Any, Iterable

import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as sps
from pydub import AudioSegment

try:
    import yaml
except ImportError:
    yaml = None


SUPPORTED_EXTENSIONS = {
    ".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aac",
    ".wma", ".aiff", ".aif", ".opus",
}
EPS = 1e-12


def json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): json_ready(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_ready(v) for v in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    return value


def safe_float(value: Any, default: float | None = None) -> float | None:
    try:
        x = float(value)
        return x if math.isfinite(x) else default
    except (TypeError, ValueError):
        return default


def slugify(text: str) -> str:
    text = re.sub(r"[^\w.-]+", "_", text.strip(), flags=re.UNICODE)
    return re.sub(r"_+", "_", text).strip("_.") or "track"


def source_id(path: Path) -> str:
    return hashlib.sha1(str(path.resolve()).encode("utf-8", "ignore")).hexdigest()[:8]


def robust_z(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64)
    if not len(x):
        return x
    med = np.nanmedian(x)
    mad = np.nanmedian(np.abs(x - med))
    scale = 1.4826 * mad
    if not np.isfinite(scale) or scale < EPS:
        std = np.nanstd(x)
        scale = std if np.isfinite(std) and std > EPS else 1.0
    return (x - med) / scale


def scale_01(x: np.ndarray, low: float = 5.0, high: float = 95.0) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64)
    if not len(x):
        return x
    lo, hi = np.nanpercentile(x, [low, high])
    if not np.isfinite(lo) or not np.isfinite(hi) or hi - lo < EPS:
        return np.zeros_like(x)
    return np.clip((x - lo) / (hi - lo), 0.0, 1.0)


def moving_average(x: np.ndarray, frames: int) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64)
    frames = max(1, min(int(frames), len(x))) if len(x) else 1
    if frames <= 1:
        return x.copy()
    return np.convolve(x, np.ones(frames) / frames, mode="same")


def align_length(x: np.ndarray, n: int, fill: float = 0.0) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64)
    if len(x) >= n:
        return x[:n]
    if not len(x):
        return np.full(n, fill, dtype=np.float64)
    return np.concatenate([x, np.full(n - len(x), x[-1])])


# ---------------------------------------------------------------------------
# Input discovery
# ---------------------------------------------------------------------------

def iter_filelist(path: Path) -> Iterable[str]:
    for raw in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        line = raw.strip()
        if line and not line.startswith("#"):
            yield line


def resolve_inputs(tokens: list[str], recursive: bool) -> list[Path]:
    found: list[Path] = []

    def handle(token: str) -> None:
        token = token.strip().strip('"')
        if not token:
            return
        if token.startswith("@"):
            p = Path(token[1:]).expanduser()
            if not p.exists():
                print(f"[WARN] file list not found: {p}", file=sys.stderr)
                return
            for nested in iter_filelist(p):
                handle(nested)
            return
        if any(ch in token for ch in "*?[]"):
            matches = glob.glob(str(Path(token).expanduser()), recursive=recursive)
            if not matches:
                print(f"[WARN] glob matched nothing: {token}", file=sys.stderr)
            for match in matches:
                handle(match)
            return

        p = Path(token).expanduser()
        if p.is_dir():
            it = p.rglob("*") if recursive else p.glob("*")
            found.extend(x for x in it if x.is_file() and x.suffix.lower() in SUPPORTED_EXTENSIONS)
        elif p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS:
            found.append(p)
        elif p.exists():
            print(f"[WARN] unsupported audio file: {p}", file=sys.stderr)
        else:
            print(f"[WARN] input not found: {p}", file=sys.stderr)

    for token in tokens:
        handle(token)

    seen = set()
    unique = []
    for p in found:
        key = str(p.resolve()).casefold()
        if key not in seen:
            seen.add(key)
            unique.append(p)
    return sorted(unique, key=lambda p: str(p).casefold())


# ---------------------------------------------------------------------------
# Optional song_lens annotations
# ---------------------------------------------------------------------------

def normalize_title(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.casefold())


def extract_song_lens_block(text: str) -> str | None:
    lines = text.splitlines()
    start = next((i for i, line in enumerate(lines) if line.strip() == "song_lens:"), None)
    if start is None:
        return None
    block = [lines[start]]
    for line in lines[start + 1:]:
        if not line.strip() or line.startswith((" ", "\t", "#")):
            block.append(line)
        else:
            break
    return "\n".join(block).strip()


def load_annotations(tokens: list[str]) -> tuple[dict[str, dict[str, Any]], list[str]]:
    result: dict[str, dict[str, Any]] = {}
    warnings: list[str] = []
    if not tokens:
        return result, warnings
    if yaml is None:
        return result, ["PyYAML is not installed; annotations skipped."]

    paths: list[Path] = []
    for token in tokens:
        if any(ch in token for ch in "*?[]"):
            paths.extend(Path(p) for p in glob.glob(token))
        else:
            p = Path(token).expanduser()
            if p.is_dir():
                for ext in ("*.yaml", "*.yml", "*.txt"):
                    paths.extend(p.glob(ext))
            elif p.is_file():
                paths.append(p)

    for p in paths:
        try:
            text = p.read_text(encoding="utf-8-sig", errors="replace")
            if p.suffix.lower() == ".txt":
                block = extract_song_lens_block(text)
                if block is None:
                    warnings.append(f"No song_lens YAML block in {p}")
                    continue
                text = block
            data = yaml.safe_load(text)
            lens = data.get("song_lens") if isinstance(data, dict) else None
            if not isinstance(lens, dict):
                warnings.append(f"No song_lens mapping in {p}")
                continue
            lens = dict(lens)
            lens["_annotation_source"] = str(p)
            title = str(lens.get("song_title", p.stem))
            result[normalize_title(title)] = lens
        except Exception as exc:
            warnings.append(f"Could not parse annotation {p}: {exc}")
    return result, warnings


def match_annotation(audio_path: Path, annotations: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    if not annotations:
        return None
    stem = normalize_title(audio_path.stem)
    if stem in annotations:
        return annotations[stem]
    matches = [(len(k), v) for k, v in annotations.items() if k and (k in stem or stem in k)]
    if matches:
        return max(matches, key=lambda item: item[0])[1]
    if len(annotations) == 1:
        return next(iter(annotations.values()))
    return None


# ---------------------------------------------------------------------------
# Audio and feature extraction
# ---------------------------------------------------------------------------

def load_audio(path: Path, target_sr: int) -> tuple[np.ndarray, np.ndarray, np.ndarray, int, int]:
    audio = AudioSegment.from_file(path)
    src_sr = int(audio.frame_rate)
    channels = int(audio.channels)
    raw = np.asarray(audio.get_array_of_samples())
    if not len(raw):
        raise ValueError("Audio contains no samples")

    if channels > 1:
        usable = (len(raw) // channels) * channels
        raw = raw[:usable].reshape((-1, channels))
    else:
        raw = raw.reshape((-1, 1))

    max_val = float(2 ** (audio.sample_width * 8 - 1))
    data = raw.astype(np.float32) / max_val
    mono = np.mean(data, axis=1)
    left = data[:, 0]
    right = data[:, 1] if channels >= 2 else data[:, 0]

    if src_sr != target_sr:
        gcd = math.gcd(src_sr, target_sr)
        up, down = target_sr // gcd, src_sr // gcd
        mono = sps.resample_poly(mono, up, down).astype(np.float32)
        left = sps.resample_poly(left, up, down).astype(np.float32)
        right = sps.resample_poly(right, up, down).astype(np.float32)
        sr = target_sr
    else:
        sr = src_sr
    return mono, left, right, sr, channels


def pad_short(y: np.ndarray, n_fft: int) -> np.ndarray:
    return y if len(y) >= n_fft else np.pad(y, (0, n_fft - len(y)))


def frame_signal(y: np.ndarray, frame_length: int, hop: int) -> np.ndarray:
    y = pad_short(np.asarray(y, dtype=np.float32), frame_length)
    return np.lib.stride_tricks.sliding_window_view(y, frame_length)[::hop]


def stft_frames(y: np.ndarray, sr: int, n_fft: int, hop: int):
    y = pad_short(y, n_fft)
    window = sps.get_window("hann", n_fft, fftbins=True)
    freqs, times, zxx = sps.stft(
        y, fs=sr, window=window, nperseg=n_fft,
        noverlap=n_fft - hop, nfft=n_fft, boundary=None, padded=False,
    )
    return freqs, times, np.abs(zxx)


def rms_frames(y: np.ndarray, n_fft: int, hop: int) -> np.ndarray:
    frames = frame_signal(y, n_fft, hop).astype(np.float64)
    return np.sqrt(np.mean(frames * frames, axis=1))


def zcr_frames(y: np.ndarray, n_fft: int, hop: int) -> np.ndarray:
    frames = frame_signal(y, n_fft, hop)
    signs = np.signbit(frames)
    return np.mean(signs[:, 1:] != signs[:, :-1], axis=1)


def spectral_centroid(S: np.ndarray, freqs: np.ndarray) -> np.ndarray:
    denom = np.sum(S, axis=0) + EPS
    return np.sum(S * freqs[:, None], axis=0) / denom


def spectral_bandwidth(S: np.ndarray, freqs: np.ndarray, centroid: np.ndarray) -> np.ndarray:
    denom = np.sum(S, axis=0) + EPS
    var = np.sum(S * (freqs[:, None] - centroid[None, :]) ** 2, axis=0) / denom
    return np.sqrt(np.maximum(var, 0.0))


def spectral_rolloff(S: np.ndarray, freqs: np.ndarray, fraction: float = 0.85) -> np.ndarray:
    cumulative = np.cumsum(S, axis=0)
    thresholds = fraction * cumulative[-1]
    idx = np.argmax(cumulative >= thresholds[None, :], axis=0)
    return freqs[idx]


def spectral_flux(S: np.ndarray) -> np.ndarray:
    norm = S / (np.sum(S, axis=0, keepdims=True) + EPS)
    diff = np.maximum(np.diff(norm, axis=1), 0.0)
    return np.sqrt(np.sum(diff * diff, axis=0))


def stereo_features(left: np.ndarray, right: np.ndarray, n_fft: int, hop: int):
    lf = frame_signal(left, n_fft, hop).astype(np.float64)
    rf = frame_signal(right, n_fft, hop).astype(np.float64)
    n = min(len(lf), len(rf))
    lf, rf = lf[:n], rf[:n]

    l0 = lf - np.mean(lf, axis=1, keepdims=True)
    r0 = rf - np.mean(rf, axis=1, keepdims=True)
    cov = np.mean(l0 * r0, axis=1)
    corr = cov / (np.sqrt(np.mean(l0*l0, axis=1)) * np.sqrt(np.mean(r0*r0, axis=1)) + EPS)
    corr = np.clip(corr, -1.0, 1.0)

    mid = 0.5 * (lf + rf)
    side = 0.5 * (lf - rf)
    width = np.sqrt(np.mean(side*side, axis=1)) / (np.sqrt(np.mean(mid*mid, axis=1)) + EPS)
    return corr, width


def mean_spectrum_peaks(S: np.ndarray, freqs: np.ndarray, top_n: int):
    mean_spec = np.mean(S, axis=1)
    rel_db = 20 * np.log10((mean_spec + EPS) / (np.max(mean_spec) + EPS))
    resolution = float(freqs[1] - freqs[0]) if len(freqs) > 1 else 1.0
    distance = max(1, int(round(20.0 / max(resolution, EPS))))
    peaks, props = sps.find_peaks(rel_db, height=-40.0, prominence=3.0, distance=distance)
    if not len(peaks):
        return [], mean_spec
    order = np.argsort(rel_db[peaks])[::-1]
    result = []
    for oi in order[:top_n]:
        p = peaks[oi]
        result.append({
            "frequency_hz": float(freqs[p]),
            "relative_db": float(rel_db[p]),
            "prominence_db": float(props["prominences"][oi]),
        })
    return result, mean_spec


def detect_onsets(flux: np.ndarray, flux_times: np.ndarray, sr: int, hop: int):
    if not len(flux):
        return np.array([]), {"threshold": 0.0}
    med = float(np.median(flux))
    mad = float(np.median(np.abs(flux - med)))
    sigma = 1.4826 * mad
    threshold = med + 2.5 * sigma if sigma > EPS else float(np.mean(flux) + np.std(flux))
    distance = max(1, int(round(0.08 * sr / hop)))
    prominence = max(sigma, float(np.std(flux)) * 0.25, EPS)
    peaks, _ = sps.find_peaks(flux, height=threshold, prominence=prominence, distance=distance)
    return flux_times[peaks], {"threshold": threshold, "mad": mad}


def estimate_tempo(flux: np.ndarray, sr: int, hop: int, min_bpm=50.0, max_bpm=200.0):
    if len(flux) < 8:
        return None, None
    env = np.maximum(np.asarray(flux, dtype=np.float64) - np.median(flux), 0.0)
    if np.max(env) < EPS:
        return None, None
    ac = sps.correlate(env, env, mode="full", method="fft")[len(env)-1:]
    frame_rate = sr / hop
    lag_min = max(1, int(frame_rate * 60 / max_bpm))
    lag_max = min(len(ac)-1, int(frame_rate * 60 / min_bpm))
    if lag_max <= lag_min:
        return None, None
    lag = lag_min + int(np.argmax(ac[lag_min:lag_max+1]))
    bpm = 60 * frame_rate / lag
    confidence = float(ac[lag] / (ac[0] + EPS))
    return float(bpm), confidence


TRANSITION_LABELS = [
    "energy shift",
    "spectral brightness sweep",
    "texture / bandwidth shift",
    "high-frequency reach shift",
    "transient-density shift",
    "spectral-flux burst",
    "stereo-space shift",
]


def build_motion(rms_db, centroid, bandwidth, rolloff, zcr, flux, width, dt):
    n = min(map(len, [rms_db, centroid, bandwidth, rolloff, zcr, flux, width]))
    rms_db, centroid, bandwidth, rolloff, zcr, flux, width = [
        np.asarray(x[:n], dtype=np.float64)
        for x in [rms_db, centroid, bandwidth, rolloff, zcr, flux, width]
    ]

    state_x = scale_01(centroid)  # brightness
    state_y = scale_01(rms_db)    # energy
    state_z = scale_01(width)     # stereo space

    features = np.vstack([
        robust_z(rms_db), robust_z(centroid), robust_z(bandwidth),
        robust_z(rolloff), robust_z(zcr), robust_z(flux), robust_z(width),
    ])
    smooth_frames = max(3, int(round(0.20 / max(dt, EPS))))
    smooth = np.vstack([moving_average(row, smooth_frames) for row in features])
    delta = np.diff(smooth, axis=1, prepend=smooth[:, :1])
    component_change = np.abs(delta) / max(dt, EPS)
    speed = np.sqrt(np.sum(delta * delta, axis=0)) / max(dt, EPS)
    speed = moving_average(speed, max(3, int(round(0.35 / max(dt, EPS)))))
    acceleration = np.diff(speed, prepend=speed[:1]) / max(dt, EPS)
    acceleration = moving_average(acceleration, max(3, int(round(0.20 / max(dt, EPS)))))
    return state_x, state_y, state_z, speed, acceleration, component_change


def detect_transitions(times, speed, component_change, max_candidates: int):
    if not len(times):
        return []
    n = min(len(times), len(speed), component_change.shape[1])
    times, speed = times[:n], speed[:n]
    dt = float(np.median(np.diff(times))) if len(times) > 1 else 0.023
    distance = max(1, int(round(2.0 / max(dt, EPS))))
    med = float(np.median(speed))
    mad = float(np.median(np.abs(speed - med)))
    prominence = max(1.4826 * mad, float(np.std(speed)) * 0.35, EPS)
    peaks, _ = sps.find_peaks(speed, distance=distance, prominence=prominence)
    if not len(peaks):
        peaks, _ = sps.find_peaks(speed, distance=distance)
    if not len(peaks):
        return []

    order = peaks[np.argsort(speed[peaks])[::-1]]
    denom = float(np.percentile(speed, 95)) + EPS
    out = []
    for p in order[:max_candidates]:
        dominant = int(np.argmax(component_change[:, p]))
        out.append({
            "time_s": float(times[p]),
            "transition_score": float(speed[p]),
            "normalized_magnitude": float(np.clip(speed[p] / denom, 0, 2)),
            "dominant_change": TRANSITION_LABELS[dominant],
        })
    return sorted(out, key=lambda row: row["time_s"])


def validate_resonance_anchors(annotation, mean_spec, freqs):
    if not annotation or not isinstance(annotation.get("resonance_anchors"), list):
        return []
    peak = float(np.max(mean_spec)) + EPS
    out = []
    for anchor in annotation["resonance_anchors"]:
        if not isinstance(anchor, dict):
            continue
        target = safe_float(anchor.get("frequency"))
        if target is None or target < 0:
            continue
        idx = int(np.argmin(np.abs(freqs - target)))
        rel_db = 20 * math.log10((float(mean_spec[idx]) + EPS) / peak)
        if rel_db >= -12:
            label = "strong spectral energy near declared frequency"
        elif rel_db >= -24:
            label = "moderate spectral energy near declared frequency"
        else:
            label = "weak spectral energy near declared frequency"
        out.append({
            "type": anchor.get("type"),
            "declared_frequency_hz": float(target),
            "nearest_fft_bin_hz": float(freqs[idx]),
            "relative_db": float(rel_db),
            "spectral_support": label,
        })
    return out


# ---------------------------------------------------------------------------
# Plot / export helpers
# ---------------------------------------------------------------------------

def summarize(x: np.ndarray) -> dict[str, float | None]:
    x = np.asarray(x, dtype=np.float64)
    x = x[np.isfinite(x)]
    if not len(x):
        return {"mean": None, "median": None, "p05": None, "p95": None, "max": None}
    return {
        "mean": float(np.mean(x)), "median": float(np.median(x)),
        "p05": float(np.percentile(x, 5)), "p95": float(np.percentile(x, 95)),
        "max": float(np.max(x)),
    }


def save_plots(track_dir, title, y, sr, times, freqs, S, rms_db, centroid,
               bandwidth, speed, acceleration, transitions, peaks, mean_spec):
    outputs = {}

    p = track_dir / "waveform.png"
    t_full = np.arange(len(y), dtype=np.float64) / sr
    down = max(1, len(y) // 5000)
    plt.figure(figsize=(11, 3)); plt.plot(t_full[::down], y[::down], linewidth=0.5)
    plt.title(f"{title} — waveform"); plt.xlabel("Time (s)"); plt.ylabel("Amplitude")
    plt.savefig(p, bbox_inches="tight", dpi=150); plt.close(); outputs["waveform"] = str(p)

    p = track_dir / "spectrogram_db.png"
    S_db = 20 * np.log10((S + EPS) / (np.max(S) + EPS))
    plt.figure(figsize=(11, 4)); plt.pcolormesh(times, freqs, S_db[:, :len(times)], shading="auto")
    plt.ylim(0, min(16000, sr/2)); plt.title(f"{title} — spectrogram")
    plt.xlabel("Time (s)"); plt.ylabel("Frequency (Hz)"); plt.colorbar(label="dB relative to peak")
    plt.savefig(p, bbox_inches="tight", dpi=150); plt.close(); outputs["spectrogram"] = str(p)

    p = track_dir / "energy_timeline.png"
    plt.figure(figsize=(11, 3)); plt.plot(times, rms_db)
    plt.title(f"{title} — RMS energy"); plt.xlabel("Time (s)"); plt.ylabel("RMS (dBFS-like)")
    plt.savefig(p, bbox_inches="tight", dpi=150); plt.close(); outputs["energy_timeline"] = str(p)

    p = track_dir / "spectral_motion.png"
    plt.figure(figsize=(11, 3)); plt.plot(times, centroid, label="Centroid"); plt.plot(times, bandwidth, label="Bandwidth")
    plt.title(f"{title} — spectral motion"); plt.xlabel("Time (s)"); plt.ylabel("Hz"); plt.legend()
    plt.savefig(p, bbox_inches="tight", dpi=150); plt.close(); outputs["spectral_motion"] = str(p)

    p = track_dir / "transition_field.png"
    abs_acc = np.abs(acceleration.copy())
    if np.max(abs_acc) > EPS and np.max(speed) > EPS:
        abs_acc = abs_acc / np.max(abs_acc) * np.max(speed)
    plt.figure(figsize=(11, 3)); plt.plot(times, speed, label="Transition speed"); plt.plot(times, abs_acc, label="|Acceleration| scaled")
    if transitions:
        ct = np.array([r["time_s"] for r in transitions]); cv = np.interp(ct, times, speed)
        plt.scatter(ct, cv, s=18, label="Candidate transitions")
    plt.title(f"{title} — acoustic transition field"); plt.xlabel("Time (s)"); plt.ylabel("Relative transition rate"); plt.legend()
    plt.savefig(p, bbox_inches="tight", dpi=150); plt.close(); outputs["transition_field"] = str(p)

    p = track_dir / "mean_spectrum_peaks.png"
    rel_db = 20 * np.log10((mean_spec + EPS) / (np.max(mean_spec) + EPS))
    plt.figure(figsize=(11, 3)); plt.plot(freqs, rel_db)
    for peak in peaks:
        plt.text(peak["frequency_hz"], peak["relative_db"], f'{peak["frequency_hz"]:.0f} Hz', fontsize=8, rotation=45)
    plt.xlim(0, min(16000, sr/2)); plt.title(f"{title} — mean spectrum peaks")
    plt.xlabel("Frequency (Hz)"); plt.ylabel("dB relative to peak")
    plt.savefig(p, bbox_inches="tight", dpi=150); plt.close(); outputs["mean_spectrum"] = str(p)

    return outputs


TIMELINE_COLUMNS = [
    "time_s", "rms", "rms_db", "centroid_hz", "bandwidth_hz", "rolloff85_hz",
    "zero_crossing_rate", "spectral_flux", "stereo_correlation", "stereo_width",
    "state_x_brightness", "state_y_energy", "state_z_space",
    "transition_speed", "transition_acceleration",
]


def write_timeline(path: Path, data: dict[str, np.ndarray]):
    n = min(len(data[k]) for k in TIMELINE_COLUMNS)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(TIMELINE_COLUMNS)
        for i in range(n):
            w.writerow([float(data[k][i]) for k in TIMELINE_COLUMNS])


def write_batch_csv(path: Path, summaries: list[dict[str, Any]]):
    columns = [
        "file", "title", "artist", "duration_s", "estimated_bpm", "tempo_confidence",
        "num_onsets", "median_rms_db", "median_centroid_hz", "median_bandwidth_hz",
        "median_stereo_width", "mean_transition_speed", "p95_transition_speed",
        "transition_candidates", "annotation_matched",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=columns); w.writeheader()
        for s in summaries:
            a = s.get("subjective_annotation") or {}; st = s["statistics"]
            w.writerow({
                "file": s["file"], "title": a.get("song_title") or Path(s["file"]).stem,
                "artist": a.get("artist"), "duration_s": s["duration_s"],
                "estimated_bpm": s["tempo"]["estimated_bpm"], "tempo_confidence": s["tempo"]["confidence"],
                "num_onsets": s["onsets"]["count"], "median_rms_db": st["rms_db"]["median"],
                "median_centroid_hz": st["centroid_hz"]["median"], "median_bandwidth_hz": st["bandwidth_hz"]["median"],
                "median_stereo_width": st["stereo_width"]["median"], "mean_transition_speed": st["transition_speed"]["mean"],
                "p95_transition_speed": st["transition_speed"]["p95"], "transition_candidates": len(s["transition_candidates"]),
                "annotation_matched": bool(a),
            })


def save_batch_plot(summaries: list[dict[str, Any]], path: Path):
    if len(summaries) < 2:
        return
    xs, ys, labels = [], [], []
    for s in summaries:
        x = s["statistics"]["centroid_hz"]["median"]
        y = s["statistics"]["transition_speed"]["mean"]
        if x is None or y is None:
            continue
        a = s.get("subjective_annotation") or {}
        xs.append(float(x)); ys.append(float(y)); labels.append(str(a.get("song_title") or Path(s["file"]).stem))
    if len(xs) < 2:
        return
    plt.figure(figsize=(8, 5)); plt.scatter(xs, ys)
    for x, y, label in zip(xs, ys, labels):
        plt.annotate(label, (x, y), xytext=(4, 4), textcoords="offset points", fontsize=8)
    plt.title("Batch comparison — brightness vs transition activity")
    plt.xlabel("Median spectral centroid (Hz)"); plt.ylabel("Mean acoustic transition speed")
    plt.savefig(path, bbox_inches="tight", dpi=150); plt.close()


# ---------------------------------------------------------------------------
# Per-track analysis
# ---------------------------------------------------------------------------

def analyze_track(audio_path: Path, output_root: Path, args, annotation):
    track_dir = output_root / f"{slugify(audio_path.stem)}_{source_id(audio_path)}"
    track_dir.mkdir(parents=True, exist_ok=True)

    y, left, right, sr, source_channels = load_audio(audio_path, args.target_sr)
    duration = len(y) / sr
    freqs, times, S = stft_frames(y, sr, args.n_fft, args.hop)

    rms = rms_frames(y, args.n_fft, args.hop)
    zcr = zcr_frames(y, args.n_fft, args.hop)
    centroid = spectral_centroid(S, freqs)
    bandwidth = spectral_bandwidth(S, freqs, centroid)
    rolloff = spectral_rolloff(S, freqs)
    flux_raw = spectral_flux(S)
    corr, width = stereo_features(left, right, args.n_fft, args.hop)

    n = min(len(times), len(rms), len(zcr), len(centroid), len(bandwidth), len(rolloff), len(corr), len(width))
    times, rms, zcr, centroid, bandwidth, rolloff, corr, width = [
        np.asarray(x[:n]) for x in [times, rms, zcr, centroid, bandwidth, rolloff, corr, width]
    ]
    rms_db = 20 * np.log10(np.maximum(rms, EPS))
    flux = align_length(np.concatenate([[0.0], flux_raw]), n)

    dt = float(np.median(np.diff(times))) if len(times) > 1 else args.hop / sr
    sx, sy, sz, speed, acceleration, component_change = build_motion(
        rms_db, centroid, bandwidth, rolloff, zcr, flux, width, dt
    )
    transitions = detect_transitions(times, speed, component_change, args.max_transitions)

    flux_onset = flux_raw[:max(0, len(times) - 1)]
    flux_times = times[1:1 + len(flux_onset)]
    onset_times, onset_detection = detect_onsets(flux_onset, flux_times, sr, args.hop)
    bpm, tempo_confidence = estimate_tempo(flux_raw, sr, args.hop)
    peaks, mean_spec = mean_spectrum_peaks(S, freqs, args.top_peaks)
    anchor_checks = validate_resonance_anchors(annotation, mean_spec, freqs)

    peak_amp = float(np.max(np.abs(y))) if len(y) else 0.0
    global_rms = float(np.sqrt(np.mean(y.astype(np.float64)**2))) if len(y) else 0.0
    crest_db = float(20 * math.log10((peak_amp + EPS)/(global_rms + EPS))) if global_rms > EPS else None
    clip_fraction = float(np.mean(np.abs(y) >= 0.999)) if len(y) else 0.0

    timeline = {
        "time_s": times, "rms": rms, "rms_db": rms_db, "centroid_hz": centroid,
        "bandwidth_hz": bandwidth, "rolloff85_hz": rolloff, "zero_crossing_rate": zcr,
        "spectral_flux": flux, "stereo_correlation": corr, "stereo_width": width,
        "state_x_brightness": sx, "state_y_energy": sy, "state_z_space": sz,
        "transition_speed": speed, "transition_acceleration": acceleration,
    }
    timeline_path = track_dir / "timeline.csv"
    write_timeline(timeline_path, timeline)

    plot_paths = {} if args.no_plots else save_plots(
        track_dir, audio_path.stem, y, sr, times, freqs, S, rms_db,
        centroid, bandwidth, speed, acceleration, transitions, peaks, mean_spec,
    )

    summary = {
        "schema": "phonic-drive-analysis-v2",
        "file": str(audio_path), "track_output_dir": str(track_dir),
        "duration_s": float(duration), "sr": int(sr), "source_channels": int(source_channels),
        "analysis_parameters": {"target_sr": args.target_sr, "n_fft": args.n_fft, "hop": args.hop, "frame_dt_s": dt},
        "signal_quality": {"peak_amplitude": peak_amp, "global_rms": global_rms, "crest_factor_db": crest_db, "clip_fraction": clip_fraction},
        "tempo": {"estimated_bpm": bpm, "confidence": tempo_confidence, "method": "spectral-flux autocorrelation"},
        "onsets": {"count": int(len(onset_times)), "times_s": onset_times.tolist(), "detection": onset_detection},
        "statistics": {
            "rms_db": summarize(rms_db), "centroid_hz": summarize(centroid), "bandwidth_hz": summarize(bandwidth),
            "rolloff85_hz": summarize(rolloff), "zero_crossing_rate": summarize(zcr), "spectral_flux": summarize(flux),
            "stereo_correlation": summarize(corr), "stereo_width": summarize(width),
            "transition_speed": summarize(speed), "transition_acceleration": summarize(acceleration),
        },
        "top_spectral_peaks": peaks,
        "transition_candidates": transitions,
        "state_space_axes": {
            "x": "spectral brightness / centroid, percentile-normalized",
            "y": "RMS energy, percentile-normalized",
            "z": "stereo spatial width, percentile-normalized",
            "note": "Export coordinates for visualization; not claims about cognition.",
        },
        "subjective_annotation": annotation,
        "declared_resonance_anchor_checks": anchor_checks,
        "outputs": {"timeline_csv": str(timeline_path), "plots": plot_paths},
    }
    summary_path = track_dir / "summary.json"
    summary["outputs"]["summary_json"] = str(summary_path)
    summary_path.write_text(json.dumps(json_ready(summary), indent=2, ensure_ascii=False), encoding="utf-8")
    return summary


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parser():
    p = argparse.ArgumentParser(
        description="Batch-capable Phonic Drive acoustic/state-space analyzer.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=r'''
Examples:
  python phonic_drive_analysis_v2.py "track.mp3"
  python phonic_drive_analysis_v2.py "a.mp3" "b.flac" "c.wav"
  python phonic_drive_analysis_v2.py "D:\Music\Phonic Drive" --recursive
  python phonic_drive_analysis_v2.py "D:\Music\Blackmill\*.mp3" "D:\Music\Audiomachine\*.flac"
  python phonic_drive_analysis_v2.py @tracks.txt
  python phonic_drive_analysis_v2.py "D:\Music\*.mp3" --annotations "lenses\*.yaml" "lenses\*.txt"
''')
    p.add_argument("inputs", nargs="+", help="Files, directories, globs, or @file-list paths")
    p.add_argument("--output", default="phonic_drive_batch", help="Output root directory")
    p.add_argument("--recursive", action="store_true", help="Recursively scan directories")
    p.add_argument("--annotations", nargs="*", default=[], help="Optional song_lens YAML/YML/TXT files, directories, or globs")
    p.add_argument("--target-sr", type=int, default=22050)
    p.add_argument("--n-fft", type=int, default=2048)
    p.add_argument("--hop", type=int, default=512)
    p.add_argument("--top-peaks", type=int, default=12)
    p.add_argument("--max-transitions", type=int, default=12)
    p.add_argument("--no-plots", action="store_true")
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    if args.target_sr <= 0 or args.n_fft < 128 or args.hop <= 0 or args.hop > args.n_fft:
        raise SystemExit("Invalid --target-sr / --n-fft / --hop values")

    files = resolve_inputs(args.inputs, args.recursive)
    if not files:
        print("No supported audio files found.", file=sys.stderr)
        return 2

    output_root = Path(args.output).expanduser()
    output_root.mkdir(parents=True, exist_ok=True)
    annotations, warnings = load_annotations(args.annotations)
    for warning in warnings:
        print(f"[WARN] {warning}", file=sys.stderr)

    print(f"Found {len(files)} audio file(s).")
    if annotations:
        print(f"Loaded {len(annotations)} song_lens annotation(s).")
    print(f"Output root: {output_root.resolve()}")

    summaries, errors = [], []
    for i, audio_path in enumerate(files, 1):
        print(f"[{i}/{len(files)}] {audio_path}")
        try:
            summary = analyze_track(audio_path, output_root, args, match_annotation(audio_path, annotations))
            summaries.append(summary)
            print(f"  -> {summary['track_output_dir']}")
        except Exception as exc:
            errors.append({"file": str(audio_path), "error": str(exc), "traceback": traceback.format_exc()})
            print(f"[ERROR] {audio_path}: {exc}", file=sys.stderr)

    batch_json = output_root / "batch_summary.json"
    batch_csv = output_root / "batch_summary.csv"
    run_json = output_root / "analysis_run.json"
    batch_json.write_text(json.dumps(json_ready(summaries), indent=2, ensure_ascii=False), encoding="utf-8")
    if summaries:
        write_batch_csv(batch_csv, summaries)
        if len(summaries) >= 2 and not args.no_plots:
            save_batch_plot(summaries, output_root / "batch_comparison.png")

    run = {
        "schema": "phonic-drive-analysis-run-v2",
        "requested_inputs": args.inputs, "resolved_audio_count": len(files),
        "successful_tracks": len(summaries), "failed_tracks": len(errors),
        "annotation_count": len(annotations), "annotation_warnings": warnings,
        "parameters": {"target_sr": args.target_sr, "n_fft": args.n_fft, "hop": args.hop,
                       "top_peaks": args.top_peaks, "max_transitions": args.max_transitions,
                       "recursive": args.recursive, "plots_enabled": not args.no_plots},
        "errors": errors,
    }
    run_json.write_text(json.dumps(json_ready(run), indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Completed: {len(summaries)} succeeded, {len(errors)} failed.")
    print(f"Batch JSON: {batch_json}")
    if summaries:
        print(f"Batch CSV:  {batch_csv}")
    print(f"Run log:   {run_json}")
    return 0 if summaries else 1


if __name__ == "__main__":
    raise SystemExit(main())
