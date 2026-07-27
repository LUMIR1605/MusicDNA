from __future__ import annotations

import json
from pathlib import Path

import pytest

from core import ingestion
from core.audio_source import SourceError, parse_audio_source
from core.publication import PublicationResult
from core.paths import write_json_atomic


URL = "https://youtu.be/H1HdZFgR-aA"
VIDEO_ID = "H1HdZFgR-aA"


def dna_payload():
    return {
        "rhythm": {
            "transients": {"count": 4},
            "bpm": {"status": "estimated", "value": 120.0},
        }
    }


def url_metadata(source_id: str = VIDEO_ID) -> dict[str, object]:
    return {
        "id": source_id,
        "title": "Example / Song: Test",
        "source_type": "url",
        "webpage_url": URL,
        "uploader": "MusicDNA tests",
        "duration": 120,
    }


def configure_pipeline(monkeypatch, tmp_path: Path):
    state = tmp_path / "ingestion" / "state.json"
    downloads = tmp_path / "downloads"
    samples = tmp_path / "samples"
    reports = tmp_path / "reports"
    monkeypatch.setattr(ingestion, "ingestion_state_path", lambda: state)
    monkeypatch.setattr(ingestion, "downloads_directory", lambda: downloads)
    monkeypatch.setattr(ingestion, "samples_directory", lambda: samples)
    monkeypatch.setattr(ingestion, "reports_directory", lambda: reports)
    monkeypatch.setattr(ingestion, "publish_pending_results", lambda _progress: PublicationResult())
    workspaces: list[str] = []
    monkeypatch.setattr(
        ingestion,
        "_create_report_workspace",
        lambda source_id, *_args: workspaces.append(source_id) or tmp_path / "Desktop" / source_id,
    )

    def build(_sample, title, metadata):
        dna_path = tmp_path / "dna" / f"{metadata['id']}.json"
        dna_path.parent.mkdir(parents=True, exist_ok=True)
        dna_path.write_text(json.dumps(dna_payload()), encoding="utf-8")
        assert title == metadata["title"]
        return dna_payload(), dna_path

    monkeypatch.setattr(ingestion, "build_dna", build)
    return state, downloads, samples, reports, workspaces


def install_url_preparation(monkeypatch, tmp_path: Path):
    raw = tmp_path / "raw.webm"
    calls: list[str] = []
    monkeypatch.setattr(ingestion, "inspect_url", lambda source: calls.append("inspect") or url_metadata(source.source_id))

    def download(_source, _destination):
        calls.append("download")
        raw.write_bytes(b"raw")
        return raw

    def normalize(_input, destination, source_id):
        calls.append("normalize")
        destination.mkdir(parents=True, exist_ok=True)
        result = destination / f"{source_id}.wav"
        result.write_bytes(b"normalized audio")
        return result

    monkeypatch.setattr(ingestion, "download_url_audio", download)
    monkeypatch.setattr(ingestion, "normalize_audio", normalize)
    return calls


def test_validate_youtube_url_keeps_single_video_compatibility():
    assert ingestion.validate_youtube_url(URL) == VIDEO_ID
    with pytest.raises(ingestion.IngestionError, match="one YouTube video"):
        ingestion.validate_youtube_url("https://www.youtube.com/playlist?list=example")


def test_url_runs_download_normalization_analysis_and_summary(monkeypatch, tmp_path: Path):
    state, _downloads, samples, reports, workspaces = configure_pipeline(monkeypatch, tmp_path)
    calls = install_url_preparation(monkeypatch, tmp_path)

    result = ingestion.ingest(URL, lambda _message: None)

    assert result.status == "completed"
    assert result.video_id == VIDEO_ID
    assert result.sample_path == samples / f"{VIDEO_ID}.wav"
    assert result.report_path == reports / f"{VIDEO_ID}_summary.txt"
    assert calls == ["inspect", "download", "normalize"]
    assert workspaces == [VIDEO_ID]
    assert "Source URL: https://youtu.be/H1HdZFgR-aA" in result.report_path.read_text(encoding="utf-8")
    assert json.loads(state.read_text(encoding="utf-8"))["items"][VIDEO_ID]["stage"] == "completed"


def test_local_file_with_spaces_and_unicode_skips_yt_dlp(monkeypatch, tmp_path: Path):
    _state, _downloads, samples, reports, workspaces = configure_pipeline(monkeypatch, tmp_path)
    local = tmp_path / "Suno exports" / "Łódź mój utwór.mp3"
    local.parent.mkdir()
    local.write_bytes(b"source")
    source = parse_audio_source(str(local))
    received: list[Path] = []

    def normalize(input_path, destination, source_id):
        received.append(Path(input_path))
        destination.mkdir(parents=True, exist_ok=True)
        result = destination / f"{source_id}.wav"
        result.write_bytes(b"normalized audio")
        return result

    monkeypatch.setattr(ingestion, "inspect_url", lambda *_args: pytest.fail("yt-dlp used for local file"))
    monkeypatch.setattr(ingestion, "download_url_audio", lambda *_args: pytest.fail("download used for local file"))
    monkeypatch.setattr(ingestion, "normalize_audio", normalize)

    result = ingestion.ingest(str(local), lambda _message: None)

    assert result.status == "completed"
    assert result.video_id == source.source_id
    assert result.sample_path == samples / f"{source.source_id}.wav"
    assert result.report_path == reports / f"{source.source_id}_summary.txt"
    assert received == [local.resolve()]
    assert workspaces == [source.source_id]
    summary = result.report_path.read_text(encoding="utf-8")
    assert "Source: local audio file" in summary
    assert str(local.resolve()) not in summary


def test_completed_source_resumes_without_network_or_reanalysis(monkeypatch, tmp_path: Path):
    _state, _downloads, _samples, _reports, workspaces = configure_pipeline(monkeypatch, tmp_path)
    calls = install_url_preparation(monkeypatch, tmp_path)
    first = ingestion.ingest(URL, lambda _message: None)
    monkeypatch.setattr(ingestion, "inspect_url", lambda *_args: pytest.fail("network used"))
    monkeypatch.setattr(ingestion, "build_dna", lambda *_args, **_kwargs: pytest.fail("analysis repeated"))

    second = ingestion.ingest(URL, lambda _message: None)

    assert first.status == "completed"
    assert second.status == "duplicate"
    assert calls == ["inspect", "download", "normalize"]
    assert workspaces == [VIDEO_ID, VIDEO_ID]


def test_normalized_sha256_duplicate_is_not_analyzed_twice(monkeypatch, tmp_path: Path):
    state, _downloads, samples, reports, _workspaces = configure_pipeline(monkeypatch, tmp_path)
    original_id = "AAAAAAAAAAA"
    original_sample = samples / "original.wav"
    original_dna = tmp_path / "dna" / "original.json"
    original_report = reports / "original_summary.txt"
    for path in (original_sample, original_dna, original_report):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"same normalized audio")
    write_json_atomic(
        state,
        {"version": 1, "items": {original_id: {"id": original_id, "metadata": url_metadata(original_id), "stage": "completed", "sample_path": str(original_sample), "dna_path": str(original_dna), "report_path": str(original_report), "sha256": ingestion._sha256(original_sample)}}},
    )
    local = tmp_path / "Suno.mp3"
    local.write_bytes(b"source")

    def normalize(_input, destination, source_id):
        destination.mkdir(parents=True, exist_ok=True)
        result = destination / f"{source_id}.wav"
        result.write_bytes(b"same normalized audio")
        return result

    monkeypatch.setattr(ingestion, "normalize_audio", normalize)
    monkeypatch.setattr(ingestion, "build_dna", lambda *_args, **_kwargs: pytest.fail("analysis repeated"))

    result = ingestion.ingest(str(local), lambda _message: None)

    assert result.status == "duplicate"
    assert result.dna_path is None


def test_downloaded_state_resumes_analysis_without_preparing_again(monkeypatch, tmp_path: Path):
    state, _downloads, samples, _reports, _workspaces = configure_pipeline(monkeypatch, tmp_path)
    sample = samples / f"{VIDEO_ID}.wav"
    sample.parent.mkdir(parents=True)
    sample.write_bytes(b"audio")
    write_json_atomic(
        state,
        {"version": 1, "items": {VIDEO_ID: {"id": VIDEO_ID, "metadata": url_metadata(), "stage": "downloaded", "sample_path": str(sample), "sha256": "fixture"}}},
    )
    monkeypatch.setattr(ingestion, "normalize_audio", lambda *_args: pytest.fail("normalization repeated"))
    monkeypatch.setattr(ingestion, "download_url_audio", lambda *_args: pytest.fail("download repeated"))

    result = ingestion.ingest(URL, lambda _message: None)

    assert result.status == "completed"
    assert result.dna_path and result.dna_path.exists()


def test_source_errors_are_user_actionable(monkeypatch, tmp_path: Path):
    with pytest.raises(ingestion.IngestionError, match="existing local file"):
        ingestion.ingest(str(tmp_path / "missing.mp3"), lambda _message: None)

    configure_pipeline(monkeypatch, tmp_path)
    monkeypatch.setattr(ingestion, "inspect_url", lambda _source: (_ for _ in ()).throw(SourceError("site rejected request")))
    with pytest.raises(ingestion.IngestionError, match="site rejected request"):
        ingestion.ingest(URL, lambda _message: None)
