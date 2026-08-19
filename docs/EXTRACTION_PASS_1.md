# Phonic Drive v3 — Extraction Pass 1

## Status

This document records the first executable migration step from the single-file v2 analyzer into the modular v3 architecture.

The goal of this pass is **behavior-preserving extraction first, new structural capability second**. The working v2 implementation remains available as a reference while the installed `phonic-drive` command begins exercising package-based v3 internals.

---

## What changed

### 1. Audio primitives moved to `phonic_drive.analysis.audio`

Extracted responsibilities:

- audio decoding through pydub
- channel normalization
- polyphase resampling
- short-signal padding
- overlapping frame creation
- STFT magnitude generation

These functions are intended to be measurements and transport utilities only. They do not attach perceptual meaning to an audio signal.

### 2. Acoustic features moved to `phonic_drive.analysis.features`

Extracted responsibilities:

- RMS energy
- zero-crossing rate
- spectral centroid
- spectral bandwidth
- spectral rolloff
- spectral flux
- stereo correlation and width

The implementations preserve the numerical procedures used by v2.

### 3. State-space motion moved to `phonic_drive.analysis.transitions`

Extracted responsibilities:

- robust z normalization
- percentile 0–1 scaling
- smoothing
- length alignment
- multidimensional transition speed
- transition acceleration
- acoustic transition candidate detection

The labels remain acoustic descriptions. They are not cognitive or physiological labels.

### 4. Installed CLI now passes through `phonic_drive.cli`

`pyproject.toml` now exposes:

```text
phonic-drive = phonic_drive.cli:main
```

The adapter installs the extracted v3 functions into the v2 orchestration module before executing it. This means the installed CLI exercises the new package modules while preserving the existing argument set and output schemas.

The legacy reference path remains available:

```text
python phonic_drive_analysis_v2.py ...
```

That reference path is intentionally retained during the migration so numerical equivalence can be tested directly.

---

## Why use an adapter instead of rewriting v2 immediately?

A full rewrite would combine two different risks:

1. reorganizing already-working code;
2. introducing new research behavior.

The compatibility adapter separates them.

At this stage:

```text
legacy orchestration
        |
        +-- v3 audio primitives
        +-- v3 measured features
        +-- v3 transition analysis
```

This gives Phonic Drive a reversible migration seam. If a regression is discovered, the original implementation is still present for comparison.

---

## New structural capability

Extraction Pass 1 also introduces the first implementation of the new `M(t)` layer.

### Multiband trajectories

`phonic_drive.analysis.bands` converts the STFT into logarithmically spaced band-energy trajectories.

For band `i`:

```text
q_i(t) = normalized energy in frequency band i at time t
```

The engine can derive:

```text
q_i(t)       band state
q'_i(t)      band velocity
q''_i(t)     band acceleration
```

### Cross-band relationships

Rolling correlation matrices describe local relationships between band trajectories:

```text
R_ij(t)
```

This is a descriptive relationship measure. It does not establish causal coupling.

### Motif candidates

`phonic_drive.motifs.detector` identifies local peaks in multiband trajectory speed and captures a time window around each peak.

A motif signature currently contains:

- mean band-state shape within the window;
- net band-direction change across the window.

The resulting object is deliberately labeled:

```text
acoustic motif candidate
```

It is not labeled with a participant effect.

### Recurrence

Motif signatures can be compared using cosine similarity. Repeated structural candidates can therefore be identified within a track without consulting `P(t)` participant annotations.

This preserves the firewall:

```text
A(t) -> M(t)

P(t) is not used to create M(t).
```

Participant response can be compared with motifs later by the Interpreter.

---

## How to run the new structural layer

The compatibility CLI accepts an adapter-only flag:

```powershell
phonic-drive "song.mp3" --structural
```

Normal v2 artifacts are created first. For each track whose v2 analysis succeeds, the adapter then adds:

```text
track_<id>/
├── summary.json                 # existing v2 schema
├── timeline.csv                 # existing v2 telemetry
├── ...
└── structural_analysis.json     # new v3 M(t) artifact
```

The structural artifact currently records:

- analysis parameters and band edges
- per-band mean and standard deviation
- per-band mean absolute velocity
- per-band mean absolute acceleration
- mean cross-band relationship matrix
- acoustic motif candidates
- recurring motif pairs

The full rolling relationship tensor is intentionally not embedded in JSON yet because it can become very large. A later pass should export dense structural telemetry as NPZ/Parquet/CSV according to use case.

---

## Tests introduced in this pass

### Equivalence tests

`tests/test_v3_equivalence.py` compares the extracted package functions directly with the retained v2 reference implementation using deterministic synthetic signals.

Coverage includes:

- frame creation
- STFT
- spectral features
- stereo features
- state-space motion
- transition detection
- CLI adapter substitution

The purpose is to detect accidental numerical changes during extraction.

### Motif tests

`tests/test_v3_motifs.py` builds synthetic repeated multiband events and verifies:

- candidate segmentation
- signature dimensions
- self-similarity
- recurrence matching

These are algorithm tests, not evidence that the synthetic pattern corresponds to a human effect.

---

## What has *not* been done yet

This pass intentionally does not:

- delete the v2 implementations;
- change the v2 `summary.json` schema;
- mix subjective annotations into motif detection;
- claim that correlation between bands is physical coupling;
- assign biological interpretations to motifs;
- implement participant event capture UI;
- implement the evidence-tier Interpreter;
- synthesize counterfactual audio;
- treat Model Lab boids/chemistry as explanatory physiology.

Those boundaries are deliberate.

---

## Next extraction pass

The next engineering step should migrate orchestration and artifact generation rather than duplicate more algorithms.

Recommended order:

1. create a v3 `TrackAnalysis` result object;
2. move per-track orchestration from `analyze_track` into package code;
3. compute `A(t)` and `M(t)` from the same STFT pass instead of decoding twice when `--structural` is used;
4. export frame-level band trajectories and motif membership;
5. add stable schema versions for structural artifacts;
6. add participant event recording as a separate `P(t)` stream;
7. only then build Interpreter correspondence analysis.

The key invariant remains:

```text
measurement -> structure -> comparison -> hypothesis -> test
```

not:

```text
experience -> explanation -> retrofitted measurement
```
