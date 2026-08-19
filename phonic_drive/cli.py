"""Compatibility CLI for the incremental Phonic Drive v3 migration.

The v2 module remains the orchestration shell for this migration stage.  Before
calling its ``main`` function, this adapter replaces extracted signal-analysis
primitives with their package implementations.  This provides three benefits:

1. the public ``phonic-drive`` command begins exercising the v3 package now;
2. current v2 output formats and command-line behavior remain stable; and
3. migration can proceed function-by-function with direct equivalence tests.

The direct legacy invocation ``python phonic_drive_analysis_v2.py`` remains
available as an untouched reference implementation during the transition.
"""

from __future__ import annotations

import phonic_drive_analysis_v2 as legacy

from .analysis.audio import frame_signal, load_audio, pad_short, stft_frames
from .analysis.features import (
    rms_frames,
    spectral_bandwidth,
    spectral_centroid,
    spectral_flux,
    spectral_rolloff,
    stereo_features,
    zcr_frames,
)
from .analysis.transitions import (
    align_length,
    build_motion,
    detect_transitions,
    moving_average,
    robust_z,
    scale_01,
)


def install_v3_primitives() -> None:
    """Route extracted v2 operations through their v3 package equivalents."""
    replacements = {
        "load_audio": load_audio,
        "pad_short": pad_short,
        "frame_signal": frame_signal,
        "stft_frames": stft_frames,
        "rms_frames": rms_frames,
        "zcr_frames": zcr_frames,
        "spectral_centroid": spectral_centroid,
        "spectral_bandwidth": spectral_bandwidth,
        "spectral_rolloff": spectral_rolloff,
        "spectral_flux": spectral_flux,
        "stereo_features": stereo_features,
        "robust_z": robust_z,
        "scale_01": scale_01,
        "moving_average": moving_average,
        "align_length": align_length,
        "build_motion": build_motion,
        "detect_transitions": detect_transitions,
    }
    for name, implementation in replacements.items():
        setattr(legacy, name, implementation)


def parser():
    """Expose the existing parser for API compatibility."""
    return legacy.parser()


def main(argv=None):
    """Run the compatibility CLI with v3 primitives installed."""
    install_v3_primitives()
    return legacy.main(argv)
