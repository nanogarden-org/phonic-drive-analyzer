"""Tests for the first provenance-bearing Vault identity helpers."""

from __future__ import annotations

import hashlib

from phonic_drive.vault.identity import artifact_identity, new_managed_id, sha256_file


def test_content_hash_tracks_bytes_not_filename(tmp_path):
    payload = b"phonic-drive-provenance-test\n"
    a = tmp_path / "first-name.bin"
    b = tmp_path / "second-name.bin"
    a.write_bytes(payload)
    b.write_bytes(payload)

    expected = hashlib.sha256(payload).hexdigest()
    assert sha256_file(a) == expected
    assert sha256_file(b) == expected


def test_artifact_identity_separates_managed_id_hash_and_location(tmp_path):
    source = tmp_path / "source.wav"
    source.write_bytes(b"RIFF synthetic fixture bytes")

    first = artifact_identity(source)
    second = artifact_identity(source)

    assert first["content_sha256"] == second["content_sha256"]
    assert first["observed_path"] == second["observed_path"]
    assert first["artifact_id"] != second["artifact_id"]
    assert first["filename"] == "source.wav"


def test_managed_ids_are_typed_and_unique():
    a = new_managed_id("session")
    b = new_managed_id("session")
    assert a.startswith("pd-session-")
    assert b.startswith("pd-session-")
    assert a != b
