"""Presentation-only bridge from Phonic Drive analysis artifacts to renderers.

The visual-state contract intentionally sits outside the scientific artifact
schemas. Renderers such as Godot may change mappings without changing A(t),
M(t), P(t), or K(t).
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import json
import os
import tempfile


@dataclass(slots=True)
class VisualState:
    time_s: float
    energy: float = 0.0
    brightness: float = 0.0
    stereo_width: float = 0.0
    transition_strength: float = 0.0
    compression: float = 0.0
    coherence: float = 0.0
    motif_activity: float = 0.0
    recurrence: float = 0.0
    response_active: bool = False
    response_type: str | None = None
    schema: str = "phonic-drive-visual-state-v1"

    def to_dict(self) -> dict:
        return asdict(self)


def write_visual_state(path: Path, state: VisualState) -> Path:
    """Atomically publish one renderer-facing visual-state snapshot."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(state.to_dict(), indent=2, ensure_ascii=False)
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)
    return path


def visual_state_from_frame(
    *,
    time_s: float,
    energy: float,
    brightness: float,
    stereo_width: float,
    transition_strength: float,
    compression: float = 0.0,
    coherence: float = 0.0,
    motif_activity: float = 0.0,
    recurrence: float = 0.0,
    response_type: str | None = None,
) -> VisualState:
    """Normalize caller-supplied presentation values into a renderer contract.

    Inputs should already be normalized presentation values in approximately
    [0, 1]. This function does not reinterpret scientific artifacts.
    """
    clip = lambda value: max(0.0, min(1.0, float(value)))
    return VisualState(
        time_s=float(time_s),
        energy=clip(energy),
        brightness=clip(brightness),
        stereo_width=clip(stereo_width),
        transition_strength=clip(transition_strength),
        compression=clip(compression),
        coherence=clip(coherence),
        motif_activity=clip(motif_activity),
        recurrence=clip(recurrence),
        response_active=response_type is not None,
        response_type=response_type,
    )
