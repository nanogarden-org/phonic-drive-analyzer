from __future__ import annotations

from pathlib import Path

import pytest

from phonic_drive.study import scan_study_folder


def _write_track(root: Path, folder: str, audio_name: str, note_name: str, note_bytes: bytes) -> None:
    path = root / folder
    path.mkdir()
    (path / audio_name).write_bytes(b"fake-audio")
    (path / note_name).write_bytes(note_bytes)


def test_scan_preserves_sequence_and_blinding(tmp_path: Path):
    _write_track(tmp_path, "01 Known", "known.mp3", "historical.txt", b"do not read this")
    _write_track(tmp_path, "02 Fresh", "fresh.mp3", "fresh.untested.txt", b"")

    manifest = scan_study_folder(tmp_path, corpus_id="PD-CORPUS-TEST")

    assert manifest["corpus_id"] == "PD-CORPUS-TEST"
    assert manifest["track_count"] == 2
    assert manifest["retrospective_count"] == 1
    assert manifest["prospective_count"] == 1
    assert [row["sequence"] for row in manifest["tracks"]] == [1, 2]
    assert manifest["tracks"][0]["study_role"] == "retrospective_known"
    assert manifest["tracks"][1]["study_role"] == "prospective_untested"
    assert manifest["tracks"][0]["annotation"]["contents_read_during_scan"] is False
    assert manifest["tracks"][1]["annotation"]["untested_marker"] is True
    assert "contents" not in manifest["tracks"][0]["annotation"]
    assert manifest["blinding"]["motif_discovery_must_not_consume_annotations"] is True


def test_scan_rejects_ambiguous_track_folder(tmp_path: Path):
    folder = tmp_path / "01 Ambiguous"
    folder.mkdir()
    (folder / "a.mp3").write_bytes(b"a")
    (folder / "b.mp3").write_bytes(b"b")
    (folder / "historical.txt").write_text("x", encoding="utf-8")

    with pytest.raises(ValueError, match="exactly one audio"):
        scan_study_folder(tmp_path)


def test_scan_rejects_duplicate_sequence_numbers(tmp_path: Path):
    _write_track(tmp_path, "01 Alpha", "alpha.mp3", "alpha.txt", b"x")
    _write_track(tmp_path, "01 Beta", "beta.mp3", "beta.untested.txt", b"")

    with pytest.raises(ValueError, match="Duplicate study sequence"):
        scan_study_folder(tmp_path)
