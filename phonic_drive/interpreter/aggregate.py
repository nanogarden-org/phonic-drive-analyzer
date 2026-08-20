"""Aggregate repeated motif/response observations across Phonic Drive sessions."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, is_dataclass

from ..trials.events import ResponseEvent, nearest_motifs


def _event_dict(event) -> dict:
    if isinstance(event, dict):
        return event
    if is_dataclass(event):
        return asdict(event)
    raise TypeError("event must be a dict or dataclass")


def aggregate_motif_response(
    sessions: list[dict],
    *,
    response_type: str | None = None,
    max_lag_s: float = 10.0,
) -> dict:
    """Summarize repeated temporal associations without causal interpretation.

    Each session mapping should contain ``events`` and ``motifs`` lists. Optional
    ``session_id`` and ``source`` values are carried into support records.
    """
    totals_by_response: dict[str, int] = defaultdict(int)
    matches_by_motif: dict[tuple[str, str], list[dict]] = defaultdict(list)

    for session in sessions:
        motifs = list(session.get("motifs", []))
        for raw_event in session.get("events", []):
            event_data = _event_dict(raw_event)
            kind = str(event_data.get("response_type", "unknown"))
            if response_type is not None and kind != response_type:
                continue
            event = ResponseEvent(**event_data)
            totals_by_response[kind] += 1
            for match in nearest_motifs(event, motifs, max_lag_s=max_lag_s):
                motif_id = str(match.get("motif_id") or "unknown")
                matches_by_motif[(kind, motif_id)].append({
                    "session_id": session.get("session_id"),
                    "source": session.get("source"),
                    "event_time_s": event.session_time_s,
                    **match,
                })

    rows = []
    for (kind, motif_id), matches in matches_by_motif.items():
        total = totals_by_response[kind]
        lags = [float(row["lag_s"]) for row in matches]
        rows.append({
            "response_type": kind,
            "motif_id": motif_id,
            "matched_events": len(matches),
            "total_events": total,
            "association_rate": (len(matches) / total) if total else 0.0,
            "mean_lag_s": sum(lags) / len(lags),
            "min_abs_lag_s": min(abs(x) for x in lags),
            "support": matches,
        })

    rows.sort(key=lambda row: (-row["association_rate"], -row["matched_events"], row["motif_id"]))
    return {
        "schema": "phonic-drive-motif-response-aggregate-v3alpha1",
        "response_event_totals": dict(totals_by_response),
        "associations": rows,
        "note": "These are repeated temporal associations, not causal or physiological conclusions.",
    }
