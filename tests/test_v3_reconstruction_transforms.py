from __future__ import annotations

import numpy as np

from phonic_drive.reconstruction import (
    ReconstructionManifest,
    TransformStep,
    apply_manifest,
    circular_shift,
    envelope_noise_control,
    reverse_time,
    rms,
    rms_match,
    segment_shuffle,
    spectral_ablation,
)


def test_reverse_and_shift_are_deterministic():
    x = np.arange(8, dtype=float)
    assert np.array_equal(reverse_time(x), x[::-1])
    assert np.array_equal(circular_shift(x, sr=4, shift_s=0.5), np.roll(x, 2))


def test_rms_match_matches_reference_level():
    reference = np.ones(100)
    candidate = np.full(100, 0.25)
    matched = rms_match(candidate, reference)
    assert abs(rms(matched) - rms(reference)) < 1e-12


def test_segment_shuffle_repeats_with_same_seed():
    x = np.arange(20, dtype=float)
    a = segment_shuffle(x, sr=10, segment_s=0.5, seed=42)
    b = segment_shuffle(x, sr=10, segment_s=0.5, seed=42)
    assert np.array_equal(a, b)
    assert sorted(a.tolist()) == sorted(x.tolist())


def test_spectral_ablation_reduces_selected_tone():
    sr = 1000
    t = np.arange(sr, dtype=float) / sr
    x = np.sin(2 * np.pi * 50 * t) + np.sin(2 * np.pi * 200 * t)
    y = spectral_ablation(x, sr=sr, low_hz=40, high_hz=60, gain=0.0)
    spec = np.abs(np.fft.rfft(y))
    freqs = np.fft.rfftfreq(len(y), 1 / sr)
    amp_50 = spec[np.argmin(np.abs(freqs - 50))]
    amp_200 = spec[np.argmin(np.abs(freqs - 200))]
    assert amp_50 < amp_200 * 0.01


def test_envelope_noise_control_is_reproducible_and_rms_matched():
    x = np.sin(np.linspace(0, 30, 1000)) * np.linspace(0.2, 1.0, 1000)
    a = envelope_noise_control(x, seed=7)
    b = envelope_noise_control(x, seed=7)
    assert np.allclose(a, b)
    assert abs(rms(a) - rms(x)) < 1e-10


def test_manifest_executes_declared_steps_in_order():
    x = np.arange(12, dtype=float)
    manifest = ReconstructionManifest(
        reconstruction_id="R1",
        source_stimulus_id="S1",
        source_motif_ids=["M1"],
        hypothesis_id="H1",
        steps=[
            TransformStep("reverse_time"),
            TransformStep("circular_shift", parameters={"shift_s": 0.5}),
        ],
    )
    y = apply_manifest(x, sr=4, manifest=manifest)
    expected = np.roll(x[::-1], 2)
    assert np.array_equal(y, expected)
