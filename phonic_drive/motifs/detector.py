"""Candidate motif segmentation and recurrence scoring.

The detector operates on multiband trajectories produced by
``phonic_drive.analysis.bands``.  It deliberately uses descriptive structural
quantities only: local trajectory speed, band-state shape, and band-direction
shape.  No user-response labels are used here.
"""

from __future__ import annotations

import numpy as np
import scipy.signal as sps

EPS = 1e-12


def _normalize_signature(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64)
    norm = float(np.linalg.norm(x))
    return x / (norm + EPS)


def detect_motif_candidates(
    band_values: np.ndarray,
    times_s: np.ndarray,
    *,
    half_window_s: float = 1.5,
    min_separation_s: float = 1.0,
    max_candidates: int = 24,
) -> list[dict]:
    """Segment candidate motifs around peaks in multiband trajectory speed.

    Each signature concatenates two descriptive components:

    - mean normalized band-state shape inside the event window;
    - net band-direction change from window start to end.

    The signature is suitable for recurrence comparison within or across tracks,
    but is not a biological or perceptual representation.
    """
    values = np.asarray(band_values, dtype=np.float64)
    times = np.asarray(times_s, dtype=np.float64)
    if values.ndim != 2:
        raise ValueError("band_values must be 2D [band, frame]")
    if times.ndim != 1 or len(times) != values.shape[1]:
        raise ValueError("times_s must match the frame dimension")
    if len(times) < 3:
        return []
    if half_window_s <= 0 or min_separation_s <= 0:
        raise ValueError("window and separation values must be > 0")

    dt = float(np.median(np.diff(times)))
    delta = np.diff(values, axis=1, prepend=values[:, :1])
    speed = np.sqrt(np.sum(delta * delta, axis=0)) / max(dt, EPS)

    med = float(np.median(speed))
    mad = float(np.median(np.abs(speed - med)))
    prominence = max(1.4826 * mad, float(np.std(speed)) * 0.35, EPS)
    distance = max(1, int(round(min_separation_s / max(dt, EPS))))
    peaks, _ = sps.find_peaks(speed, prominence=prominence, distance=distance)
    if not len(peaks):
        peaks, _ = sps.find_peaks(speed, distance=distance)
    if not len(peaks):
        return []

    ranked = peaks[np.argsort(speed[peaks])[::-1]][:max_candidates]
    radius = max(1, int(round(half_window_s / max(dt, EPS))))
    scale = float(np.percentile(speed, 95)) + EPS
    motifs = []

    for rank, peak in enumerate(ranked, 1):
        start = max(0, int(peak) - radius)
        end = min(values.shape[1] - 1, int(peak) + radius)
        window = values[:, start : end + 1]

        mean_state = np.mean(window, axis=1)
        state_total = float(np.sum(mean_state))
        if state_total > EPS:
            mean_state = mean_state / state_total
        direction = window[:, -1] - window[:, 0]
        signature = _normalize_signature(np.concatenate([mean_state, direction]))

        motifs.append({
            "candidate_id": f"motif-{rank:03d}",
            "start_s": float(times[start]),
            "end_s": float(times[end]),
            "peak_s": float(times[peak]),
            "trajectory_speed": float(speed[peak]),
            "normalized_magnitude": float(np.clip(speed[peak] / scale, 0.0, 2.0)),
            "mean_band_state": mean_state.tolist(),
            "net_band_direction": direction.tolist(),
            "signature": signature.tolist(),
            "label": "acoustic motif candidate",
        })

    return sorted(motifs, key=lambda row: row["peak_s"])


def motif_similarity_matrix(motifs: list[dict]) -> np.ndarray:
    """Return cosine-similarity matrix for motif signatures."""
    if not motifs:
        return np.zeros((0, 0), dtype=np.float64)
    signatures = np.asarray([m["signature"] for m in motifs], dtype=np.float64)
    norms = np.linalg.norm(signatures, axis=1, keepdims=True)
    normalized = signatures / (norms + EPS)
    sim = normalized @ normalized.T
    return np.clip(sim, -1.0, 1.0)


def recurring_pairs(motifs: list[dict], *, threshold: float = 0.92) -> list[dict]:
    """Return motif pairs whose structural signatures exceed a similarity threshold."""
    if not -1.0 <= threshold <= 1.0:
        raise ValueError("threshold must be between -1 and 1")
    sim = motif_similarity_matrix(motifs)
    pairs = []
    for i in range(len(motifs)):
        for j in range(i + 1, len(motifs)):
            if sim[i, j] >= threshold:
                pairs.append({
                    "a": motifs[i]["candidate_id"],
                    "b": motifs[j]["candidate_id"],
                    "similarity": float(sim[i, j]),
                    "delta_peak_s": float(motifs[j]["peak_s"] - motifs[i]["peak_s"]),
                })
    return pairs
