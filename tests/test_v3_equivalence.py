import numpy as np

import phonic_drive_analysis_v2 as legacy
from phonic_drive.analysis import audio, features, transitions
from phonic_drive import cli


def test_frame_and_stft_equivalence():
    sr = 8000
    n_fft = 256
    hop = 64
    t = np.arange(sr, dtype=np.float64) / sr
    y = (0.5 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)

    np.testing.assert_allclose(
        audio.frame_signal(y, n_fft, hop),
        legacy.frame_signal(y, n_fft, hop),
        rtol=0,
        atol=0,
    )

    f_new, t_new, s_new = audio.stft_frames(y, sr, n_fft, hop)
    f_old, t_old, s_old = legacy.stft_frames(y, sr, n_fft, hop)
    np.testing.assert_allclose(f_new, f_old)
    np.testing.assert_allclose(t_new, t_old)
    np.testing.assert_allclose(s_new, s_old)


def test_feature_equivalence_on_synthetic_signal():
    sr = 8000
    n_fft = 256
    hop = 64
    t = np.arange(sr, dtype=np.float64) / sr
    left = (0.45 * np.sin(2 * np.pi * 220 * t) + 0.15 * np.sin(2 * np.pi * 880 * t)).astype(np.float32)
    right = (0.40 * np.sin(2 * np.pi * 220 * t + 0.2) + 0.12 * np.sin(2 * np.pi * 880 * t)).astype(np.float32)
    mono = ((left + right) / 2).astype(np.float32)

    freqs, _, S = audio.stft_frames(mono, sr, n_fft, hop)
    centroid_new = features.spectral_centroid(S, freqs)
    centroid_old = legacy.spectral_centroid(S, freqs)
    np.testing.assert_allclose(centroid_new, centroid_old)

    np.testing.assert_allclose(
        features.spectral_bandwidth(S, freqs, centroid_new),
        legacy.spectral_bandwidth(S, freqs, centroid_old),
    )
    np.testing.assert_allclose(features.spectral_rolloff(S, freqs), legacy.spectral_rolloff(S, freqs))
    np.testing.assert_allclose(features.spectral_flux(S), legacy.spectral_flux(S))
    np.testing.assert_allclose(features.rms_frames(mono, n_fft, hop), legacy.rms_frames(mono, n_fft, hop))
    np.testing.assert_allclose(features.zcr_frames(mono, n_fft, hop), legacy.zcr_frames(mono, n_fft, hop))

    corr_new, width_new = features.stereo_features(left, right, n_fft, hop)
    corr_old, width_old = legacy.stereo_features(left, right, n_fft, hop)
    np.testing.assert_allclose(corr_new, corr_old)
    np.testing.assert_allclose(width_new, width_old)


def test_transition_equivalence():
    n = 300
    t = np.linspace(0, 12, n)
    base = np.sin(t)
    rms_db = -24 + 4 * base
    centroid = 900 + 250 * np.sin(t * 0.7)
    bandwidth = 500 + 100 * np.cos(t * 0.5)
    rolloff = 2500 + 400 * np.sin(t * 0.4)
    zcr = 0.08 + 0.02 * np.sin(t * 1.3)
    flux = np.abs(np.sin(t * 1.9))
    width = 0.2 + 0.1 * np.cos(t * 0.9)
    dt = float(np.median(np.diff(t)))

    new = transitions.build_motion(rms_db, centroid, bandwidth, rolloff, zcr, flux, width, dt)
    old = legacy.build_motion(rms_db, centroid, bandwidth, rolloff, zcr, flux, width, dt)
    for a, b in zip(new, old):
        np.testing.assert_allclose(a, b)

    assert transitions.detect_transitions(t, new[3], new[5], 8) == legacy.detect_transitions(t, old[3], old[5], 8)


def test_cli_adapter_installs_extracted_functions():
    cli.install_v3_primitives()
    assert legacy.stft_frames is audio.stft_frames
    assert legacy.spectral_flux is features.spectral_flux
    assert legacy.build_motion is transitions.build_motion
