from __future__ import annotations

import json
from pathlib import Path

from phonic_drive.interpreter.manifest_aggregate import aggregate_manifest_tree
from phonic_drive.reconstruction import build_recipe_manifest, list_recipes
from phonic_drive.schemas import migrate_artifact, validate_artifact
from phonic_drive.visualization.timeline import plot_shared_timeline


def test_reconstruction_recipe_builds_traceable_manifest():
    names = {row["name"] for row in list_recipes()}
    assert {"time_reverse", "timing_scramble", "band_ablation", "envelope_control"} <= names
    manifest = build_recipe_manifest(
        "band_ablation",
        reconstruction_id="R1",
        source_stimulus_id="S1",
        source_motif_ids=["M1"],
        hypothesis_id="H1",
        parameters={"low_hz": 60.0, "high_hz": 90.0},
    )
    assert manifest.steps[0].operation == "spectral_ablation"
    assert manifest.steps[0].disrupts == ["selected_frequency_band"]
    assert manifest.steps[0].parameters["low_hz"] == 60.0


def test_schema_validation_and_explicit_migration():
    old = {
        "schema": "phonic-drive-response-events-v3alpha1",
        "trial_id": "T1",
        "stimulus": "song.wav",
        "events": [],
    }
    assert validate_artifact(old)["valid"] is True
    new = migrate_artifact(old, "phonic-drive-response-events-v3alpha2")
    assert new["schema"] == "phonic-drive-response-events-v3alpha2"
    assert new["clock"] == "monotonic_session_seconds"
    assert new["source_audio"] == "song.wav"


def test_manifest_tree_aggregation_loads_linked_files(tmp_path: Path):
    session = tmp_path / "session1"
    session.mkdir()
    events = {"schema": "phonic-drive-response-events-v3alpha2", "clock": "monotonic_session_seconds", "events": [
        {"session_time_s": 5.0, "response_type": "piloerection", "intensity": None, "region": None, "confidence": None, "note": None}
    ]}
    motifs = {"schema": "phonic-drive-motifs-v3alpha1", "source": "song.wav", "motifs": [{"id": "M1", "peak_time_s": 4.0}], "recurring_pairs": []}
    (session / "events.json").write_text(json.dumps(events), encoding="utf-8")
    (session / "motifs.json").write_text(json.dumps(motifs), encoding="utf-8")
    manifest = {
        "schema": "phonic-drive-session-manifest-v3alpha1",
        "session_id": "PDS-1",
        "participant_pseudonym": "P001",
        "source_audio": "song.wav",
        "analysis_id": "PDA-1",
        "structural_id": "PDM-1",
        "response_events_file": "events.json",
        "motifs_file": "motifs.json",
    }
    (session / "session_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    result = aggregate_manifest_tree(tmp_path, response_type="piloerection", max_lag_s=2.0)
    assert result["loaded_sessions"] == 1
    assert result["associations"][0]["motif_id"] == "M1"


def test_shared_timeline_writes_png(tmp_path: Path):
    acoustic = tmp_path / "acoustic.csv"
    structural = tmp_path / "structural.csv"
    acoustic.write_text(
        "time_s,rms_db,transition_speed\n0,-20,0\n1,-10,1\n2,-15,0.5\n",
        encoding="utf-8",
    )
    structural.write_text(
        "time_s,band_00_energy,band_01_energy\n0,0.2,0.8\n1,0.5,0.5\n2,0.3,0.7\n",
        encoding="utf-8",
    )
    responses = tmp_path / "responses.json"
    behavior = tmp_path / "behavior.json"
    motifs = tmp_path / "motifs.json"
    responses.write_text(json.dumps({"events": [{"session_time_s": 1.1, "response_type": "piloerection"}]}), encoding="utf-8")
    behavior.write_text(json.dumps({"events": [{"session_time_s": 0.8, "event_type": "typing_burst"}]}), encoding="utf-8")
    motifs.write_text(json.dumps({"motifs": [{"id": "M1", "peak_time_s": 1.0}]}), encoding="utf-8")
    output = plot_shared_timeline(acoustic, structural, tmp_path / "timeline.png", response_events_json=responses, behavior_events_json=behavior, motifs_json=motifs)
    assert output.exists()
    assert output.stat().st_size > 0
