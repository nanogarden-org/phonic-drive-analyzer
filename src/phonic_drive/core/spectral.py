"""Spectral-analysis primitives extracted from the v0.2 analyzer."""

from __future__ import annotations

import numpy as np
import scipy.signal as sps

from .numerics import EPS


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
