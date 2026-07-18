from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from core.paths import data_root, write_json_atomic
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


def test_atomic_json_write_normalizes_nested_numpy_values(tmp_path: Path):
    target = tmp_path / "data.json"
    write_json_atomic(
        target,
        {
            "float64": np.float64(1.25),
            "float32": np.float32(2.5),
            "int64": np.int64(7),
            "array": np.array([np.int64(1), np.float32(2.5)]),
            "nested": ({"value": np.float64(3.5)},),
        },
    )

    assert json.loads(target.read_text(encoding="utf-8")) == {
        "float64": 1.25,
        "float32": 2.5,
        "int64": 7,
        "array": [1, 2.5],
        "nested": [{"value": 3.5}],
    }


def test_atomic_json_write_rejects_unsupported_values(tmp_path: Path):
    target = tmp_path / "data.json"

    with pytest.raises(TypeError, match="Unsupported value for JSON serialization"):
        write_json_atomic(target, {"unsupported": object()})

    assert not target.exists()
