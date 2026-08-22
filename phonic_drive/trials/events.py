"""Participant event capture and alignment utilities.

These records preserve what a participant reported and when. They do not infer
cause. Alignment functions only compute temporal proximity to measured acoustic
or motif events.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json
import time


@dataclass(slots=True)
class ResponseEvent:
    session_time_s: float
    response_type: str
    intensity: float | None = None
    region: str | None = None
    confidence: float | None = None
    note: str | None = None


class EventRecorder:
    """Simple monotonic-clock event recorder suitable for hotkey/UI front ends."""
    def __init__(self) -> None:
        self._started = time.monotonic()
        self.events: list[ResponseEvent] = []

    @property
    def elapsed_s(self) -> float:
        return time.monotonic() - self._started

    def mark(
        self,
        response_type: str,
        *,
        intensity: float | None = None,
        region: str | None = None,
        confidence: float | None = None,
        note: str | None = None,
    ) -> ResponseEvent:
        event = ResponseEvent(
            session_time_s=self.elapsed_s,
            response_type=response_type,
            intensity=intensity,
            region=region,
            confidence=confidence,
            note=note,
        )
        self.events.append(event)
        return event

    def write_json(self, path: Path, *, trial_id: str | None = None, stimulus: str | None = None) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema": "phonic-drive-response-events-v3alpha1",
            "trial_id": trial_id,
            "stimulus": stimulus,
            "events": [asdict(event) for event in self.events],
            "note": "Participant reports are observations, not causal labels.",
        }
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return path


def event_windows(event: ResponseEvent, *, pre_s: tuple[float, ...] = (0.25, 0.5, 1, 2, 5, 10), post_s: float = 3.0) -> list[dict]:
    """Return canonical pre/post windows around one participant marker."""
    return [
        {
            "pre_s": float(pre),
            "post_s": float(post_s),
            "start_s": max(0.0, event.session_time_s - float(pre)),
            "event_s": event.session_time_s,
            "end_s": event.session_time_s + float(post_s),
        }
        for pre in pre_s
    ]


def _motif_peak(motif: dict) -> float | None:
    """Read the canonical v3 motif peak with compatibility fallbacks."""
    for key in ("peak_s", "peak_time_s", "time_s"):
        value = motif.get(key)
        if value is not None:
            return float(value)
    return None


def _motif_id(motif: dict) -> str | None:
    """Read the canonical v3 candidate id with compatibility fallback."""
    value = motif.get("candidate_id", motif.get("id"))
    return str(value) if value is not None else None


def nearest_motifs(event: ResponseEvent, motifs: list[dict], *, max_lag_s: float = 10.0) -> list[dict]:
    """Find motif candidates whose peak precedes or closely follows a response event."""
    matches = []
    for motif in motifs:
        peak = _motif_peak(motif)
        if peak is None:
            continue
        lag = event.session_time_s - peak
        if -1.0 <= lag <= max_lag_s:
            matches.append({"motif_id": _motif_id(motif), "peak_time_s": peak, "lag_s": float(lag)})
    return sorted(matches, key=lambda row: abs(row["lag_s"]))
