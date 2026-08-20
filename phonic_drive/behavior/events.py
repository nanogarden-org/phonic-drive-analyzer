"""Behavioral telemetry stream K(t) for Phonic Drive v3.

These records describe observable workflow/input behavior synchronized to a
session clock. They are not treated as cognitive-state measurements.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json
import time


@dataclass(slots=True)
class BehaviorEvent:
    session_time_s: float
    event_type: str
    value: float | str | None = None
    unit: str | None = None
    source: str | None = None
    note: str | None = None


class BehaviorRecorder:
    """Minimal monotonic-clock recorder suitable for keyboard/workflow adapters."""
    def __init__(self) -> None:
        self._started = time.monotonic()
        self.events: list[BehaviorEvent] = []

    @property
    def elapsed_s(self) -> float:
        return time.monotonic() - self._started

    def mark(
        self,
        event_type: str,
        *,
        value: float | str | None = None,
        unit: str | None = None,
        source: str | None = None,
        note: str | None = None,
    ) -> BehaviorEvent:
        event = BehaviorEvent(
            session_time_s=self.elapsed_s,
            event_type=event_type,
            value=value,
            unit=unit,
            source=source,
            note=note,
        )
        self.events.append(event)
        return event

    def write_json(self, path: Path, *, session_id: str | None = None) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema": "phonic-drive-behavior-events-v3alpha1",
            "session_id": session_id,
            "events": [asdict(event) for event in self.events],
            "note": "Behavioral telemetry is an observed K(t) stream, not a direct cognitive-state label.",
        }
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return path
