"""Compatibility CLI for the incremental Phonic Drive v3 migration.

The v2 module remains the orchestration shell for this migration stage. Before
calling its ``main`` function, this adapter replaces extracted signal-analysis
primitives with their package implementations.

An opt-in ``--structural`` flag adds the first v3-native artifact,
``structural_analysis.json``, beside each successful track output. The existing
v2 summary/timeline schemas remain untouched.
"""

from __future__ import annotations

import sys
from pathlib import Path

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
from .structural import write_structural_analysis


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
    """Expose the legacy parser; ``--structural`` is handled by this adapter."""
    return legacy.parser()


def _split_adapter_flags(argv: list[str]) -> tuple[list[str], bool]:
    structural = "--structural" in argv
    cleaned = [token for token in argv if token != "--structural"]
    return cleaned, structural


def _run_structural_exports(cleaned_argv: list[str]) -> None:
    args = legacy.parser().parse_args(cleaned_argv)
    files = legacy.resolve_inputs(args.inputs, args.recursive)
    output_root = Path(args.output).expanduser()

    for audio_path in files:
        track_dir = output_root / f"{legacy.slugify(audio_path.stem)}_{legacy.source_id(audio_path)}"
        # Only add structural output for tracks that completed the v2 pass.
        if not (track_dir / "summary.json").exists():
            continue
        try:
            result = write_structural_analysis(
                audio_path,
                track_dir / "structural_analysis.json",
                target_sr=args.target_sr,
                n_fft=args.n_fft,
                hop=args.hop,
            )
            print(
                f"  structural -> {track_dir / 'structural_analysis.json'} "
                f"({len(result['motif_candidates'])} motif candidates)"
            )
        except Exception as exc:
            print(f"[WARN] structural analysis failed for {audio_path}: {exc}", file=sys.stderr)


def main(argv=None):
    """Run v2-compatible analysis with extracted v3 primitives installed."""
    raw_argv = list(sys.argv[1:] if argv is None else argv)
    cleaned_argv, structural = _split_adapter_flags(raw_argv)
    install_v3_primitives()
    status = legacy.main(cleaned_argv)
    if structural and status == 0:
        _run_structural_exports(cleaned_argv)
    return status
