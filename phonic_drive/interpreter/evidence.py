"""Evidence-oriented interpretation helpers.

The interpreter grades what kind of evidence exists. It does not convert
association into causation or assign biological meaning to an acoustic motif.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass(slots=True)
class EvidenceStatement:
    level: int
    label: str
    statement: str
    support: dict

    def to_dict(self) -> dict:
        return asdict(self)


LEVELS = {
    0: "observation",
    1: "temporal proximity",
    2: "within-participant structural association",
    3: "cross-stimulus recurrence",
    4: "perturbation evidence",
    5: "reconstruction evidence",
}


def observation(response_event: dict) -> EvidenceStatement:
    return EvidenceStatement(
        0,
        LEVELS[0],
        "A participant response was recorded at the stated session time.",
        {"response_event": response_event},
    )


def temporal_proximity(response_event: dict, motif_match: dict) -> EvidenceStatement:
    lag = float(motif_match["lag_s"])
    return EvidenceStatement(
        1,
        LEVELS[1],
        f"A measured acoustic motif candidate occurred {abs(lag):.3f} s {'before' if lag >= 0 else 'after'} the participant marker.",
        {"response_event": response_event, "motif_match": motif_match},
    )


def structural_association(*, motif_id: str, matched_events: int, total_events: int) -> EvidenceStatement:
    rate = matched_events / total_events if total_events else 0.0
    return EvidenceStatement(
        2,
        LEVELS[2],
        "The same descriptive acoustic motif was repeatedly temporally associated with this response class within the analyzed participant data.",
        {"motif_id": motif_id, "matched_events": matched_events, "total_events": total_events, "association_rate": rate},
    )


def perturbation_evidence(*, hypothesis_id: str, retained_condition: str, altered_condition: str, effect_summary: dict) -> EvidenceStatement:
    return EvidenceStatement(
        4,
        LEVELS[4],
        "A controlled stimulus perturbation changed the observed response pattern while testing a prespecified structural hypothesis.",
        {
            "hypothesis_id": hypothesis_id,
            "retained_condition": retained_condition,
            "altered_condition": altered_condition,
            "effect_summary": effect_summary,
        },
    )


def reconstruction_evidence(*, hypothesis_id: str, reconstruction_id: str, control_id: str, effect_summary: dict) -> EvidenceStatement:
    return EvidenceStatement(
        5,
        LEVELS[5],
        "A synthetic reconstruction retaining the candidate structure differed from a control under the recorded trial conditions.",
        {
            "hypothesis_id": hypothesis_id,
            "reconstruction_id": reconstruction_id,
            "control_id": control_id,
            "effect_summary": effect_summary,
        },
    )
