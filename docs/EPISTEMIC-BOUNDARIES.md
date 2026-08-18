# Epistemic Boundaries

Phonic Drive is designed to compare different classes of evidence without silently collapsing them into one another.

## Evidence streams

### A(t) — measured acoustic state

Machine-derived measurements from the audio signal, including energy, spectral features, stereo width, onset candidates, and multi-feature transition activity.

### P(t) — reported phenomenological state

Listener-authored reports such as piloerection, tingling, pressure, perceived motion, spatial expansion or contraction, affect, imagery, and freeform description.

### K(t) — behavioral telemetry

Optional future workflow or interaction measurements such as keypresses, typing rate, pauses, manual markers, or other observable behavior.

### B(t) — optional biosensor telemetry

A future extension for independently measured physiological data when users voluntarily provide compatible sensor data. Biosensor values remain a separate evidence stream.

## Required distinctions

Phonic Drive must preserve the following distinctions in data models, UI labels, exports, and documentation:

```text
acoustic observation != subjective report
subjective report != physiological measurement
correlation != causation
projection != source state
interpretation != observation
```

## Allowed conclusion classes

Downstream interpretation should classify statements as one of:

- `observation` — directly represented in a source record
- `association` — a relationship observed between records, such as temporal proximity
- `hypothesis` — a proposed explanation requiring additional evidence
- `unsupported` — not justified by the available records

## Acoustic event naming

Detected peaks in multi-feature acoustic motion are **acoustic transition candidates**. They are not automatically cognitive, emotional, neurological, or physiological transitions.

## Experience event naming

Experience events record what a listener reports. A report of piloerection, perceived motion, spatial expansion, tingling, or another sensation is evidence that the listener reported the experience at or near that time. It is not by itself evidence of a specific biological mechanism.

## Correlation rules

A correlation record may state that two independently recorded events occurred within a defined temporal window. It may describe the measured acoustic context and the reported experience. It must not promote temporal proximity to causation without additional evidence.

## UI rule against priming

In the listening-session workflow, the listener should complete or substantially capture the subjective report before the application reveals machine-selected acoustic transition candidates. This reduces suggestion and preserves the independence of the two streams.

## Instrument-survives-hypothesis rule

The acoustic analyzer, experience recorder, vault, and correlation machinery should remain useful even if the originating hypothesis about embodied acoustic effects is revised or rejected.
