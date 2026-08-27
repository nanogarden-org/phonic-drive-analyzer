# Phonic Drive v3 — six-layer operations

This document records the operational sequence added after the empirical v3 spine was established.

The order is intentional: each layer produces durable inputs for the next one.

```text
1 corpus validation
      ↓
2 synchronized user trial capture
      ↓
3 manifest-driven repeated-session aggregation
      ↓
4 reusable reconstruction recipes
      ↓
5 schema validation / explicit migration
      ↓
6 aligned A/M/P/K visualization
```

## 1. Corpus runner

Run retained v2 and native v3 on the same source corpus:

```powershell
phonic-drive-corpus "D:\Music\Phonic Drive" --recursive --output "runs\corpus-001"
```

Outputs are separated into:

```text
v2/
v3/
comparison/
corpus_run.json
```

Each successfully paired track receives a numeric timeline discrepancy report. The corpus report aggregates mean absolute error and worst observed mean error by overlapping feature column.

Purpose: determine whether native v3 can replace compatibility orchestration using representative data rather than assumptions.

## 2. Synchronized trial runner

Capture timestamp-first participant observations during stimulus playback:

```powershell
phonic-drive-trial "stimuli\original.wav" `
  --participant P001 `
  --trial-id T001 `
  --stimulus-id S001 `
  --output "sessions\T001\response_events.json"
```

Default keys:

```text
1 piloerection
2 perceived movement
3 pressure / tension
4 release
5 emotional peak
6 spatial change
7 other
q end trial
```

FFplay is used when available because FFmpeg is already a Phonic Drive dependency. `--no-playback` permits marker-only capture.

The runner records observations on a monotonic session clock. It does not interpret them.

## 3. Manifest-driven aggregation

Aggregate whole trees of session manifests instead of hand-constructing session dictionaries:

```powershell
phonic-drive-ops aggregate "sessions" `
  --response-type piloerection `
  --max-lag 5 `
  --participant P001 `
  --output "reports\p001-piloerection.json"
```

For every discovered `session_manifest.json`, the loader resolves linked participant-event and motif files and then applies the existing repeated-session motif/response association analysis.

## 4. Reconstruction recipes

Inspect reusable recipes:

```powershell
phonic-drive-ops recipes
```

Initial recipes:

```text
time_reverse
timing_scramble
band_ablation
envelope_control
phase_shift_control
```

Recipes declare both what they intend to preserve and what they intentionally disrupt. A recipe becomes a `ReconstructionManifest`, after which the existing manifest renderer performs the deterministic signal operations.

Examples of experimental questions:

```text
Does the response survive when global timing order is scrambled?
Does it survive removal of a selected frequency band?
Does it survive when only an approximate amplitude envelope remains?
```

These are falsification tools, not effect generators.

## 5. Schema validation and migration

Validate any known JSON artifact:

```powershell
phonic-drive-ops validate "sessions\T001\response_events.json"
```

Migrate only through an explicitly supported migration path:

```powershell
phonic-drive-ops migrate "old-events.json" `
  phonic-drive-response-events-v3alpha2 `
  --output "events-v3alpha2.json"
```

Unknown schemas, missing required fields, and unsupported migrations fail explicitly. Phonic Drive does not silently reinterpret older records.

## 6. Shared A/M/P/K timeline

Create one horizontally aligned view while keeping semantic streams in distinct lanes:

```powershell
phonic-drive-ops visualize `
  --acoustic "run\acoustic_timeline.csv" `
  --structural "run\structural_timeline.csv" `
  --motifs "run\motifs.json" `
  --responses "session\response_events.json" `
  --behavior "session\behavior_events.json" `
  --output "session\shared_timeline.png"
```

Panels remain separate:

```text
A(t) measured acoustic state
M(t) descriptive acoustic structure
P(t) participant response observations
K(t) observable workflow / behavior events
```

Alignment means shared time coordinates. It does not mean semantic equivalence.

## Complete operational loop

```text
source corpus
   ↓
corpus runner ─────────────→ migration discrepancy evidence
   ↓
native TrackAnalysis
   ├── A(t)
   └── M(t)
   ↓
trial manifest / reconstruction recipe
   ↓
rendered stimulus
   ↓
synchronized trial runner
   ├── P(t)
   └── optional K(t)
   ↓
session manifest
   ↓
manifest-tree aggregation
   ↓
evidence ladder
   ↓
shared timeline / reports
   ↓
new hypothesis or falsification step
```

Model Lab remains outside this empirical loop. Synthetic dynamics may be projected into motif space for comparison later, but similarity to empirical `M(t)` is not by itself an explanation of participant physiology.
