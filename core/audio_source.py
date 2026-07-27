"""Source detection, download, and WAV normalization for MusicDNA ingestion."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal
from urllib.parse import parse_qs, urlparse

from core.runtime import require_binary, require_url_ingestion_capabilities
from core.subprocesses import console_python_executable, run_process


SUPPORTED_AUDIO_EXTENSIONS = frozenset({".wav", ".mp3", ".flac", ".m4a", ".ogg", ".opus", ".webm", ".mp4"})
VIDEO_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{11}$")
SourceKind = Literal["url", "file"]


class SourceError(RuntimeError):
    """Raised when MusicDNA cannot prepare a user-supplied audio source."""


@dataclass(frozen=True)
class AudioSource:
    """A validated source before it is downloaded or normalized."""

    kind: SourceKind
    value: str
    source_id: str
    path: Path | None = None


def _stable_id(prefix: str, value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:24]
    return f"{prefix}-{digest}"


def youtube_video_id(url: str) -> str | None:
    """Return a single YouTube video ID when one is present in *url*."""

    parsed = urlparse(url)
    host = parsed.netloc.lower().split(":", 1)[0]
    parts = [part for part in parsed.path.split("/") if part]
    video_id: str | None = None
    if host in {"youtu.be", "www.youtu.be"} and parts:
        video_id = parts[0]
    elif host in {"youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com"}:
        if parsed.path == "/watch":
            video_id = parse_qs(parsed.query).get("v", [None])[0]
        elif len(parts) >= 2 and parts[0] in {"shorts", "embed", "live"}:
            video_id = parts[1]
    return video_id if video_id and VIDEO_ID_PATTERN.fullmatch(video_id) else None


def parse_audio_source(value: str) -> AudioSource:
    """Recognize one supported http(s) URL or one supported local media file."""

    source = value.strip()
    if not source:
        raise SourceError("Provide a supported URL or an audio/video file path.")

    parsed = urlparse(source)
    if parsed.scheme in {"http", "https"} and parsed.netloc:
        return AudioSource("url", source, youtube_video_id(source) or _stable_id("url", source))

    path = Path(source).expanduser()
    if not path.is_file():
        raise SourceError("The source is neither a complete http(s) URL nor an existing local file.")
    if path.suffix.lower() not in SUPPORTED_AUDIO_EXTENSIONS:
        formats = ", ".join(extension.removeprefix(".").upper() for extension in sorted(SUPPORTED_AUDIO_EXTENSIONS))
        raise SourceError(f"Unsupported local file format. Supported formats: {formats}.")
    resolved = path.resolve()
    return AudioSource("file", str(resolved), _stable_id("file", str(resolved)), resolved)


def metadata_for_local_file(source: AudioSource) -> dict[str, Any]:
    """Return publish-safe metadata; deliberately do not retain a local path."""

    if source.kind != "file" or source.path is None:
        raise SourceError("Local-file metadata was requested for a non-file source.")
    return {
        "id": source.source_id,
        "title": source.path.stem or "untitled",
        "source_type": "file",
        "source_name": source.path.name,
        "uploader": "",
        "duration": None,
    }


def _raise_process_failure(message: str, result: Any) -> None:
    detail = str(getattr(result, "stderr", "") or "").strip()
    if detail:
        raise SourceError(message) from RuntimeError(detail)
    raise SourceError(message)


def inspect_url(source: AudioSource) -> dict[str, Any]:
    """Read metadata using yt-dlp in the same interpreter that runs MusicDNA."""

    if source.kind != "url":
        raise SourceError("URL inspection was requested for a local file.")
    require_url_ingestion_capabilities()
    command = [
        console_python_executable(),
        "-m",
        "yt_dlp",
        "--no-playlist",
        "--skip-download",
        "--dump-single-json",
        source.value,
    ]
    result = run_process(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        _raise_process_failure("yt-dlp could not read the requested URL.", result)
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise SourceError("yt-dlp did not return valid source metadata.") from error
    if not isinstance(payload, dict):
        raise SourceError("yt-dlp returned unsupported source metadata.")
    return {
        "id": source.source_id,
        "title": str(payload.get("title") or source.source_id),
        "source_type": "url",
        "webpage_url": str(payload.get("webpage_url") or source.value),
        "uploader": str(payload.get("uploader") or ""),
        "duration": payload.get("duration"),
        "upstream_id": str(payload.get("id") or ""),
        "extractor": str(payload.get("extractor_key") or ""),
    }


def download_url_audio(source: AudioSource, destination: Path) -> Path:
    """Download URL media without conversion; normalization is a separate step."""

    if source.kind != "url":
        raise SourceError("URL download was requested for a local file.")
    require_url_ingestion_capabilities()
    destination.mkdir(parents=True, exist_ok=True)
    output_template = destination / f"{source.source_id}.%(ext)s"
    command = [
        console_python_executable(),
        "-m",
        "yt_dlp",
        "--no-playlist",
        "--continue",
        "--no-progress",
        "--format",
        "bestaudio/best",
        "--output",
        str(output_template),
        "--print",
        "after_move:filepath",
        source.value,
    ]
    result = run_process(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        _raise_process_failure("yt-dlp could not download the requested audio.", result)
    candidates = [Path(line.strip()) for line in result.stdout.splitlines() if line.strip()]
    for candidate in reversed(candidates):
        if candidate.is_file():
            return candidate
    files = sorted(destination.glob(f"{source.source_id}.*"), key=lambda item: item.stat().st_mtime)
    if not files:
        raise SourceError("yt-dlp finished without producing an audio file.")
    return files[-1]


def normalize_audio(source_path: Path, destination: Path, source_id: str) -> Path:
    """Convert supported input media to mono 48 kHz PCM WAV for current engines."""

    input_path = Path(source_path)
    if not input_path.is_file():
        raise SourceError("The audio file disappeared before normalization.")
    destination.mkdir(parents=True, exist_ok=True)
    output_path = destination / f"{source_id}.wav"
    temporary_path = destination / f".{source_id}.normalizing.wav"
    if temporary_path.exists():
        temporary_path.unlink()
    command = [
        require_binary("ffmpeg"),
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(input_path),
        "-vn",
        "-ac",
        "1",
        "-ar",
        "48000",
        "-c:a",
        "pcm_s16le",
        str(temporary_path),
    ]
    result = run_process(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        if temporary_path.exists():
            temporary_path.unlink()
        _raise_process_failure("ffmpeg could not normalize the audio to WAV.", result)
    if not temporary_path.is_file():
        raise SourceError("ffmpeg finished without producing a normalized WAV file.")
    temporary_path.replace(output_path)
    return output_path
