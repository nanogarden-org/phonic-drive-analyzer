# Phonic Drive Vault Specification

## Purpose

The Vault preserves source identity, repeated listening sessions, acoustic observations, subjective reports, derived correlations, transformations, and cross-session links without overwriting historical states.

The Vault is session-centered rather than song-centered. Repeated exposure to the same source creates a new session.

## Core entities

- `artifact` — a managed source object such as an audio file
- `session` — one bounded listening/analysis encounter
- `acoustic_observation` — measured output derived from an artifact in a session
- `experience_report` — user-authored phenomenological observations for a session
- `correlation_report` — derived associations between independent records
- `transformation` — a record of how one or more inputs produced one or more outputs
- `derived_analysis` — cross-session or higher-order analysis that never overwrites its sources

## Suggested directory layout

```text
PhonicDrive-Vault/
├── vault.yaml
├── index/
│   ├── artifacts.yaml
│   ├── sessions.yaml
│   ├── tags.yaml
│   └── relationships.yaml
├── artifacts/
│   └── <artifact-id>/
│       ├── artifact.yaml
│       └── source.ref
└── sessions/
    └── YYYY/
        └── MM/
            └── <session-id>/
                ├── session.yaml
                ├── acoustic/
                │   ├── observation.yaml
                │   ├── timeline.csv
                │   └── plots/
                ├── experience/
                │   └── report.yaml
                ├── correlation/
                │   └── correlation.yaml
                ├── prompts/
                │   ├── analyze-session.md
                │   └── ai-packet.yaml
                └── derived/
```

## Identity

Artifact identity must not depend on filesystem path.

Recommended fields:

```yaml
identity:
  id: pd-artifact-...
  type: audio-artifact

content:
  sha256: ...
  filename: track.flac
  original_path: D:/Music/track.flac
```

The content hash answers whether the source bytes are the same. The managed ID identifies the Vault object. Paths describe locations and may change.

## Session identity

A session is unique even when the same listener uses the same artifact repeatedly.

```yaml
identity:
  id: pd-session-...
  type: listening-session

relations:
  artifact: pd-artifact-...
```

Repeated sessions preserve time, conditions, and prior observations instead of replacing them.

## Tags versus relationships

Tags classify a node:

```yaml
tags:
  - piloerection
  - spatial-expansion
  - headphones
```

Relationships encode graph structure:

```yaml
relations:
  session: pd-session-...
  derived_from:
    - pd-acoustic-...
    - pd-experience-...
  supersedes: null
```

Do not use tags as substitutes for provenance edges.

## Provenance header

Every major YAML record should contain:

```yaml
schema:
  name: phonic-drive-...
  version: "1.0"

identity:
  id: ...
  type: ...

provenance:
  created_at: ...
  created_by: ...
  software:
    name: phonic-drive
    version: ...

relations: {}
tags: []

epistemic_status:
  layer: ...
  measurement_claim: false
  causation_claim: false
```

Fields may be specialized by record type, but the common envelope should remain stable.

## Transformation records

Every nontrivial derived artifact may optionally record its transformation:

```yaml
transformation:
  id: pd-transform-...
  operation: acoustic-analysis
  inputs:
    - pd-artifact-...
  outputs:
    - pd-acoustic-...
  implementation:
    engine: phonic-drive
    version: 0.3.0
  parameters: {}
  reversible: false
  recovery:
    original_preserved: true
    recomputable: true
```

A transformation can be non-invertible while its lineage remains regressable.

## Historical rule

No accepted observation is destroyed merely because a newer interpretation exists. New interpretations, corrections, and cross-session analyses become new nodes linked to the records they depend on.
