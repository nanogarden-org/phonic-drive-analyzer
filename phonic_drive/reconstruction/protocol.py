"""Provenance contracts for reconstruction and ablation stimuli.

This module records *what* was changed and why before synthesis/rendering code is
added. The goal is to make every experimental stimulus traceable to its source
motif and hypothesis.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
import json


@dataclass(slots=True)
class TransformStep:
    operation: str
    parameters: dict = field(default_factory=dict)
    preserves: list[str] = field(default_factory=list)
    disrupts: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ReconstructionManifest:
    reconstruction_id: str
    source_stimulus_id: str
    source_motif_ids: list[str]
    hypothesis_id: str | None
    steps: list[TransformStep]
    output_path: str | None = None
    schema: str = "phonic-drive-reconstruction-v3alpha1"

    def write_json(self, path: Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(self), indent=2, ensure_ascii=False), encoding="utf-8")
        return path


def ablation_manifest(
    *,
    reconstruction_id: str,
    source_stimulus_id: str,
    source_motif_ids: list[str],
    hypothesis_id: str | None,
    preserve: list[str],
    disrupt: list[str],
    operation: str = "structural_ablation",
    parameters: dict | None = None,
) -> ReconstructionManifest:
    """Create a traceable transform specification for a controlled ablation."""
    step = TransformStep(
        operation=operation,
        parameters=dict(parameters or {}),
        preserves=list(preserve),
        disrupts=list(disrupt),
    )
    return ReconstructionManifest(
        reconstruction_id=reconstruction_id,
        source_stimulus_id=source_stimulus_id,
        source_motif_ids=list(source_motif_ids),
        hypothesis_id=hypothesis_id,
        steps=[step],
    )
