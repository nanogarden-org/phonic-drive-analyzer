"""Console trial runner with synchronized playback and immediate event markers.

FFplay is used as an optional playback process because FFmpeg is already a
project requirement. Participant markers use a monotonic clock; playback and
recording start from the same runner boundary. The event stream remains an
observation record, not an interpretation layer.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

from .events import ResponseEvent

KEYMAP = {
    "1": "piloerection",
    "2": "perceived_movement",
    "3": "pressure_tension",
    "4": "release",
    "5": "emotional_peak",
    "6": "spatial_change",
    "7": "other",
}


def _read_key() -> str:
    """Read one key without requiring Enter on Windows or POSIX terminals."""
    if sys.platform.startswith("win"):
        import msvcrt
        return msvcrt.getwch()

    import termios
    import tty
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def run_trial(
    audio_path: Path,
    output_path: Path,
    *,
    trial_id: str | None = None,
    stimulus_id: str | None = None,
    participant_pseudonym: str | None = None,
    play_audio: bool = True,
) -> dict:
    audio_path = Path(audio_path)
    output_path = Path(output_path)
    if not audio_path.is_file():
        raise FileNotFoundError(audio_path)

    player = None
    if play_audio:
        ffplay = shutil.which("ffplay")
        if ffplay is None:
            raise RuntimeError("ffplay not found on PATH; use --no-playback for marker-only capture")
        player = subprocess.Popen(
            [ffplay, "-nodisp", "-autoexit", "-loglevel", "error", str(audio_path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    started = time.monotonic()
    events: list[ResponseEvent] = []
    print("Trial active. Keys 1-7 mark responses; q ends the session.")
    print("1 piloerection | 2 movement | 3 tension | 4 release | 5 emotional peak | 6 spatial change | 7 other")

    try:
        while True:
            if player is not None and player.poll() is not None:
                break
            key = _read_key().lower()
            if key == "q":
                break
            response_type = KEYMAP.get(key)
            if response_type is None:
                continue
            event = ResponseEvent(
                session_time_s=time.monotonic() - started,
                response_type=response_type,
            )
            events.append(event)
            print(f"  {event.session_time_s:8.3f}s  {response_type}")
    finally:
        if player is not None and player.poll() is None:
            player.terminate()

    payload = {
        "schema": "phonic-drive-response-events-v3alpha2",
        "trial_id": trial_id,
        "stimulus_id": stimulus_id,
        "participant_pseudonym": participant_pseudonym,
        "source_audio": str(audio_path),
        "clock": "monotonic_session_seconds",
        "events": [
            {
                "session_time_s": event.session_time_s,
                "response_type": event.response_type,
                "intensity": event.intensity,
                "region": event.region,
                "confidence": event.confidence,
                "note": event.note,
            }
            for event in events
        ],
        "note": "Participant markers are observations, not causal labels.",
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return payload


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Play one stimulus and capture synchronized participant markers")
    p.add_argument("audio")
    p.add_argument("--output", default="response_events.json")
    p.add_argument("--trial-id")
    p.add_argument("--stimulus-id")
    p.add_argument("--participant")
    p.add_argument("--no-playback", action="store_true", help="Capture markers without launching FFplay")
    return p


def main(argv=None) -> int:
    args = parser().parse_args(argv)
    payload = run_trial(
        Path(args.audio),
        Path(args.output),
        trial_id=args.trial_id,
        stimulus_id=args.stimulus_id,
        participant_pseudonym=args.participant,
        play_audio=not args.no_playback,
    )
    print(f"Recorded events: {len(payload['events'])}")
    print(f"Output: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
