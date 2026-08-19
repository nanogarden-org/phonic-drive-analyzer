from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class AcousticFrame:
    """One measured acoustic state sample A(t).

    Values here are measurements or direct transforms of measurements. Subjective
    labels do not belong in this object.
    """

    time_s: float
    features: dict[str, float]
    band_energy: tuple[float, ...] = ()
    band_edges_hz: tuple[float, ...] = ()


@dataclass(frozen=True)
class MotifEvent:
    """A descriptive structural event M(t) derived from acoustic measurements."""

    motif_id: str
    start_s: float
    end_s: float
    topology: tuple[str, ...]
    relationships: dict[str, float] = field(default_factory=dict)
    confidence: float | None = None
    provenance: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ResponseEvent:
    """A participant-authored or participant-triggered event P(t)."""

    time_s: float
    response_type: str
    intensity: float | None = None
    body_region: str | None = None
    confidence: float | None = None
    note: str | None = None


@dataclass(frozen=True)
class TrialRecord:
    """Conditions and provenance T for a listening / reconstruction trial."""

    trial_id: str
    stimulus_id: str
    session_id: str
    transform_id: str | None = None
    randomization_index: int | None = None
    analyzer_version: str | None = None
    schema_version: str = "1.0"
    metadata: dict[str, Any] = field(default_factory=dict)
