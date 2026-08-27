# Phonic Drive Godot Visualizer Architecture

Status: alpha v0.1

## Decision

Phonic Drive will keep Python as the authoritative analysis, experiment, provenance, and reconstruction layer while using Godot as the primary advanced visualization and interactive desktop presentation engine.

```text
Python domain engine
    A(t) / M(t) / P(t) / K(t)
             |
             v
renderer-facing visual-state adapter
             |
             v
Godot
    mesh / ribbons / particles / camera / HUD / overlays
```

The renderer is not allowed to silently redefine scientific quantities. Rendering mappings are presentation choices and must remain documented separately from the underlying analysis artifacts.

## Why this boundary

Python already owns:

- audio decoding and analysis
- acoustic state A(t)
- structural state M(t)
- trial capture P(t)
- behavior K(t)
- reconstruction and perturbation
- evidence calculations
- schemas and provenance

Godot is better suited to:

- interactive 3D mesh deformation
- GPU shaders
- particles and fields
- camera control
- responsive desktop UI
- timeline overlays
- spatial interaction
- future installation / VR modes

This prevents the visualization engine from becoming a second analysis implementation.

## Visual-state contract

Initial schema: `phonic-drive-visual-state-v1`.

Current fields:

```text
time_s
energy
brightness
stereo_width
transition_strength
compression
coherence
motif_activity
recurrence
response_active
response_type
```

The first transport is an atomically replaced JSON file. This is intentionally simple for contract validation. Once stable, the transport may become localhost TCP/WebSocket/UDP without changing the schema semantics.

## First mesh mappings

Current shader mappings are exploratory presentation choices:

```text
energy              -> displacement amplitude
brightness          -> wave density / visual mix
stereo_width        -> secondary surface displacement
transition_strength -> torsion + emission
compression         -> center constriction
coherence           -> secondary spatial frequency
motif_activity      -> motif-wave contribution
recurrence          -> denser repeated geometry
```

These mappings must never be described as direct biological meanings.

## UX/UI integration

Godot should become the visible desktop shell rather than an optional visualization launched after analysis.

Target screens:

- Study
- Analyze
- Trial
- Compare
- Reconstruct
- Outputs
- Settings

The central viewport can switch among:

- Mesh
- Ribbon
- Field
- Recurrence
- Shared A/M/P/K timeline

### Trial-safe mode

During prospective response capture:

- no motif labels
- no transition timestamps
- no prediction overlays
- no historical-note content
- visual behavior should be either neutralized or use only predeclared non-priming mappings

After the trial is frozen, overlays may be enabled for comparison.

## Data flow phases

### Phase 1 — contract test

Python writes `visual_state.json`; Godot polls and applies shader uniforms.

### Phase 2 — playback timeline publisher

Python reads existing v3 artifacts and publishes normalized frames synchronized to playback.

### Phase 3 — localhost stream

Replace file polling with a local stream while preserving `phonic-drive-visual-state-v1` semantics.

### Phase 4 — application shell

Godot owns study selection, track selection, playback controls, response pad, artifact status, and output navigation. Python services are invoked through a local application bridge rather than CLI text.

### Phase 5 — reconstruction / experiment mode

Godot presents randomized conditions and records responses while Python creates reconstruction manifests and transformed stimuli.

## Repository boundary

```text
phonic_drive/
    visual_bridge.py       Python presentation contract

godot/
    phonic_drive_visualizer/
        project.godot
        main.tscn
        scripts/
        shaders/
```

The Godot project is part of Phonic Drive but remains cleanly separated from Python scientific artifacts and tests.

## Near-term definition of done

The first usable Godot milestone is complete when a user can:

1. open the Godot Phonic Drive shell without a CLI workflow;
2. select a v3 analyzed track;
3. play it;
4. see the mesh evolve from Python-derived A(t)/M(t) state;
5. switch to a trial-safe response screen;
6. click response buttons during playback;
7. have the response JSON persist automatically;
8. reopen the completed trial in Compare mode with overlays enabled.
