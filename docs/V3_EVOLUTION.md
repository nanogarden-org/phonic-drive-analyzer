# Phonic Drive v3 — Architecture Evolution

## Status

This document defines the v3 migration path from a monolithic acoustic analyzer into a layered research system. It is an architectural contract, not a claim that the biological mechanisms discussed in Model Lab are established.

## Why v3 exists

Phonic Drive v2 successfully established two important foundations:

1. time-resolved measured acoustic state; and
2. strict separation between measured acoustic features and user-authored subjective annotations.

The next research question is no longer only **which acoustic features are present?** It is also:

> What recurring temporal and cross-band interaction structures appear, and do those structures correspond reproducibly with reported or behavioral events?

That requires an intermediate representation between raw measurement and interpretation.

## Core streams

```text
A(t) = measured acoustic state
M(t) = measured/descriptive motif state
P(t) = reported perceptual / phenomenological state
K(t) = behavioral telemetry
T    = trial conditions and provenance
I    = interpretation/evidence assembly
```

The critical rule is that these streams remain distinguishable in storage and code.

### A(t): acoustic measurement

Contains directly computed audio features and their derivatives. Examples:

- RMS / RMS dB
- spectral centroid
- bandwidth
- rolloff
- zero-crossing rate
- spectral flux
- stereo correlation / width
- band-energy trajectories
- first and second temporal derivatives
- cross-band relationship measurements

A(t) answers: **what was measured in the audio?**

### M(t): motif / interaction structure

M(t) describes recurring temporal shapes derived from A(t). It is deliberately descriptive.

Candidate motif vocabulary includes:

- convergence
- divergence
- pulse
- sweep
- compression
- expansion
- oscillation
- branch
- collapse
- release
- recurrence

M(t) must not silently become a biological label. A motif such as `low_band_rise__mid_suppression__high_burst` describes acoustic topology; it does not mean "dopamine event", "entrainment event", or any other causal interpretation.

### P(t): subjective response

Contains participant-authored reports and event markers. Examples:

- piloerection marker
- perceived motion
- pressure/tension
- release
- emotional peak
- spatial change
- free-text note

P(t) answers: **what did the participant report?**

### K(t): behavioral state

Future/optional synchronized telemetry such as:

- keypress events
- typing cadence
- pause duration
- burst length
- active application/window
- manual event markers

K(t) answers: **what observable behavior changed?**

### T: trial conditions

Trial metadata preserves experimental context:

- stimulus identity
- transform / ablation identity
- randomization order
- session identifier
- analyzer version
- schema version
- timing synchronization
- participant-provided context

T answers: **under what conditions were A, M, P, and K collected?**

## Processing pipeline

```text
Audio
  |
  v
A(t): measured acoustic features
  |
  +--> band-energy field
  +--> derivatives
  +--> cross-band relationships
  |
  v
M(t): motif detection / recurrence / similarity
  |
  +--------------------+
  |                    |
  v                    v
P(t)                 K(t)
reported state       behavior
  |                    |
  +----------+---------+
             |
             v
I: evidence assembly
             |
             v
candidate relationships
             |
             v
reconstruction / ablation / trial
```

## Repository boundaries

```text
phonic_drive/
├── analysis/          # A(t): physical/acoustic measurement
├── motifs/            # M(t): structural descriptions derived from A(t)
├── interpreter/       # evidence assembly; never invents measurements
├── trials/            # trial/session/event/provenance contracts
├── reconstruction/    # controlled stimulus transforms and ablations
└── model_lab/         # optional dynamical-system simulations
```

### Why these boundaries exist

`analysis/` must remain usable without subjective reports.

`motifs/` may depend on measured analysis but must not depend on participant interpretation.

`interpreter/` may join A/M/P/K/T, but should emit evidence statements with provenance and strength rather than causal declarations.

`trials/` owns synchronization and experimental conditions so user reports are not retroactively rewritten by analysis.

`reconstruction/` creates counterfactual stimuli for falsification.

`model_lab/` is intentionally isolated because simulation analogy is not measurement. Boid-like agents, fields, reaction-diffusion systems, excitation, saturation, hysteresis, or other mechanisms can be explored there without being represented as established biological mechanisms.

## Migration strategy

### Phase 0 — preserve v2

Keep `phonic_drive_analysis_v2.py` operational while v3 package boundaries are introduced. No working capability should be lost merely to improve organization.

### Phase 1 — contracts and pure functions

Introduce typed, dependency-light data contracts and pure motif/relationship helpers. Add tests before moving CLI orchestration.

### Phase 2 — extract acoustic modules

Move feature extraction from the monolith into `phonic_drive.analysis` while retaining compatibility imports/wrappers in the v2 script.

### Phase 3 — motif engine

Add:

- log-spaced or configurable band-energy trajectories;
- temporal derivatives;
- rolling cross-band relationship matrices;
- motif segmentation;
- motif similarity and recurrence.

### Phase 4 — user event trials

Add low-friction timestamp markers and a trial schema that records events before interpretation.

For each event at time `t_e`, preserve multi-scale context windows such as:

```text
250 ms
500 ms
1 s
2 s
5 s
10 s
```

and lagged comparisons such as:

```text
M(t - tau) <-> P(t)
A(t - tau) <-> K(t)
```

### Phase 5 — reconstruction and falsification

Generate controlled variants that retain or destroy selected structural properties while matching obvious confounds where possible.

Examples:

- original segment
- lyric-removed / instrumental where legally and technically available
- altered timbre
- preserved temporal envelope
- preserved band trajectory
- reversed trajectory
- timing-scrambled control
- RMS-matched control
- synthetic motif reconstruction

### Phase 6 — Model Lab

Use synthetic dynamical systems to ask whether simple local rules can generate topology similar to measured M(t).

This layer can explore abstractions such as:

```text
B_i(t) = moving energy/interaction agent
C(x,t) = stateful substrate / field
```

with local rules for attraction, repulsion, alignment, scattering, diffusion, excitation, decay, saturation, refractory periods, or hysteresis.

Model Lab output is compared to motif geometry. It is not substituted for physiological evidence.

## Evidence ladder

Interpreter output should distinguish at least these levels:

0. **Observation** — a user or instrument event occurred.
1. **Temporal proximity** — an acoustic event occurred within a defined window.
2. **Within-session association** — a motif repeatedly co-occurs with a response in one session.
3. **Cross-stimulus recurrence** — similar motif geometry recurs across different tracks/stimuli with similar responses.
4. **Perturbation evidence** — altering a structural property changes the response distribution.
5. **Reconstruction evidence** — a synthetic or transformed stimulus preserving the candidate structure reproduces the association more than controls.

None of these automatically establishes a biological mechanism. Mechanistic claims require independent evidence appropriate to that domain.

## Design invariant

The central v3 rule is:

> Preserve provenance and relationships while keeping measurement, report, interpretation, simulation, and causal claim as different object types.

That invariant should guide every new feature and schema change.