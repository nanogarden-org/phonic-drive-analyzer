"""Experimental v3 structural-analysis pipeline.

This module converts an audio file into multiband trajectories, temporal
relationships, and descriptive motif candidates.  It is intentionally separate
from participant-response interpretation.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from .analysis.audio import load_audio, stft_frames
from .analysis.bands import (
    band_energy_trajectories,
    logarithmic_band_edges,
    rolling_relationships,
    temporal_derivatives,
)
from .motifs import detect_motif_candidates, recurring_pairs


def analyze_audio_structure(
    audio_path: Path,
    *,
    target_sr: int = 22050,
    n_fft: int = 2048,
    hop: int = 512,
    bands: int = 10,
    min_hz: float = 20.0,
    relationship_window_s: float = 2.0,
    motif_half_window_s: float = 1.5,
) -> dict:
    """Return v3 structural telemetry for one audio file."""
    y, _, _, sr, _ = load_audio(Path(audio_path), target_sr)
    freqs, times, spectrum = stft_frames(y, sr, n_fft, hop)
    if len(times) < 2:
        raise ValueError("Audio is too short for structural analysis")

    max_hz = min(float(sr) / 2.0, float(freqs[-1]))
    lower = max(float(min_hz), float(freqs[1]) if len(freqs) > 1 else float(min_hz))
    if max_hz <= lower:
        raise ValueError("No usable frequency span for structural analysis")

    edges = logarithmic_band_edges(lower, max_hz, bands)
    trajectories = band_energy_trajectories(spectrum, freqs, edges, normalize_per_frame=True)
    dt = float(np.median(np.diff(times)))
    velocity, acceleration = temporal_derivatives(trajectories, dt)
    relationship_frames = max(2, int(round(relationship_window_s / dt)))
    relationships = rolling_relationships(trajectories, relationship_frames)
    motifs = detect_motif_candidates(
        trajectories,
        times,
        half_window_s=motif_half_window_s,
    )
    recurrence = recurring_pairs(motifs)

    # Store relationship summaries rather than the full frames×bands×bands cube
    # in the default JSON. Full arrays can be added later as NPZ/CSV artifacts.
    mean_relationship = np.mean(relationships, axis=0)

    return {
        "schema": "phonic-drive-structural-v3alpha1",
        "source": str(Path(audio_path)),
        "analysis_parameters": {
            "target_sr": int(target_sr),
            "sample_rate": int(sr),
            "n_fft": int(n_fft),
            "hop": int(hop),
            "frame_dt_s": dt,
            "bands": int(bands),
            "band_edges_hz": edges.tolist(),
            "relationship_window_s": float(relationship_window_s),
            "motif_half_window_s": float(motif_half_window_s),
        },
        "representation_note": (
            "Band trajectories, relationships, and motif candidates are descriptive acoustic structures; "
            "they do not establish perceptual, physiological, or causal effects."
        ),
        "frames": int(trajectories.shape[1]),
        "band_trajectory_summary": {
            "mean": np.mean(trajectories, axis=1).tolist(),
            "std": np.std(trajectories, axis=1).tolist(),
            "mean_abs_velocity": np.mean(np.abs(velocity), axis=1).tolist(),
            "mean_abs_acceleration": np.mean(np.abs(acceleration), axis=1).tolist(),
        },
        "mean_cross_band_relationship": mean_relationship.tolist(),
        "motif_candidates": motifs,
        "recurring_motif_pairs": recurrence,
    }


def write_structural_analysis(audio_path: Path, output_path: Path, **kwargs) -> dict:
    """Analyze one file and write a JSON artifact."""
    result = analyze_audio_structure(audio_path, **kwargs)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    return result
