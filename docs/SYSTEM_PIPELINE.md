# Phonic Drive v3 system pipeline

## Purpose

This document records how the v3 engine moves from source audio through measured structure, participant observations, and evidence-oriented interpretation without collapsing those layers into one claim.

## 1. Single-pass track object

`phonic_drive.track.TrackAnalysis` is the new computational center of the engine.

One decode and one STFT feed both:

```text
Audio
  -> decoded samples
  -> STFT
      -> A(t): measured acoustic features / transition field
      -> M(t): multiband trajectories / relationships / motif candidates
```

The object intentionally does **not** contain participant reports or biological interpretation.

### Why

The previous compatibility path could recompute the same source audio for structural analysis. That was acceptable for migration but wasteful and conceptually fragmented. `TrackAnalysis` makes shared source data explicit and keeps derived layers synchronized to the same frame clock.

## 2. Native and compatibility commands

Two commands coexist during migration.

### `phonic-drive`

Compatibility command. It preserves the established v2 orchestration and output schemas while routing extracted signal primitives through the v3 package.

### `phonic-drive-v3`

Native research command. It creates a `TrackAnalysis` once and emits v3 structural artifacts directly.

Example:

```powershell
phonic-drive-v3 "song.mp3" --output "runs/v3-test"
```

The compatibility command remains the behavioral reference until native output coverage and CI confidence are sufficient for an intentional switchover.

## 3. Structural artifact bundle

The native engine emits:

```text
structural_analysis.json
structural_timeline.csv
motifs.json
relationships.npz
```

### `structural_analysis.json`

Human- and machine-readable summary of band geometry, descriptive relationships, motif candidates, and recurrence.

### `structural_timeline.csv`

Dense time-aligned values for every spectral band:

```text
energy
first derivative / velocity
second derivative / acceleration
```

This is the practical bridge into notebooks, visualization, clustering, and later user-event alignment.

### `motifs.json`

Motif candidates and structural recurrence are separated from the larger summary so they can become durable graph/provenance objects later.

### `relationships.npz`

Compressed numerical storage of the complete time-varying cross-band relationship tensor. JSON stores summaries; NPZ preserves the dense research representation.

## 4. Participant response stream P(t)

`phonic_drive.trials` introduces `EventRecorder` and `ResponseEvent`.

A user interface or hotkey layer can call:

```text
mark(response_type, intensity, region, confidence, note)
```

The recorder uses a monotonic session clock and writes participant observations separately from acoustic analysis.

Canonical windows currently include:

```text
250 ms
500 ms
1 s
2 s
5 s
10 s
```

before an event, plus a configurable post-event window.

## 5. Alignment is not interpretation

`nearest_motifs()` answers only:

> Which measured motif candidates are temporally near this participant marker, and at what lag?

It does not assign causality or biological meaning.

This preserves the intended separation:

```text
A(t) measured acoustic state
M(t) descriptive acoustic structure
P(t) participant response reports
K(t) future behavioral telemetry
T    trial conditions
```

## 6. Interpreter evidence ladder

`phonic_drive.interpreter` now encodes explicit evidence levels:

```text
0 observation
1 temporal proximity
2 within-participant structural association
3 cross-stimulus recurrence
4 perturbation evidence
5 reconstruction evidence
```

The interpreter's job is therefore not to invent an explanation. Its job is to say what level of support exists for a statement and preserve the supporting records.

## 7. What remains next

The next engineering passes should proceed in this order:

1. add a native measured `A(t)` timeline/export so v3 no longer relies on v2 output formats for acoustic telemetry;
2. add trial manifest/schema objects connecting stimulus, participant event file, transform, and hypothesis IDs;
3. implement randomized A/B/X trial ordering and reproducible seeds;
4. add motif-to-response aggregation across repeated sessions;
5. add reconstruction/ablation transforms while retaining provenance to the source motif;
6. add optional `K(t)` behavioral telemetry;
7. only after those layers are stable, connect Model Lab synthetic dynamics to motif-space comparison.

## 8. Boundary for Model Lab

Boid, field, reaction-diffusion, chemistry, or photon-like agent simulations remain a separate synthetic hypothesis layer.

The permitted relationship is:

```text
synthetic dynamics
    -> synthetic structural motif
    -> compare geometry against empirical M(t)
```

The prohibited shortcut is:

```text
simulation resembles data
    -> therefore simulation explains physiology
```

Similarity is a hypothesis generator, not a causal conclusion.

## 9. Migration criterion

The default `phonic-drive` command should switch from compatibility orchestration to the native `TrackAnalysis` engine only when:

- native A(t) outputs cover the useful v2 measured telemetry;
- regression tests demonstrate acceptable numerical equivalence where equivalence is intended;
- new M(t) outputs have stable schemas;
- CI passes across supported Python versions;
- a representative audio corpus has been run through both paths without unexplained discrepancies.

Until then, the dual-command arrangement is intentional technical scaffolding, not duplication by accident.
