"""Native single-pass Phonic Drive v3 command.

This command is additive while the compatibility CLI remains available.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from .exports import write_v3_bundle
from .session import build_session_manifest
from .track import analyze_track


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Native single-pass Phonic Drive v3 analyzer")
    p.add_argument("input", help="One audio file")
    p.add_argument("--output", default="phonic_drive_v3", help="Output directory")
    p.add_argument("--target-sr", type=int, default=22050)
    p.add_argument("--n-fft", type=int, default=2048)
    p.add_argument("--hop", type=int, default=512)
    p.add_argument("--bands", type=int, default=10)
    p.add_argument("--relationship-window", type=float, default=2.0)
    p.add_argument("--motif-half-window", type=float, default=1.5)
    p.add_argument("--participant", help="Optional participant pseudonym; enables session_manifest.json")
    p.add_argument("--trial-id", help="Optional trial identifier linked into the session manifest")
    p.add_argument("--hypothesis-id", action="append", default=[], help="Hypothesis ID; may be repeated")
    p.add_argument("--transform-id", action="append", default=[], help="Stimulus transform/reconstruction ID; may be repeated")
    p.add_argument("--response-events", help="Optional path to a response-events JSON file")
    p.add_argument("--behavior-events", help="Optional path to a K(t) behavior-events JSON file")
    return p


def main(argv=None) -> int:
    args = parser().parse_args(argv)
    source = Path(args.input).expanduser()
    if not source.is_file():
        raise SystemExit(f"Input audio not found: {source}")
    if args.target_sr <= 0 or args.n_fft < 128 or args.hop <= 0 or args.hop > args.n_fft or args.bands < 2:
        raise SystemExit("Invalid analysis parameters")

    track = analyze_track(
        source,
        target_sr=args.target_sr,
        n_fft=args.n_fft,
        hop=args.hop,
        bands=args.bands,
        relationship_window_s=args.relationship_window,
        motif_half_window_s=args.motif_half_window,
    )
    output_dir = Path(args.output).expanduser() / source.stem
    artifacts = write_v3_bundle(track, output_dir)

    if args.participant:
        response_file = str(Path(args.response_events).expanduser()) if args.response_events else None
        behavior_file = str(Path(args.behavior_events).expanduser()) if args.behavior_events else None
        manifest = build_session_manifest(
            participant_pseudonym=args.participant,
            source_audio=str(source),
            artifacts=artifacts,
            trial_id=args.trial_id,
            hypothesis_ids=args.hypothesis_id,
            transform_ids=args.transform_id,
            response_events_file=response_file,
            behavior_events_file=behavior_file,
        )
        manifest_path = manifest.write_json(output_dir / "session_manifest.json")
        artifacts["session_manifest_json"] = str(manifest_path)

    print(f"Analyzed {source}")
    print(f"Duration: {track.duration_s:.2f} s")
    print(f"Transition candidates: {len(track.transition_candidates)}")
    print(f"Motif candidates: {len(track.motif_candidates)}")
    print(f"Recurring pairs: {len(track.recurring_motif_pairs)}")
    for name, path in artifacts.items():
        print(f"{name}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
