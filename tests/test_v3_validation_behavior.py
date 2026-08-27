from __future__ import annotations

from pathlib import Path

from phonic_drive.behavior import BehaviorEvent, BehaviorRecorder
from phonic_drive.validation import compare_timelines, corpus_report


def _write_csv(path: Path, rows: list[tuple[float, float]]) -> None:
    path.write_text(
        "time_s,rms_db\n" + "\n".join(f"{t},{v}" for t, v in rows) + "\n",
        encoding="utf-8",
    )


def test_timeline_comparison_reports_numeric_error(tmp_path: Path):
    reference = tmp_path / "reference.csv"
    candidate = tmp_path / "candidate.csv"
    _write_csv(reference, [(0.0, -10.0), (1.0, -8.0)])
    _write_csv(candidate, [(0.0, -9.0), (1.0, -7.0)])
    report = compare_timelines(reference, candidate, columns=("rms_db",))
    metric = report["metrics"]["rms_db"]
    assert metric["mean_abs_error"] == 1.0
    assert metric["max_abs_error"] == 1.0


def test_corpus_report_aggregates_tracks(tmp_path: Path):
    pairs = []
    for index in range(2):
        reference = tmp_path / f"r{index}.csv"
        candidate = tmp_path / f"c{index}.csv"
        _write_csv(reference, [(0.0, 1.0), (1.0, 2.0)])
        _write_csv(candidate, [(0.0, 1.5), (1.0, 2.5)])
        pairs.append((reference, candidate))
    report = corpus_report(pairs)
    assert report["tracks"] == 2
    assert report["summary"]["rms_db"]["tracks"] == 2


def test_behavior_event_contract_and_recorder():
    event = BehaviorEvent(1.25, "typing_rate", value=42.0, unit="wpm", source="keyboard")
    assert event.event_type == "typing_rate"
    recorder = BehaviorRecorder()
    marked = recorder.mark("manual_marker", value="focus_shift", source="hotkey")
    assert marked.session_time_s >= 0.0
    assert recorder.events[-1].value == "focus_shift"
