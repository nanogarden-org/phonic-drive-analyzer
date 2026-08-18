"""Stereo-field analysis extracted from the v0.2 analyzer."""

from __future__ import annotations

import numpy as np

from .numerics import EPS


def _pad_short(y: np.ndarray, frame_length: int) -> np.ndarray:
    return y if len(y) >= frame_length else np.pad(y, (0, frame_length - len(y)))


def _frame_signal(y: np.ndarray, frame_length: int, hop: int) -> np.ndarray:
    y = _pad_short(np.asarray(y, dtype=np.float32), frame_length)
    return np.lib.stride_tricks.sliding_window_view(y, frame_length)[::hop]


def stereo_features(left: np.ndarray, right: np.ndarray, n_fft: int, hop: int):
    lf = _frame_signal(left, n_fft, hop).astype(np.float64)
    rf = _frame_signal(right, n_fft, hop).astype(np.float64)
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
