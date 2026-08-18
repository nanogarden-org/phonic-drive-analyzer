"""Pure acoustic-analysis primitives for Phonic Drive.

This package is being extracted from the v0.2 monolith without changing the
numerical behavior.  During the migration, regression tests compare these
functions directly against ``phonic_drive_analysis_v2.py``.
"""

from .numerics import EPS, align_length, moving_average, robust_z, scale_01
from .spectral import (
    mean_spectrum_peaks,
    spectral_bandwidth,
    spectral_centroid,
    spectral_flux,
    spectral_rolloff,
)
from .state_space import TRANSITION_LABELS, build_motion, detect_transitions
from .stereo import stereo_features

__all__ = [
    "EPS",
    "TRANSITION_LABELS",
    "align_length",
    "build_motion",
    "detect_transitions",
    "mean_spectrum_peaks",
    "moving_average",
    "robust_z",
    "scale_01",
    "spectral_bandwidth",
    "spectral_centroid",
    "spectral_flux",
    "spectral_rolloff",
    "stereo_features",
]
