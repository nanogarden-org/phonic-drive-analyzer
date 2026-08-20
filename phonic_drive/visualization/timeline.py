"""Shared A/M/P/K timeline visualization.

The streams share one horizontal time axis but remain in distinct panels so
measured acoustics, structural motifs, participant reports, and behavioral
telemetry are never visually collapsed into one variable.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt


def _read_csv(path: Path) -> list[dict]:
    with Path(path).open("r", newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def _read_json(path: Path | None) -> dict:
    if path is None:
        return {}
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _float_column(rows: list[dict], name: str) -> tuple[list[float], list[float]]:
    x, y = [], []
    for row in rows:
        try:
            t = float(row["time_s"])
            v = float(row[name])
        except (KeyError, TypeError, ValueError):
            continue
        x.append(t)
        y.append(v)
    return x, y


def plot_shared_timeline(
    acoustic_csv: Path,
    structural_csv: Path,
    output_png: Path,
    *,
    response_events_json: Path | None = None,
    behavior_events_json: Path | None = None,
    motifs_json: Path | None = None,
) -> Path:
    acoustic = _read_csv(Path(acoustic_csv))
    structural = _read_csv(Path(structural_csv))
    responses = _read_json(response_events_json).get("events", [])
    behavior = _read_json(behavior_events_json).get("events", [])
    motifs = _read_json(motifs_json).get("motifs", []) if motifs_json else []

    figure, axes = plt.subplots(4, 1, figsize=(13, 10), sharex=True)

    # A(t): selected measured acoustic state.
    at, rms_db = _float_column(acoustic, "rms_db")
    _, speed = _float_column(acoustic, "transition_speed")
    if at:
        axes[0].plot(at, rms_db, label="RMS dB")
    if speed:
        axes[0].plot(at[: len(speed)], speed, label="transition speed")
    axes[0].set_ylabel("A(t)")
    axes[0].set_title("Measured acoustic state")
    axes[0].legend(loc="upper right")

    # M(t): show all band-energy trajectories faintly plus motif peaks.
    band_columns = [name for name in (structural[0].keys() if structural else []) if name.endswith("_energy")]
    for name in band_columns:
        mt, values = _float_column(structural, name)
        if mt:
            axes[1].plot(mt, values, linewidth=0.8, alpha=0.7)
    for motif in motifs:
        peak = motif.get("peak_time_s", motif.get("time_s"))
        if peak is not None:
            axes[1].axvline(float(peak), linewidth=0.8, alpha=0.6)
    axes[1].set_ylabel("M(t)")
    axes[1].set_title("Structural band trajectories and motif candidates")

    # P(t): participant observations as event ticks.
    for i, event in enumerate(responses):
        t = event.get("session_time_s")
        if t is None:
            continue
        axes[2].scatter([float(t)], [i + 1], marker="|")
        axes[2].text(float(t), i + 1, str(event.get("response_type", "event")), fontsize=8, va="bottom")
    axes[2].set_ylabel("P(t)")
    axes[2].set_title("Participant response markers")

    # K(t): observable workflow/input events only.
    for i, event in enumerate(behavior):
        t = event.get("session_time_s")
        if t is None:
            continue
        axes[3].scatter([float(t)], [i + 1], marker="|")
        axes[3].text(float(t), i + 1, str(event.get("event_type", "behavior")), fontsize=8, va="bottom")
    axes[3].set_ylabel("K(t)")
    axes[3].set_title("Behavior/workflow telemetry")
    axes[3].set_xlabel("Session time (s)")

    figure.suptitle("Phonic Drive shared timeline — streams aligned, semantics separated")
    figure.tight_layout()
    output_png = Path(output_png)
    output_png.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_png, dpi=150, bbox_inches="tight")
    plt.close(figure)
    return output_png
