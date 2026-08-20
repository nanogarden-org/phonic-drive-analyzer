"""Run compatibility and native Phonic Drive analysis across a corpus.

The runner is a migration/validation tool. It executes both paths on the same
source set, records per-track success/failure, and writes discrepancy reports
for overlapping measured telemetry.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import phonic_drive_analysis_v2 as legacy

from .exports import write_v3_bundle
from .track import analyze_track
from .validation.corpus import compare_timelines, corpus_report


def _track_dir(root: Path, audio_path: Path) -> Path:
    return root / f"{legacy.slugify(audio_path.stem)}_{legacy.source_id(audio_path)}"


def run_corpus(
    inputs: list[str],
    *,
    output: Path,
    recursive: bool = False,
    target_sr: int = 22050,
    n_fft: int = 2048,
    hop: int = 512,
    bands: int = 10,
) -> dict:
    files = legacy.resolve_inputs(inputs, recursive)
    output = Path(output)
    v2_root = output / "v2"
    v3_root = output / "v3"
    report_root = output / "comparison"
    for path in (v2_root, v3_root, report_root):
        path.mkdir(parents=True, exist_ok=True)

    rows = []
    pairs: list[tuple[Path, Path]] = []

    for audio_path in files:
        record = {"source": str(audio_path), "v2": None, "v3": None, "comparison": None}

        # Run the retained v2 reference path directly.
        args = legacy.parser().parse_args([
            str(audio_path),
            "--output", str(v2_root),
            "--target-sr", str(target_sr),
            "--n-fft", str(n_fft),
            "--hop", str(hop),
            "--no-plots",
        ])
        try:
            summary = legacy.analyze_track(audio_path, v2_root, args, annotation=None)
            record["v2"] = {"status": "ok", "track_dir": summary["track_output_dir"]}
        except Exception as exc:
            record["v2"] = {"status": "error", "error": str(exc)}

        try:
            track = analyze_track(
                audio_path,
                target_sr=target_sr,
                n_fft=n_fft,
                hop=hop,
                bands=bands,
            )
            native_dir = v3_root / f"{legacy.slugify(audio_path.stem)}_{legacy.source_id(audio_path)}"
            artifacts = write_v3_bundle(track, native_dir)
            record["v3"] = {"status": "ok", "track_dir": str(native_dir), "artifacts": artifacts}
        except Exception as exc:
            record["v3"] = {"status": "error", "error": str(exc)}

        if record["v2"]["status"] == "ok" and record["v3"]["status"] == "ok":
            ref = Path(record["v2"]["track_dir"]) / "timeline.csv"
            cand = Path(record["v3"]["artifacts"]["acoustic_timeline_csv"])
            comparison = compare_timelines(ref, cand)
            comparison_path = report_root / f"{legacy.slugify(audio_path.stem)}_comparison.json"
            comparison_path.write_text(json.dumps(comparison, indent=2), encoding="utf-8")
            record["comparison"] = str(comparison_path)
            pairs.append((ref, cand))

        rows.append(record)

    aggregate = corpus_report(pairs)
    result = {
        "schema": "phonic-drive-corpus-run-v3alpha1",
        "requested_inputs": inputs,
        "resolved_tracks": len(files),
        "successful_pairs": len(pairs),
        "tracks": rows,
        "comparison": aggregate,
    }
    (output / "corpus_run.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    (report_root / "corpus_comparison.json").write_text(json.dumps(aggregate, indent=2), encoding="utf-8")
    return result


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Run v2 and native v3 across the same audio corpus")
    p.add_argument("inputs", nargs="+", help="Files, directories, globs, or @file-list paths")
    p.add_argument("--output", default="phonic_drive_corpus")
    p.add_argument("--recursive", action="store_true")
    p.add_argument("--target-sr", type=int, default=22050)
    p.add_argument("--n-fft", type=int, default=2048)
    p.add_argument("--hop", type=int, default=512)
    p.add_argument("--bands", type=int, default=10)
    return p


def main(argv=None) -> int:
    args = parser().parse_args(argv)
    result = run_corpus(
        args.inputs,
        output=Path(args.output),
        recursive=args.recursive,
        target_sr=args.target_sr,
        n_fft=args.n_fft,
        hop=args.hop,
        bands=args.bands,
    )
    print(f"Resolved tracks: {result['resolved_tracks']}")
    print(f"Successful v2/v3 pairs: {result['successful_pairs']}")
    print(f"Report: {Path(args.output) / 'corpus_run.json'}")
    return 0 if result["resolved_tracks"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
