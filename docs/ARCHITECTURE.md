# Architecture

## 1. Design principle

Phonic Drive keeps measurement, structural description, participant report, behavior, interpretation, and simulation as distinct epistemic objects.

The v3 conceptual streams are:

```text
A(t) = measured acoustic state
M(t) = descriptive motif / interaction state derived from A(t)
P(t) = reported perceptual / phenomenological state
K(t) = workflow / behavioral state
T    = trial conditions and provenance
I    = evidence assembly across the streams
```

The current v2 analyzer already implements `A(t)` and can attach user-authored `P(t)` annotations. v3 introduces package boundaries and the first primitives for `M(t)` while preserving the v2 CLI during migration.

The separation matters: correlation can be tested without redefining subjective experience as acoustic measurement, and simulation can be explored without presenting analogy as mechanism.

See [`V3_EVOLUTION.md`](V3_EVOLUTION.md) for the migration rationale and [`USER_TRIAL_PROTOCOL.md`](USER_TRIAL_PROTOCOL.md) for the trial loop.

## 2. Measured acoustic state — A(t)

The v2 per-frame feature vector includes:

```text
energy                 RMS / RMS dB
brightness             spectral centroid
spectral spread         spectral bandwidth
high-frequency reach    85% spectral rolloff
transient texture       zero-crossing rate
spectral change         positive normalized spectral flux
spatial field           stereo correlation + mid/side width
```

Features are robustly normalized before the transition metric is formed.

v3 extends A(t) with explicitly measured relational structure:

```text
band-energy trajectories
first temporal derivatives
second temporal derivatives
rolling cross-band relationship matrices
```

These additional measurements are implemented initially in `phonic_drive.analysis.bands`.

## 3. Transition field

Let the normalized v2 acoustic feature vector be:

```text
A(t) = [E, C, B, R, Z, F, W]
```

where the elements correspond roughly to energy, centroid, bandwidth, rolloff, zero-crossing rate, flux, and stereo width.

The analyzer estimates a magnitude of motion through this feature space:

```text
transition_speed(t) ≈ || dA/dt ||
```

and then:

```text
transition_acceleration(t) ≈ d(transition_speed)/dt
```

Candidate transition events are local peaks in this multi-feature motion signal. Each event is tagged with the feature dimension contributing the largest local change.

This remains an **acoustic transition candidate**, not a cognitive transition.

## 4. Motif / interaction state — M(t)

v3 adds an intermediate structural representation derived from measured acoustics.

A motif describes temporal topology such as:

```text
convergence
-> suppression
-> burst
-> release
```

or other descriptive primitives such as sweep, expansion, compression, oscillation, divergence, recurrence, branch, or collapse.

A motif can retain:

- start/end timestamps
- ordered topology labels
- duration
- transition peaks
- band relationships
- lead/lag values
- recurrence descriptors
- similarity scores
- provenance back to source analysis

M(t) is deliberately descriptive. Biological or cognitive labels do not belong in the motif detector unless they are separately represented as hypotheses or evidence-linked interpretations.

## 5. 3D export trajectory

For visualization, v2 exports three normalized coordinates:

```text
X = spectral brightness
Y = RMS energy
Z = stereo width
```

A track therefore becomes a trajectory rather than a single summary point:

```text
Gamma(t) = [X(t), Y(t), Z(t)]
```

The full `timeline.csv` retains more dimensions than the 3D projection. v3 motif analysis should operate on the richer measured state rather than treating the 3D visualization projection as the complete state space.

## 6. Subjective annotations — P(t)

Optional `song_lens` files may contain:

- temporal anchors
- frequency layers
- inflection points
- reflection patterns
- resonance anchors
- cognitive-field effects

These remain stored separately as participant/user-authored material.

Declared resonance-anchor frequencies receive only a narrow spectral-neighborhood check. That check means measurable spectral energy is or is not strong near the declared frequency. It does not establish perceptual causation, biological resonance, or cross-domain physical equivalence.

v3 trials add timestamp-first response events so observations can be captured with minimal interpretation during playback.

## 7. Behavioral telemetry — K(t)

Planned synchronized behavioral telemetry can include:

```text
timestamp
characters_per_second
words_per_minute
backspace_rate
pause_duration
burst_length
active_window
manual_event_marker
```

This permits lagged comparisons such as:

```text
Delta A(t) -> Delta K(t + tau)
M(t)       -> Delta K(t + tau)
```

## 8. Trial conditions — T

Trial conditions preserve the experimental context rather than reconstructing it afterward.

Examples include:

- session identifier
- stimulus/source identifier
- transformation or ablation identifier
- randomization index
- blinded label
- analyzer version
- schema version
- playback metadata

For user-event analysis, multiple pre/post windows and lag values should be tested explicitly and recorded in the output.

## 9. Interpreter — I

The interpreter joins evidence; it does not manufacture measurements.

Its inputs may include:

```text
A(t): measured acoustic data
M(t): structural motifs
P(t): participant reports
K(t): behavior
T:    trial conditions
```

Outputs should identify evidence level, provenance, negative results, contradictions, tested lag windows, and uncertainty.

A recommended evidence ladder is:

```text
0 observation
1 temporal proximity
2 within-session association
3 cross-stimulus recurrence
4 perturbation evidence
5 reconstruction evidence
```

Mechanistic claims remain outside this ladder unless independently supported by evidence appropriate to the claimed domain.

## 10. Reconstruction / falsification

The reconstruction layer creates counterfactual stimuli by retaining or destroying selected structural properties.

Examples include:

```text
original segment
preserved temporal envelope
preserved band trajectory
reversed trajectory
timing-scrambled control
RMS-matched control
synthetic motif reconstruction
```

This supports questions of the form:

```text
property retained -> does association persist?
property destroyed -> does association weaken/change?
```

## 11. Model Lab

`phonic_drive/model_lab/` is an optional simulation sandbox.

It may explore boid-like agents, energy-transfer agents, fields, reaction-diffusion systems, excitation, decay, saturation, refractory behavior, or hysteresis.

Model Lab is isolated because structural analogy is not empirical identity. A simulation may generate a motif resembling measured audio without thereby demonstrating that photons, chemistry, neurons, or any other biological substrate use the same mechanism.

Model Lab should exchange structural descriptors with the motif engine and preserve the distinction:

```text
measured motif != simulated motif != biological mechanism
```

## 12. Batch layer

A v2 batch produces:

- per-track summaries
- per-track frame timelines
- batch summary CSV
- batch summary JSON
- comparison plot for 2+ tracks
- run log containing failures and parameters

v3 should preserve these outputs while progressively adding band-field telemetry, motif records, trial/session records, and evidence reports.

## 13. Migration invariant

The v3 migration should be incremental:

1. preserve the working v2 CLI;
2. add typed contracts and pure functions;
3. extract measurement code into `phonic_drive.analysis`;
4. add motif detection and recurrence;
5. add timestamp-first user trials;
6. add evidence assembly;
7. add reconstruction / ablation;
8. keep Model Lab optional and epistemically separate.

The central invariant is:

> Preserve provenance and relationships while keeping measurement, report, interpretation, simulation, and causal claim as different object types.
