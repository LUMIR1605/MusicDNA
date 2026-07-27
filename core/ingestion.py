"""Resumable URL and local-file ingestion for the unchanged MusicDNA engines."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from core.audio_source import (
    AudioSource,
    SourceError,
    download_url_audio,
    inspect_url,
    metadata_for_local_file,
    normalize_audio,
    parse_audio_source,
    youtube_video_id,
)
from core.paths import (
    downloads_directory,
    ingestion_state_path,
    reports_directory,
    samples_directory,
    write_json_atomic,
    write_text_atomic,
)
from core.publication import PublicationError, publish_pending_results
from core.report_workspace import ReportWorkspaceError, create_report_workspace
from engines.dna_builder import build as build_dna


SAFE_FILENAME_PATTERN = re.compile(r'[<>:"/\\|?*\x00-\x1f]+')


class IngestionError(RuntimeError):
    """An expected, user-actionable ingestion failure."""


@dataclass(frozen=True)
class IngestionResult:
    """The persisted result for one source; ``video_id`` is a legacy source ID."""

    video_id: str
    status: str
    title: str
    sample_path: Path | None
    dna_path: Path | None
    report_path: Path | None
    workspace_path: Path | None = None


def validate_youtube_url(url: str) -> str:
    """Keep the previous single-YouTube validation helper for API compatibility."""

    video_id = youtube_video_id(url.strip())
    if video_id is None:
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


def _write_summary(
    report_path: Path,
    source_id: str,
    metadata: dict[str, Any],
    sample_path: Path,
    dna_path: Path,
    dna: dict[str, Any],
) -> None:
    bpm = dna["rhythm"]["bpm"]
    bpm_text = str(bpm["value"]) if bpm["status"] == "estimated" else "unavailable"
    source_line = (
        f"Source URL: {metadata['webpage_url']}"
        if metadata.get("source_type") == "url"
        else "Source: local audio file"
    )
    lines = [
        "MusicDNA ingestion summary",
        f"Title: {metadata['title']}",
        f"Source ID: {source_id}",
        source_line,
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


def _find_content_duplicate(items: dict[str, Any], source_id: str, digest: str) -> dict[str, Any] | None:
    for candidate_id, item in items.items():
        if candidate_id != source_id and item.get("sha256") == digest and item.get("stage") == "completed":
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
    source_id: str,
    metadata: dict[str, Any],
    dna_path: Path,
    progress: Callable[[str], None],
) -> Path | None:
    """Create a desktop copy without invalidating completed local analysis data."""

    try:
        dna = json.loads(dna_path.read_text(encoding="utf-8"))
        if not isinstance(dna, dict):
            raise ReportWorkspaceError("The completed DNA artifact is unreadable.")
        workspace = create_report_workspace(source_id, metadata, dna)
    except ReportWorkspaceError as error:
        progress(f"Desktop report workspace was not updated: {error} Local analysis remains available.")
        return None
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        progress("Desktop report workspace could not be created. Local analysis remains available.")
        return None
    progress(f"Desktop report workspace: {workspace.directory}")
    return workspace.directory


def _metadata_for_source(source: AudioSource) -> dict[str, Any]:
    try:
        return inspect_url(source) if source.kind == "url" else metadata_for_local_file(source)
    except SourceError as error:
        raise IngestionError(str(error)) from error


def _normalize_source(source: AudioSource, source_id: str) -> Path:
    try:
        if source.kind == "url":
            downloaded = download_url_audio(source, downloads_directory())
            return normalize_audio(downloaded, samples_directory(), source_id)
        assert source.path is not None
        return normalize_audio(source.path, samples_directory(), source_id)
    except SourceError as error:
        raise IngestionError(str(error)) from error


def ingest(value: str, progress: Callable[[str], None] = print) -> IngestionResult:
    """Detect a source, prepare WAV, then run the existing analysis and publishing flow."""

    try:
        source = parse_audio_source(value)
    except SourceError as error:
        raise IngestionError(str(error)) from error

    source_id = source.source_id
    state_path = ingestion_state_path()
    state = _load_state(state_path)
    items = state["items"]
    existing = items.get(source_id)
    if existing:
        completed = _existing_completed_result(existing)
        if completed:
            progress("Duplicate detected: this source has already been processed.")
            workspace_path = _create_report_workspace(source_id, existing["metadata"], completed.dna_path, progress)
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
        progress("Reading source metadata..." if source.kind == "url" else "Preparing local file metadata...")
        metadata = _metadata_for_source(source)

    sample_path = Path(existing["sample_path"]) if existing and existing.get("sample_path") else None
    if sample_path is None or not sample_path.exists():
        progress("Downloading audio..." if source.kind == "url" else "Normalizing local audio...")
        items[source_id] = {"id": source_id, "metadata": metadata, "stage": "preparing"}
        _save_state(state_path, state)
        sample_path = _normalize_source(source, source_id)
        digest = _sha256(sample_path)
        duplicate = _find_content_duplicate(items, source_id, digest)
        if duplicate:
            items[source_id] = {
                "id": source_id,
                "metadata": metadata,
                "stage": "duplicate",
                "duplicate_of": duplicate["id"],
                "sample_path": str(sample_path),
                "sha256": digest,
            }
            _save_state(state_path, state)
            progress("Duplicate audio detected; analysis was not repeated.")
            return IngestionResult(source_id, "duplicate", metadata["title"], sample_path, None, None)
        items[source_id] = {
            "id": source_id,
            "metadata": metadata,
            "stage": "downloaded",
            "sample_path": str(sample_path),
            "sha256": digest,
        }
        _save_state(state_path, state)

    record = items[source_id]
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

    report_path = reports_directory() / f"{source_id}_summary.txt"
    if not report_path.exists():
        progress("Generating summary report...")
        _write_summary(report_path, source_id, metadata, sample_path, dna_path, dna)

    record["report_path"] = str(report_path)
    record["stage"] = "completed"
    record.pop("error", None)
    _save_state(state_path, state)
    progress("Completed.")
    workspace_path = _create_report_workspace(source_id, metadata, dna_path, progress)
    _publish_completed_analyses(progress)
    return IngestionResult(source_id, "completed", metadata["title"], sample_path, dna_path, report_path, workspace_path)
