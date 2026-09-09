"""Numerical helpers extracted from the v0.2 analyzer.

Behavior is intentionally kept equivalent to the legacy implementation during
this migration tranche.
"""

from __future__ import annotations

import numpy as np

EPS = 1e-12


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
