"""Regression parity tests for the first v0.3 core extraction.

These tests intentionally compare the new package functions against the v0.2
monolith. They are migration guards, not a claim that the v0.2 algorithms are
scientifically final.
"""

from __future__ import annotations

import numpy as np

import phonic_drive_analysis_v2 as legacy
from phonic_drive.core import (
    align_length,
    build_motion,
    detect_transitions,
    frame_signal,
    pad_short,
    rms_frames,
    robust_z,
    scale_01,
    spectral_bandwidth,
    spectral_centroid,
    spectral_flux,
    spectral_rolloff,
    stereo_features,
    stft_frames,
    zcr_frames,
)


def assert_array_equalish(a, b):
    np.testing.assert_allclose(np.asarray(a), np.asarray(b), rtol=1e-12, atol=1e-12, equal_nan=True)


def test_numerical_helpers_match_legacy():
    x = np.array([-8.0, -2.0, 0.0, 0.5, 2.0, 9.0, 30.0])
    assert_array_equalish(robust_z(x), legacy.robust_z(x))
    assert_array_equalish(scale_01(x), legacy.scale_01(x))
    assert_array_equalish(align_length(x[:3], 7), legacy.align_length(x[:3], 7))


def test_audio_framing_and_stft_match_legacy():
    sr = 22050
    t = np.arange(sr // 2, dtype=np.float64) / sr
    y = 0.65 * np.sin(2 * np.pi * 330.0 * t) + 0.15 * np.sin(2 * np.pi * 990.0 * t)

    assert_array_equalish(pad_short(y[:100], 256), legacy.pad_short(y[:100], 256))
    assert_array_equalish(frame_signal(y, 1024, 256), legacy.frame_signal(y, 1024, 256))
    assert_array_equalish(rms_frames(y, 1024, 256), legacy.rms_frames(y, 1024, 256))
    assert_array_equalish(zcr_frames(y, 1024, 256), legacy.zcr_frames(y, 1024, 256))

    new_freqs, new_times, new_S = stft_frames(y, sr, 1024, 256)
    old_freqs, old_times, old_S = legacy.stft_frames(y, sr, 1024, 256)
    assert_array_equalish(new_freqs, old_freqs)
    assert_array_equalish(new_times, old_times)
    assert_array_equalish(new_S, old_S)


def test_spectral_primitives_match_legacy():
    rng = np.random.default_rng(42017)
    S = np.abs(rng.normal(size=(64, 80))) + 1e-6
    freqs = np.linspace(0.0, 11025.0, S.shape[0])

    centroid_new = spectral_centroid(S, freqs)
    centroid_old = legacy.spectral_centroid(S, freqs)
    assert_array_equalish(centroid_new, centroid_old)
    assert_array_equalish(
        spectral_bandwidth(S, freqs, centroid_new),
        legacy.spectral_bandwidth(S, freqs, centroid_old),
    )
    assert_array_equalish(spectral_rolloff(S, freqs), legacy.spectral_rolloff(S, freqs))
    assert_array_equalish(spectral_flux(S), legacy.spectral_flux(S))


def test_stereo_features_match_legacy():
    sr = 22050
    t = np.arange(sr, dtype=np.float64) / sr
    left = 0.7 * np.sin(2 * np.pi * 220.0 * t)
    right = 0.5 * np.sin(2 * np.pi * 220.0 * t + 0.35) + 0.1 * np.sin(2 * np.pi * 440.0 * t)

    corr_new, width_new = stereo_features(left, right, 2048, 512)
    corr_old, width_old = legacy.stereo_features(left, right, 2048, 512)
    assert_array_equalish(corr_new, corr_old)
    assert_array_equalish(width_new, width_old)


def test_state_space_and_transitions_match_legacy():
    rng = np.random.default_rng(73)
    n = 180
    dt = 512 / 22050
    base = np.linspace(0.0, 1.0, n)

    rms_db = -28 + 8 * np.sin(base * 9) + rng.normal(0, 0.4, n)
    centroid = 1200 + 700 * np.sin(base * 11) + rng.normal(0, 30, n)
    bandwidth = 900 + 300 * np.cos(base * 7) + rng.normal(0, 20, n)
    rolloff = 3500 + 800 * np.sin(base * 5)
    zcr = 0.08 + 0.03 * np.sin(base * 13)
    flux = np.abs(np.sin(base * 19)) + rng.normal(0, 0.02, n)
    width = 0.25 + 0.18 * np.cos(base * 8)

    new = build_motion(rms_db, centroid, bandwidth, rolloff, zcr, flux, width, dt)
    old = legacy.build_motion(rms_db, centroid, bandwidth, rolloff, zcr, flux, width, dt)
    for a, b in zip(new, old):
        assert_array_equalish(a, b)

    times = np.arange(n) * dt
    assert detect_transitions(times, new[3], new[5], 12) == legacy.detect_transitions(times, old[3], old[5], 12)
