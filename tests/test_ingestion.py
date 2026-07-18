from __future__ import annotations

import json
from pathlib import Path

import pytest

from core import ingestion
from core.publication import PublicationResult
from core.paths import write_json_atomic


URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
VIDEO_ID = "dQw4w9WgXcQ"


def metadata(video_id: str = VIDEO_ID):
    return {
        "id": video_id,
        "title": "Example / Song: Test",
        "webpage_url": URL,
        "uploader": "MusicDNA tests",
        "duration": 120,
    }


def dna_payload():
    return {
        "rhythm": {
            "transients": {"count": 4},
            "bpm": {"status": "estimated", "value": 120.0},
        }
    }


def configure_pipeline(monkeypatch, tmp_path: Path):
    state = tmp_path / "ingestion" / "state.json"
    samples = tmp_path / "samples"
    reports = tmp_path / "reports"
    monkeypatch.setattr(ingestion, "require_ingestion_capabilities", lambda: None)
    monkeypatch.setattr(ingestion, "ingestion_state_path", lambda: state)
    monkeypatch.setattr(ingestion, "samples_directory", lambda: samples)
    monkeypatch.setattr(ingestion, "reports_directory", lambda: reports)
    monkeypatch.setattr(ingestion, "publish_pending_results", lambda _progress: PublicationResult())
    return state, samples, reports


def test_validate_youtube_url_supports_video_forms_and_rejects_invalid_values():
    assert ingestion.validate_youtube_url(URL) == VIDEO_ID
    assert ingestion.validate_youtube_url(f"https://youtu.be/{VIDEO_ID}") == VIDEO_ID
    assert ingestion.validate_youtube_url(f"https://www.youtube.com/shorts/{VIDEO_ID}") == VIDEO_ID

    with pytest.raises(ingestion.IngestionError, match="one YouTube video"):
        ingestion.validate_youtube_url("https://www.youtube.com/playlist?list=example")


def test_safe_filename_removes_portability_hazards():
    assert ingestion.safe_filename('  A/B:C*D?E"F<G>H|  ') == "A_B_C_D_E_F_G_H"
    assert ingestion.safe_filename("...") == "untitled"


def test_ingest_runs_download_analysis_persistence_and_summary(monkeypatch, tmp_path: Path):
    state, samples, reports = configure_pipeline(monkeypatch, tmp_path)
    monkeypatch.setattr(ingestion, "inspect_video", lambda *_args: metadata())

    def download(_url, info, destination):
        destination.mkdir(parents=True, exist_ok=True)
        sample = destination / f"{info['id']}_example.wav"
        sample.write_bytes(b"audio")
        return sample

    def build(sample, title, metadata):
        dna_path = tmp_path / "dna" / "example.json"
        dna_path.parent.mkdir(parents=True, exist_ok=True)
        dna_path.write_text(json.dumps(dna_payload()), encoding="utf-8")
        assert Path(sample).exists()
        assert title == "Example / Song: Test"
        assert metadata["id"] == VIDEO_ID
        return dna_payload(), dna_path

    monkeypatch.setattr(ingestion, "download_audio", download)
    monkeypatch.setattr(ingestion, "build_dna", build)
    progress: list[str] = []

    result = ingestion.ingest(URL, progress.append)

    assert result.status == "completed"
    assert result.sample_path == samples / f"{VIDEO_ID}_example.wav"
    assert result.dna_path and result.dna_path.exists()
    assert result.report_path == reports / f"{VIDEO_ID}_summary.txt"
    assert "Estimated BPM: 120.0" in result.report_path.read_text(encoding="utf-8")
    assert progress == [
        "Reading YouTube metadata...",
        "Downloading and converting audio...",
        "Running MusicDNA analysis...",
        "Generating summary report...",
        "Completed.",
    ]
    saved_state = json.loads(state.read_text(encoding="utf-8"))
    assert saved_state["items"][VIDEO_ID]["stage"] == "completed"


def test_completed_video_is_detected_without_network_or_reanalysis(monkeypatch, tmp_path: Path):
    configure_pipeline(monkeypatch, tmp_path)
    monkeypatch.setattr(ingestion, "inspect_video", lambda *_args: metadata())

    def download(_url, info, destination):
        destination.mkdir(parents=True, exist_ok=True)
        sample = destination / "sample.wav"
        sample.write_bytes(b"audio")
        return sample

    def build(*_args, **_kwargs):
        dna_path = tmp_path / "dna" / "example.json"
        dna_path.parent.mkdir(parents=True, exist_ok=True)
        dna_path.write_text(json.dumps(dna_payload()), encoding="utf-8")
        return dna_payload(), dna_path

    monkeypatch.setattr(ingestion, "download_audio", download)
    monkeypatch.setattr(ingestion, "build_dna", build)
    ingestion.ingest(URL, lambda _message: None)

    monkeypatch.setattr(ingestion, "inspect_video", lambda *_args: pytest.fail("network used"))
    monkeypatch.setattr(ingestion, "build_dna", lambda *_args, **_kwargs: pytest.fail("analysis repeated"))
    result = ingestion.ingest(URL, lambda _message: None)

    assert result.status == "duplicate"


def test_completed_analysis_publication_failure_does_not_invalidate_local_result(monkeypatch, tmp_path: Path):
    configure_pipeline(monkeypatch, tmp_path)
    monkeypatch.setattr(ingestion, "inspect_video", lambda *_args: metadata())
    monkeypatch.setattr(ingestion, "download_audio", lambda *_args: (tmp_path / "sample.wav"))

    sample = tmp_path / "sample.wav"
    sample.write_bytes(b"audio")

    def build(*_args, **_kwargs):
        dna_path = tmp_path / "dna" / "example.json"
        dna_path.parent.mkdir(parents=True, exist_ok=True)
        dna_path.write_text(json.dumps(dna_payload()), encoding="utf-8")
        return dna_payload(), dna_path

    monkeypatch.setattr(ingestion, "build_dna", build)
    monkeypatch.setattr(
        ingestion,
        "publish_pending_results",
        lambda _progress: PublicationResult(failed=[VIDEO_ID]),
    )

    result = ingestion.ingest(URL, lambda _message: None)

    assert result.status == "completed"
    assert result.report_path and result.report_path.exists()


def test_downloaded_state_resumes_analysis_without_downloading(monkeypatch, tmp_path: Path):
    state, samples, _reports = configure_pipeline(monkeypatch, tmp_path)
    sample = samples / "resume.wav"
    sample.parent.mkdir(parents=True, exist_ok=True)
    sample.write_bytes(b"audio")
    write_json_atomic(
        state,
        {
            "version": 1,
            "items": {
                VIDEO_ID: {
                    "id": VIDEO_ID,
                    "metadata": metadata(),
                    "stage": "downloaded",
                    "sample_path": str(sample),
                    "sha256": "fixture",
                }
            },
        },
    )
    monkeypatch.setattr(ingestion, "download_audio", lambda *_args: pytest.fail("download repeated"))

    def build(*_args, **_kwargs):
        dna_path = tmp_path / "dna" / "resume.json"
        dna_path.parent.mkdir(parents=True, exist_ok=True)
        dna_path.write_text(json.dumps(dna_payload()), encoding="utf-8")
        return dna_payload(), dna_path

    monkeypatch.setattr(ingestion, "build_dna", build)

    result = ingestion.ingest(URL, lambda _message: None)

    assert result.status == "completed"
    assert result.dna_path and result.dna_path.name == "resume.json"


def test_content_duplicate_is_not_analyzed_twice(monkeypatch, tmp_path: Path):
    state, samples, reports = configure_pipeline(monkeypatch, tmp_path)
    original_id = "AAAAAAAAAAA"
    original_sample = samples / "original.wav"
    original_dna = tmp_path / "dna" / "original.json"
    original_report = reports / "original.txt"
    for path in (original_sample, original_dna, original_report):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("fixture", encoding="utf-8")
    write_json_atomic(
        state,
        {
            "version": 1,
            "items": {
                original_id: {
                    "id": original_id,
                    "metadata": metadata(original_id),
                    "stage": "completed",
                    "sample_path": str(original_sample),
                    "dna_path": str(original_dna),
                    "report_path": str(original_report),
                    "sha256": ingestion._sha256(original_sample),
                }
            },
        },
    )
    monkeypatch.setattr(ingestion, "inspect_video", lambda *_args: metadata())

    def download(_url, _info, destination):
        destination.mkdir(parents=True, exist_ok=True)
        duplicate = destination / "duplicate.wav"
        duplicate.write_text("fixture", encoding="utf-8")
        return duplicate

    monkeypatch.setattr(ingestion, "download_audio", download)
    monkeypatch.setattr(ingestion, "build_dna", lambda *_args, **_kwargs: pytest.fail("analysis repeated"))

    result = ingestion.ingest(URL, lambda _message: None)

    assert result.status == "duplicate"
    assert result.dna_path is None
