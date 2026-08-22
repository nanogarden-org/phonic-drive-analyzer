"""Central user-facing path configuration for Phonic Drive.

Normal users should not need to know repository-relative artifact locations.
Configuration is persisted under the user's local application-data directory,
with optional environment-variable overrides for automation.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path

APP_NAME = "PhonicDrive"


def _default_config_dir() -> Path:
    if os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / APP_NAME


def _default_data_dir() -> Path:
    override = os.environ.get("PHONIC_DRIVE_HOME")
    if override:
        return Path(override).expanduser()
    documents = Path.home() / "Documents"
    return documents / "PhonicDrive"


CONFIG_DIR = _default_config_dir()
CONFIG_FILE = CONFIG_DIR / "config.json"


@dataclass(slots=True)
class UserConfig:
    data_root: str
    corpus_root: str | None = None
    output_root: str | None = None
    participant_pseudonym: str = "P001"

    @property
    def data_path(self) -> Path:
        return Path(self.data_root).expanduser()

    @property
    def corpus_path(self) -> Path | None:
        return Path(self.corpus_root).expanduser() if self.corpus_root else None

    @property
    def output_path(self) -> Path:
        override = os.environ.get("PHONIC_DRIVE_OUTPUT")
        if override:
            return Path(override).expanduser()
        if self.output_root:
            return Path(self.output_root).expanduser()
        return self.data_path / "runs"


def load_config() -> UserConfig:
    data_root = str(_default_data_dir())
    config = UserConfig(data_root=data_root)
    if CONFIG_FILE.is_file():
        try:
            payload = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            config = UserConfig(
                data_root=str(payload.get("data_root") or data_root),
                corpus_root=payload.get("corpus_root"),
                output_root=payload.get("output_root"),
                participant_pseudonym=str(payload.get("participant_pseudonym") or "P001"),
            )
        except (OSError, ValueError, TypeError):
            pass

    corpus_override = os.environ.get("PHONIC_DRIVE_CORPUS")
    if corpus_override:
        config.corpus_root = corpus_override
    return config


def save_config(config: UserConfig) -> Path:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(asdict(config), indent=2), encoding="utf-8")
    return CONFIG_FILE


def ensure_user_dirs(config: UserConfig) -> None:
    config.data_path.mkdir(parents=True, exist_ok=True)
    config.output_path.mkdir(parents=True, exist_ok=True)
