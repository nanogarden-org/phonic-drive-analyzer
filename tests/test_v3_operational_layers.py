from __future__ import annotations

from phonic_drive.schemas import migrate_artifact, validate_artifact


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
