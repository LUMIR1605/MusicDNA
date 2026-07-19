"""Safe, human-friendly desktop workspaces for completed MusicDNA analyses."""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.paths import desktop_reports_directory, ensure_directory, write_json_atomic, write_text_atomic


FOLDER_UNSAFE = re.compile(r"[^A-Za-z0-9._-]+")
VIDEO_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{11}$")
PACKAGE_VERSION = "musicdna-analysis-package-v1"
PACKAGE_FILES = ("summary.md", "analysis_package.json", "metadata.json")
PRIVATE_FIELD_NAMES = frozenset(
    {
        "sample_path",
        "dna_path",
        "report_path",
        "temp_path",
        "log_path",
        "local_path",
        "credentials",
        "credential",
        "token",
    }
)


class ReportWorkspaceError(RuntimeError):
    """Raised when a desktop report workspace cannot be safely prepared."""


@dataclass(frozen=True)
class ReportWorkspace:
    """Paths exposed to the launcher after a report workspace is synchronized."""

    directory: Path
    summary_path: Path
    package_path: Path
    metadata_path: Path


def safe_track_name(value: str) -> str:
    """Return an ASCII-safe folder component derived from the source title."""

    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    safe = FOLDER_UNSAFE.sub("_", normalized).strip("._-")
    return safe[:80] or "untitled"


def _snapshot_package(directory: Path) -> dict[str, bytes | None]:
    return {
        name: (path.read_bytes() if (path := directory / name).is_file() else None)
        for name in PACKAGE_FILES
    }


def _is_link_or_junction(path: Path) -> bool:
    is_junction = getattr(path, "is_junction", None)
    return path.is_symlink() or (bool(is_junction()) if is_junction is not None else False)


def _reject_unexpected_entries(directory: Path) -> None:
    """Keep each track workspace a controlled package, without deleting user files."""

    if _is_link_or_junction(directory) or not directory.is_dir():
        raise ReportWorkspaceError("The report workspace target is not a directory.")
    unexpected = []
    for entry in directory.iterdir():
        if _is_link_or_junction(entry) or not entry.is_file() or entry.name not in PACKAGE_FILES:
            unexpected.append(entry.name)
    if unexpected:
        raise ReportWorkspaceError(
            "The report folder contains unexpected files and was left unchanged."
        )


def is_valid_report_workspace(directory: Path | None) -> bool:
    """Return whether a workspace contains exactly the controlled report package."""

    if directory is None:
        return False
    path = Path(directory)
    try:
        _reject_unexpected_entries(path)
    except (OSError, ReportWorkspaceError):
        return False
    return {entry.name for entry in path.iterdir()} == set(PACKAGE_FILES)


def _restore_package(directory: Path, previous: dict[str, bytes | None]) -> None:
    for name, content in previous.items():
        path = directory / name
        if content is None:
            if path.is_file():
                path.unlink()
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    if directory.exists() and not any(directory.iterdir()):
        directory.rmdir()


def _safe_metadata(metadata: dict[str, Any], video_id: str) -> dict[str, Any]:
    source_url = metadata.get("webpage_url")
    if not isinstance(source_url, str) or not source_url:
        raise ReportWorkspaceError("The completed analysis has no source URL.")
    title = metadata.get("title")
    if not isinstance(title, str) or not title:
        raise ReportWorkspaceError("The completed analysis has no track title.")
    uploader = metadata.get("uploader")
    duration = metadata.get("duration")
    return {
        "video_id": video_id,
        "title": title,
        "source_url": source_url,
        "uploader": uploader if isinstance(uploader, str) else "",
        "duration_seconds": duration if isinstance(duration, (int, float)) and not isinstance(duration, bool) else None,
    }


def _reject_private_dna_fields(value: Any) -> None:
    """Refuse a desktop export when a validated artifact carries local-only data."""

    if isinstance(value, dict):
        for key, item in value.items():
            if isinstance(key, str) and key.lower() in PRIVATE_FIELD_NAMES:
                raise ReportWorkspaceError("The completed DNA artifact contains private local data.")
            _reject_private_dna_fields(item)
    elif isinstance(value, list):
        for item in value:
            _reject_private_dna_fields(item)


def _summary_markdown(metadata: dict[str, Any], dna: dict[str, Any]) -> str:
    rhythm = dna.get("rhythm") if isinstance(dna.get("rhythm"), dict) else {}
    bpm = rhythm.get("bpm") if isinstance(rhythm.get("bpm"), dict) else {}
    transients = rhythm.get("transients") if isinstance(rhythm.get("transients"), dict) else {}
    bpm_value = bpm.get("value") if bpm.get("status") == "estimated" else "unavailable"
    return "\n".join(
        [
            "# MusicDNA report",
            "",
            f"- Title: {metadata['title']}",
            f"- YouTube video ID: {metadata['video_id']}",
            f"- Source URL: {metadata['source_url']}",
            f"- Transient candidates: {transients.get('count', 'unavailable')}",
            f"- Estimated BPM: {bpm_value}",
            "",
        ]
    )


def create_report_workspace(
    video_id: str,
    metadata: dict[str, Any],
    dna: dict[str, Any],
    *,
    workspace_root: Path | None = None,
    analysis_timestamp: str | None = None,
) -> ReportWorkspace:
    """Synchronize one safe desktop report folder without moving local artifacts."""

    if not isinstance(video_id, str) or not VIDEO_ID_PATTERN.fullmatch(video_id):
        raise ReportWorkspaceError("The completed analysis has an invalid video ID.")
    if not isinstance(dna, dict):
        raise ReportWorkspaceError("The completed DNA artifact is unreadable.")

    safe_metadata = _safe_metadata(metadata, video_id)
    _reject_private_dna_fields(dna)
    root = desktop_reports_directory() if workspace_root is None else Path(workspace_root)
    directory = root / f"{video_id}_{safe_track_name(safe_metadata['title'])}"
    if directory.exists():
        _reject_unexpected_entries(directory)
    previous = _snapshot_package(directory) if directory.is_dir() else {name: None for name in PACKAGE_FILES}
    try:
        ensure_directory(directory)
        _reject_unexpected_entries(directory)
    except OSError as error:
        raise ReportWorkspaceError("The report workspace target cannot be created.") from error
    timestamp = analysis_timestamp or datetime.now(timezone.utc).isoformat()
    schema_version = dna.get("schema_version")
    package = {
        "package_version": PACKAGE_VERSION,
        "schema_version": schema_version if isinstance(schema_version, str) else "unknown",
        "analysis_timestamp": timestamp,
        "source_url": safe_metadata["source_url"],
        "ingestion_status": "completed",
        "metadata": safe_metadata,
        "dna": dna,
    }
    summary_path = directory / "summary.md"
    package_path = directory / "analysis_package.json"
    metadata_path = directory / "metadata.json"
    try:
        write_text_atomic(summary_path, _summary_markdown(safe_metadata, dna))
        write_json_atomic(package_path, package)
        write_json_atomic(metadata_path, safe_metadata)
    except (OSError, TypeError, ValueError) as error:
        try:
            _restore_package(directory, previous)
        except OSError as rollback_error:
            raise ReportWorkspaceError(
                "The report workspace could not be restored after a write failure."
            ) from rollback_error
        raise ReportWorkspaceError("The report workspace could not be written safely.") from error
    return ReportWorkspace(directory, summary_path, package_path, metadata_path)
