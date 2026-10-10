# Perceptual morphogenesis annotations

The perceptual morphogenesis layer records what a listener reports experiencing while listening: forms, organization, and transformations across time. It extends the existing `song_lens` idea with a versioned, time-aligned event format for particle fields, aggregation, topology, growth, transformation, color/texture, and persistence.

This is a first-person annotation stream. It remains separate from measured acoustic features and derived motif candidates. An optional `acoustic_transition_ref` can link an annotation to a separately produced acoustic event, but the link does not assert causation or a universal mapping between sound and imagery.

## Record structure

- **Stimulus and session provenance:** identify the recording and each listening session. Repeated sessions can be compared without overwriting earlier reports.
- **Time range:** use approximate source-audio seconds as `[start, end]`.
- **Report:** capture the overall perceived form, what changed, and what persisted.
- **Dimensions:** add any applicable observations. Each dimension supports free text and optional labels; there is no requirement that every listener use every category.
- **Confidence:** optional value from 0 to 1 for confidence in recall/reporting, not a probability that the experience is objectively true.

## Files

- Schema: [`schemas/perceptual-morphogenesis-v1.schema.json`](../schemas/perceptual-morphogenesis-v1.schema.json)
- Example: [`examples/annotations/perceptual_morphogenesis.example.yaml`](../examples/annotations/perceptual_morphogenesis.example.yaml)

The example is a template and does not claim to reproduce any particular listener's experience. The schema defines an annotation contract; it does not yet add a UI or runtime annotation capture workflow.
