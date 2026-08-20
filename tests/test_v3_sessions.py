from __future__ import annotations

from phonic_drive.interpreter import aggregate_motif_response
from phonic_drive.session import build_session_manifest, stable_id


def test_stable_id_is_deterministic():
    assert stable_id("PDS", "a", "b") == stable_id("PDS", "a", "b")
    assert stable_id("PDS", "a", "b") != stable_id("PDS", "a", "c")


def test_session_manifest_links_artifacts_and_streams():
    artifacts = {
        "acoustic_json": "run/acoustic_summary.json",
        "acoustic_timeline_csv": "run/acoustic_timeline.csv",
        "transitions_json": "run/transitions.json",
        "structural_json": "run/structural_analysis.json",
        "structural_timeline_csv": "run/structural_timeline.csv",
        "motifs_json": "run/motifs.json",
        "relationships_npz": "run/relationships.npz",
    }
    manifest = build_session_manifest(
        participant_pseudonym="P001",
        source_audio="song.wav",
        artifacts=artifacts,
        trial_id="T001",
        hypothesis_ids=["H001"],
        transform_ids=["R001"],
        response_events_file="run/events.json",
        behavior_events_file="run/behavior.json",
    )
    payload = manifest.to_dict()
    assert payload["schema"] == "phonic-drive-session-manifest-v3alpha2"
    assert payload["trial_id"] == "T001"
    assert payload["motifs_file"] == "run/motifs.json"
    assert payload["response_events_file"] == "run/events.json"
    assert payload["behavior_events_file"] == "run/behavior.json"


def test_repeated_session_aggregation_counts_temporal_associations():
    sessions = [
        {
            "session_id": "S1",
            "source": "a.wav",
            "events": [
                {"session_time_s": 10.0, "response_type": "piloerection", "intensity": 0.7, "region": None, "confidence": 0.8, "note": None},
            ],
            "motifs": [{"id": "M1", "peak_time_s": 9.0}],
        },
        {
            "session_id": "S2",
            "source": "b.wav",
            "events": [
                {"session_time_s": 20.0, "response_type": "piloerection", "intensity": 0.9, "region": None, "confidence": 0.9, "note": None},
            ],
            "motifs": [{"id": "M1", "peak_time_s": 18.5}],
        },
    ]
    result = aggregate_motif_response(sessions, response_type="piloerection", max_lag_s=3.0)
    assert result["response_event_totals"]["piloerection"] == 2
    row = result["associations"][0]
    assert row["motif_id"] == "M1"
    assert row["matched_events"] == 2
    assert row["association_rate"] == 1.0
