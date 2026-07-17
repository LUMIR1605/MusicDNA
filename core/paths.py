"""Cross-platform locations and atomic writes for MusicDNA runtime data."""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping


APP_NAME = "MusicDNA"


def data_root(
    environ: Mapping[str, str] | None = None,
    home: Path | None = None,
    platform_name: str | None = None,
) -> Path:
    """Return the application data directory without creating it."""

    environment = os.environ if environ is None else environ
    user_home = Path.home() if home is None else Path(home)
    configured = environment.get("MUSICDNA_DATA_DIR")
    if configured:
        return Path(configured).expanduser()

    system = sys.platform if platform_name is None else platform_name
    if system.startswith("win"):
        local_app_data = environment.get("LOCALAPPDATA")
        base = Path(local_app_data) if local_app_data else user_home / "AppData" / "Local"
        return base / APP_NAME

    if environment.get("TERMUX_VERSION"):
        return user_home / ".local" / "share" / "musicdna"

    xdg_data_home = environment.get("XDG_DATA_HOME")
    base = Path(xdg_data_home) if xdg_data_home else user_home / ".local" / "share"
    return base / "musicdna"


def knowledge_database_path() -> Path:
    return data_root() / "knowledge" / "knowledge.json"


def dna_output_directory() -> Path:
    return data_root() / "dna"


def ensure_directory(directory: Path) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def write_text_atomic(path: Path, content: str, encoding: str = "utf-8") -> None:
    """Write a file in its target directory and replace it only after a full write."""

    target = Path(path)
    ensure_directory(target.parent)
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding=encoding,
            dir=target.parent,
            prefix=f".{target.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_name = temporary_file.name
            temporary_file.write(content)
        Path(temporary_name).replace(target)
    finally:
        if temporary_name:
            temporary_path = Path(temporary_name)
            if temporary_path.exists():
                temporary_path.unlink()


def write_json_atomic(path: Path, data: Any) -> None:
    write_text_atomic(path, json.dumps(data, indent=2, ensure_ascii=False))
