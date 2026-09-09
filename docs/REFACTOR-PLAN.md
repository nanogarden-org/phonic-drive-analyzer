# Phonic Drive v0.3 Refactor Plan

## Objective

Refactor the working v0.2 analyzer into a public-facing, session-centered research instrument without changing the current acoustic analysis behavior during the first migration stage.

The redesign separates five responsibilities:

1. **Acoustic Engine** — measured audio features and state-space transitions: `A(t)`.
2. **Experience Lens** — independently authored phenomenological observations: `P(t)`.
3. **Correlation Engine** — derived temporal associations between source records.
4. **Vault** — provenance, identity, lineage, repeated-session history, and links.
5. **Interpreter Packet** — provider-neutral YAML + prompt export for optional AI analysis.

## Core invariants

- Measurement, experience, and interpretation remain distinct records.
- Acoustic events are not labeled as cognitive or physiological events.
- A projection or summary never replaces its richer source record.
- Transformations may be lossy; lineage must remain regressable.
- Human observations are captured before machine interpretation is revealed when using the listening-session workflow.
- AI interpretation is optional and provider-neutral.
- The instrument must remain useful even if the originating hypothesis is wrong.

## Migration stages

### Stage 0 — Freeze baseline

- Keep `main` as the known-working v0.2 baseline.
- Preserve representative outputs from several tracks for regression comparison.
- Do not alter the existing numerical algorithms during structural extraction.

### Stage 1 — Package decomposition

Create `src/phonic_drive/` and move functions by responsibility while preserving behavior.

Target modules:

```text
src/phonic_drive/
├── cli.py
├── app.py
├── core/
│   ├── audio.py
│   ├── spectral.py
│   ├── stereo.py
│   ├── state_space.py
│   ├── transitions.py
│   └── statistics.py
├── experience/
├── correlation/
├── schemas/
├── vault/
├── exporters/
└── ui/
```

Keep `phonic_drive_analysis_v2.py` temporarily as a compatibility wrapper until parity tests pass.

### Stage 2 — Typed schemas and YAML output

Introduce explicit schemas for:

- artifact identity and provenance
- acoustic observation
- experience report
- correlation report
- session manifest
- transformation record

Continue JSON output for compatibility while adding YAML as the public interchange format.

### Stage 3 — Artifact and session identity

Replace path-derived source identity with:

- stable managed IDs for artifacts and sessions
- SHA-256 content hashes for source identity
- storage paths as mutable location metadata rather than identity

### Stage 4 — Session Vault

Implement a session-centered vault where repeated exposure to the same source creates new session records rather than mutating earlier observations.

### Stage 5 — Experience capture

Add timestamped user events for piloerection, perceived motion, spatial expansion/contraction, tingling, pressure, temperature, affect, imagery, and freeform notes.

### Stage 6 — Correlation layer

Create derived records that align independently recorded acoustic and experiential events. Correlation outputs must never modify either source record.

### Stage 7 — Provider-neutral AI packet

Export a self-contained folder containing session, acoustic, experience, and correlation YAML plus a methodology-governed analysis prompt.

### Stage 8 — Desktop UX

Build a PySide6 application around the research-session workflow:

```text
select source
→ create session
→ capture conditions
→ listen / mark sensations
→ finish subjective report
→ run acoustic analysis
→ reveal comparison
→ review associations
→ export packet
```

### Stage 9 — Repeated-session analysis

Add vault queries and derived analyses across sessions, tracks, tags, event classes, and acoustic patterns.

## Compatibility test

Before algorithm changes are allowed, representative inputs should satisfy:

```text
v0.2 output ≈ refactored output
```

within documented floating-point tolerances for unchanged algorithms.

## Public-release evidence gates

A public release should provide three independently reviewable layers:

1. acoustic analyzer and reproducible outputs
2. independent experience capture with explicit epistemic status
3. correlation explorer that reports temporal association without automatic causal inference

## Current migration status

As of the first v0.3 extraction tranche:

- `main` remains unchanged as the v0.2 reference implementation.
- `src/phonic_drive/core/` now contains extracted numerical, framing/STFT, spectral, stereo, and state-space/transition primitives.
- The legacy functions remain in `phonic_drive_analysis_v2.py`; no production call sites have been switched yet.
- Migration regression tests compare the extracted functions directly against the legacy implementations on deterministic synthetic inputs.
- Vault identity tests verify that content identity follows source bytes rather than filename/path and that managed IDs remain independent of content hashes.
- The existing GitHub Actions matrix is being used as the first automated parity gate.

### Current hold point

Do not rewire the CLI or change the acoustic algorithms until the regression suite passes on the supported Python matrix. After that gate, the next structural tranche is:

1. extract remaining analysis helpers (onsets, tempo, statistics, resonance checks, export helpers)
2. introduce a package-level analysis service while retaining legacy compatibility
3. add typed record models and YAML serialization alongside existing JSON
4. wire artifact/session identity into newly generated v0.3 records
