# Architecture

## 1. Design principle

Phonic Drive Analyzer keeps three conceptual streams distinct:

```text
A(t) = measured acoustic state
P(t) = reported perceptual / phenomenological state
K(t) = workflow / keyboard behavior (future layer)
```

The current v2 implements `A(t)` and can attach user-authored `P(t)` annotations. `K(t)` is a roadmap item.

The separation matters: correlation can be tested later without defining the subjective experience as if it were already an acoustic measurement.

Phonic Drive now adds a second objective level inside the acoustic stream:

```text
measured features
      ↓
structural relationships
      ↓
emergent temporal geometry
```

This geometry is derived from measurable relationships among acoustic states. It is not inferred cognition, emotion, or meaning.

## 2. Measured acoustic state

The per-frame feature vector currently includes:

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

## 3. Transition field

Let the normalized acoustic feature vector be:

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

This is intentionally named an **acoustic transition candidate**, not a cognitive transition.

## 4. 3D export trajectory

For visualization, three normalized coordinates are exported:

```text
X = spectral brightness
Y = RMS energy
Z = stereo width
```

A track therefore becomes a trajectory rather than a single summary point:

```text
Gamma(t) = [X(t), Y(t), Z(t)]
```

The full `timeline.csv` retains more dimensions than the 3D projection.

## 5. Layered temporal geometry

### 5.1 Core observation

Tracks can share nearly the same temporal substrate while producing very different higher-order structures.

A common beat or phrase grid therefore does not imply common organization.

The compact invariant is:

```text
Same Ground != Same Growth
```

Phonic Drive defines **layered temporal geometry** as:

> The measurable higher-order structure produced when multiple acoustic layers evolve, recur, couple, diverge, and transform over a shared temporal substrate.

The important object is not only the value of each feature at time `t`, but the relationships among features and between present and prior states.

A useful abstraction is:

```text
Ground + Layers + Relations + Transformations -> Emergent Geometry
```

### 5.2 Ground

The **ground** is the relatively invariant coordinate system on which change occurs. Candidate ground variables include:

```text
tempo / beat lattice
meter
bar boundaries
phrase periodicity
tonal or harmonic reference frame
```

Ground is not assumed to be perfectly static. It is the slowest or most persistent organizing substrate relative to the structures being measured.

### 5.3 Layers

A **layer** is a measurable acoustic process evolving over the ground. Examples include:

```text
rhythmic energy
bass activity
harmonic content
melodic density
transient activity
spectral distribution
stereo / phase field
ambient or sustained energy
```

Layers may share a clock without sharing the same trajectory.

### 5.4 State

At a given time, a richer structural state may be represented as:

```text
X(t) = [E, F, H, P, S, D, R]
```

where, conceptually:

```text
E = energy
F = spectral distribution
H = harmonic state
P = phase structure
S = stereo / spatial state
D = event or layer density
R = recurrence relationships
```

Not every component is currently implemented. This vector defines the target structural model rather than claiming all dimensions are already measured.

### 5.5 Relations

The geometry appears in relationships, including:

```text
synchronization
recurrence
divergence / convergence
phase coupling
amplitude coupling
harmonic ratio relationships
cross-layer lag
self-similarity across bars or phrases
```

A central future measurement is therefore not just `X(t)`, but:

```text
R(X(t), X(t-n))
```

for musically meaningful lags `n`.

This distinguishes exact repetition from transformed recurrence:

```text
A -> A -> A -> A
```

versus:

```text
A -> A' -> A'' -> A'''
```

Both may occupy the same beat and phrase lattice while describing different structural geometries.

### 5.6 Transformations

Candidate measurable transformations include:

```text
repeat
translate in time
expand / contract
phase-shift
mirror or invert
increase / decrease density
diverge / converge spatially
deform while retaining recurrence
bifurcate into distinct states
collapse into a simpler state
```

These names describe signal relationships, not compositional intent unless separately annotated.

### 5.7 Geometry classes

The following classes are provisional descriptive models for comparing tracks:

**Hierarchical / lattice geometry**

```text
small recurring cells remain visible inside progressively larger recurrence intervals
```

**Tessellated / state geometry**

```text
reusable local cells occupy different discrete larger-scale acoustic states
```

**Trajectory / transformational geometry**

```text
a stable temporal substrate persists while the multivariate acoustic state continuously deforms and later revisits related regions of state-space
```

These classes are not genre labels and are not mutually exclusive. A track may transition between them.

### 5.8 Reference observation set

The distinction was clarified by comparing three tracks with an approximately 128 BPM ground but visibly different recurrence and spatial organizations:

```text
Quezacotl          -> hierarchical / lattice-like growth
Right This Second  -> tessellated / state-machine-like growth
Nocturne           -> trajectory / transformational growth
```

The tracks are reference observations, not normative templates. The architectural point is that comparable ground conditions can support different geometric growth patterns.

### 5.9 Implementation direction

A future temporal-geometry analyzer should derive bar- or phrase-synchronous representations and expose at least:

```text
beat/bar/phrase grid
bar-to-bar self-similarity matrix
recurrence score by lag
macro-dynamic envelope
stereo correlation trajectory
cross-feature coupling trajectories
candidate structural boundaries
transformation labels with confidence
```

This layer should remain traceable back to measured acoustic features so that every structural claim can be inspected.

## 6. Subjective annotations

Optional `song_lens` files may contain:

- temporal anchors
- frequency layers
- inflection points
- reflection patterns
- resonance anchors
- cognitive-field effects

These are stored verbatim as `subjective_annotation` in the per-track JSON summary.

Declared resonance-anchor frequencies receive a narrow spectral-neighborhood check. The check means only that measurable spectral energy is or is not strong near the declared frequency. It does not establish perceptual causation, biological resonance, or cross-domain physical equivalence.

## 7. Batch layer

A batch produces:

- per-track summaries
- per-track frame timelines
- batch summary CSV
- batch summary JSON
- comparison plot for 2+ tracks
- run log containing failures and parameters

This permits comparisons across tracks and artists without losing the time-resolved data.

## 8. Planned third stream: workflow telemetry

The strongest next extension is synchronized behavioral telemetry such as:

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

That would permit lagged comparisons such as:

```text
Delta A(t)  ->  Delta K(t + tau)
```

and allow subjective event markers `P(t)` to be compared against both.
