# Phonic Drive Core Migration Path

Status: architecture path v0.1

Phonic Drive is intentionally designed so that implementation languages can change without changing the research contracts, evidence boundaries, or user-facing artifacts.

The planned migration is:

```text
Python reference implementation
        ↓ refine + validate contracts
Rust production core
        ↓
shared stable interfaces
   ┌────┼─────────┐
   ↓    ↓         ↓
Python Godot      CLI
research UX       automation
```

Python is the current reference implementation. Rust is the planned production implementation for mature deterministic numerical components. Godot is an optional presentation/interaction consumer. The CLI remains an automation and debugging adapter.

## 1. Architectural invariant

The core rule is:

> Implementation may change; contracts must remain stable unless they are explicitly versioned.

The following boundaries must survive a Python-to-Rust migration:

```text
Signal ≠ Feature ≠ Inference ≠ Claim ≠ Authorized action
```

For Phonic Drive specifically:

```text
A(t) = measured acoustic state
M(t) = descriptive structural / motif state
P(t) = reported participant state
K(t) = behavioral telemetry
T    = trial conditions + provenance
R    = reconstruction / perturbation record
```

No implementation language may silently collapse those layers.

## 2. Three implementation roles

### Python — reference and research layer

Python remains the fastest-changing layer and is the source of truth while algorithms, schemas, and experimental assumptions are still being refined.

Primary responsibilities:

- research iteration
- study orchestration
- experiment protocol development
- evidence logic
- schema evolution and migration
- corpus tooling
- notebooks / exploratory analysis
- compatibility reference implementations
- Python desktop fallback UI

Python code should remain readable enough to serve as an executable specification for Rust ports.

### Rust — production numerical core

Rust becomes the preferred implementation only after a component's input/output behavior is sufficiently stable and parity tests exist.

Likely Rust targets:

- audio sample normalization
- framing / STFT primitives
- spectral features
- band-energy trajectories
- temporal derivatives
- transition detection
- cross-band relationship matrices
- motif candidate primitives
- recurrence search
- reconstruction / ablation DSP
- high-volume deterministic transforms

Rust is selected for predictable performance, explicit memory ownership, concurrency, portability, and durable compiled deployment—not because Python is considered invalid.

### Godot — optional UX / visualization layer

Godot consumes stable presentation contracts. It must not own scientific analysis logic.

Godot responsibilities may include:

- desktop interaction
- playback controls
- trial response buttons
- 2D/3D visualization
- mesh / ribbon / particle views
- event overlays
- camera and spatial interaction
- later VR / installation modes

Godot must remain optional. Absence of Godot must not prevent analysis, trial persistence, corpus validation, or artifact generation.

## 3. End-state topology

Target long-term topology:

```text
                         ┌─────────────────────┐
                         │   Stable contracts  │
                         │ schemas / IDs / time│
                         └──────────┬──────────┘
                                    │
                         ┌──────────▼──────────┐
                         │      Rust Core      │
                         │ deterministic DSP + │
                         │ structural analysis │
                         └──────┬─────┬─────┬──┘
                                │     │     │
                      ┌─────────┘     │     └─────────┐
                      ▼               ▼               ▼
               Python research     Godot UX        CLI adapters
               orchestration       visualization   automation
                      │               │               │
                      └───────────────┼───────────────┘
                                      ▼
                              shared artifacts
                         A(t) / M(t) / P(t) / K(t)
```

Python may continue to call Rust directly even after Rust becomes the default numerical backend.

## 4. Python ↔ Rust bridge

Preferred first bridge: PyO3 + maturin.

Desired Python-facing shape:

```python
from phonic_drive_core import analyze_track
```

The Python application should not need to know whether `analyze_track` is pure Python or backed by compiled Rust.

During migration, the Python package may expose explicit backend selection for validation:

```python
analyze_track(source, backend="python")
analyze_track(source, backend="rust")
```

After parity is established, `backend="auto"` may prefer Rust while keeping Python as the reference / fallback path where practical.

## 5. Godot ↔ core bridge

Godot must consume renderer-facing state rather than internal Python or Rust objects.

Current first contract:

```text
phonic-drive-visual-state-v1
```

Near-term:

```text
Python analysis → visual-state JSON → Godot
```

Later:

```text
Rust/Python state publisher → localhost stream → Godot
```

Possible mature path:

```text
Rust core → native Godot extension / GDExtension
```

That direct path is optional and should only be introduced when live visualization latency or deployment simplicity justifies it.

## 6. Contract surfaces to freeze before Rust migration

The following should be versioned and tested before substantial Rust porting begins:

### Artifact schemas

- acoustic summary
- acoustic timeline
- transitions
- structural summary
- structural timeline
- motifs
- response events
- behavioral events
- trial manifest
- session manifest
- reconstruction manifest
- visual-state contract

### Identity and provenance

- source identity rules
- content hashes where applicable
- analysis IDs
- structural IDs
- session IDs
- trial IDs
- reconstruction IDs
- schema versions
- code/backend version metadata

### Timing semantics

- sample rate
- frame origin
- frame time convention
- hop size semantics
- event clock semantics
- playback synchronization assumptions
- lag sign conventions

### Numerical semantics

- windowing method
- FFT magnitude / power convention
- normalization rules
- percentile scaling
- band-edge construction
- transition scoring
- motif signature construction
- recurrence similarity metric

## 7. Migration rule: no rewrite day

Phonic Drive should migrate component-by-component.

Example sequence:

```text
Stage 0
Python decode
Python STFT
Python features
Python motifs

Stage 1
Rust framing/STFT
Python features
Python motifs

Stage 2
Rust framing/STFT/features/bands
Python motif/evidence layers

Stage 3
Rust deterministic numerical core
Python research + orchestration
Godot presentation
```

Each replacement must pass parity gates before becoming the default.

## 8. Parity gates

A Python component should not be retired merely because the Rust version runs faster.

Minimum gate:

1. same accepted inputs;
2. same documented failure behavior where practical;
3. same artifact schema;
4. numerically equivalent outputs within explicit tolerances;
5. representative corpus comparison;
6. no unexplained discrepancy clusters;
7. deterministic behavior where the Python contract is deterministic;
8. provenance records backend/version identity;
9. CI covers both implementations during migration;
10. rollback to the Python reference remains possible until the Rust path is established.

## 9. Differential testing

The existing v2/v3 corpus-validation idea becomes the model for Python/Rust migration.

For the same source:

```text
source audio
   ├── Python reference
   └── Rust candidate
          ↓
field-by-field comparison
          ↓
parity report
```

Parity reports should distinguish:

- exact matches
- expected floating-point differences
- acceptable tolerance differences
- schema differences
- unexplained numerical differences
- behavioral/failure-mode differences

Negative results are retained rather than hidden.

## 10. Backend identity in provenance

Once multiple implementations exist, generated records should identify the backend.

Example:

```json
{
  "engine": {
    "backend": "rust",
    "core_version": "0.1.0",
    "contract_version": "phonic-drive-acoustic-v3alpha1"
  }
}
```

The backend identifier describes implementation provenance, not a different scientific meaning.

## 11. Optional capability ladder

Phonic Drive should continue to function at several hardware levels:

```text
Level 1 — Python core
analysis + trials + artifacts + static plots

Level 2 — Python desktop
study management + buttons + compare UI

Level 3 — Python/Rust + Godot
interactive 3D visualization + richer UX

Level 4 — Rust-native live path
high-rate streaming / installations / advanced rendering
```

A higher level augments the lower one. It does not invalidate it.

## 12. What must never become mandatory

Unless the project explicitly changes policy, none of these should become requirements for basic research use:

- Godot
- discrete GPU
- cloud services
- Rust compiler on end-user machines
- live network connection
- proprietary visualization software

Packaged Rust binaries may eventually improve the default experience, but source-level Rust tooling should remain a developer concern rather than an end-user prerequisite.

## 13. Immediate engineering consequences

Current development should therefore:

1. keep Python APIs clean and domain-oriented;
2. separate CLI parsing from domain logic;
3. keep Godot behind renderer-facing contracts;
4. version schemas before changing them;
5. add backend/version provenance fields when Rust work begins;
6. maintain corpus parity tests;
7. avoid Python-only object shapes in persistent artifacts;
8. avoid Godot-specific assumptions in scientific state;
9. define numerical tolerances explicitly before each Rust port;
10. preserve the Python implementation as a readable reference until the Rust equivalent is trusted.

## 14. Rust migration readiness checklist

A component is ready to port when:

- its purpose is stable;
- its inputs/outputs are documented;
- its artifact/schema contract exists;
- tests cover normal and edge cases;
- representative real-world corpus behavior is known;
- unresolved algorithmic questions are small enough not to cause repeated redesign;
- performance or deployment benefit justifies the port.

If those conditions are not met, keep refining it in Python.

## 15. Guiding principle

Phonic Drive is not "a Python program that will later be rewritten in Rust."

It is a contract-defined system whose current reference implementation is Python and whose mature deterministic core is expected to move progressively into Rust.

That distinction is what allows the research layer, visualization layer, automation layer, and compiled core to evolve at different speeds without forcing an architectural reset.