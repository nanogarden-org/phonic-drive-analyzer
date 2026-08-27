# Phonic Drive Godot Visualizer

Status: alpha scaffold

This project is the optional Godot presentation surface for Phonic Drive. Godot is intentionally separated from the scientific core so Phonic Drive can run on lower-capability systems without a GPU-heavy renderer, while stronger systems can add interactive 3D visualization and richer UX.

## Architectural role

Current path:

```text
Python reference core
A(t) + M(t) + optional P(t)/K(t)
        │
        ▼
phonic-drive-visual-state-v1
        │
        ▼
Godot renderer
mesh + UX + overlays
```

Planned mature path:

```text
                         Rust Core
                      /      |      \
                     /       |       \
                Python     Godot      CLI
               research      UX      automation
```

Godot must consume stable renderer-facing contracts rather than Python- or Rust-specific internal objects. That allows the backend to move from Python to Rust later without forcing a visualizer rewrite.

See [`../../docs/CORE_MIGRATION_PATH.md`](../../docs/CORE_MIGRATION_PATH.md).

## Godot is optional

Godot is an augmentation, not a dependency.

Basic Phonic Drive functionality must remain available without Godot:

- acoustic analysis
- structural analysis
- trial capture and persistence
- study/corpus validation
- reconstruction tooling
- provenance records
- static Python plots / fallback views

The capability ladder is therefore:

```text
Level 1 — Python core
analysis + trials + artifacts

Level 2 — Python desktop
study management + lightweight UX

Level 3 — Python/Rust + Godot
interactive 3D visualization + richer UX

Level 4 — Rust-native live path
high-rate streaming / installations / advanced rendering
```

Higher levels augment lower ones rather than replacing them.

## Renderer boundary

The Godot renderer is presentation only. Mesh deformation, camera motion, glow, persistence, particles, or color mappings are visualization choices, not scientific claims.

Current visual-state fields include:

- `time_s`
- `energy`
- `brightness`
- `stereo_width`
- `transition_strength`
- `compression`
- `coherence`
- `motif_activity`
- `recurrence`
- `response_active`
- `response_type`

Values other than time/response fields are normalized renderer-facing presentation values, approximately `[0, 1]`.

Godot should never infer scientific meaning from these fields that is not present in the contract.

## Current renderer

The first scene is deliberately small:

- 96 × 96 subdivided plane mesh
- wireframe shader
- Python-state polling
- deformation driven by energy / width / compression / transition / motif / recurrence fields
- HUD connection/status display
- Godot Compatibility renderer target

This is a visual-contract test, not the final Phonic Drive UX.

## Transport evolution

The initial bridge is intentionally simple:

```text
Python
  ↓
atomic visual_state.json replacement
  ↓
Godot polling
```

Once `phonic-drive-visual-state-v1` stabilizes, transport may evolve without changing state meaning:

```text
Python or Rust publisher
        ↓
localhost stream
        ↓
Godot
```

A later high-performance path may use a Rust-native Godot GDExtension if latency, deployment, or installation modes justify it.

That direct Rust/Godot integration is an optimization, not an architectural requirement.

## Prospective-trial safety

During prospective response capture the visualizer must support a restricted trial mode that does **not** disclose information capable of priming the participant.

Hide during prospective capture:

- motif identities / timestamps
- transition prediction markers
- historical annotation content
- response-association predictions
- retrospective comparison overlays

After the response record is frozen, Compare mode may expose those layers.

## UX role

The long-term Godot application may own:

- study/track selection
- playback transport
- large response buttons
- mesh/ribbon/particle visualization
- A/M/P/K overlays
- event inspection
- reconstruction/trial handoff
- camera presets
- spatial / installation modes
- later VR interaction

Scientific computation remains below the UX boundary.

## Python → Rust compatibility requirement

The Godot project must not assume that Python is permanently present in the live rendering path.

Renderer code should depend on:

```text
visual contract + transport
```

not:

```text
Python classes + Python filesystem layout
```

When the Rust core begins replacing mature Python numerical components, the same visual-state contract should remain valid.

## Near-term next steps

1. Add a Python timeline publisher that converts existing v3 A(t)/M(t) artifacts into successive visual-state frames.
2. Synchronize frame publication with playback position.
3. Add playback controls and connection/status UX.
4. Add a trial-safe response-pad view.
5. Add post-trial response markers and A/M/P/K overlays.
6. Add camera presets and ribbon/field modes.
7. Add recurrence-history geometry.
8. Replace filesystem polling with localhost streaming after the visual contract stabilizes.
9. Add renderer capability detection so Godot absence never blocks the Python path.
10. Keep the visual contract suitable for future Rust publishers.

## Hardware strategy

The project currently targets Godot 4.x using the Compatibility renderer to keep the initial GPU requirements modest.

The repository does not assume that every development or end-user machine can run the Godot renderer well. Older machines can continue using the Python core and lightweight UX while contributors with stronger hardware test and refine Godot-specific features.

## Related architecture

- [`../../docs/GODOT_VISUALIZER_ARCHITECTURE.md`](../../docs/GODOT_VISUALIZER_ARCHITECTURE.md)
- [`../../docs/CORE_MIGRATION_PATH.md`](../../docs/CORE_MIGRATION_PATH.md)
- [`../../docs/DESKTOP_UI_UX_SPEC.md`](../../docs/DESKTOP_UI_UX_SPEC.md)
- [`../../docs/DESKTOP_COMPONENT_MAP.md`](../../docs/DESKTOP_COMPONENT_MAP.md)
