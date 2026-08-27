from phonic_drive.reconstruction import ablation_manifest
from phonic_drive.trials import StimulusCondition, build_manifest, randomized_order, stable_seed


def test_trial_randomization_is_reproducible():
    conditions = [
        StimulusCondition("A", "a.wav", role="original"),
        StimulusCondition("B", "b.wav", role="ablation"),
        StimulusCondition("X", "x.wav", role="control"),
    ]
    seed = stable_seed("trial-001", "hyp-001")
    assert randomized_order(conditions, seed) == randomized_order(conditions, seed)

    manifest = build_manifest(
        trial_id="trial-001",
        hypothesis_id="hyp-001",
        participant_id="participant-pseudonym",
        conditions=conditions,
    )
    assert sorted(manifest.order) == ["A", "B", "X"]
    assert manifest.seed == seed


def test_ablation_manifest_records_preserved_and_disrupted_structure():
    manifest = ablation_manifest(
        reconstruction_id="R-001",
        source_stimulus_id="S-001",
        source_motif_ids=["M-001"],
        hypothesis_id="H-001",
        preserve=["band_energy_trajectory"],
        disrupt=["timing_order"],
        parameters={"shuffle_window_s": 0.5},
    )
    assert manifest.steps[0].preserves == ["band_energy_trajectory"]
    assert manifest.steps[0].disrupts == ["timing_order"]
    assert manifest.hypothesis_id == "H-001"
