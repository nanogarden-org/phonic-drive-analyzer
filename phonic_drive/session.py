"""Session/result manifests for linking Phonic Drive artifacts by provenance."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
import hashlib
import json


def stable_id(prefix: str, *parts: str) -> str:
    payload = "|".join(str(part) for part in parts).encode("utf-8", "replace")
    digest = hashlib.sha256(payload).hexdigest()[:12]
    return f"{prefix}-{digest}"


@dataclass(slots=True)
class SessionManifest:
    session_id: str
    participant_pseudonym: str
    source_audio: str
    analysis_id: str
    structural_id: str
    trial_id: str | None = None
    hypothesis_ids: list[str] = field(default_factory=list)
    transform_ids: list[str] = field(default_factory=list)
    response_events_file: str | None = None
    behavior_events_file: str | None = None
    acoustic_summary_file: str | None = None
    acoustic_timeline_file: str | None = None
    transitions_file: str | None = None
    structural_summary_file: str | None = None
    structural_timeline_file: str | None = None
    motifs_file: str | None = None
    relationships_file: str | None = None
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"schema": "phonic-drive-session-manifest-v3alpha2", **asdict(self)}

    def write_json(self, path: Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
        return path


def build_session_manifest(
    *,
    participant_pseudonym: str,
    source_audio: str,
    artifacts: dict[str, str],
    trial_id: str | None = None,
    hypothesis_ids: list[str] | None = None,
    transform_ids: list[str] | None = None,
    response_events_file: str | None = None,
    behavior_events_file: str | None = None,
) -> SessionManifest:
    analysis_id = stable_id("PDA", source_audio, artifacts.get("acoustic_json", ""))
    structural_id = stable_id("PDM", source_audio, artifacts.get("structural_json", ""))
    session_id = stable_id(
        "PDS",
        participant_pseudonym,
        source_audio,
        trial_id or "",
        response_events_file or "",
        behavior_events_file or "",
    )
    return SessionManifest(
        session_id=session_id,
        participant_pseudonym=participant_pseudonym,
        source_audio=source_audio,
        analysis_id=analysis_id,
        structural_id=structural_id,
        trial_id=trial_id,
        hypothesis_ids=list(hypothesis_ids or []),
        transform_ids=list(transform_ids or []),
        response_events_file=response_events_file,
        behavior_events_file=behavior_events_file,
        acoustic_summary_file=artifacts.get("acoustic_json"),
        acoustic_timeline_file=artifacts.get("acoustic_timeline_csv"),
        transitions_file=artifacts.get("transitions_json"),
        structural_summary_file=artifacts.get("structural_json"),
        structural_timeline_file=artifacts.get("structural_timeline_csv"),
        motifs_file=artifacts.get("motifs_json"),
        relationships_file=artifacts.get("relationships_npz"),
    )
