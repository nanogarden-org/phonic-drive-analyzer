"""Audio framing and transform primitives extracted from the v0.2 analyzer."""

from __future__ import annotations

import numpy as np
import scipy.signal as sps


def pad_short(y: np.ndarray, n_fft: int) -> np.ndarray:
    return y if len(y) >= n_fft else np.pad(y, (0, n_fft - len(y)))


def frame_signal(y: np.ndarray, frame_length: int, hop: int) -> np.ndarray:
    y = pad_short(np.asarray(y, dtype=np.float32), frame_length)
    return np.lib.stride_tricks.sliding_window_view(y, frame_length)[::hop]


def stft_frames(y: np.ndarray, sr: int, n_fft: int, hop: int):
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


def rms_frames(y: np.ndarray, n_fft: int, hop: int) -> np.ndarray:
    frames = frame_signal(y, n_fft, hop).astype(np.float64)
    return np.sqrt(np.mean(frames * frames, axis=1))


def zcr_frames(y: np.ndarray, n_fft: int, hop: int) -> np.ndarray:
    frames = frame_signal(y, n_fft, hop)
    signs = np.signbit(frames)
    return np.mean(signs[:, 1:] != signs[:, :-1], axis=1)
