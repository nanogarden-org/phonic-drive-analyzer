import numpy as np

from phonic_drive.motifs import detect_motif_candidates, motif_similarity_matrix, recurring_pairs


def _repeated_band_pattern():
    times = np.linspace(0.0, 12.0, 241)
    values = np.zeros((4, len(times)), dtype=np.float64)
    values[0] = 0.35
    values[1] = 0.25
    values[2] = 0.20
    values[3] = 0.20

    # Two deliberately similar structural events centered near 3 s and 9 s.
    for center in (3.0, 9.0):
        pulse = np.exp(-0.5 * ((times - center) / 0.18) ** 2)
        values[0] += 0.22 * pulse
        values[1] -= 0.10 * pulse
        values[2] += 0.05 * pulse
        values[3] -= 0.03 * pulse

    values = np.maximum(values, 1e-6)
    values /= np.sum(values, axis=0, keepdims=True)
    return values, times


def test_detects_repeated_candidate_shapes():
    values, times = _repeated_band_pattern()
    motifs = detect_motif_candidates(
        values,
        times,
        half_window_s=0.6,
        min_separation_s=2.0,
        max_candidates=6,
    )
    assert len(motifs) >= 2
    assert all(m["label"] == "acoustic motif candidate" for m in motifs)
    assert all(len(m["signature"]) == values.shape[0] * 2 for m in motifs)


def test_similarity_and_recurrence_are_structural_only():
    values, times = _repeated_band_pattern()
    motifs = detect_motif_candidates(
        values,
        times,
        half_window_s=0.6,
        min_separation_s=2.0,
        max_candidates=6,
    )
    sim = motif_similarity_matrix(motifs)
    assert sim.shape == (len(motifs), len(motifs))
    np.testing.assert_allclose(np.diag(sim), 1.0)

    pairs = recurring_pairs(motifs, threshold=0.90)
    assert any(pair["similarity"] >= 0.90 for pair in pairs)
