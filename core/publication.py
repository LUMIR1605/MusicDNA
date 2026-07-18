"""Private, retryable publication of completed MusicDNA analyses."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable
from urllib.parse import parse_qs, urlparse

from core.paths import (
    data_root,
    ensure_directory,
    ingestion_state_path,
    publication_config_path,
    publication_state_path,
    publication_workspace_directory,
    write_json_atomic,
    write_text_atomic,
)
from core.runtime import RuntimeCapabilityError, require_publication_capabilities


RESEARCH_REPOSITORY_URL = "https://github.com/LUMIR1605/MusicDNA-Research.git"
DEFAULT_CONFIG = {
    "version": 1,
    "enabled": True,
    "repository_url": RESEARCH_REPOSITORY_URL,
    "branch": "main",
}
FOLDER_UNSAFE = re.compile(r"[^A-Za-z0-9._-]+")


class PublicationError(RuntimeError):
    """Raised for a user-actionable private publication failure."""


@dataclass(frozen=True)
class CompletedAnalysis:
    video_id: str
    title: str
    metadata: dict[str, Any]
    dna_path: Path
    summary_path: Path


@dataclass
class PublicationResult:
    published: list[str] = field(default_factory=list)
    already_published: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)
    incomplete: list[str] = field(default_factory=list)
    unmatched: list[str] = field(default_factory=list)
    disabled: bool = False

    @property
    def has_failures(self) -> bool:
        return bool(self.failed or self.incomplete or self.unmatched)


def _root(root: Path | None = None) -> Path:
    return data_root() if root is None else Path(root)


def _config_path(root: Path | None = None) -> Path:
    return publication_config_path() if root is None else _root(root) / "publication" / "config.json"


def _state_path(root: Path | None = None) -> Path:
    return publication_state_path() if root is None else _root(root) / "publication" / "state.json"


def _workspace_path(root: Path | None = None) -> Path:
    return publication_workspace_directory() if root is None else _root(root) / "publication" / "MusicDNA-Research"


def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise PublicationError("MusicDNA publication data is unreadable. Fix it locally and retry.") from error


def load_publication_config(root: Path | None = None) -> dict[str, Any]:
    """Create the local, credential-free publication configuration on first use."""

    path = _config_path(root)
    config = _load_json(path, None)
    if config is None:
        config = dict(DEFAULT_CONFIG)
        write_json_atomic(path, config)
    if not isinstance(config, dict) or not isinstance(config.get("enabled"), bool):
        raise PublicationError("MusicDNA publication configuration has an unsupported format.")
    if not isinstance(config.get("repository_url"), str) or not config["repository_url"]:
        raise PublicationError("MusicDNA publication repository is not configured.")
    if not isinstance(config.get("branch"), str) or not config["branch"]:
        raise PublicationError("MusicDNA publication branch is not configured.")
    return config


def _load_publication_state(root: Path | None = None) -> dict[str, Any]:
    state = _load_json(_state_path(root), {"version": 1, "tracks": {}})
    if not isinstance(state, dict) or not isinstance(state.get("tracks"), dict):
        raise PublicationError("MusicDNA publication state has an unsupported format.")
    return state


def _save_publication_state(state: dict[str, Any], root: Path | None = None) -> None:
    write_json_atomic(_state_path(root), state)


def _video_id_from_url(url: str) -> str | None:
    parsed = urlparse(url)
    host = parsed.netloc.lower().split(":", 1)[0]
    if host in {"youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com"}:
        return parse_qs(parsed.query).get("v", [None])[0]
    if host in {"youtu.be", "www.youtu.be"}:
        return parsed.path.strip("/").split("/", 1)[0] or None
    return None


def _safe_track_name(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    safe = FOLDER_UNSAFE.sub("_", normalized).strip("._-")
    return safe[:80] or "untitled"


def _read_completed_record(video_id: str, record: dict[str, Any]) -> CompletedAnalysis:
    metadata = record.get("metadata")
    if not isinstance(metadata, dict) or metadata.get("id") != video_id:
        raise PublicationError("metadata does not match the completed video ID")
    source_url = metadata.get("webpage_url")
    if not isinstance(source_url, str) or _video_id_from_url(source_url) != video_id:
        raise PublicationError("source metadata does not match the completed video ID")
    dna_path = Path(str(record.get("dna_path", "")))
    summary_path = Path(str(record.get("report_path", "")))
    if not dna_path.is_file() or not summary_path.is_file():
        raise PublicationError("DNA or summary artifact is missing")
    try:
        dna = json.loads(dna_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise PublicationError("DNA artifact is unreadable") from error
    if not isinstance(dna, dict):
        raise PublicationError("DNA artifact has an unsupported format")
    summary = summary_path.read_text(encoding="utf-8")
    summary_url = next((line[13:].strip() for line in summary.splitlines() if line.startswith("YouTube URL:")), "")
    if _video_id_from_url(summary_url) != video_id:
        raise PublicationError("summary does not match the completed video ID")
    title = metadata.get("title")
    if not isinstance(title, str) or not title:
        raise PublicationError("completed analysis has no title")
    return CompletedAnalysis(video_id, title, dict(metadata), dna_path, summary_path)


def discover_completed_analyses(root: Path | None = None) -> tuple[list[CompletedAnalysis], list[str], list[str]]:
    """Find completed, matchable records without modifying local analysis artifacts."""

    state_path = ingestion_state_path() if root is None else _root(root) / "ingestion" / "state.json"
    ingestion_state = _load_json(state_path, {"version": 1, "items": {}})
    if not isinstance(ingestion_state, dict) or not isinstance(ingestion_state.get("items"), dict):
        raise PublicationError("MusicDNA ingestion state has an unsupported format.")

    records: list[CompletedAnalysis] = []
    incomplete: list[str] = []
    referenced: set[Path] = set()
    for video_id, record in ingestion_state["items"].items():
        if not isinstance(video_id, str) or not isinstance(record, dict) or record.get("stage") != "completed":
            continue
        try:
            completed = _read_completed_record(video_id, record)
        except PublicationError as error:
            incomplete.append(f"{video_id}: {error}")
            continue
        records.append(completed)
        referenced.update({completed.dna_path.resolve(), completed.summary_path.resolve()})

    base = _root(root)
    unmatched: list[str] = []
    for directory, pattern in ((base / "dna", "*.json"), (base / "reports", "*_summary.txt")):
        if directory.exists():
            for artifact in directory.glob(pattern):
                if artifact.resolve() not in referenced:
                    unmatched.append(f"{artifact.name}: no completed ingestion record")
    return records, incomplete, unmatched


def _safe_metadata(record: CompletedAnalysis) -> dict[str, Any]:
    return {
        "video_id": record.video_id,
        "title": record.title,
        "source_url": record.metadata["webpage_url"],
        "uploader": record.metadata.get("uploader", ""),
        "duration_seconds": record.metadata.get("duration"),
    }


def _summary_markdown(record: CompletedAnalysis, dna: dict[str, Any]) -> str:
    rhythm = dna.get("rhythm", {}) if isinstance(dna.get("rhythm"), dict) else {}
    bpm = rhythm.get("bpm", {}) if isinstance(rhythm.get("bpm"), dict) else {}
    transients = rhythm.get("transients", {}) if isinstance(rhythm.get("transients"), dict) else {}
    bpm_value = bpm.get("value") if bpm.get("status") == "estimated" else "unavailable"
    return "\n".join(
        [
            "# MusicDNA analysis summary",
            "",
            f"- Title: {record.title}",
            f"- YouTube video ID: {record.video_id}",
            f"- Source URL: {record.metadata['webpage_url']}",
            f"- Transient candidates: {transients.get('count', 'unavailable')}",
            f"- Estimated BPM: {bpm_value}",
            "",
        ]
    )


def _fingerprint(analysis: dict[str, Any], metadata: dict[str, Any], summary: str) -> str:
    digest = hashlib.sha256()
    for value in (analysis, metadata):
        digest.update(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
    digest.update(summary.encode("utf-8"))
    return digest.hexdigest()


def _run_git(arguments: list[str], cwd: Path | None = None) -> str:
    result = subprocess.run(
        ["git", *arguments],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise PublicationError("GitHub publication failed. Check your GitHub sign-in and retry.")
    return result.stdout


def _prepare_repository(config: dict[str, Any], root: Path | None = None) -> Path:
    require_publication_capabilities()
    workspace = _workspace_path(root)
    if not (workspace / ".git").is_dir():
        if workspace.exists() and any(workspace.iterdir()):
            raise PublicationError("MusicDNA publication workspace is not a Git repository.")
        ensure_directory(workspace.parent)
        _run_git(["clone", "--branch", config["branch"], "--single-branch", config["repository_url"], str(workspace)])
    else:
        _run_git(["fetch", "origin"], workspace)
        _run_git(["checkout", config["branch"]], workspace)
        _run_git(["pull", "--ff-only", "origin", config["branch"]], workspace)
    if _run_git(["status", "--porcelain"], workspace).strip():
        raise PublicationError("MusicDNA publication workspace has uncommitted changes.")
    return workspace


def _remote_directory(workspace: Path, record: CompletedAnalysis) -> Path:
    analyses = workspace / "analyses"
    if analyses.exists():
        for candidate in analyses.glob(f"{record.video_id}_*"):
            status_path = candidate / "status.json"
            if status_path.is_file():
                status = _load_json(status_path, {})
                if isinstance(status, dict) and status.get("video_id") == record.video_id:
                    return candidate
    return analyses / f"{record.video_id}_{_safe_track_name(record.title)}"


def _write_package(workspace: Path, record: CompletedAnalysis) -> tuple[Path, str]:
    analysis = _load_json(record.dna_path, None)
    if not isinstance(analysis, dict):
        raise PublicationError("DNA artifact has an unsupported format")
    metadata = _safe_metadata(record)
    summary = _summary_markdown(record, analysis)
    fingerprint = _fingerprint(analysis, metadata, summary)
    directory = _remote_directory(workspace, record)
    status = {
        "version": 1,
        "video_id": record.video_id,
        "ingestion_status": "completed",
        "content_fingerprint": fingerprint,
    }
    if directory.exists():
        existing = _load_json(directory / "status.json", {})
        if isinstance(existing, dict) and existing.get("content_fingerprint") == fingerprint:
            return directory, "unchanged"
    write_json_atomic(directory / "analysis.json", analysis)
    write_json_atomic(directory / "metadata.json", metadata)
    write_json_atomic(directory / "status.json", status)
    write_text_atomic(directory / "summary.md", summary)
    return directory, fingerprint


def _mark_track(state: dict[str, Any], video_id: str, status: str, fingerprint: str | None = None) -> None:
    entry: dict[str, Any] = {"status": status}
    if fingerprint is not None:
        entry["content_fingerprint"] = fingerprint
    state["tracks"][video_id] = entry


def publish_pending_results(
    progress: Callable[[str], None] = print,
    root: Path | None = None,
) -> PublicationResult:
    """Publish every matchable completed analysis, without rerunning analysis or downloads."""

    config = load_publication_config(root)
    records, incomplete, unmatched = discover_completed_analyses(root)
    result = PublicationResult(incomplete=incomplete, unmatched=unmatched)
    if not config["enabled"]:
        result.disabled = True
        progress("Publication disabled.")
        return result

    state = _load_publication_state(root)
    if not records:
        _save_publication_state(state, root)
        return result
    try:
        workspace = _prepare_repository(config, root)
    except (PublicationError, RuntimeCapabilityError):
        for record in records:
            _mark_track(state, record.video_id, "failed")
            result.failed.append(record.video_id)
        _save_publication_state(state, root)
        progress("Publication failed. Completed analyses remain local and can be retried.")
        return result

    changed: list[tuple[str, str]] = []
    for record in records:
        try:
            directory, fingerprint = _write_package(workspace, record)
        except PublicationError:
            _mark_track(state, record.video_id, "failed")
            result.failed.append(record.video_id)
            continue
        if fingerprint == "unchanged":
            _mark_track(state, record.video_id, "published")
            result.already_published.append(record.video_id)
            progress(f"Already published: {record.video_id}")
        else:
            changed.append((record.video_id, fingerprint))
            progress(f"Prepared for publication: {record.video_id}")

    if changed:
        try:
            _run_git(["add", "--", "analyses"], workspace)
            if _run_git(["status", "--porcelain", "--", "analyses"], workspace).strip():
                _run_git(["commit", "-m", f"Publish MusicDNA analyses: {', '.join(video_id for video_id, _ in changed)}"], workspace)
                _run_git(["push", "origin", config["branch"]], workspace)
            for video_id, fingerprint in changed:
                _mark_track(state, video_id, "published", fingerprint)
                result.published.append(video_id)
                progress(f"Published: {video_id}")
        except PublicationError:
            for video_id, _ in changed:
                _mark_track(state, video_id, "failed")
                result.failed.append(video_id)
            progress("Publication failed. Completed analyses remain local and can be retried.")

    _save_publication_state(state, root)
    return result


def publication_status_label(root: Path | None = None) -> str:
    """Return one launcher-safe, user-visible publication status."""

    config = load_publication_config(root)
    if not config["enabled"]:
        return "Publication disabled"
    state = _load_publication_state(root)
    statuses = [entry.get("status") for entry in state["tracks"].values() if isinstance(entry, dict)]
    if "failed" in statuses:
        return "Publication failed"
    records, incomplete, unmatched = discover_completed_analyses(root)
    if incomplete or unmatched or any(state["tracks"].get(record.video_id, {}).get("status") != "published" for record in records):
        return "Pending publication"
    return "Publication enabled"
