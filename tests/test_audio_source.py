from __future__ import annotations

from pathlib import Path

import pytest

from core import audio_source


def test_parse_source_accepts_any_complete_https_url():
    source = audio_source.parse_audio_source("https://example.com/track")

    assert source.kind == "url"
    assert source.source_id.startswith("url-")


def test_parse_source_keeps_legacy_youtube_identifier():
    source = audio_source.parse_audio_source("https://youtu.be/H1HdZFgR-aA")

    assert source.kind == "url"
    assert source.source_id == "H1HdZFgR-aA"


def test_parse_source_accepts_windows_style_unicode_file_name(tmp_path: Path):
    media = tmp_path / "Suno exports" / "Łódź – mój utwór.MP3"
    media.parent.mkdir()
    media.write_bytes(b"fixture")

    source = audio_source.parse_audio_source(str(media))

    assert source.kind == "file"
    assert source.path == media.resolve()
    assert source.source_id.startswith("file-")
    assert audio_source.metadata_for_local_file(source)["title"] == "Łódź – mój utwór"


def test_parse_source_rejects_missing_or_unsupported_local_file(tmp_path: Path):
    with pytest.raises(audio_source.SourceError, match="existing local file"):
        audio_source.parse_audio_source(str(tmp_path / "missing.mp3"))

    document = tmp_path / "track.txt"
    document.write_text("not audio", encoding="utf-8")
    with pytest.raises(audio_source.SourceError, match="Unsupported local file format"):
        audio_source.parse_audio_source(str(document))


def test_download_and_normalization_are_separate(monkeypatch, tmp_path: Path):
    source = audio_source.parse_audio_source("https://example.com/track")
    downloaded = tmp_path / "downloads" / f"{source.source_id}.webm"
    normalized = tmp_path / "samples" / f"{source.source_id}.wav"
    received: list[list[str]] = []

    monkeypatch.setattr(audio_source, "require_url_ingestion_capabilities", lambda: None)

    def download_process(command, **_kwargs):
        received.append(list(command))
        downloaded.parent.mkdir(parents=True, exist_ok=True)
        downloaded.write_bytes(b"downloaded")
        return type("Result", (), {"returncode": 0, "stdout": f"{downloaded}\n", "stderr": ""})()

    monkeypatch.setattr(audio_source, "run_process", download_process)
    assert audio_source.download_url_audio(source, downloaded.parent) == downloaded
    assert "--format" in received[0]
    assert "--extract-audio" not in received[0]

    def normalize_process(command, **_kwargs):
        received.append(list(command))
        temporary = Path(command[-1])
        temporary.write_bytes(b"wav")
        return type("Result", (), {"returncode": 0, "stdout": "", "stderr": ""})()

    monkeypatch.setattr(audio_source, "require_binary", lambda _name: "ffmpeg")
    monkeypatch.setattr(audio_source, "run_process", normalize_process)
    assert audio_source.normalize_audio(downloaded, normalized.parent, source.source_id) == normalized
    assert normalized.read_bytes() == b"wav"
    assert received[1][0] == "ffmpeg"
    assert received[1][-1].endswith(".normalizing.wav")


def test_normalization_preserves_ffmpeg_stderr(monkeypatch, tmp_path: Path):
    media = tmp_path / "input.mp3"
    media.write_bytes(b"fixture")
    monkeypatch.setattr(audio_source, "require_binary", lambda _name: "ffmpeg")
    monkeypatch.setattr(
        audio_source,
        "run_process",
        lambda *_args, **_kwargs: type("Result", (), {"returncode": 1, "stdout": "", "stderr": "invalid data"})(),
    )

    with pytest.raises(audio_source.SourceError, match="could not normalize") as error:
        audio_source.normalize_audio(media, tmp_path / "samples", "file-123")

    assert str(error.value.__cause__) == "invalid data"
