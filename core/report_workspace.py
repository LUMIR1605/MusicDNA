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
PACKAGE_VERSION = "musicdna-analysis-package-v1"


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


def _safe_metadata(metadata: dict[str, Any], video_id: str) -> dict[str, Any]:
    source_url = metadata.get("webpage_url")
    if not isinstance(source_url, str) or not source_url:
        raise ReportWorkspaceError("The completed analysis has no source URL.")
    title = metadata.get("title")
    if not isinstance(title, str) or not title:
        raise ReportWorkspaceError("The completed analysis has no track title.")
    return {
        "video_id": video_id,
        "title": title,
        "source_url": source_url,
        "uploader": metadata.get("uploader", ""),
        "duration_seconds": metadata.get("duration"),
    }


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

    if not isinstance(video_id, str) or not video_id:
        raise ReportWorkspaceError("The completed analysis has no video ID.")
    if not isinstance(dna, dict):
        raise ReportWorkspaceError("The completed DNA artifact is unreadable.")

    safe_metadata = _safe_metadata(metadata, video_id)
    root = desktop_reports_directory() if workspace_root is None else Path(workspace_root)
    directory = ensure_directory(root / f"{video_id}_{safe_track_name(safe_metadata['title'])}")
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
    write_text_atomic(summary_path, _summary_markdown(safe_metadata, dna))
    write_json_atomic(package_path, package)
    write_json_atomic(metadata_path, safe_metadata)
    return ReportWorkspace(directory, summary_path, package_path, metadata_path)
