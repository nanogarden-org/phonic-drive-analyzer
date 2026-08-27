"""Reproducible trial manifests and A/B/X ordering."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import hashlib
import json
import random


@dataclass(slots=True)
class StimulusCondition:
    condition_id: str
    stimulus_path: str
    transform_id: str | None = None
    role: str = "test"


@dataclass(slots=True)
class TrialManifest:
    trial_id: str
    hypothesis_id: str | None
    participant_id: str | None
    seed: int
    conditions: list[StimulusCondition]
    order: list[str]
    schema: str = "phonic-drive-trial-v3alpha1"

    def write_json(self, path: Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(self), indent=2, ensure_ascii=False), encoding="utf-8")
        return path


def stable_seed(trial_id: str, hypothesis_id: str | None = None) -> int:
    """Generate a reproducible non-secret randomization seed from trial identity."""
    material = f"{trial_id}|{hypothesis_id or ''}".encode("utf-8")
    return int.from_bytes(hashlib.sha256(material).digest()[:8], "big")


def randomized_order(conditions: list[StimulusCondition], seed: int) -> list[str]:
    ids = [condition.condition_id for condition in conditions]
    rng = random.Random(seed)
    rng.shuffle(ids)
    return ids


def build_manifest(
    *,
    trial_id: str,
    conditions: list[StimulusCondition],
    hypothesis_id: str | None = None,
    participant_id: str | None = None,
    seed: int | None = None,
) -> TrialManifest:
    resolved_seed = stable_seed(trial_id, hypothesis_id) if seed is None else int(seed)
    return TrialManifest(
        trial_id=trial_id,
        hypothesis_id=hypothesis_id,
        participant_id=participant_id,
        seed=resolved_seed,
        conditions=list(conditions),
        order=randomized_order(conditions, resolved_seed),
    )
