from pathlib import Path

import numpy as np

from phonic_drive.exports import acoustic_summary, structural_summary, write_v3_bundle
from phonic_drive.interpreter import observation, temporal_proximity
from phonic_drive.track import TrackAnalysis
from phonic_drive.trials import ResponseEvent, event_windows, nearest_motifs


def _fake_track() -> TrackAnalysis:
    times = np.array([0.0, 1.0, 2.0])
    band = np.array([[0.2, 0.4, 0.3], [0.8, 0.6, 0.7]])
    zeros = np.zeros(3)
    relationships = np.stack([np.eye(2), np.eye(2), np.eye(2)])
    motif = {"id": "M1", "peak_time_s": 1.0, "signature": [1.0, 0.0]}
    return TrackAnalysis(
        source=Path("example.wav"), sr=1000, source_channels=1, target_sr=1000,
        n_fft=16, hop=8, mono=zeros, left=zeros, right=zeros,
        freqs=np.array([0.0, 100.0]), times=times, spectrum=np.zeros((2, 3)),
        rms=zeros, rms_db=zeros, zcr=zeros, centroid=zeros, bandwidth=zeros,
        rolloff=zeros, flux=zeros, stereo_correlation=zeros, stereo_width=zeros,
        state_x=zeros, state_y=zeros, state_z=zeros, transition_speed=zeros,
        transition_acceleration=zeros, transition_candidates=[],
        band_edges_hz=np.array([20.0, 200.0, 500.0]), band_trajectories=band,
        band_velocity=np.zeros_like(band), band_acceleration=np.zeros_like(band),
        relationships=relationships, motif_candidates=[motif], recurring_motif_pairs=[],
    )


def test_acoustic_summary_preserves_measured_layer():
    summary = acoustic_summary(_fake_track())
    assert summary["schema"] == "phonic-drive-acoustic-v3alpha1"
    assert "centroid_hz" in summary["statistics"]
    assert summary["state_space_axes"]["x"].startswith("spectral brightness")


def test_structural_summary_preserves_motif_layer():
    summary = structural_summary(_fake_track())
    assert summary["schema"] == "phonic-drive-structural-v3alpha2"
    assert summary["motif_candidates"][0]["id"] == "M1"
    assert len(summary["mean_cross_band_relationship"]) == 2


def test_v3_bundle_contains_acoustic_and_structural_artifacts(tmp_path: Path):
    outputs = write_v3_bundle(_fake_track(), tmp_path)
    expected = {
        "acoustic_json", "acoustic_timeline_csv", "transitions_json",
        "structural_json", "structural_timeline_csv", "motifs_json", "relationships_npz",
    }
    assert expected.issubset(outputs)
    for key in expected:
        assert Path(outputs[key]).exists()


def test_response_windows_and_nearest_motif_are_descriptive():
    event = ResponseEvent(1.5, "piloerection", intensity=0.7)
    windows = event_windows(event, pre_s=(1.0, 2.0), post_s=3.0)
    assert windows[0]["start_s"] == 0.5
    matches = nearest_motifs(event, [{"id": "M1", "peak_time_s": 1.0}])
    assert matches[0]["lag_s"] == 0.5

    obs = observation({"session_time_s": 1.5, "response_type": "piloerection"})
    prox = temporal_proximity({"session_time_s": 1.5}, matches[0])
    assert obs.level == 0
    assert prox.level == 1
    assert "caus" not in prox.statement.lower()
