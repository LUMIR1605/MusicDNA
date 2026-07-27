from __future__ import annotations

import pytest
from pathlib import Path

from core import launcher_service
from core.ingestion import IngestionError, IngestionResult


URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


def test_validate_add_url_accepts_single_video_url():
    assert launcher_service.validate_add_url(URL) == "dQw4w9WgXcQ"


def test_validate_add_url_rejects_invalid_url_before_ingestion():
    with pytest.raises(IngestionError):
        launcher_service.validate_add_url("not a URL")


def test_validate_add_source_accepts_local_file(tmp_path: Path):
    source = tmp_path / "Suno export.mp3"
    source.write_bytes(b"audio")

    assert launcher_service.validate_add_source(str(source)).startswith("file-")


def test_run_add_delegates_to_existing_ingestion_pipeline(monkeypatch):
    progress: list[str] = []
    result = IngestionResult("dQw4w9WgXcQ", "completed", "Example", None, None, None)
    received: list[tuple[str, object]] = []

    def fake_ingest(url, callback):
        received.append((url, callback))
        callback("Downloading and converting audio...")
        return result

    monkeypatch.setattr(launcher_service, "ingest", fake_ingest)

    assert launcher_service.run_add(URL, progress.append) is result
    assert received[0][0] == URL
    assert progress == ["Downloading and converting audio..."]
