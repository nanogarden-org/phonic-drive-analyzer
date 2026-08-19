from __future__ import annotations

import numpy as np

EPS = 1e-12


def logarithmic_band_edges(
    min_hz: float,
    max_hz: float,
    bands: int,
) -> np.ndarray:
    """Return logarithmically spaced frequency-band edges.

    This is a representation choice, not a perceptual or biological claim.
    """
    if min_hz <= 0:
        raise ValueError("min_hz must be > 0 for logarithmic bands")
    if max_hz <= min_hz:
        raise ValueError("max_hz must be greater than min_hz")
    if bands < 1:
        raise ValueError("bands must be >= 1")
    return np.geomspace(float(min_hz), float(max_hz), int(bands) + 1)


def band_energy_trajectories(
    magnitude_spectrum: np.ndarray,
    freqs_hz: np.ndarray,
    band_edges_hz: np.ndarray,
    *,
    normalize_per_frame: bool = True,
) -> np.ndarray:
    """Aggregate an STFT magnitude/power-like matrix into frequency bands.

    Parameters
    ----------
    magnitude_spectrum:
        Shape ``(frequency_bins, frames)``.
    freqs_hz:
        Frequency value for each spectrum row.
    band_edges_hz:
        Monotonic edges; N+1 edges produce N bands.

    Returns
    -------
    np.ndarray
        Shape ``(bands, frames)``.
    """
    spectrum = np.asarray(magnitude_spectrum, dtype=np.float64)
    freqs = np.asarray(freqs_hz, dtype=np.float64)
    edges = np.asarray(band_edges_hz, dtype=np.float64)

    if spectrum.ndim != 2:
        raise ValueError("magnitude_spectrum must be 2D [frequency, frame]")
    if spectrum.shape[0] != len(freqs):
        raise ValueError("freqs_hz length must equal spectrum frequency bins")
    if len(edges) < 2 or np.any(np.diff(edges) <= 0):
        raise ValueError("band_edges_hz must contain increasing edges")

    out = np.zeros((len(edges) - 1, spectrum.shape[1]), dtype=np.float64)
    power = np.square(np.maximum(spectrum, 0.0))

    for i, (lo, hi) in enumerate(zip(edges[:-1], edges[1:])):
        # Include the final upper edge to avoid dropping the highest bin.
        mask = (freqs >= lo) & (freqs < hi)
        if i == len(edges) - 2:
            mask = (freqs >= lo) & (freqs <= hi)
        if np.any(mask):
            out[i] = np.sum(power[mask], axis=0)

    if normalize_per_frame:
        out = out / (np.sum(out, axis=0, keepdims=True) + EPS)
    return out


def temporal_derivatives(values: np.ndarray, dt_s: float) -> tuple[np.ndarray, np.ndarray]:
    """Return first and second finite-difference derivatives along time."""
    if dt_s <= 0:
        raise ValueError("dt_s must be > 0")
    x = np.asarray(values, dtype=np.float64)
    if x.ndim != 2:
        raise ValueError("values must be 2D [feature, frame]")
    d1 = np.diff(x, axis=1, prepend=x[:, :1]) / dt_s
    d2 = np.diff(d1, axis=1, prepend=d1[:, :1]) / dt_s
    return d1, d2


def rolling_relationships(
    band_values: np.ndarray,
    window_frames: int,
) -> np.ndarray:
    """Compute rolling Pearson cross-band relationship matrices.

    Returns ``(frames, bands, bands)``. These are descriptive local
    relationships and should not be interpreted as causal coupling.
    """
    x = np.asarray(band_values, dtype=np.float64)
    if x.ndim != 2:
        raise ValueError("band_values must be 2D [band, frame]")
    if window_frames < 2:
        raise ValueError("window_frames must be >= 2")

    bands, frames = x.shape
    result = np.zeros((frames, bands, bands), dtype=np.float64)
    for t in range(frames):
        start = max(0, t - window_frames + 1)
        window = x[:, start : t + 1]
        if window.shape[1] < 2:
            result[t] = np.eye(bands)
            continue
        centered = window - np.mean(window, axis=1, keepdims=True)
        denom = np.sqrt(np.sum(centered * centered, axis=1, keepdims=True))
        normed = centered / (denom + EPS)
        corr = normed @ normed.T
        corr = np.clip(corr, -1.0, 1.0)
        np.fill_diagonal(corr, 1.0)
        result[t] = corr
    return result
