"""Corpus-level comparison helpers for Phonic Drive migration validation."""
from __future__ import annotations

import csv
from pathlib import Path
import math


COMMON_COLUMNS = (
    "time_s",
    "rms",
    "rms_db",
    "centroid_hz",
    "bandwidth_hz",
    "rolloff85_hz",
    "zero_crossing_rate",
    "spectral_flux",
    "stereo_correlation",
    "stereo_width",
    "state_x_brightness",
    "state_y_energy",
    "state_z_space",
    "transition_speed",
    "transition_acceleration",
)


def read_numeric_csv(path: Path) -> dict[str, list[float]]:
    path = Path(path)
    columns: dict[str, list[float]] = {}
    with path.open("r", newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        for name in reader.fieldnames or []:
            columns[name] = []
        for row in reader:
            for name in columns:
                raw = row.get(name, "")
                try:
                    value = float(raw)
                except (TypeError, ValueError):
                    value = float("nan")
                columns[name].append(value)
    return columns


def _finite_pairs(a: list[float], b: list[float]) -> list[tuple[float, float]]:
    n = min(len(a), len(b))
    return [(a[i], b[i]) for i in range(n) if math.isfinite(a[i]) and math.isfinite(b[i])]


def compare_timelines(reference_csv: Path, candidate_csv: Path, *, columns=COMMON_COLUMNS) -> dict:
    """Compare overlapping numeric columns between two timeline exports."""
    reference = read_numeric_csv(reference_csv)
    candidate = read_numeric_csv(candidate_csv)
    metrics = {}
    for name in columns:
        if name not in reference or name not in candidate:
            continue
        pairs = _finite_pairs(reference[name], candidate[name])
        if not pairs:
            continue
        errors = [abs(x - y) for x, y in pairs]
        sq = [(x - y) ** 2 for x, y in pairs]
        metrics[name] = {
            "samples": len(pairs),
            "mean_abs_error": sum(errors) / len(errors),
            "max_abs_error": max(errors),
            "rmse": math.sqrt(sum(sq) / len(sq)),
        }
    return {
        "schema": "phonic-drive-timeline-comparison-v3alpha1",
        "reference": str(reference_csv),
        "candidate": str(candidate_csv),
        "reference_rows": max((len(v) for v in reference.values()), default=0),
        "candidate_rows": max((len(v) for v in candidate.values()), default=0),
        "metrics": metrics,
    }


def corpus_report(pairs: list[tuple[Path, Path]]) -> dict:
    """Aggregate many reference/candidate timeline comparisons."""
    reports = [compare_timelines(reference, candidate) for reference, candidate in pairs]
    by_column: dict[str, list[float]] = {}
    for report in reports:
        for name, metric in report["metrics"].items():
            by_column.setdefault(name, []).append(float(metric["mean_abs_error"]))
    summary = {
        name: {
            "tracks": len(values),
            "mean_of_mean_abs_error": sum(values) / len(values),
            "worst_mean_abs_error": max(values),
        }
        for name, values in by_column.items()
    }
    return {
        "schema": "phonic-drive-corpus-comparison-v3alpha1",
        "tracks": len(reports),
        "summary": summary,
        "reports": reports,
    }
