"""Descriptive temporal motif detection for Phonic Drive v3.

Motifs describe repeated acoustic trajectory shapes.  They are not labels for
physiological, cognitive, emotional, or causal effects.
"""

from .detector import detect_motif_candidates, motif_similarity_matrix, recurring_pairs

__all__ = ["detect_motif_candidates", "motif_similarity_matrix", "recurring_pairs"]
