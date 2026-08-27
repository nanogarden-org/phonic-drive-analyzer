"""Study-corpus discovery and provenance for Phonic Drive experiments.

A study folder is intentionally simple::

    01 Track Name/
        audio.mp3
        historical-output.txt
    04 New Track/
        audio.mp3
        observations.untested.txt

Scanning never reads note contents. Retrospective notes remain sealed until an
independent acoustic/structural analysis has been produced.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from .corpus_runner import run_corpus

AUDIO_SUFFIXES = {".mp3", ".wav", ".flac", ".m4a", ".ogg", ".aif", ".aiff"}
_FOLDER_RE = re.compile(r"^(?P<sequence>\d+)\s+(?P<title>.+)$")


def sha256_file(path: Path, *, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as fh:
        while chunk := fh.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def _relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _file_record(path: Path, root: Path) -> dict:
    return {
        "path": _relative(path, root),
        "size_bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def discover_track_folder(folder: Path, root: Path) -> dict:
    match = _FOLDER_RE.match(folder.name)
    if not match:
        raise ValueError(f"Study folder must begin with a numeric sequence: {folder.name}")

    audio_files = sorted(p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in AUDIO_SUFFIXES)
    note_files = sorted(p for p in folder.iterdir() if p.is_file() and p.suffix.lower() == ".txt")
    if len(audio_files) != 1:
        raise ValueError(f"Expected exactly one audio file in {folder.name}; found {len(audio_files)}")
    if len(note_files) != 1:
        raise ValueError(f"Expected exactly one .txt note/marker in {folder.name}; found {len(note_files)}")

    audio = audio_files[0]
    note = note_files[0]
    untested_marker = ".untested" in note.name.lower()
    role = "prospective_untested" if untested_marker else "retrospective_known"
    audio_hash = sha256_file(audio)

    return {
        "sequence": int(match.group("sequence")),
        "title": match.group("title"),
        "folder": folder.name,
        "track_id": f"PDT-{audio_hash[:12]}",
        "study_role": role,
        "audio": _file_record(audio, root),
        "annotation": {
            **_file_record(note, root),
            "sealed": True,
            "untested_marker": untested_marker,
            "contents_read_during_scan": False,
        },
    }


def scan_study_folder(root: Path, *, corpus_id: str | None = None) -> dict:
    root = Path(root).resolve()
    folders = sorted((p for p in root.iterdir() if p.is_dir()), key=lambda p: p.name.lower())
    tracks = [discover_track_folder(folder, root) for folder in folders]
    tracks.sort(key=lambda row: row["sequence"])
    sequences = [row["sequence"] for row in tracks]
    if len(sequences) != len(set(sequences)):
        raise ValueError("Duplicate study sequence numbers are not allowed")

    identity = hashlib.sha256()
    for track in tracks:
        identity.update(str(track["sequence"]).encode("ascii"))
        identity.update(track["audio"]["sha256"].encode("ascii"))
        identity.update(track["annotation"]["sha256"].encode("ascii"))
    derived_id = f"PD-CORPUS-{identity.hexdigest()[:12].upper()}"

    return {
        "schema": "phonic-drive-study-corpus-v3alpha1",
        "corpus_id": corpus_id or derived_id,
        "root": str(root),
        "blinding": {
            "retrospective_annotation_contents_read": False,
            "motif_discovery_must_not_consume_annotations": True,
            "prospective_tracks_require_fresh_response_capture": True,
        },
        "track_count": len(tracks),
        "retrospective_count": sum(t["study_role"] == "retrospective_known" for t in tracks),
        "prospective_count": sum(t["study_role"] == "prospective_untested" for t in tracks),
        "tracks": tracks,
    }


def write_study_manifest(root: Path, output: Path, *, corpus_id: str | None = None) -> dict:
    manifest = scan_study_folder(root, corpus_id=corpus_id)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def analyze_study(
    root: Path,
    *,
    output: Path,
    corpus_id: str | None = None,
    target_sr: int = 22050,
    n_fft: int = 2048,
    hop: int = 512,
    bands: int = 10,
) -> dict:
    """Run blind acoustic/structural analysis across a study corpus.

    Only audio paths from the sealed study manifest are passed to the analysis
    runner. Annotation files are never opened here.
    """
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    manifest = write_study_manifest(root, output / "study_manifest.json", corpus_id=corpus_id)
    audio_paths = [str(Path(root).resolve() / row["audio"]["path"]) for row in manifest["tracks"]]
    corpus = run_corpus(
        audio_paths,
        output=output / "analysis",
        recursive=False,
        target_sr=target_sr,
        n_fft=n_fft,
        hop=hop,
        bands=bands,
    )
    result = {
        "schema": "phonic-drive-study-run-v3alpha1",
        "corpus_id": manifest["corpus_id"],
        "study_manifest": "study_manifest.json",
        "analysis_root": "analysis",
        "track_count": manifest["track_count"],
        "retrospective_count": manifest["retrospective_count"],
        "prospective_count": manifest["prospective_count"],
        "analysis": corpus,
        "next_gate": "collect_prospective_response_events_before_unsealing_retrospective_annotations",
    }
    (output / "study_run.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result
