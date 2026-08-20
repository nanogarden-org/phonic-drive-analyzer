from __future__ import annotations

from phonic_drive.reconstruction import build_recipe_manifest, list_recipes
from phonic_drive.schemas import migrate_artifact, validate_artifact


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
