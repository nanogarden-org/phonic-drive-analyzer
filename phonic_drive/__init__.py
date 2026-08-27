"""Phonic Drive v3 package boundary.

The v2 CLI remains operational during migration. New code is organized around
explicit measurement, motif, interpretation, trial, reconstruction, and model
lab layers.
"""

from .contracts import AcousticFrame, MotifEvent, ResponseEvent, TrialRecord

__all__ = [
    "AcousticFrame",
    "MotifEvent",
    "ResponseEvent",
    "TrialRecord",
]

__version__ = "0.3.0-dev"
