"""Audio loading and framing primitives for Phonic Drive v3.

These functions are behavior-preserving extractions from the v2 analyzer.  They
contain no interpretation logic: their job is to decode audio, normalize sample
arrays, resample when requested, and expose deterministic frame/STFT helpers.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import scipy.signal as sps
from pydub import AudioSegment


def load_audio(path: Path, target_sr: int) -> tuple[np.ndarray, np.ndarray, np.ndarray, int, int]:
    """Decode an audio file and return mono/left/right floating arrays.

    Returns ``(mono, left, right, sample_rate, source_channels)``.  Stereo and
    mono sources are normalized to approximately [-1, 1].  Resampling uses the
    same polyphase method as the v2 implementation.
    """
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
    """Pad audio shorter than one FFT frame."""
    return y if len(y) >= n_fft else np.pad(y, (0, n_fft - len(y)))


def frame_signal(y: np.ndarray, frame_length: int, hop: int) -> np.ndarray:
    """Create overlapping analysis frames using the v2 stride convention."""
    y = pad_short(np.asarray(y, dtype=np.float32), frame_length)
    return np.lib.stride_tricks.sliding_window_view(y, frame_length)[::hop]


def stft_frames(y: np.ndarray, sr: int, n_fft: int, hop: int):
    """Return frequency bins, frame times, and STFT magnitudes."""
    y = pad_short(y, n_fft)
    window = sps.get_window("hann", n_fft, fftbins=True)
    freqs, times, zxx = sps.stft(
        y,
        fs=sr,
        window=window,
        nperseg=n_fft,
        noverlap=n_fft - hop,
        nfft=n_fft,
        boundary=None,
        padded=False,
    )
    return freqs, times, np.abs(zxx)
