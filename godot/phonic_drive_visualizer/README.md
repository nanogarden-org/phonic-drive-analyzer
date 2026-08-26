# Phonic Drive Godot Visualizer

Status: alpha scaffold

This project is the first Godot presentation surface for Phonic Drive. Python remains the authoritative analysis/trial/reconstruction engine; Godot consumes a stable renderer-facing state contract.

## Boundary

```text
Python Phonic Drive
A(t) + M(t) + optional P(t)/K(t)
        |
        v
phonic-drive-visual-state-v1
        |
        v
Godot renderer
mesh + UI + overlays
```

The Godot renderer is presentation only. Mesh deformation choices are visual mappings, not scientific claims.

## Current visual-state fields

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

Values other than time/response fields are expected to be normalized presentation values in approximately `[0, 1]`.

## Current renderer

The first scene is deliberately small:

- 96 x 96 subdivided plane mesh
- wireframe material
- Python-state polling
- mesh deformation for energy/width/compression/transition/motif/recurrence
- HUD connection/status display

This is a visual contract test, not the final Phonic Drive UX.

## Next steps

1. Add a Python timeline publisher that converts an existing v3 A(t)/M(t) bundle into successive visual-state frames.
2. Replace filesystem polling with a localhost stream after the state contract stabilizes.
3. Add transport synchronization and playback position.
4. Add trial-safe mode that hides motif/transition overlays during prospective capture.
5. Add response markers and A/M/P/K overlays after a trial is complete.
6. Add camera presets, ribbon/field modes, and recurrence-history geometry.
7. Integrate this Godot surface into the normal Phonic Drive desktop shell.

## Godot version

Target Godot 4.x. The project currently uses the Compatibility renderer to keep the first workstation requirements modest.
