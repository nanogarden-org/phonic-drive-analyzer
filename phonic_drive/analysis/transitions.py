"""Acoustic state-space motion and transition detection for Phonic Drive v3."""

from __future__ import annotations

import numpy as np
import scipy.signal as sps

EPS = 1e-12

TRANSITION_LABELS = [
    "energy shift",
    "spectral brightness sweep",
    "texture / bandwidth shift",
    "high-frequency reach shift",
    "transient-density shift",
    "spectral-flux burst",
    "stereo-space shift",
]


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


def build_motion(rms_db, centroid, bandwidth, rolloff, zcr, flux, width, dt):
    n = min(map(len, [rms_db, centroid, bandwidth, rolloff, zcr, flux, width]))
    rms_db, centroid, bandwidth, rolloff, zcr, flux, width = [
        np.asarray(x[:n], dtype=np.float64)
        for x in [rms_db, centroid, bandwidth, rolloff, zcr, flux, width]
    ]

    state_x = scale_01(centroid)
    state_y = scale_01(rms_db)
    state_z = scale_01(width)

    features = np.vstack([
        robust_z(rms_db),
        robust_z(centroid),
        robust_z(bandwidth),
        robust_z(rolloff),
        robust_z(zcr),
        robust_z(flux),
        robust_z(width),
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
