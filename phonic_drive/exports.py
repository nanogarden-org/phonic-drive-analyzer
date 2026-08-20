"""Artifact writers for Phonic Drive v3."""
from __future__ import annotations

import csv
import json
from pathlib import Path
import numpy as np

from .track import TrackAnalysis


def json_ready(value):
    if isinstance(value, dict):
        return {str(k): json_ready(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_ready(v) for v in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    return value


def structural_summary(track: TrackAnalysis) -> dict:
    return {
        "schema": "phonic-drive-structural-v3alpha2",
        "source": str(track.source),
        "analysis_parameters": {
            "sample_rate": track.sr,
            "target_sr": track.target_sr,
            "n_fft": track.n_fft,
            "hop": track.hop,
            "frame_dt_s": track.dt,
            "band_edges_hz": track.band_edges_hz,
        },
        "representation_note": "Descriptive acoustic structure only; no perceptual, physiological, or causal claim is implied.",
        "frames": int(track.band_trajectories.shape[1]),
        "band_trajectory_summary": {
            "mean": np.mean(track.band_trajectories, axis=1),
            "std": np.std(track.band_trajectories, axis=1),
            "mean_abs_velocity": np.mean(np.abs(track.band_velocity), axis=1),
            "mean_abs_acceleration": np.mean(np.abs(track.band_acceleration), axis=1),
        },
        "mean_cross_band_relationship": np.mean(track.relationships, axis=0),
        "motif_candidates": track.motif_candidates,
        "recurring_motif_pairs": track.recurring_motif_pairs,
    }


def write_structural_json(track: TrackAnalysis, path: Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(json_ready(structural_summary(track)), indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def write_structural_timeline(track: TrackAnalysis, path: Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    bands = track.band_trajectories.shape[0]
    header = ["time_s"]
    for i in range(bands):
        header += [f"band_{i:02d}_energy", f"band_{i:02d}_velocity", f"band_{i:02d}_acceleration"]
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(header)
        for t in range(len(track.times)):
            row = [float(track.times[t])]
            for i in range(bands):
                row += [float(track.band_trajectories[i,t]), float(track.band_velocity[i,t]), float(track.band_acceleration[i,t])]
            writer.writerow(row)
    return path
