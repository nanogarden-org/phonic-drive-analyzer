"""Deterministic audio transforms for Phonic Drive reconstruction/ablation trials.

Each function performs one narrowly described manipulation. The transform itself
is not evidence; provenance belongs in ``ReconstructionManifest``.
"""
from __future__ import annotations

import numpy as np
import scipy.signal as sps

EPS = 1e-12


def rms(values: np.ndarray) -> float:
    x = np.asarray(values, dtype=np.float64)
    return float(np.sqrt(np.mean(x * x))) if len(x) else 0.0


def rms_match(candidate: np.ndarray, reference: np.ndarray) -> np.ndarray:
    """Scale candidate to the reference RMS while preserving candidate shape."""
    x = np.asarray(candidate, dtype=np.float64)
    target = rms(reference)
    current = rms(x)
    if current < EPS or target < EPS:
        return np.zeros_like(x) if target < EPS else x.copy()
    return x * (target / current)


def reverse_time(audio: np.ndarray) -> np.ndarray:
    """Reverse sample order exactly."""
    return np.asarray(audio, dtype=np.float64)[::-1].copy()


def circular_shift(audio: np.ndarray, *, sr: int, shift_s: float) -> np.ndarray:
    """Circularly shift a waveform by a reproducible time offset."""
    if sr <= 0:
        raise ValueError("sr must be > 0")
    x = np.asarray(audio, dtype=np.float64)
    samples = int(round(float(shift_s) * sr))
    return np.roll(x, samples)


def spectral_ablation(
    audio: np.ndarray,
    *,
    sr: int,
    low_hz: float,
    high_hz: float,
    gain: float = 0.0,
) -> np.ndarray:
    """Attenuate one frequency interval using a whole-signal FFT mask.

    ``gain=0`` removes the selected band; ``gain=1`` leaves it unchanged.
    This is deliberately simple and deterministic for controlled experiments.
    """
    if sr <= 0:
        raise ValueError("sr must be > 0")
    if low_hz < 0 or high_hz <= low_hz or high_hz > sr / 2:
        raise ValueError("invalid ablation frequency range")
    if gain < 0:
        raise ValueError("gain must be >= 0")
    x = np.asarray(audio, dtype=np.float64)
    spec = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(len(x), d=1.0 / sr)
    mask = (freqs >= low_hz) & (freqs <= high_hz)
    spec[mask] *= float(gain)
    return np.fft.irfft(spec, n=len(x))


def segment_shuffle(
    audio: np.ndarray,
    *,
    sr: int,
    segment_s: float,
    seed: int,
) -> np.ndarray:
    """Shuffle fixed-duration segments while preserving samples inside segments."""
    if sr <= 0 or segment_s <= 0:
        raise ValueError("sr and segment_s must be > 0")
    x = np.asarray(audio, dtype=np.float64)
    segment_samples = max(1, int(round(segment_s * sr)))
    chunks = [x[i : i + segment_samples] for i in range(0, len(x), segment_samples)]
    if len(chunks) <= 1:
        return x.copy()
    rng = np.random.default_rng(int(seed))
    order = np.arange(len(chunks))
    rng.shuffle(order)
    return np.concatenate([chunks[i] for i in order])


def envelope_noise_control(audio: np.ndarray, *, seed: int) -> np.ndarray:
    """Preserve a smoothed amplitude envelope while replacing fine structure with noise."""
    x = np.asarray(audio, dtype=np.float64)
    if not len(x):
        return x.copy()
    envelope = np.abs(sps.hilbert(x))
    # Smooth over roughly 1% of the signal, bounded to remain usable for short clips.
    window = max(3, min(len(x), max(3, len(x) // 100)))
    if window % 2 == 0:
        window += 1
    if window > len(x):
        window = len(x) if len(x) % 2 == 1 else max(1, len(x) - 1)
    if window >= 3:
        envelope = sps.savgol_filter(envelope, window_length=window, polyorder=min(2, window - 1))
    rng = np.random.default_rng(int(seed))
    noise = rng.standard_normal(len(x))
    candidate = noise * np.maximum(envelope, 0.0)
    return rms_match(candidate, x)
