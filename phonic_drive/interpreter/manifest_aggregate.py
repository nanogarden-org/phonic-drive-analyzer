"""Load session manifests and aggregate motif/response associations across a vault."""
from __future__ import annotations

import json
from pathlib import Path

from .aggregate import aggregate_motif_response


def _load_json(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def discover_manifests(root: Path) -> list[Path]:
    root = Path(root)
    if root.is_file():
        return [root]
    return sorted(root.rglob("session_manifest.json"))


def load_session_from_manifest(path: Path) -> dict:
    path = Path(path)
    manifest = _load_json(path)
    base = path.parent

    events = []
    response_file = manifest.get("response_events_file")
    if response_file:
        response_path = Path(response_file)
        if not response_path.is_absolute():
            response_path = base / response_path
        if response_path.exists():
            events = _load_json(response_path).get("events", [])

    motifs = []
    motifs_file = manifest.get("motifs_file")
    if motifs_file:
        motif_path = Path(motifs_file)
        if not motif_path.is_absolute():
            motif_path = base / motif_path
        if motif_path.exists():
            motif_payload = _load_json(motif_path)
            motifs = motif_payload.get("motifs", motif_payload.get("motif_candidates", []))

    return {
        "session_id": manifest.get("session_id"),
        "participant_pseudonym": manifest.get("participant_pseudonym"),
        "source": manifest.get("source_audio"),
        "trial_id": manifest.get("trial_id"),
        "hypothesis_ids": manifest.get("hypothesis_ids", []),
        "transform_ids": manifest.get("transform_ids", []),
        "events": events,
        "motifs": motifs,
        "manifest_path": str(path),
    }


def aggregate_manifest_tree(
    root: Path,
    *,
    response_type: str,
    max_lag_s: float = 10.0,
    participant_pseudonym: str | None = None,
) -> dict:
    manifests = discover_manifests(root)
    sessions = [load_session_from_manifest(path) for path in manifests]
    if participant_pseudonym is not None:
        sessions = [s for s in sessions if s.get("participant_pseudonym") == participant_pseudonym]
    result = aggregate_motif_response(sessions, response_type=response_type, max_lag_s=max_lag_s)
    result["manifest_root"] = str(root)
    result["manifest_count"] = len(manifests)
    result["loaded_sessions"] = len(sessions)
    result["participant_filter"] = participant_pseudonym
    return result
