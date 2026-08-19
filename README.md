# Phonic Drive Analyzer

A batch-capable acoustic and state-space research toolkit for exploring how music changes over time and how recurring temporal structures can be compared with separately recorded participant observations.

## Current architecture

Phonic Drive deliberately keeps different evidence streams separate:

```text
A(t) = measured acoustic state
M(t) = descriptive motif / interaction state derived from A(t)
P(t) = reported perceptual / phenomenological state
K(t) = behavioral telemetry (planned)
T    = trial conditions and provenance
```

The working v2 CLI implements the measured acoustic stream and optional subjective `song_lens` annotations. The v3 migration now adds a real Python package boundary, typed research contracts, multiband acoustic trajectories, temporal derivatives, rolling cross-band relationships, and documented user-trial / falsification architecture.

The project does **not** silently turn subjective experience, simulation, or structural similarity into an objective biological claim.

See:

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — system architecture and evidence boundaries
- [`docs/V3_EVOLUTION.md`](docs/V3_EVOLUTION.md) — what is changing, where, how, and why
- [`docs/USER_TRIAL_PROTOCOL.md`](docs/USER_TRIAL_PROTOCOL.md) — timestamp-first participant trials and reconstruction loop
- [`phonic_drive/model_lab/README.md`](phonic_drive/model_lab/README.md) — optional dynamical-system simulation boundary

## Existing measured features

The v2 analyzer currently computes:

- waveform / STFT
- RMS energy
- spectral centroid
- spectral bandwidth
- 85% rolloff
- zero-crossing rate
- normalized spectral flux
- onset candidates
- tempo proxy
- stereo correlation / mid-side width
- multivariate transition speed / acceleration
- normalized 3D trajectory coordinates

It also:

- analyzes one file, batches, directories, globs, or `@file-list` inputs;
- continues a batch when one track fails;
- produces per-track plots, JSON summaries, and frame-level CSV telemetry;
- attaches optional `song_lens` annotations without mixing them into measured features;
- checks whether user-declared resonance-anchor frequencies have nearby spectral energy;
- produces batch-level CSV/JSON comparison outputs.

## v3 structural layer

The first v3 code lives under `phonic_drive/` while the v2 CLI remains operational during migration.

Initial v3 primitives include:

```text
frequency-band energy trajectories
first temporal derivatives
second temporal derivatives
rolling cross-band relationship matrices
```

These provide the foundation for an intermediate motif state `M(t)`: a descriptive representation of recurring temporal topology such as convergence, divergence, pulse, sweep, expansion, compression, oscillation, release, or recurrence.

A motif is a structural description. It is not automatically an entrainment event, neurological state, biochemical mechanism, or causal explanation.

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

The compatibility CLI currently continues to use the proven v2 orchestration while v3 internals are migrated module-by-module.

You can also run the legacy script directly:

```powershell
python .\phonic_drive_analysis_v2.py "song.mp3"
```

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
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

The v2 compatibility analyzer currently produces:

```text
phonic_drive_batch/
├── analysis_run.json
├── batch_summary.csv
├── batch_summary.json
├── batch_comparison.png
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

v3 will progressively add band-field telemetry, motif records, trial/session records, and evidence reports without discarding the existing outputs.

## State-space model

For each frame, v2 builds an acoustic feature vector containing energy, centroid, bandwidth, rolloff, zero-crossing rate, spectral flux, and stereo width.

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

v3 extends the measured representation into a multiband field and cross-band relationships before motif detection.

## `song_lens` annotations

See [`examples/annotations/song_lens.example.yaml`](examples/annotations/song_lens.example.yaml).

The analyzer keeps these records separate under `subjective_annotation` in the output summary. That makes it possible to compare:

```text
measured acoustic transition
        ↕
descriptive acoustic motif
        ↕
reported participant event
        ↕
behavioral telemetry
```

without collapsing one layer into another.

## User trials

The v3 trial model uses timestamp-first participant markers. A participant can mark an event during listening, with optional intensity/body-region/context added afterward.

The analysis layer can then compare multiple windows and lags around that event rather than assuming the acoustic correlate occurs at the exact motor-response timestamp.

Later trial stages can compare original, transformed, scrambled, RMS-matched, or reconstructed stimuli to test whether candidate structural properties survive controlled perturbation.

## Model Lab

`phonic_drive/model_lab/` is an optional simulation sandbox for exploring whether simple local interaction rules can generate structural motifs similar to those measured in audio.

Boid-like agents, fields, reaction-diffusion behavior, excitation, decay, saturation, refractory behavior, and hysteresis are legitimate simulation abstractions there. Structural similarity from Model Lab is not evidence that the same physical mechanism produced a biological response.

## Development

```bash
pip install -e ".[dev]"
pytest
```

Syntax check for the compatibility analyzer:

```bash
python -m py_compile phonic_drive_analysis_v2.py
```

## Migration roadmap

1. preserve v2 behavior and outputs;
2. establish typed v3 contracts and pure functions;
3. extract acoustic analysis into `phonic_drive.analysis`;
4. implement motif segmentation, similarity, and recurrence;
5. add timestamp-first user trials;
6. build an evidence-oriented interpreter;
7. add reconstruction / ablation controls;
8. keep Model Lab optional and epistemically separate.

## License

This project is licensed under the [MIT License](LICENSE).
