"""Lightweight schema registry, validation, and explicit version migrations.

Phonic Drive artifacts are intentionally self-describing through a top-level
``schema`` field. Validation here focuses on required structure and known
versions without adding a heavyweight runtime dependency.
"""
from __future__ import annotations

from copy import deepcopy


REQUIRED_FIELDS: dict[str, tuple[str, ...]] = {
    "phonic-drive-acoustic-v3alpha1": ("schema", "source", "analysis_parameters", "statistics", "transition_candidates"),
    "phonic-drive-structural-v3alpha2": ("schema", "source", "analysis_parameters", "motif_candidates", "recurring_motif_pairs"),
    "phonic-drive-motifs-v3alpha1": ("schema", "source", "motifs", "recurring_pairs"),
    "phonic-drive-response-events-v3alpha1": ("schema", "events"),
    "phonic-drive-response-events-v3alpha2": ("schema", "events", "clock"),
    "phonic-drive-session-manifest-v3alpha1": ("schema", "session_id", "participant_pseudonym", "source_audio", "analysis_id", "structural_id"),
    "phonic-drive-trial-manifest-v3alpha1": ("schema", "trial_id", "participant_pseudonym", "stimuli", "presentation_order", "randomization_seed"),
    "phonic-drive-reconstruction-v3alpha1": ("schema", "reconstruction_id", "source_stimulus_id", "source_motif_ids", "steps"),
    "phonic-drive-behavior-events-v3alpha1": ("schema", "events", "clock"),
}


class SchemaError(ValueError):
    pass


def validate_artifact(payload: dict) -> dict:
    """Validate a known Phonic Drive artifact and return a compact report."""
    if not isinstance(payload, dict):
        raise SchemaError("artifact must be a mapping")
    schema = payload.get("schema")
    if not schema:
        raise SchemaError("artifact has no schema field")
    required = REQUIRED_FIELDS.get(str(schema))
    if required is None:
        raise SchemaError(f"unknown schema: {schema}")
    missing = [name for name in required if name not in payload]
    if missing:
        raise SchemaError(f"{schema} missing required fields: {', '.join(missing)}")

    if "events" in payload and not isinstance(payload["events"], list):
        raise SchemaError(f"{schema} events must be a list")
    if "steps" in payload and not isinstance(payload["steps"], list):
        raise SchemaError(f"{schema} steps must be a list")

    return {"schema": schema, "valid": True, "required_fields": list(required)}


def migrate_artifact(payload: dict, target_schema: str) -> dict:
    """Perform one explicit supported migration; never silently reinterpret data."""
    source_schema = payload.get("schema") if isinstance(payload, dict) else None
    if source_schema == target_schema:
        validate_artifact(payload)
        return deepcopy(payload)

    if source_schema == "phonic-drive-response-events-v3alpha1" and target_schema == "phonic-drive-response-events-v3alpha2":
        out = deepcopy(payload)
        out["schema"] = target_schema
        out.setdefault("stimulus_id", None)
        out.setdefault("participant_pseudonym", None)
        out.setdefault("source_audio", out.pop("stimulus", None))
        out.setdefault("clock", "monotonic_session_seconds")
        validate_artifact(out)
        return out

    raise SchemaError(f"unsupported migration: {source_schema} -> {target_schema}")


def known_schemas() -> list[str]:
    return sorted(REQUIRED_FIELDS)
