# Phonic Drive v3 system pipeline

## Purpose

This document records how the v3 engine moves from source audio through measured structure, participant observations, controlled trials, reconstruction, behavioral telemetry, and evidence-oriented interpretation without collapsing those layers into one claim.

## 1. Single-pass track object

`phonic_drive.track.TrackAnalysis` is the computational center of the native engine.

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

Native research command. It creates a `TrackAnalysis` once and emits native A(t) and M(t) artifacts directly.

```powershell
phonic-drive-v3 "song.mp3" --output "runs/v3-test"
```

Optional provenance linkage can be added with participant/trial/hypothesis/transform arguments so the same run also emits `session_manifest.json`.

The compatibility command remains the behavioral reference until native output coverage and validation justify an intentional switchover.

## 3. Native A(t) measured artifact bundle

The native engine now emits:

```text
acoustic_summary.json
acoustic_timeline.csv
transitions.json
```

`acoustic_summary.json` stores compact descriptive statistics and the native state-space axis definitions.

`acoustic_timeline.csv` preserves the measured per-frame telemetry used by the v2 analyzer:

```text
RMS / RMS dB
spectral centroid
spectral bandwidth
85% rolloff
zero-crossing rate
spectral flux
stereo correlation / width
state X/Y/Z
transition speed / acceleration
```

`transitions.json` separates candidate acoustic transition events into a durable object.

These are measured acoustic records, not cognitive or physiological labels.

## 4. Native M(t) structural artifact bundle

The same single-pass analysis emits:

```text
structural_analysis.json
structural_timeline.csv
motifs.json
relationships.npz
```

`structural_analysis.json` contains human/machine-readable structural summaries.

`structural_timeline.csv` preserves dense time-aligned band energy, first derivative / velocity, and second derivative / acceleration.

`motifs.json` separates motif candidates and recurrence into durable objects suitable for graph/provenance linking.

`relationships.npz` preserves the complete time-varying cross-band relationship tensor while JSON remains compact and inspectable.

## 5. Participant response stream P(t)

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

## 6. Reproducible trial layer T

`phonic_drive.trials.protocol` provides:

```text
StimulusCondition
TrialManifest
stable_seed()
randomized_order()
build_manifest()
```

This makes A/B/X ordering reproducible and places randomization inside trial provenance rather than leaving it as a manual procedural note.

A trial manifest can connect trial ID, hypothesis ID, participant pseudonym, stimulus conditions, transform IDs, randomization seed, and presentation order.

## 7. Behavioral/workflow telemetry K(t)

`phonic_drive.behavior` now provides a minimal `BehaviorEvent` / `BehaviorRecorder` contract using the same monotonic-session-clock approach as participant events.

Examples include:

```text
typing_rate
backspace_rate
pause_duration
manual_marker
active_window change
workflow burst
```

These are observable workflow/input events. They must not be promoted into direct measurements of cognition merely because they are synchronized to audio.

## 8. Session/result provenance

`phonic_drive.session.SessionManifest` links independent artifacts without merging their meanings.

A manifest can connect:

```text
session ID
participant pseudonym
source audio
A(t) analysis ID and files
M(t) structural ID and files
P(t) response-event file
K(t) behavior-event file
trial ID
hypothesis IDs
transform/reconstruction IDs
```

Stable hash-derived IDs make repeated automated runs linkable without depending on filenames alone.

## 9. Repeated-session aggregation

`phonic_drive.interpreter.aggregate_motif_response()` summarizes repeated temporal motif/response associations across sessions and stimuli.

It records association rate, match count, lag statistics, and supporting session records.

The output remains an association record. Repetition raises evidence quality but does not by itself establish causality.

## 10. Interpreter evidence ladder

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

## 11. Reconstruction and ablation R

`phonic_drive.reconstruction` contains both provenance contracts and deterministic first-generation transforms.

Implemented operations include:

```text
reverse_time
circular_shift
spectral_ablation
segment_shuffle
RMS matching
envelope-preserving noise control
```

A `ReconstructionManifest` records what is preserved, what is disrupted, operation parameters, source stimulus/motif IDs, and the hypothesis being tested.

The manifest can now directly drive transform execution and WAV rendering.

This creates a traceable path from:

```text
hypothesis
  -> declared transform
  -> rendered stimulus
  -> randomized trial
  -> participant/behavior observations
  -> evidence update
```

## 12. Migration and corpus validation

`phonic_drive.validation` compares overlapping numeric timeline columns between reference and candidate runs and aggregates discrepancy metrics across a corpus.

This supports the migration criterion with data rather than intuition:

```text
v2 timeline
   <->
v3 acoustic_timeline
   -> per-column error metrics
   -> corpus discrepancy report
```

## 13. Current implemented path

```text
Audio
  -> one decode / one STFT
       -> A(t) native measured acoustic state
       -> M(t) structural acoustic state
            -> dense timeline
            -> relationship tensor
            -> motif candidates
            -> recurrence

P(t) participant response events
K(t) optional behavioral/workflow events
T    reproducible randomized trial manifest
R    executable reconstruction / ablation manifest

SessionManifest links artifacts and IDs without collapsing layers.

A + M + P + K + T + R
        -> evidence-oriented Interpreter
        -> repeated-session aggregation
        -> perturbation / reconstruction tests
```

## 14. Model Lab boundary

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

## 15. Next engineering passes

The empirical spine is now scaffolded end to end. The next work should focus on depth and operational usability rather than adding more conceptual layers:

1. add a corpus-runner command that executes v2/v3 paired analyses and writes discrepancy reports automatically;
2. add a participant hotkey/UI trial runner that synchronizes playback, P(t), and optional K(t);
3. add response/motif aggregation keyed through session manifests rather than ad-hoc in-memory session dictionaries;
4. add reconstruction recipes for specific falsification questions such as timing-order disruption, spectral-band removal, and envelope-preserved controls;
5. add schema validation/version migration for durable YAML/JSON artifacts;
6. add visualization of A(t), M(t), P(t), and K(t) on a shared but visually separated time axis;
7. only after representative empirical trials are stable, connect Model Lab synthetic dynamics to motif-space comparison.

## 16. Migration criterion

The default `phonic-drive` command should switch from compatibility orchestration to native `TrackAnalysis` only when:

- native `A(t)` outputs cover the useful v2 measured telemetry;
- regression tests demonstrate acceptable numerical equivalence where equivalence is intended;
- `M(t)` schemas are stable enough for trial/interpreter consumers;
- CI passes across supported Python versions;
- a representative audio corpus has been run through both paths without unexplained discrepancies.

Until then, the dual-command arrangement is intentional migration scaffolding rather than accidental duplication.
