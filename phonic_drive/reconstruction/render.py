"""Execute reconstruction manifests against mono audio arrays or source files."""
from __future__ import annotations

from pathlib import Path

import numpy as np
from scipy.io import wavfile

from ..analysis.audio import load_audio
from .protocol import ReconstructionManifest, TransformStep
from .transforms import (
    circular_shift,
    envelope_noise_control,
    reverse_time,
    rms_match,
    segment_shuffle,
    spectral_ablation,
)


def apply_step(audio: np.ndarray, *, sr: int, step: TransformStep, reference: np.ndarray | None = None) -> np.ndarray:
    """Apply one manifest step using an explicit operation registry."""
    op = step.operation
    p = step.parameters
    if op == "reverse_time":
        return reverse_time(audio)
    if op == "circular_shift":
        return circular_shift(audio, sr=sr, shift_s=float(p["shift_s"]))
    if op == "spectral_ablation":
        return spectral_ablation(
            audio,
            sr=sr,
            low_hz=float(p["low_hz"]),
            high_hz=float(p["high_hz"]),
            gain=float(p.get("gain", 0.0)),
        )
    if op == "segment_shuffle":
        return segment_shuffle(audio, sr=sr, segment_s=float(p["segment_s"]), seed=int(p["seed"]))
    if op == "envelope_noise_control":
        return envelope_noise_control(audio, seed=int(p["seed"]))
    if op == "rms_match":
        if reference is None:
            raise ValueError("rms_match requires a reference array")
        return rms_match(audio, reference)
    raise ValueError(f"unsupported reconstruction operation: {op}")


def apply_manifest(audio: np.ndarray, *, sr: int, manifest: ReconstructionManifest) -> np.ndarray:
    """Apply a manifest sequentially, keeping the original as RMS reference."""
    original = np.asarray(audio, dtype=np.float64)
    transformed = original.copy()
    for step in manifest.steps:
        transformed = apply_step(transformed, sr=sr, step=step, reference=original)
    return transformed


def render_manifest(
    source_path: Path,
    manifest: ReconstructionManifest,
    output_path: Path,
    *,
    target_sr: int = 22050,
) -> Path:
    """Load a source stimulus, execute its manifest, and write a float32 WAV."""
    source_path = Path(source_path)
    mono, _, _, sr, _ = load_audio(source_path, target_sr)
    transformed = apply_manifest(mono, sr=sr, manifest=manifest)
    peak = float(np.max(np.abs(transformed))) if len(transformed) else 0.0
    if peak > 1.0:
        transformed = transformed / peak
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    wavfile.write(output_path, sr, transformed.astype(np.float32))
    manifest.output_path = str(output_path)
    return output_path
