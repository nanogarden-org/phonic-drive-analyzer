# Phonic Drive Analyzer

Phonic Drive is a contract-first acoustic, structural, trial, and visualization research toolkit for exploring how music changes over time and how recurring temporal structures can be compared with separately recorded participant observations.

The project is currently implemented primarily in Python for fast research iteration. Mature deterministic numerical components are intended to migrate progressively into a Rust core without changing the scientific contracts or user-facing artifact semantics. Godot is an optional UX/visualization layer, not a core dependency.

## Current architecture

Phonic Drive deliberately keeps different evidence streams separate:

```text
A(t) = measured acoustic state
M(t) = descriptive motif / interaction state derived from A(t)
P(t) = reported perceptual / phenomenological state
K(t) = behavioral telemetry
T    = trial conditions and provenance
R    = reconstruction / perturbation records
```

The project does **not** silently turn subjective experience, simulation, structural similarity, or visualization geometry into an objective biological claim.

Core invariant:

```text
Signal ≠ Feature ≠ Inference ≠ Claim ≠ Authorized action
```

## Implementation strategy

Phonic Drive is not being designed as "a Python program that will later be rewritten in Rust." It is being designed as a contract-defined system whose implementations can change independently.

Planned topology:

```text
                         Stable contracts
                    schemas / IDs / timing
                              │
                              ▼
                         Rust Core
                deterministic numerical engine
                      /       |        \
                     /        |         \
                Python      Godot       CLI
               research       UX       automation
```

### Python

Python is the current reference and research implementation. It remains the fastest-moving layer for:

- algorithm development
- experiment orchestration
- evidence logic
- schema evolution
- corpus validation
- compatibility testing
- lightweight desktop fallback UI

### Rust

Rust is the planned production core for mature deterministic components such as:

- framing / STFT
- spectral features
- band trajectories
- temporal derivatives
- transition detection
- relationship matrices
- motif primitives
- recurrence search
- reconstruction DSP

The preferred first Python↔Rust bridge is PyO3/maturin so Python-facing APIs can remain stable while implementations move underneath them.

Target shape:

```python
from phonic_drive_core import analyze_track
```

### Godot

Godot is an optional presentation and interaction consumer for:

- desktop UX
- 2D/3D mesh visualization
- playback controls
- trial response capture
- overlays and event inspection
- future spatial / installation / VR modes

Godot consumes renderer-facing contracts rather than scientific internals. Phonic Drive must remain usable without Godot.

See [`docs/CORE_MIGRATION_PATH.md`](docs/CORE_MIGRATION_PATH.md) for the complete Python → Rust migration path, parity gates, timing/numerical contracts, backend provenance, and capability ladder.

## Current v3 architecture

The v3 package lives under `phonic_drive/` and includes:

```text
phonic_drive/
├── analysis/          measured acoustic primitives
├── motifs/            descriptive motif candidates and recurrence
├── trials/            timestamp-first response capture
├── behavior/          K(t) behavioral telemetry
├── interpreter/       evidence and alignment utilities
├── reconstruction/    perturbation / falsification transforms
├── validation/        corpus and timeline comparison
├── visualization/     Python-side visualization helpers
├── study.py           study/corpus conventions
├── session.py         provenance-linked session records
├── visual_bridge.py   renderer-facing Python → Godot contract
└── desktop/           emerging non-CLI application layer
```

Native v3 uses one decode/STFT pass to derive both measured acoustic state A(t) and structural state M(t).

## Native v3 artifacts

A successful native v3 analysis currently writes:

```text
acoustic_summary.json
acoustic_timeline.csv
transitions.json
structural_analysis.json
structural_timeline.csv
motifs.json
relationships.npz
```

These are intended to remain implementation-independent artifacts: a future Rust backend should produce the same versioned contracts within documented numerical tolerances.

## Structural layer M(t)

Current structural primitives include:

- logarithmic multiband energy trajectories
- first temporal derivatives
- second temporal derivatives
- rolling cross-band relationship matrices
- acoustic motif candidate segmentation
- motif signature similarity
- structural recurrence detection

A motif is a structural description. It is not automatically an entrainment event, neurological state, biochemical mechanism, or causal explanation.

## Trials and evidence

The v3 trial model records timestamp-first participant events separately from acoustic analysis.

Response categories currently include:

- piloerection
- perceived movement
- pressure / tension
- release
- emotional peak
- spatial change
- other

Participant markers remain observations rather than causal labels.

The evidence system supports progressive testing from observation and temporal proximity through repeated structural association, perturbation, and reconstruction.

## Reconstruction and falsification

Phonic Drive includes controlled reconstruction transforms such as:

- time reversal
- timing scramble / segment shuffle
- spectral-band ablation
- envelope-preserved noise controls
- RMS matching
- circular time shifts

The purpose is to test whether candidate relationships survive transformations that selectively preserve or disrupt parts of the acoustic structure.

## Godot visualizer

The first optional Godot visualizer scaffold is under:

```text
godot/phonic_drive_visualizer/
```

Current boundary:

```text
Python A(t) / M(t) / optional P(t)/K(t)
        ↓
phonic-drive-visual-state-v1
        ↓
Godot renderer
mesh + UI + overlays
```

The first transport is an atomically replaced JSON visual-state file. Once the contract stabilizes it may move to localhost streaming, and a later Rust core may publish the same contract directly.

See [`godot/phonic_drive_visualizer/README.md`](godot/phonic_drive_visualizer/README.md) and [`docs/GODOT_VISUALIZER_ARCHITECTURE.md`](docs/GODOT_VISUALIZER_ARCHITECTURE.md).

## Desktop UX direction

CLI commands remain useful for automation, CI, batch work, and debugging, but they are not intended to remain the normal user interface.

The desktop target is:

```text
open Phonic Drive
→ choose/resume study
→ select track
→ Analyze
→ Start Trial
→ click response buttons
→ auto-save
→ Compare / Visualize
```

The application should remember study/output locations and derive artifact paths from manifests rather than requiring users to manage absolute paths manually.

See:

- [`docs/DESKTOP_UI_UX_SPEC.md`](docs/DESKTOP_UI_UX_SPEC.md)
- [`docs/DESKTOP_COMPONENT_MAP.md`](docs/DESKTOP_COMPONENT_MAP.md)

## Requirements

Core Python path:

- Python 3.10+
- FFmpeg available on `PATH`

Python 3.13+ installs `audioop-lts` automatically because `audioop` was removed from the Python standard library.

Optional:

- Godot 4.x for the 3D visualization/UX project
- Rust toolchain only for developers working on the future compiled core

Basic research use must not require Godot, a discrete GPU, a cloud service, or a Rust compiler on an end-user machine.

## Python installation

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Install FFmpeg separately and verify `ffmpeg`, `ffprobe`, and `ffplay` are available on `PATH` when playback is required.

## Commands

Compatibility path:

```powershell
phonic-drive "song.mp3"
```

Native v3:

```powershell
phonic-drive-v3 "song.mp3"
```

Corpus validation:

```powershell
phonic-drive-corpus "C:\path\to\music" --recursive
```

Study-folder workflow:

```powershell
phonic-drive-study "C:\path\to\study"
```

Timestamp-first trial capture:

```powershell
phonic-drive-trial "song.mp3"
```

Operational tools:

```powershell
phonic-drive-ops --help
```

These commands remain adapters over domain functionality; desktop and Godot development should increasingly call shared Python services directly rather than spawning CLI subprocesses.

## Study and session provenance

Phonic Drive study/session records preserve links among:

- source stimulus
- study ID
- track sequence
- participant pseudonym when applicable
- analysis ID
- structural ID
- trial ID
- hypothesis IDs
- transform IDs
- artifact paths
- schema versions

As multiple backends emerge, provenance will also identify the engine/backend version used to generate an artifact without changing its scientific meaning.

## Model Lab

`phonic_drive/model_lab/` remains an optional simulation sandbox for asking whether simple local interaction rules can generate structures similar to measured acoustic motifs.

Simulation similarity does not establish the same mechanism in physiology.

## Migration rules

Python → Rust migration follows these rules:

1. no rewrite day;
2. port one mature deterministic component at a time;
3. freeze/version the relevant contracts first;
4. run Python and Rust side by side;
5. compare outputs on representative corpora;
6. document numerical tolerances explicitly;
7. retain unexplained discrepancies as defects/evidence rather than hiding them;
8. record backend/version provenance;
9. keep the Python reference available until the Rust path is trusted;
10. let Godot consume stable contracts rather than backend-specific objects.

A component is ready for Rust only when its purpose, inputs, outputs, tests, representative behavior, and unresolved algorithmic questions are sufficiently stable to justify the port.

## Documentation

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — evidence and system architecture
- [`docs/V3_EVOLUTION.md`](docs/V3_EVOLUTION.md) — v3 migration history and rationale
- [`docs/SYSTEM_PIPELINE.md`](docs/SYSTEM_PIPELINE.md) — current operational pipeline
- [`docs/CORE_MIGRATION_PATH.md`](docs/CORE_MIGRATION_PATH.md) — Python → Rust core path
- [`docs/DESKTOP_UI_UX_SPEC.md`](docs/DESKTOP_UI_UX_SPEC.md) — desktop product specification
- [`docs/DESKTOP_COMPONENT_MAP.md`](docs/DESKTOP_COMPONENT_MAP.md) — UI/controller/domain mapping
- [`docs/GODOT_VISUALIZER_ARCHITECTURE.md`](docs/GODOT_VISUALIZER_ARCHITECTURE.md) — Python/Godot renderer boundary
- [`docs/USER_TRIAL_PROTOCOL.md`](docs/USER_TRIAL_PROTOCOL.md) — trial and falsification protocol
- [`phonic_drive/model_lab/README.md`](phonic_drive/model_lab/README.md) — simulation boundary

## Development

```bash
python -m pip install -e ".[dev]"
pytest
```

During Rust migration, differential Python/Rust corpus tests will become a required gate before compiled implementations become defaults.

## License

This project is licensed under the [MIT License](LICENSE).
