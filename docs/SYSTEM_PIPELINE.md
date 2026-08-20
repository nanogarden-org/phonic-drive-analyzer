# Phonic Drive v3 system pipeline

## Purpose

This document records how the v3 engine moves from source audio through measured structure, participant observations, controlled trials, and evidence-oriented interpretation without collapsing those layers into one claim.

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

`TrackAnalysis` keeps measured and structural layers synchronized to one frame clock and removes the architectural need to decode the same source again for structural work.

## 2. Native and compatibility commands

Two commands coexist during migration.

### `phonic-drive`

Compatibility command. It preserves established v2 orchestration/output behavior while routing extracted signal primitives through the v3 package.

### `phonic-drive-v3`

Native research command. It creates a `TrackAnalysis` once and emits v3 structural artifacts directly.

```powershell
phonic-drive-v3 "song.mp3" --output "runs/v3-test"
```

The compatibility command remains the behavioral reference until native output coverage and validation justify an intentional switchover.

## 3. Structural artifact bundle

The native engine emits:

```text
structural_analysis.json
structural_timeline.csv
motifs.json
relationships.npz
```

`structural_analysis.json` contains human/machine-readable structural summaries.

`structural_timeline.csv` preserves dense time-aligned band energy, first derivative / velocity, and second derivative / acceleration.

`motifs.json` separates motif candidates and recurrence into durable objects suitable for later graph/provenance linking.

`relationships.npz` preserves the complete time-varying cross-band relationship tensor while JSON remains compact and inspectable.

## 4. Participant response stream P(t)

`phonic_drive.trials` contains `EventRecorder` and `ResponseEvent`.

A hotkey/UI layer can record:

```text
mark(response_type, intensity, region, confidence, note)
```

The recorder uses a monotonic session clock and writes participant observations separately from acoustic analysis.

Canonical pre-event windows include:

```text
250 ms
500 ms
1 s
2 s
5 s
10 s
```

plus a configurable post-event interval.

`nearest_motifs()` only computes temporal proximity and lag. It does not assign causality or biological meaning.

## 5. Reproducible trial layer T

`phonic_drive.trials.protocol` now provides:

```text
StimulusCondition
TrialManifest
stable_seed()
randomized_order()
build_manifest()
```

This makes A/B/X ordering reproducible and places randomization inside trial provenance rather than leaving it as a manual procedural note.

A trial manifest can connect:

```text
trial_id
hypothesis_id
participant pseudonym
stimulus conditions
transform IDs
randomization seed
presentation order
```

## 6. Interpreter evidence ladder

`phonic_drive.interpreter` encodes explicit evidence levels:

```text
0 observation
1 temporal proximity
2 within-participant structural association
3 cross-stimulus recurrence
4 perturbation evidence
5 reconstruction evidence
```

The interpreter's job is not to invent an explanation. Its job is to state what kind of support exists and preserve the records supporting that statement.

## 7. Reconstruction and ablation provenance

`phonic_drive.reconstruction` now provides manifests describing controlled stimulus variants before synthesis/rendering is implemented.

Each transform can record:

```text
reconstruction_id
source stimulus
source motif IDs
hypothesis ID
operation
parameters
properties preserved
properties disrupted
output path
```

This is the provenance bridge required for later questions such as:

```text
preserve band trajectory
but disrupt timing order
```

or:

```text
preserve temporal envelope
but alter timbre
```

A reconstruction should never become an anonymous derived audio file whose relationship to the hypothesis has been lost.

## 8. Current implemented path

```text
Audio
  -> one decode / one STFT
       -> A(t) measured acoustic state
       -> M(t) structural acoustic state
            -> dense timeline
            -> relationship tensor
            -> motif candidates
            -> recurrence

P(t) participant response events
T    reproducible randomized trial manifest
R    reconstruction / ablation manifest

A + M + P + T + R
        -> evidence-oriented Interpreter
```

`K(t)` behavioral/workflow telemetry remains a future optional stream.

## 9. Model Lab boundary

Boid, field, reaction-diffusion, chemistry, or photon-like agent simulations remain a separate synthetic hypothesis layer.

Permitted relationship:

```text
synthetic dynamics
    -> synthetic structural motif
    -> compare geometry against empirical M(t)
```

Prohibited shortcut:

```text
simulation resembles data
    -> therefore simulation explains physiology
```

Similarity is a hypothesis generator, not a causal conclusion.

## 10. Next engineering passes

With single-pass analysis, structural exports, event capture, randomized manifests, evidence levels, and reconstruction provenance now scaffolded, the next work should proceed approximately as follows:

1. add a native measured `A(t)` timeline/export so v3 fully covers useful measured telemetry without relying on v2 schemas;
2. add motif-to-response aggregation across repeated sessions and stimuli;
3. implement concrete reconstruction/ablation audio transforms behind the existing provenance contracts;
4. add session/result manifests linking analysis IDs, event files, trial conditions, transforms, and interpreter outputs;
5. add optional `K(t)` behavioral telemetry;
6. add representative-corpus v2/v3 comparison tooling and discrepancy reports;
7. only after the empirical pipeline is stable, connect Model Lab synthetic dynamics to motif-space comparison.

## 11. Migration criterion

The default `phonic-drive` command should switch from compatibility orchestration to native `TrackAnalysis` only when:

- native `A(t)` outputs cover the useful v2 measured telemetry;
- regression tests demonstrate acceptable numerical equivalence where equivalence is intended;
- `M(t)` schemas are stable enough for trial/interpreter consumers;
- CI passes across supported Python versions;
- a representative audio corpus has been run through both paths without unexplained discrepancies.

Until then, the dual-command arrangement is intentional migration scaffolding rather than accidental duplication.
