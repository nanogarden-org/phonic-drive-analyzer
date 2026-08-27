"""CLI for blinded Phonic Drive study-corpus ingestion and analysis."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .study import analyze_study, write_study_manifest


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Scan or analyze a numbered Phonic Drive study folder")
    sub = p.add_subparsers(dest="command", required=True)

    scan = sub.add_parser("scan", help="Create a sealed study manifest without reading note contents")
    scan.add_argument("root")
    scan.add_argument("--corpus-id")
    scan.add_argument("--output", default="study_manifest.json")

    analyze = sub.add_parser("analyze", help="Run blind v2/v3 analysis using audio only")
    analyze.add_argument("root")
    analyze.add_argument("--corpus-id")
    analyze.add_argument("--output", default="phonic_drive_study")
    analyze.add_argument("--target-sr", type=int, default=22050)
    analyze.add_argument("--n-fft", type=int, default=2048)
    analyze.add_argument("--hop", type=int, default=512)
    analyze.add_argument("--bands", type=int, default=10)
    return p


def main(argv=None) -> int:
    args = parser().parse_args(argv)
    if args.command == "scan":
        manifest = write_study_manifest(Path(args.root), Path(args.output), corpus_id=args.corpus_id)
        print(json.dumps({
            "corpus_id": manifest["corpus_id"],
            "tracks": manifest["track_count"],
            "retrospective": manifest["retrospective_count"],
            "prospective": manifest["prospective_count"],
            "manifest": str(Path(args.output)),
        }, indent=2))
        return 0

    result = analyze_study(
        Path(args.root),
        output=Path(args.output),
        corpus_id=args.corpus_id,
        target_sr=args.target_sr,
        n_fft=args.n_fft,
        hop=args.hop,
        bands=args.bands,
    )
    print(json.dumps({
        "corpus_id": result["corpus_id"],
        "tracks": result["track_count"],
        "retrospective": result["retrospective_count"],
        "prospective": result["prospective_count"],
        "next_gate": result["next_gate"],
        "output": str(Path(args.output)),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
