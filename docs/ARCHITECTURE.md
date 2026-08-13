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

## 5. Subjective annotations

Optional `song_lens` files may contain:

- temporal anchors
- frequency layers
- inflection points
- reflection patterns
- resonance anchors
- cognitive-field effects

These are stored verbatim as `subjective_annotation` in the per-track JSON summary.

Declared resonance-anchor frequencies receive a narrow spectral-neighborhood check. The check means only that measurable spectral energy is or is not strong near the declared frequency. It does not establish perceptual causation, biological resonance, or cross-domain physical equivalence.

## 6. Batch layer

A batch produces:

- per-track summaries
- per-track frame timelines
- batch summary CSV
- batch summary JSON
- comparison plot for 2+ tracks
- run log containing failures and parameters

This permits comparisons across tracks and artists without losing the time-resolved data.

## 7. Planned third stream: workflow telemetry

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
