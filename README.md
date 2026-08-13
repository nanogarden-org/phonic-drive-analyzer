# Phonic Drive Analyzer

A batch-capable acoustic and state-space analysis tool for exploring how music changes over time.

The project deliberately keeps two layers separate:

1. **Measured acoustic features** — waveform/STFT, RMS energy, spectral centroid, bandwidth, rolloff, zero-crossing rate, spectral flux, onset candidates, tempo proxy, stereo correlation/width, and multivariate transition speed/acceleration.
2. **Subjective Phonic Drive annotations** — optional `song_lens` YAML/TXT records describing perceived motion, dimensional expansion, stability, inflection points, and resonance anchors.

The point is not to silently turn subjective experience into an objective claim. Instead, the tool puts both streams on a common timeline so they can be compared later.

## Features

- Analyze one file, many files, directories, globs, or `@file-list` inputs.
- Continue a batch when one track fails.
- Produce per-track plots, JSON summaries, and frame-level CSV telemetry.
- Export normalized 3D coordinates for:
  - spectral brightness
  - acoustic energy
  - stereo spatial width
- Detect candidate acoustic transition events from a multi-feature state vector.
- Attach optional `song_lens` annotations without mixing them into measured features.
- Check whether user-declared resonance-anchor frequencies have nearby spectral energy.
- Produce batch-level CSV/JSON comparison outputs.

## Requirements

- Python 3.10+
- FFmpeg available on `PATH`

Python dependencies are listed in `pyproject.toml` and `requirements.txt`.

## Quick start

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e .
```

Install FFmpeg separately and make sure `ffmpeg` is available from PowerShell.

Then:

```powershell
phonic-drive "song.mp3"
```

You can also run the script directly:

```powershell
python .\phonic_drive_analysis_v2.py "song.mp3"
```

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e .
phonic-drive "song.mp3"
```

## Input modes

One track:

```bash
phonic-drive "track.mp3"
```

Several tracks:

```bash
phonic-drive "a.mp3" "b.flac" "c.wav"
```

Directory:

```bash
phonic-drive "/path/to/music" --recursive
```

Globs:

```bash
phonic-drive "/music/Blackmill/*.mp3" "/music/Audiomachine/*.flac"
```

File list:

```bash
phonic-drive @tracks.txt
```

With annotations:

```bash
phonic-drive "/music/*.mp3" --annotations "examples/annotations/*.yaml"
```

Custom output location:

```bash
phonic-drive "/music" --recursive --output "runs/run_001"
```

Skip PNG generation:

```bash
phonic-drive "/music" --recursive --no-plots
```

## Output layout

```text
phonic_drive_batch/
├── analysis_run.json
├── batch_summary.csv
├── batch_summary.json
├── batch_comparison.png        # when 2+ tracks and plots enabled
├── track_A_<source-id>/
│   ├── summary.json
│   ├── timeline.csv
│   ├── waveform.png
│   ├── spectrogram_db.png
│   ├── energy_timeline.png
│   ├── spectral_motion.png
│   ├── transition_field.png
│   └── mean_spectrum_peaks.png
└── track_B_<source-id>/
    └── ...
```

## State-space model

For each frame, the analyzer builds an acoustic feature vector containing energy, centroid, bandwidth, rolloff, zero-crossing rate, spectral flux, and stereo width.

After robust normalization and smoothing, it estimates:

- **transition speed** — magnitude of change through acoustic feature-space
- **transition acceleration** — change in transition speed

It also exports a compact 3D trajectory:

```text
X = spectral brightness / centroid
Y = RMS energy
Z = stereo spatial width
```

These are visualization coordinates, not claims that the axes directly measure cognition.

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the conceptual model.

## `song_lens` annotations

See [`examples/annotations/song_lens.example.yaml`](examples/annotations/song_lens.example.yaml).

The analyzer keeps these records separate under `subjective_annotation` in the output summary. That makes it possible to later test relationships such as:

```text
measured acoustic transition
        ↕
reported spatial / cognitive transition
        ↕
workflow telemetry
```

without collapsing one layer into another.

## Development

```bash
pip install -e ".[dev]"
pytest
```

Syntax check only:

```bash
python -m py_compile phonic_drive_analysis_v2.py
```

## Roadmap

Likely next layers:

- keyboard/workflow telemetry synchronized to audio time
- user event-marker hotkeys during listening/work sessions
- 3D trajectory viewer
- transition-type clustering across tracks
- session-level comparisons across artists/playlists
- richer tempo/onset estimation via an optional audio-analysis backend
- annotation schema validation and versioning

## License

This project is licensed under the [MIT License](LICENSE).
