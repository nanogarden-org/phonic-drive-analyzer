"""Test bootstrap for the v0.3 package migration.

The repository keeps the working v0.2 flat module in place while the new
``src/phonic_drive`` package is extracted.  Add ``src`` to sys.path only for
migration tests so packaging changes can happen after numerical parity is
established.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
