"""Prospective response-to-structure alignment with circular-shift null controls.

The null preserves the participant event sequence and inter-event spacing while
rotating the entire response pattern around the stimulus duration. This avoids
comparing a clustered real response stream against independent uniform samples.
Results are descriptive/exploratory and do not establish causality.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, is_dataclass

import numpy as np


def _event_dict(event) -> dict:
    if isinstance(event, dict):
        return event
    if is_dataclass(event):
        return asdict(event)
    raise TypeError("event must be a mapping or dataclass")


def _motif_peak(motif: dict) -> float:
    for key in ("peak_s", "peak_time_s", "time_s"):
        if motif.get(key) is not None:
            return float(motif[key])
    raise ValueError("motif is missing a supported peak-time field")


def _motif_id(motif: dict) -> str:
    return str(motif.get("candidate_id") or motif.get("motif_id") or motif.get("id") or "unknown")


def _inside(t: float, intervals: list[tuple[float, float]]) -> bool:
    return any(start <= t <= end for start, end in intervals)


def _metrics(times: np.ndarray, peaks: np.ndarray, intervals: list[tuple[float, float]]) -> dict:
    if not len(times):
        return {"events": 0, "motif_window_hits": 0, "median_abs_peak_distance_s": None}
    distances = np.asarray([np.min(np.abs(peaks - t)) for t in times], dtype=float)
    return {
        "events": int(len(times)),
        "motif_window_hits": int(sum(_inside(float(t), intervals) for t in times)),
        "median_abs_peak_distance_s": float(np.median(distances)),
    }


def circular_shift_alignment(
    *,
    events: list,
    motifs: list[dict],
    duration_s: float,
    simulations: int = 20000,
    seed: int = 0,
) -> dict:
    """Compare observed response/motif alignment with circular time shifts.

    The same random shift is applied to every participant event in a simulation,
    modulo stimulus duration, preserving event count, ordering, and spacing.
    """
    if duration_s <= 0:
        raise ValueError("duration_s must be positive")
    if simulations < 100:
        raise ValueError("simulations must be >= 100")
    if not motifs:
        raise ValueError("motifs cannot be empty")

    parsed = [_event_dict(event) for event in events]
    times = np.asarray([float(event["session_time_s"]) for event in parsed], dtype=float)
    types = np.asarray([str(event.get("response_type", "unknown")) for event in parsed], dtype=object)
    peaks = np.asarray([_motif_peak(motif) for motif in motifs], dtype=float)
    intervals = [
        (float(motif.get("start_s", _motif_peak(motif))), float(motif.get("end_s", _motif_peak(motif))))
        for motif in motifs
    ]

    observed = _metrics(times, peaks, intervals)
    rng = np.random.default_rng(seed)
    shifts = rng.uniform(0.0, float(duration_s), int(simulations))

    null_hits = np.empty(simulations, dtype=int)
    null_medians = np.empty(simulations, dtype=float)
    for i, shift in enumerate(shifts):
        shifted = np.mod(times + shift, duration_s)
        row = _metrics(shifted, peaks, intervals)
        null_hits[i] = row["motif_window_hits"]
        null_medians[i] = row["median_abs_peak_distance_s"]

    observed["p_window_hits_ge"] = float((np.sum(null_hits >= observed["motif_window_hits"]) + 1) / (simulations + 1))
    observed["p_median_distance_le"] = float((np.sum(null_medians <= observed["median_abs_peak_distance_s"]) + 1) / (simulations + 1))

    by_type = {}
    for response_type in sorted(set(types.tolist())):
        mask = types == response_type
        subset = times[mask]
        row = _metrics(subset, peaks, intervals)
        type_hits = np.empty(simulations, dtype=int)
        type_medians = np.empty(simulations, dtype=float)
        for i, shift in enumerate(shifts):
            shifted = np.mod(times + shift, duration_s)[mask]
            null_row = _metrics(shifted, peaks, intervals)
            type_hits[i] = null_row["motif_window_hits"]
            type_medians[i] = null_row["median_abs_peak_distance_s"]
        row["p_window_hits_ge"] = float((np.sum(type_hits >= row["motif_window_hits"]) + 1) / (simulations + 1))
        row["p_median_distance_le"] = float((np.sum(type_medians <= row["median_abs_peak_distance_s"]) + 1) / (simulations + 1))
        by_type[response_type] = row

    return {
        "schema": "phonic-drive-circular-shift-alignment-v1",
        "duration_s": float(duration_s),
        "motif_count": int(len(motifs)),
        "simulation_count": int(simulations),
        "seed": int(seed),
        "overall": observed,
        "by_response_type": by_type,
        "note": (
            "Circular-shift p-values are exploratory controls that preserve participant event spacing. "
            "They do not establish biological or causal relationships, and subtype results are not multiple-comparison corrected."
        ),
    }
