from __future__ import annotations

import json
from pathlib import Path

from core.paths import data_root
from engines.dna_store import save
from engines.knowledge_engine import analyze


def test_data_root_uses_windows_local_app_data(tmp_path: Path):
    root = data_root(
        environ={"LOCALAPPDATA": str(tmp_path / "AppData" / "Local")},
        home=tmp_path / "home",
        platform_name="win32",
    )

    assert root == tmp_path / "AppData" / "Local" / "MusicDNA"


def test_data_root_uses_termux_home_without_hard_coded_storage(tmp_path: Path):
    root = data_root(
        environ={"TERMUX_VERSION": "0.118"},
        home=tmp_path / "home",
        platform_name="linux",
    )

    assert root == tmp_path / "home" / ".local" / "share" / "musicdna"


def test_data_root_honours_explicit_override(tmp_path: Path):
    configured = tmp_path / "custom-data"

    assert data_root(
        environ={"MUSICDNA_DATA_DIR": str(configured)},
        home=tmp_path / "home",
        platform_name="linux",
    ) == configured


def test_first_knowledge_write_creates_parent_directory(tmp_path: Path):
    database = tmp_path / "knowledge" / "knowledge.json"

    stored = analyze("fixture.wav", {"schema_version": "dna-output-v1"}, database_path=database)

    assert database.exists()
    assert json.loads(database.read_text(encoding="utf-8")) == stored
    assert stored[0]["title"] == "fixture.wav"


def test_dna_store_creates_output_directory(tmp_path: Path):
    output_directory = tmp_path / "dna"

    saved = save("fixture.wav", {"schema_version": "dna-output-v1"}, output_directory=output_directory)

    assert saved == output_directory / "fixture.json"
    assert json.loads(saved.read_text(encoding="utf-8"))["schema_version"] == "dna-output-v1"
