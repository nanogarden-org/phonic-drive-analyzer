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


def acoustic_summary(track: TrackAnalysis) -> dict:
    """Return a compact native A(t) summary without interpretive claims."""
    def stats(values: np.ndarray) -> dict:
        x = np.asarray(values, dtype=np.float64)
        return {
            "mean": float(np.mean(x)),
            "median": float(np.median(x)),
            "std": float(np.std(x)),
            "p05": float(np.percentile(x, 5)),
            "p95": float(np.percentile(x, 95)),
            "min": float(np.min(x)),
            "max": float(np.max(x)),
        }

    return {
        "schema": "phonic-drive-acoustic-v3alpha1",
        "source": str(track.source),
        "duration_s": track.duration_s,
        "sample_rate": int(track.sr),
        "source_channels": int(track.source_channels),
        "analysis_parameters": {
            "target_sr": int(track.target_sr),
            "n_fft": int(track.n_fft),
            "hop": int(track.hop),
            "frame_dt_s": track.dt,
        },
        "representation_note": "Measured acoustic telemetry only; axes and transitions are not claims about cognition or physiology.",
        "statistics": {
            "rms_db": stats(track.rms_db),
            "centroid_hz": stats(track.centroid),
            "bandwidth_hz": stats(track.bandwidth),
            "rolloff85_hz": stats(track.rolloff),
            "zero_crossing_rate": stats(track.zcr),
            "spectral_flux": stats(track.flux),
            "stereo_correlation": stats(track.stereo_correlation),
            "stereo_width": stats(track.stereo_width),
            "transition_speed": stats(track.transition_speed),
            "transition_acceleration": stats(track.transition_acceleration),
        },
        "state_space_axes": {
            "x": "spectral brightness / centroid, percentile-normalized",
            "y": "RMS energy, percentile-normalized",
            "z": "stereo spatial width, percentile-normalized",
        },
        "transition_candidates": track.transition_candidates,
    }


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


def write_acoustic_json(track: TrackAnalysis, path: Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(json_ready(acoustic_summary(track)), indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def write_acoustic_timeline(track: TrackAnalysis, path: Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    columns = [
        ("time_s", track.times),
        ("rms", track.rms),
        ("rms_db", track.rms_db),
        ("centroid_hz", track.centroid),
        ("bandwidth_hz", track.bandwidth),
        ("rolloff85_hz", track.rolloff),
        ("zero_crossing_rate", track.zcr),
        ("spectral_flux", track.flux),
        ("stereo_correlation", track.stereo_correlation),
        ("stereo_width", track.stereo_width),
        ("state_x_brightness", track.state_x),
        ("state_y_energy", track.state_y),
        ("state_z_space", track.state_z),
        ("transition_speed", track.transition_speed),
        ("transition_acceleration", track.transition_acceleration),
    ]
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow([name for name, _ in columns])
        for i in range(len(track.times)):
            writer.writerow([float(values[i]) for _, values in columns])
    return path


def write_transitions_json(track: TrackAnalysis, path: Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "phonic-drive-transitions-v3alpha1",
        "source": str(track.source),
        "transition_candidates": track.transition_candidates,
    }
    path.write_text(json.dumps(json_ready(payload), indent=2, ensure_ascii=False), encoding="utf-8")
    return path


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


def write_motifs_json(track: TrackAnalysis, path: Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "phonic-drive-motifs-v3alpha1",
        "source": str(track.source),
        "motifs": track.motif_candidates,
        "recurring_pairs": track.recurring_motif_pairs,
    }
    path.write_text(json.dumps(json_ready(payload), indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def write_relationships_npz(track: TrackAnalysis, path: Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, times=track.times, band_edges_hz=track.band_edges_hz, relationships=track.relationships)
    return path


def write_v3_bundle(track: TrackAnalysis, output_dir: Path) -> dict[str, str]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "acoustic_json": write_acoustic_json(track, output_dir / "acoustic_summary.json"),
        "acoustic_timeline_csv": write_acoustic_timeline(track, output_dir / "acoustic_timeline.csv"),
        "transitions_json": write_transitions_json(track, output_dir / "transitions.json"),
        "structural_json": write_structural_json(track, output_dir / "structural_analysis.json"),
        "structural_timeline_csv": write_structural_timeline(track, output_dir / "structural_timeline.csv"),
        "motifs_json": write_motifs_json(track, output_dir / "motifs.json"),
        "relationships_npz": write_relationships_npz(track, output_dir / "relationships.npz"),
    }
    return {key: str(value) for key, value in outputs.items()}
