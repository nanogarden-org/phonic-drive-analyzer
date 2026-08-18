"""Identity helpers for provenance-bearing Phonic Drive records.

Managed IDs identify Vault objects. Content hashes identify source bytes. File
paths are location metadata and must not be used as artifact identity.
"""

from __future__ import annotations

import hashlib
import uuid
from pathlib import Path


def new_managed_id(kind: str) -> str:
    """Return a stable-format managed ID for a new Vault object.

    The UUID is intentionally independent of source path or human-readable name.
    """
    normalized = kind.strip().lower().replace("_", "-")
    if not normalized:
        raise ValueError("kind must not be empty")
    return f"pd-{normalized}-{uuid.uuid4()}"


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    """Return the SHA-256 digest of a file's bytes."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def artifact_identity(path: Path) -> dict[str, str]:
    """Create identity metadata without conflating content and location."""
    resolved = path.expanduser().resolve()
    if not resolved.is_file():
        raise FileNotFoundError(resolved)
    return {
        "artifact_id": new_managed_id("artifact"),
        "content_sha256": sha256_file(resolved),
        "filename": resolved.name,
        "observed_path": str(resolved),
    }
