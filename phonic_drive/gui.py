"""Desktop UI for normal Phonic Drive use.

The CLI remains available for automation/debugging, but this module is the
human-facing path for selecting audio, running v3 analysis, and recording P(t)
response events without hand-entering paths or JSON.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .config import UserConfig, ensure_user_dirs, load_config, save_config
from .exports import write_v3_bundle
from .track import analyze_track

RESPONSE_TYPES = [
    ("Piloerection", "piloerection"),
    ("Perceived movement", "perceived_movement"),
    ("Pressure / tension", "pressure_tension"),
    ("Release", "release"),
    ("Emotional peak", "emotional_peak"),
    ("Spatial change", "spatial_change"),
    ("Other", "other"),
]


class PhonicDriveApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Phonic Drive")
        self.geometry("820x620")
        self.minsize(720, 560)
        self.config_state: UserConfig = load_config()
        ensure_user_dirs(self.config_state)

        self.audio_path: Path | None = None
        self.player: subprocess.Popen | None = None
        self.trial_started: float | None = None
        self.trial_events: list[dict] = []
        self.trial_id: str | None = None
        self.stimulus_id: str | None = None

        self.audio_var = tk.StringVar(value="No audio selected")
        self.corpus_var = tk.StringVar(value=self.config_state.corpus_root or "No corpus folder selected")
        self.output_var = tk.StringVar(value=str(self.config_state.output_path))
        self.participant_var = tk.StringVar(value=self.config_state.participant_pseudonym)
        self.status_var = tk.StringVar(value="Ready")
        self.event_count_var = tk.StringVar(value="Events recorded: 0")
        self.time_var = tk.StringVar(value="00:00.0")

        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        outer = ttk.Frame(self, padding=16)
        outer.pack(fill="both", expand=True)

        ttk.Label(outer, text="PHONIC DRIVE", font=("Segoe UI", 18, "bold")).pack(anchor="w")
        ttk.Label(outer, text="Analyze structure and capture synchronized human response events.").pack(anchor="w", pady=(0, 14))

        source = ttk.LabelFrame(outer, text="Source", padding=12)
        source.pack(fill="x")
        ttk.Label(source, textvariable=self.audio_var, wraplength=650).grid(row=0, column=0, sticky="w", padx=(0, 8))
        ttk.Button(source, text="Choose audio…", command=self.choose_audio).grid(row=0, column=1, sticky="e")
        ttk.Label(source, textvariable=self.corpus_var, wraplength=650).grid(row=1, column=0, sticky="w", pady=(8, 0), padx=(0, 8))
        ttk.Button(source, text="Choose corpus…", command=self.choose_corpus).grid(row=1, column=1, sticky="e", pady=(8, 0))
        source.columnconfigure(0, weight=1)

        settings = ttk.LabelFrame(outer, text="Session", padding=12)
        settings.pack(fill="x", pady=12)
        ttk.Label(settings, text="Participant").grid(row=0, column=0, sticky="w")
        ttk.Entry(settings, textvariable=self.participant_var, width=18).grid(row=0, column=1, sticky="w", padx=(8, 20))
        ttk.Label(settings, text="Output").grid(row=0, column=2, sticky="w")
        ttk.Entry(settings, textvariable=self.output_var).grid(row=0, column=3, sticky="ew", padx=8)
        ttk.Button(settings, text="Choose…", command=self.choose_output).grid(row=0, column=4)
        settings.columnconfigure(3, weight=1)

        actions = ttk.Frame(outer)
        actions.pack(fill="x")
        ttk.Button(actions, text="Analyze with v3", command=self.analyze_selected).pack(side="left")
        ttk.Button(actions, text="Open output folder", command=self.open_output).pack(side="left", padx=8)
        self.start_trial_button = ttk.Button(actions, text="Start response trial", command=self.start_trial)
        self.start_trial_button.pack(side="right")

        trial = ttk.LabelFrame(outer, text="Live response capture", padding=12)
        trial.pack(fill="both", expand=True, pady=(12, 0))
        top = ttk.Frame(trial)
        top.pack(fill="x")
        ttk.Label(top, textvariable=self.time_var, font=("Segoe UI", 20, "bold")).pack(side="left")
        ttk.Label(top, textvariable=self.event_count_var).pack(side="right")

        buttons = ttk.Frame(trial)
        buttons.pack(fill="both", expand=True, pady=12)
        for i, (label, key) in enumerate(RESPONSE_TYPES):
            button = ttk.Button(buttons, text=label, command=lambda k=key: self.mark_response(k))
            button.grid(row=i // 2, column=i % 2, sticky="nsew", padx=5, pady=5, ipady=12)
        for col in range(2):
            buttons.columnconfigure(col, weight=1)
        for row in range(4):
            buttons.rowconfigure(row, weight=1)

        bottom = ttk.Frame(trial)
        bottom.pack(fill="x")
        self.end_trial_button = ttk.Button(bottom, text="End trial & save", command=self.end_trial, state="disabled")
        self.end_trial_button.pack(side="right")
        ttk.Label(bottom, textvariable=self.status_var, wraplength=560).pack(side="left")

    def choose_audio(self):
        initial = self.config_state.corpus_root or str(Path.home())
        path = filedialog.askopenfilename(
            title="Choose audio",
            initialdir=initial,
            filetypes=[("Audio files", "*.mp3 *.wav *.flac *.m4a *.ogg"), ("All files", "*.*")],
        )
        if path:
            self.audio_path = Path(path)
            self.audio_var.set(str(self.audio_path))

    def choose_corpus(self):
        path = filedialog.askdirectory(title="Choose Phonic Drive corpus folder", initialdir=self.config_state.corpus_root or str(Path.home()))
        if path:
            self.config_state.corpus_root = path
            self.corpus_var.set(path)
            self._persist_config()

    def choose_output(self):
        path = filedialog.askdirectory(title="Choose output folder", initialdir=self.output_var.get())
        if path:
            self.output_var.set(path)
            self.config_state.output_root = path
            self._persist_config()

    def _persist_config(self):
        self.config_state.participant_pseudonym = self.participant_var.get().strip() or "P001"
        self.config_state.output_root = self.output_var.get().strip() or None
        save_config(self.config_state)

    def analyze_selected(self):
        if self.audio_path is None:
            self.choose_audio()
        if self.audio_path is None:
            return
        self._persist_config()
        source = self.audio_path
        output = Path(self.output_var.get()) / "analysis" / source.stem
        self.status_var.set(f"Analyzing {source.name}…")

        def worker():
            try:
                track = analyze_track(source)
                artifacts = write_v3_bundle(track, output)
                self.after(0, lambda: self.status_var.set(f"Analysis complete: {output}"))
                self.after(0, lambda: messagebox.showinfo("Phonic Drive", f"Analysis complete.\n\n{len(track.transition_candidates)} transitions\n{len(track.motif_candidates)} motifs\n\nSaved to:\n{output}"))
            except Exception as exc:
                self.after(0, lambda: messagebox.showerror("Analysis failed", str(exc)))
                self.after(0, lambda: self.status_var.set("Analysis failed"))

        threading.Thread(target=worker, daemon=True).start()

    def start_trial(self):
        if self.audio_path is None:
            self.choose_audio()
        if self.audio_path is None:
            return
        if self.player is not None:
            messagebox.showwarning("Trial active", "A trial is already running.")
            return
        ffplay = shutil.which("ffplay")
        if ffplay is None:
            messagebox.showerror("FFplay missing", "FFplay was not found. Install FFmpeg, then reopen Phonic Drive.")
            return

        self._persist_config()
        stamp = time.strftime("%Y%m%d-%H%M%S")
        self.trial_id = f"PD-{stamp}"
        self.stimulus_id = self.audio_path.stem
        self.trial_events = []
        self.event_count_var.set("Events recorded: 0")
        self.player = subprocess.Popen(
            [ffplay, "-nodisp", "-autoexit", "-loglevel", "error", str(self.audio_path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        self.trial_started = time.monotonic()
        self.start_trial_button.configure(state="disabled")
        self.end_trial_button.configure(state="normal")
        self.status_var.set(f"Trial active: {self.audio_path.name}")
        self.after(50, self._poll_trial)

    def _poll_trial(self):
        if self.player is None or self.trial_started is None:
            return
        elapsed = time.monotonic() - self.trial_started
        minutes = int(elapsed // 60)
        seconds = elapsed - minutes * 60
        self.time_var.set(f"{minutes:02d}:{seconds:04.1f}")
        if self.player.poll() is not None:
            self.end_trial(auto=True)
            return
        self.after(50, self._poll_trial)

    def mark_response(self, response_type: str):
        if self.trial_started is None or self.player is None:
            return
        event = {
            "session_time_s": time.monotonic() - self.trial_started,
            "response_type": response_type,
            "intensity": None,
            "region": None,
            "confidence": None,
            "note": None,
        }
        self.trial_events.append(event)
        self.event_count_var.set(f"Events recorded: {len(self.trial_events)}")

    def end_trial(self, auto: bool = False):
        if self.player is None and self.trial_started is None:
            return
        if self.player is not None and self.player.poll() is None:
            self.player.terminate()
        source = self.audio_path
        output_root = Path(self.output_var.get()) / "trials"
        output_root.mkdir(parents=True, exist_ok=True)
        safe_name = source.stem if source else "trial"
        output = output_root / f"{safe_name}_response_events.json"
        payload = {
            "schema": "phonic-drive-response-events-v3alpha2",
            "trial_id": self.trial_id,
            "stimulus_id": self.stimulus_id,
            "participant_pseudonym": self.participant_var.get().strip() or "P001",
            "source_audio": str(source) if source else None,
            "clock": "monotonic_session_seconds",
            "events": self.trial_events,
            "note": "Participant markers are observations, not causal labels.",
        }
        output.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        count = len(self.trial_events)
        self.player = None
        self.trial_started = None
        self.start_trial_button.configure(state="normal")
        self.end_trial_button.configure(state="disabled")
        self.status_var.set(f"Trial saved automatically: {output}")
        messagebox.showinfo("Trial saved", f"Recorded {count} events.\n\nSaved to:\n{output}")

    def open_output(self):
        path = Path(self.output_var.get())
        path.mkdir(parents=True, exist_ok=True)
        if os.name == "nt":
            os.startfile(path)  # type: ignore[attr-defined]
        else:
            subprocess.Popen(["xdg-open", str(path)])

    def _on_close(self):
        self._persist_config()
        if self.player is not None and self.player.poll() is None:
            self.player.terminate()
        self.destroy()


def main() -> int:
    app = PhonicDriveApp()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
