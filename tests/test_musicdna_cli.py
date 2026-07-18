from __future__ import annotations

from pathlib import Path

import musicdna
from core.ingestion import IngestionError, IngestionResult


def test_add_command_reports_completed_result(monkeypatch, capsys):
    result = IngestionResult(
        "dQw4w9WgXcQ",
        "completed",
        "Example",
        Path("sample.wav"),
        Path("dna.json"),
        Path("summary.txt"),
    )
    monkeypatch.setattr(musicdna, "ingest", lambda _url: result)

    assert musicdna.main(["add", "https://www.youtube.com/watch?v=dQw4w9WgXcQ"]) == 0
    output = capsys.readouterr().out
    assert "Status: completed" in output
    assert "Summary: summary.txt" in output


def test_add_command_reports_expected_ingestion_error(monkeypatch, capsys):
    monkeypatch.setattr(musicdna, "ingest", lambda _url: (_ for _ in ()).throw(IngestionError("bad URL")))

    assert musicdna.main(["add", "https://example.com"]) == 2
    assert "MusicDNA add failed: bad URL" in capsys.readouterr().out
