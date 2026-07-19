"""Resumable YouTube-to-MusicDNA ingestion pipeline."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable
from urllib.parse import parse_qs, urlparse

from core.paths import (
    ingestion_state_path,
    reports_directory,
    samples_directory,
    write_json_atomic,
    write_text_atomic,
)
from core.publication import PublicationError, publish_pending_results
from core.report_workspace import ReportWorkspaceError, create_report_workspace
from core.runtime import require_binary, require_ingestion_capabilities
from core.subprocesses import console_python_executable, run_process
from engines.dna_builder import build as build_dna


VIDEO_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{11}$")
SAFE_FILENAME_PATTERN = re.compile(r'[<>:"/\\|?*\x00-\x1f]+')


class IngestionError(RuntimeError):
    """An expected, user-actionable ingestion failure."""


@dataclass(frozen=True)
class IngestionResult:
    video_id: str
    status: str
    title: str
    sample_path: Path | None
    dna_path: Path | None
    report_path: Path | None
    workspace_path: Path | None = None


def validate_youtube_url(url: str) -> str:
    """Validate a single YouTube video URL and return its video ID."""

    parsed = urlparse(url.strip())
    if parsed.scheme not in {"http", "https"}:
        raise IngestionError("Provide a complete http or https YouTube URL.")

    host = parsed.netloc.lower().split(":", 1)[0]
    path_parts = [part for part in parsed.path.split("/") if part]
    video_id: str | None = None

    if host in {"youtu.be", "www.youtu.be"} and path_parts:
        video_id = path_parts[0]
    elif host in {
        "youtube.com",
        "www.youtube.com",
        "m.youtube.com",
        "music.youtube.com",
    }:
        if parsed.path == "/watch":
            video_id = parse_qs(parsed.query).get("v", [None])[0]
        elif len(path_parts) >= 2 and path_parts[0] in {"shorts", "embed", "live"}:
            video_id = path_parts[1]

    if not video_id or not VIDEO_ID_PATTERN.fullmatch(video_id):
        raise IngestionError("The URL must point to one YouTube video, not a playlist or channel.")
    return video_id


def safe_filename(value: str, maximum_length: int = 80) -> str:
    """Create a portable filename component without changing the source title."""

    cleaned = SAFE_FILENAME_PATTERN.sub(" ", value)
    cleaned = re.sub(r"\s+", "_", cleaned).strip("._ ")
    return (cleaned[:maximum_length] or "untitled").strip("._ ") or "untitled"


def _load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"version": 1, "items": {}}
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise IngestionError(f"Ingestion state is unreadable: {error.msg}") from error
    if not isinstance(state, dict) or not isinstance(state.get("items"), dict):
        raise IngestionError("Ingestion state has an unsupported format.")
    return state


def _save_state(path: Path, state: dict[str, Any]) -> None:
    write_json_atomic(path, state)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as sample:
        for block in iter(lambda: sample.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _metadata_from_json(payload: dict[str, Any], url: str, expected_id: str) -> dict[str, Any]:
    video_id = str(payload.get("id", ""))
    if video_id != expected_id:
        raise IngestionError("yt-dlp returned metadata for a different video.")
    title = str(payload.get("title") or video_id)
    return {
        "id": video_id,
        "title": title,
        "webpage_url": str(payload.get("webpage_url") or url),
        "uploader": str(payload.get("uploader") or ""),
        "duration": payload.get("duration"),
    }


def _raise_process_failure(message: str, result: Any) -> None:
    """Raise a concise UI error while preserving child-process diagnostics in the log."""

    detail = str(getattr(result, "stderr", "") or "").strip()
    if detail:
        raise IngestionError(message) from RuntimeError(detail)
    raise IngestionError(message)


def inspect_video(url: str, video_id: str) -> dict[str, Any]:
    """Request metadata only for the video the user explicitly asked to ingest."""

    command = [
        console_python_executable(),
        "-m",
        "yt_dlp",
        "--no-playlist",
        "--skip-download",
        "--dump-single-json",
        url,
    ]
    result = run_process(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        _raise_process_failure("yt-dlp could not read the requested YouTube video.", result)
    try:
        return _metadata_from_json(json.loads(result.stdout), url, video_id)
    except json.JSONDecodeError as error:
        raise IngestionError("yt-dlp did not return valid video metadata.") from error


def download_audio(url: str, metadata: dict[str, Any], destination: Path) -> Path:
    """Download only the requested video and extract a WAV sample with ffmpeg."""

    destination.mkdir(parents=True, exist_ok=True)
    video_id = metadata["id"]
    output_template = destination / f"{video_id}_{safe_filename(metadata['title'])}.%(ext)s"
    ffmpeg_path = require_binary("ffmpeg")
    command = [
        console_python_executable(),
        "-m",
        "yt_dlp",
        "--no-playlist",
        "--continue",
        "--no-progress",
        "--extract-audio",
        "--audio-format",
        "wav",
        "--ffmpeg-location",
        str(Path(ffmpeg_path).parent),
        "--output",
        str(output_template),
        url,
    ]
    result = run_process(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        _raise_process_failure("yt-dlp could not download or convert the requested audio.", result)

    candidates = sorted(destination.glob(f"{video_id}_*.wav"), key=lambda item: item.stat().st_mtime)
    if not candidates:
        raise IngestionError("yt-dlp finished without producing a WAV sample.")
    return candidates[-1]


def _write_summary(
    report_path: Path,
    metadata: dict[str, Any],
    sample_path: Path,
    dna_path: Path,
    dna: dict[str, Any],
) -> None:
    bpm = dna["rhythm"]["bpm"]
    bpm_text = str(bpm["value"]) if bpm["status"] == "estimated" else "unavailable"
    lines = [
        "MusicDNA ingestion summary",
        f"Title: {metadata['title']}",
        f"YouTube URL: {metadata['webpage_url']}",
        f"Sample: {sample_path}",
        f"DNA: {dna_path}",
        f"Transient candidates: {dna['rhythm']['transients']['count']}",
        f"Estimated BPM: {bpm_text}",
    ]
    write_text_atomic(report_path, "\n".join(lines) + "\n")


def _existing_completed_result(item: dict[str, Any]) -> IngestionResult | None:
    if item.get("stage") != "completed":
        return None
    sample = Path(item["sample_path"])
    dna = Path(item["dna_path"])
    report = Path(item["report_path"])
    if not all(path.exists() for path in (sample, dna, report)):
        return None
    return IngestionResult(item["id"], "duplicate", item["metadata"]["title"], sample, dna, report)


def _find_content_duplicate(items: dict[str, Any], video_id: str, digest: str) -> dict[str, Any] | None:
    for candidate_id, item in items.items():
        if candidate_id != video_id and item.get("sha256") == digest and item.get("stage") == "completed":
            return item
    return None


def _publish_completed_analyses(progress: Callable[[str], None]) -> None:
    """Publish after local completion without allowing publication to invalidate analysis."""

    try:
        publication = publish_pending_results(progress)
    except PublicationError:
        progress("Publication failed. Completed analyses remain local and can be retried.")
        return
    if publication.failed:
        progress("Publication failed. Completed analyses remain local and can be retried.")
    elif publication.published:
        progress("Publication completed.")


def _create_report_workspace(
    video_id: str,
    metadata: dict[str, Any],
    dna_path: Path,
    progress: Callable[[str], None],
) -> Path | None:
    """Create a desktop copy without invalidating completed local analysis data."""

    try:
        dna = json.loads(dna_path.read_text(encoding="utf-8"))
        if not isinstance(dna, dict):
            raise ReportWorkspaceError("The completed DNA artifact is unreadable.")
        workspace = create_report_workspace(video_id, metadata, dna)
    except ReportWorkspaceError as error:
        progress(f"Desktop report workspace was not updated: {error} Local analysis remains available.")
        return None
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        progress("Desktop report workspace could not be created. Local analysis remains available.")
        return None
    progress(f"Desktop report workspace: {workspace.directory}")
    return workspace.directory


def ingest(url: str, progress: Callable[[str], None] = print) -> IngestionResult:
    """Run validation, download, analysis, persistence, and short reporting."""

    require_ingestion_capabilities()
    video_id = validate_youtube_url(url)
    state_path = ingestion_state_path()
    state = _load_state(state_path)
    items = state["items"]
    existing = items.get(video_id)
    if existing:
        completed = _existing_completed_result(existing)
        if completed:
            progress("Duplicate detected: this video has already been processed.")
            workspace_path = _create_report_workspace(
                completed.video_id,
                existing["metadata"],
                completed.dna_path,
                progress,
            )
            _publish_completed_analyses(progress)
            return IngestionResult(
                completed.video_id,
                completed.status,
                completed.title,
                completed.sample_path,
                completed.dna_path,
                completed.report_path,
                workspace_path,
            )

    metadata = existing.get("metadata") if existing else None
    if not metadata:
        progress("Reading YouTube metadata...")
        metadata = inspect_video(url, video_id)

    sample_path = Path(existing["sample_path"]) if existing and existing.get("sample_path") else None
    if sample_path is None or not sample_path.exists():
        progress("Downloading and converting audio...")
        items[video_id] = {"id": video_id, "metadata": metadata, "stage": "downloading"}
        _save_state(state_path, state)
        sample_path = download_audio(url, metadata, samples_directory())
        digest = _sha256(sample_path)
        duplicate = _find_content_duplicate(items, video_id, digest)
        if duplicate:
            items[video_id] = {
                "id": video_id,
                "metadata": metadata,
                "stage": "duplicate",
                "duplicate_of": duplicate["id"],
                "sample_path": str(sample_path),
                "sha256": digest,
            }
            _save_state(state_path, state)
            progress("Duplicate audio detected; analysis was not repeated.")
            return IngestionResult(video_id, "duplicate", metadata["title"], sample_path, None, None)
        items[video_id] = {
            "id": video_id,
            "metadata": metadata,
            "stage": "downloaded",
            "sample_path": str(sample_path),
            "sha256": digest,
        }
        _save_state(state_path, state)

    record = items[video_id]
    dna_path = Path(record["dna_path"]) if record.get("dna_path") else None
    if dna_path is not None and dna_path.exists():
        dna = json.loads(dna_path.read_text(encoding="utf-8"))
    else:
        progress("Running MusicDNA analysis...")
        record["stage"] = "analyzing"
        _save_state(state_path, state)
        try:
            dna, dna_path = build_dna(str(sample_path), title=metadata["title"], metadata=metadata)
        except Exception as error:
            record["stage"] = "failed"
            record["error"] = type(error).__name__
            _save_state(state_path, state)
            raise IngestionError("MusicDNA analysis did not complete; rerun the same command to resume.") from error
        record["dna_path"] = str(dna_path)
        record["stage"] = "analyzed"
        _save_state(state_path, state)

    report_path = reports_directory() / f"{video_id}_summary.txt"
    if not report_path.exists():
        progress("Generating summary report...")
        _write_summary(report_path, metadata, sample_path, dna_path, dna)

    record["report_path"] = str(report_path)
    record["stage"] = "completed"
    record.pop("error", None)
    _save_state(state_path, state)
    progress("Completed.")
    workspace_path = _create_report_workspace(video_id, metadata, dna_path, progress)
    _publish_completed_analyses(progress)
    return IngestionResult(
        video_id,
        "completed",
        metadata["title"],
        sample_path,
        dna_path,
        report_path,
        workspace_path,
    )
