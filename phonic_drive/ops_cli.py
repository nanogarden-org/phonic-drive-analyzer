"""Operational CLI for aggregation, recipes, schema checks, and visualization."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .interpreter.manifest_aggregate import aggregate_manifest_tree
from .reconstruction.recipes import list_recipes
from .schemas import migrate_artifact, validate_artifact
from .visualization.timeline import plot_shared_timeline


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Phonic Drive v3 operational utilities")
    sub = p.add_subparsers(dest="command", required=True)

    a = sub.add_parser("aggregate", help="Aggregate response/motif associations from session manifests")
    a.add_argument("root")
    a.add_argument("--response-type", required=True)
    a.add_argument("--max-lag", type=float, default=10.0)
    a.add_argument("--participant")
    a.add_argument("--output", default="manifest_aggregate.json")

    sub.add_parser("recipes", help="List reconstruction recipes")

    v = sub.add_parser("validate", help="Validate one JSON artifact")
    v.add_argument("artifact")

    m = sub.add_parser("migrate", help="Migrate one supported artifact schema")
    m.add_argument("artifact")
    m.add_argument("target_schema")
    m.add_argument("--output", required=True)

    t = sub.add_parser("visualize", help="Create an aligned A/M/P/K timeline PNG")
    t.add_argument("--acoustic", required=True)
    t.add_argument("--structural", required=True)
    t.add_argument("--output", default="shared_timeline.png")
    t.add_argument("--responses")
    t.add_argument("--behavior")
    t.add_argument("--motifs")
    return p


def main(argv=None) -> int:
    args = parser().parse_args(argv)

    if args.command == "aggregate":
        result = aggregate_manifest_tree(
            Path(args.root),
            response_type=args.response_type,
            max_lag_s=args.max_lag,
            participant_pseudonym=args.participant,
        )
        Path(args.output).write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(args.output)
        return 0

    if args.command == "recipes":
        print(json.dumps(list_recipes(), indent=2))
        return 0

    if args.command == "validate":
        payload = json.loads(Path(args.artifact).read_text(encoding="utf-8"))
        print(json.dumps(validate_artifact(payload), indent=2))
        return 0

    if args.command == "migrate":
        payload = json.loads(Path(args.artifact).read_text(encoding="utf-8"))
        migrated = migrate_artifact(payload, args.target_schema)
        Path(args.output).write_text(json.dumps(migrated, indent=2), encoding="utf-8")
        print(args.output)
        return 0

    if args.command == "visualize":
        path = plot_shared_timeline(
            Path(args.acoustic),
            Path(args.structural),
            Path(args.output),
            response_events_json=Path(args.responses) if args.responses else None,
            behavior_events_json=Path(args.behavior) if args.behavior else None,
            motifs_json=Path(args.motifs) if args.motifs else None,
        )
        print(path)
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
