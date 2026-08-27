"""Measured acoustic feature extraction for Phonic Drive v3.

This module contains only signal-derived quantities.  It intentionally does not
attach perceptual, biological, or causal meaning to those quantities.
"""

from __future__ import annotations

import numpy as np

from .audio import frame_signal

EPS = 1e-12


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
    corr = cov / (
        np.sqrt(np.mean(l0 * l0, axis=1)) * np.sqrt(np.mean(r0 * r0, axis=1)) + EPS
    )
    corr = np.clip(corr, -1.0, 1.0)

    mid = 0.5 * (lf + rf)
    side = 0.5 * (lf - rf)
    width = np.sqrt(np.mean(side * side, axis=1)) / (
        np.sqrt(np.mean(mid * mid, axis=1)) + EPS
    )
    return corr, width
