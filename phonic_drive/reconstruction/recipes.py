"""Named, reusable reconstruction recipes for controlled Phonic Drive trials."""
from __future__ import annotations

from dataclasses import dataclass

from .protocol import ReconstructionManifest, TransformStep


@dataclass(frozen=True, slots=True)
class Recipe:
    name: str
    description: str
    preserves: tuple[str, ...]
    disrupts: tuple[str, ...]
    operation: str
    default_parameters: dict


RECIPES = {
    "time_reverse": Recipe(
        "time_reverse",
        "Reverse the complete stimulus in time while preserving sample values and duration.",
        ("sample_values", "duration", "global_spectrum"),
        ("temporal_order", "attack_decay_direction", "causal_sequence"),
        "reverse_time",
        {},
    ),
    "timing_scramble": Recipe(
        "timing_scramble",
        "Shuffle fixed-duration segments with a reproducible seed.",
        ("local_spectral_content", "local_timbre", "duration"),
        ("global_temporal_order", "long_range_trajectory"),
        "segment_shuffle",
        {"segment_s": 0.5, "seed": 0},
    ),
    "band_ablation": Recipe(
        "band_ablation",
        "Suppress a selected spectral band while retaining the rest of the signal.",
        ("timing", "unselected_frequency_content", "duration"),
        ("selected_frequency_band",),
        "spectral_ablation",
        {"low_hz": 40.0, "high_hz": 80.0, "gain": 0.0},
    ),
    "envelope_control": Recipe(
        "envelope_control",
        "Generate deterministic noise following an approximate source amplitude envelope.",
        ("approximate_amplitude_envelope", "global_rms", "duration"),
        ("melody", "harmony", "fine_spectral_structure", "timbre"),
        "envelope_noise_control",
        {"envelope_samples": 1024, "seed": 0},
    ),
    "phase_shift_control": Recipe(
        "phase_shift_control",
        "Circularly shift the waveform while preserving all sample values.",
        ("sample_values", "global_spectrum", "duration"),
        ("absolute_event_timing", "alignment_to_external_markers"),
        "circular_shift",
        {"shift_s": 1.0},
    ),
}


def list_recipes() -> list[dict]:
    return [
        {
            "name": r.name,
            "description": r.description,
            "preserves": list(r.preserves),
            "disrupts": list(r.disrupts),
            "operation": r.operation,
            "default_parameters": dict(r.default_parameters),
        }
        for r in RECIPES.values()
    ]


def build_recipe_manifest(
    recipe_name: str,
    *,
    reconstruction_id: str,
    source_stimulus_id: str,
    source_motif_ids: list[str],
    hypothesis_id: str | None,
    parameters: dict | None = None,
) -> ReconstructionManifest:
    try:
        recipe = RECIPES[recipe_name]
    except KeyError as exc:
        raise ValueError(f"Unknown reconstruction recipe: {recipe_name}") from exc
    merged = dict(recipe.default_parameters)
    merged.update(parameters or {})
    step = TransformStep(
        operation=recipe.operation,
        parameters=merged,
        preserves=list(recipe.preserves),
        disrupts=list(recipe.disrupts),
    )
    return ReconstructionManifest(
        reconstruction_id=reconstruction_id,
        source_stimulus_id=source_stimulus_id,
        source_motif_ids=list(source_motif_ids),
        hypothesis_id=hypothesis_id,
        steps=[step],
    )
