import numpy as np

from phonic_drive.analysis import (
    band_energy_trajectories,
    logarithmic_band_edges,
    rolling_relationships,
    temporal_derivatives,
)


def test_logarithmic_band_edges_are_monotonic():
    edges = logarithmic_band_edges(20.0, 20000.0, 10)
    assert len(edges) == 11
    assert np.all(np.diff(edges) > 0)
    assert edges[0] == 20.0
    assert np.isclose(edges[-1], 20000.0)


def test_band_energy_normalizes_each_nonempty_frame():
    freqs = np.array([20.0, 40.0, 80.0, 160.0])
    spectrum = np.array(
        [
            [1.0, 2.0],
            [1.0, 1.0],
            [2.0, 1.0],
            [1.0, 3.0],
        ]
    )
    edges = np.array([20.0, 80.0, 200.0])
    bands = band_energy_trajectories(spectrum, freqs, edges)
    assert bands.shape == (2, 2)
    assert np.allclose(np.sum(bands, axis=0), 1.0)


def test_temporal_derivatives_keep_shape():
    values = np.array([[0.0, 1.0, 3.0], [2.0, 2.0, 1.0]])
    d1, d2 = temporal_derivatives(values, 0.5)
    assert d1.shape == values.shape
    assert d2.shape == values.shape


def test_rolling_relationships_are_symmetric():
    values = np.array(
        [
            [0.0, 1.0, 2.0, 3.0],
            [0.0, 2.0, 4.0, 6.0],
            [3.0, 2.0, 1.0, 0.0],
        ]
    )
    rel = rolling_relationships(values, window_frames=4)
    assert rel.shape == (4, 3, 3)
    assert np.allclose(rel[-1], rel[-1].T)
    assert np.allclose(np.diag(rel[-1]), 1.0)
    assert rel[-1, 0, 1] > 0.99
    assert rel[-1, 0, 2] < -0.99
