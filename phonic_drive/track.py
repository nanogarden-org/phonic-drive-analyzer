"""Single-pass track analysis for Phonic Drive v3.

A TrackAnalysis owns the expensive decoded/STFT representation and derives
measured acoustic state A(t) plus structural state M(t) from that shared basis.
Participant responses and interpretation are deliberately not part of this
object.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from .analysis.audio import load_audio, stft_frames
from .analysis.bands import band_energy_trajectories, logarithmic_band_edges, rolling_relationships, temporal_derivatives
from .analysis.features import rms_frames, spectral_bandwidth, spectral_centroid, spectral_flux, spectral_rolloff, stereo_features, zcr_frames
from .analysis.transitions import align_length, build_motion, detect_transitions
from .motifs import detect_motif_candidates, recurring_pairs

EPS = 1e-12


@dataclass(slots=True)
class TrackAnalysis:
    source: Path
    sr: int
    source_channels: int
    target_sr: int
    n_fft: int
    hop: int
    mono: np.ndarray
    left: np.ndarray
    right: np.ndarray
    freqs: np.ndarray
    times: np.ndarray
    spectrum: np.ndarray
    rms: np.ndarray
    rms_db: np.ndarray
    zcr: np.ndarray
    centroid: np.ndarray
    bandwidth: np.ndarray
    rolloff: np.ndarray
    flux: np.ndarray
    stereo_correlation: np.ndarray
    stereo_width: np.ndarray
    state_x: np.ndarray
    state_y: np.ndarray
    state_z: np.ndarray
    transition_speed: np.ndarray
    transition_acceleration: np.ndarray
    transition_candidates: list[dict]
    band_edges_hz: np.ndarray
    band_trajectories: np.ndarray
    band_velocity: np.ndarray
    band_acceleration: np.ndarray
    relationships: np.ndarray
    motif_candidates: list[dict]
    recurring_motif_pairs: list[dict]

    @property
    def dt(self) -> float:
        return float(np.median(np.diff(self.times))) if len(self.times) > 1 else self.hop / self.sr

    @property
    def duration_s(self) -> float:
        return float(len(self.mono) / self.sr)


def analyze_track(
    source: Path,
    *,
    target_sr: int = 22050,
    n_fft: int = 2048,
    hop: int = 512,
    bands: int = 10,
    min_hz: float = 20.0,
    relationship_window_s: float = 2.0,
    motif_half_window_s: float = 1.5,
    max_transitions: int = 12,
) -> TrackAnalysis:
    """Decode once and derive both A(t) and M(t) from one STFT."""
    source = Path(source)
    mono, left, right, sr, source_channels = load_audio(source, target_sr)
    freqs, times, spectrum = stft_frames(mono, sr, n_fft, hop)
    if len(times) < 2:
        raise ValueError("Audio is too short for track analysis")

    rms = rms_frames(mono, n_fft, hop)
    zcr = zcr_frames(mono, n_fft, hop)
    centroid = spectral_centroid(spectrum, freqs)
    bandwidth = spectral_bandwidth(spectrum, freqs, centroid)
    rolloff = spectral_rolloff(spectrum, freqs)
    flux_raw = spectral_flux(spectrum)
    corr, width = stereo_features(left, right, n_fft, hop)

    n = min(len(times), len(rms), len(zcr), len(centroid), len(bandwidth), len(rolloff), len(corr), len(width))
    times, rms, zcr, centroid, bandwidth, rolloff, corr, width = [
        np.asarray(x[:n]) for x in [times, rms, zcr, centroid, bandwidth, rolloff, corr, width]
    ]
    spectrum = spectrum[:, :n]
    rms_db = 20 * np.log10(np.maximum(rms, EPS))
    flux = align_length(np.concatenate([[0.0], flux_raw]), n)
    dt = float(np.median(np.diff(times)))

    sx, sy, sz, speed, acceleration, component_change = build_motion(
        rms_db, centroid, bandwidth, rolloff, zcr, flux, width, dt
    )
    transitions = detect_transitions(times, speed, component_change, max_transitions)

    max_hz = min(float(sr) / 2.0, float(freqs[-1]))
    lower = max(float(min_hz), float(freqs[1]) if len(freqs) > 1 else float(min_hz))
    edges = logarithmic_band_edges(lower, max_hz, bands)
    trajectories = band_energy_trajectories(spectrum, freqs, edges, normalize_per_frame=True)
    band_velocity, band_acceleration = temporal_derivatives(trajectories, dt)
    rel_frames = max(2, int(round(relationship_window_s / dt)))
    relationships = rolling_relationships(trajectories, rel_frames)
    motifs = detect_motif_candidates(trajectories, times, half_window_s=motif_half_window_s)
    recurrence = recurring_pairs(motifs)

    return TrackAnalysis(
        source=source, sr=sr, source_channels=source_channels, target_sr=target_sr,
        n_fft=n_fft, hop=hop, mono=mono, left=left, right=right, freqs=freqs,
        times=times, spectrum=spectrum, rms=rms, rms_db=rms_db, zcr=zcr,
        centroid=centroid, bandwidth=bandwidth, rolloff=rolloff, flux=flux,
        stereo_correlation=corr, stereo_width=width, state_x=sx, state_y=sy,
        state_z=sz, transition_speed=speed, transition_acceleration=acceleration,
        transition_candidates=transitions, band_edges_hz=edges,
        band_trajectories=trajectories, band_velocity=band_velocity,
        band_acceleration=band_acceleration, relationships=relationships,
        motif_candidates=motifs, recurring_motif_pairs=recurrence,
    )
