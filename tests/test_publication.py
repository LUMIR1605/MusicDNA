from __future__ import annotations

import json
from pathlib import Path

import pytest

from core import publication
from core.paths import write_json_atomic, write_text_atomic


TRACKS = {
    "gSXJVMU3OFk": "Waiting All Night",
    "-yOZEiHLuVU": "Now We Are Free",
    "qMYI9xLu8dA": "Take Me Away",
}


def _seed_completed_records(root: Path) -> None:
    items = {}
    for video_id, title in TRACKS.items():
        dna_path = root / "dna" / f"{video_id}.json"
        report_path = root / "reports" / f"{video_id}_summary.txt"
        write_json_atomic(
            dna_path,
            {
                "schema_version": "dna-output-v1",
                "rhythm": {
                    "transients": {"count": 7},
                    "bpm": {"status": "estimated", "value": 120.0},
                },
            },
        )
        write_text_atomic(
            report_path,
            "\n".join(
                [
                    "MusicDNA ingestion summary",
                    f"Title: {title}",
                    f"YouTube URL: https://www.youtube.com/watch?v={video_id}",
                    f"Sample: {root / 'samples' / (video_id + '.wav')}",
                ]
            ),
        )
        items[video_id] = {
            "id": video_id,
            "stage": "completed",
            "metadata": {
                "id": video_id,
                "title": title,
                "webpage_url": f"https://www.youtube.com/watch?v={video_id}",
                "uploader": "Test uploader",
                "duration": 120,
            },
            "sample_path": str(root / "samples" / f"{video_id}.wav"),
            "dna_path": str(dna_path),
            "report_path": str(report_path),
        }
    write_json_atomic(root / "ingestion" / "state.json", {"version": 1, "items": items})


def _mock_repository(monkeypatch, root: Path):
    workspace = root / "publication" / "MusicDNA-Research"
    workspace.mkdir(parents=True)
    calls: list[list[str]] = []

    monkeypatch.setattr(publication, "require_publication_capabilities", lambda: None)
    monkeypatch.setattr(publication, "_prepare_repository", lambda _config, _root=None: workspace)

    def run_git(arguments: list[str], _cwd=None) -> str:
        calls.append(arguments)
        if arguments[:2] == ["status", "--porcelain"]:
            return " M analyses"
        return ""

    monkeypatch.setattr(publication, "_run_git", run_git)
    monkeypatch.setattr(
        publication,
        "_remote_package_fingerprint",
        lambda _workspace, _branch, directory: json.loads(
            (directory / "status.json").read_text(encoding="utf-8")
        ).get("content_fingerprint"),
    )
    return workspace, calls


def test_first_use_creates_credential_free_local_config(tmp_path: Path):
    config = publication.load_publication_config(tmp_path)
    content = (tmp_path / "publication" / "config.json").read_text(encoding="utf-8").lower()

    assert config["enabled"] is True
    assert config["repository_url"] == publication.RESEARCH_REPOSITORY_URL
    assert "token" not in content
    assert "password" not in content


def test_backfill_publishes_completed_records_without_media_or_local_paths(monkeypatch, tmp_path: Path):
    _seed_completed_records(tmp_path)
    workspace, calls = _mock_repository(monkeypatch, tmp_path)

    result = publication.publish_pending_results(lambda _message: None, tmp_path)

    assert result.published == list(TRACKS)
    assert not result.has_failures
    for video_id in TRACKS:
        folders = list((workspace / "analyses").glob(f"{video_id}_*"))
        assert len(folders) == 1
        package = folders[0]
        assert {item.name for item in package.iterdir()} == {
            "analysis.json",
            "metadata.json",
            "status.json",
            "summary.md",
        }
        for item in package.iterdir():
            assert item.suffix not in {".wav", ".mp3", ".log", ".tmp"}
            assert str(tmp_path) not in item.read_text(encoding="utf-8")
    assert any(call[:2] == ["commit", "-m"] for call in calls)
    assert any(call[:2] == ["push", "origin"] for call in calls)


def test_backfill_skips_already_published_records(monkeypatch, tmp_path: Path):
    _seed_completed_records(tmp_path)
    _mock_repository(monkeypatch, tmp_path)
    first = publication.publish_pending_results(lambda _message: None, tmp_path)
    second = publication.publish_pending_results(lambda _message: None, tmp_path)

    assert first.published == list(TRACKS)
    assert second.already_published == list(TRACKS)
    assert not second.published


def test_discovery_reports_unmatched_or_incomplete_records(tmp_path: Path):
    _seed_completed_records(tmp_path)
    state_path = tmp_path / "ingestion" / "state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["items"]["gSXJVMU3OFk"]["report_path"] = str(tmp_path / "reports" / "missing.txt")
    write_json_atomic(state_path, state)
    write_json_atomic(tmp_path / "dna" / "orphan.json", {"schema_version": "dna-output-v1"})

    records, incomplete, unmatched = publication.discover_completed_analyses(tmp_path)

    assert {record.video_id for record in records} == {"-yOZEiHLuVU", "qMYI9xLu8dA"}
    assert any(item.startswith("gSXJVMU3OFk:") for item in incomplete)
    assert any(item.startswith("orphan.json:") for item in unmatched)


def test_launcher_status_distinguishes_enabled_pending_disabled_and_failed(tmp_path: Path):
    _seed_completed_records(tmp_path)
    assert publication.publication_status_label(tmp_path) == "Pending publication"

    config_path = tmp_path / "publication" / "config.json"
    write_json_atomic(config_path, {**publication.DEFAULT_CONFIG, "enabled": False})
    assert publication.publication_status_label(tmp_path) == "Publication disabled"

    write_json_atomic(config_path, publication.DEFAULT_CONFIG)
    write_json_atomic(
        tmp_path / "publication" / "state.json",
        {"version": 1, "tracks": {"gSXJVMU3OFk": {"status": "failed"}}},
    )
    assert publication.publication_status_label(tmp_path) == "Publication failed"


def _relation_git(monkeypatch, workspace: Path, initial_relation: str):
    """Mock the Git state machine used by repository preparation."""

    state = {"relation": initial_relation}
    calls: list[list[str]] = []
    workspace.mkdir(parents=True, exist_ok=True)
    (workspace / ".git").mkdir()
    monkeypatch.setattr(publication, "require_publication_capabilities", lambda: None)

    def run_git(arguments: list[str], _cwd=None) -> str:
        calls.append(arguments)
        if arguments[:2] == ["status", "--porcelain"]:
            return " M analyses" if state["relation"] == "dirty" else ""
        if arguments[0] == "rev-list":
            return {
                "synchronized": "0 0",
                "ahead": "0 1",
                "remote_ahead": "1 0",
                "diverged": "1 1",
            }[state["relation"]]
        if arguments[0] in {"push", "pull"}:
            state["relation"] = "synchronized"
        return ""

    monkeypatch.setattr(publication, "_run_git", run_git)
    return calls


def test_prepare_repository_retries_clean_local_branch_ahead(monkeypatch, tmp_path: Path):
    workspace = tmp_path / "publication" / "MusicDNA-Research"
    calls = _relation_git(monkeypatch, workspace, "ahead")

    assert publication._prepare_repository(publication.DEFAULT_CONFIG, tmp_path) == workspace
    assert ["push", "origin", "main"] in calls


def test_prepare_repository_handles_remote_ahead_and_dirty_workspace(monkeypatch, tmp_path: Path):
    workspace = tmp_path / "publication" / "MusicDNA-Research"
    calls = _relation_git(monkeypatch, workspace, "remote_ahead")

    assert publication._prepare_repository(publication.DEFAULT_CONFIG, tmp_path) == workspace
    assert ["pull", "--ff-only", "origin", "main"] in calls

    dirty_workspace = tmp_path / "dirty" / "MusicDNA-Research"
    _relation_git(monkeypatch, dirty_workspace, "dirty")
    monkeypatch.setattr(publication, "_workspace_path", lambda _root=None: dirty_workspace)
    with pytest.raises(publication.PublicationError, match="uncommitted changes"):
        publication._prepare_repository(publication.DEFAULT_CONFIG, tmp_path)


def test_prepare_repository_rejects_diverged_workspace(monkeypatch, tmp_path: Path):
    workspace = tmp_path / "publication" / "MusicDNA-Research"
    _relation_git(monkeypatch, workspace, "diverged")

    with pytest.raises(publication.PublicationError, match="diverged"):
        publication._prepare_repository(publication.DEFAULT_CONFIG, tmp_path)


def test_push_failure_after_commit_keeps_local_commit_and_marks_tracks_failed(monkeypatch, tmp_path: Path):
    _seed_completed_records(tmp_path)
    workspace = tmp_path / "publication" / "MusicDNA-Research"
    workspace.mkdir(parents=True)
    calls: list[list[str]] = []

    monkeypatch.setattr(publication, "_prepare_repository", lambda _config, _root=None: workspace)

    def run_git(arguments: list[str], _cwd=None) -> str:
        calls.append(arguments)
        if arguments[:2] == ["status", "--porcelain"]:
            return " M analyses" if len(arguments) > 2 else ""
        if arguments[0] == "push":
            raise publication.PublicationError("push failed")
        return ""

    monkeypatch.setattr(publication, "_run_git", run_git)
    result = publication.publish_pending_results(lambda _message: None, tmp_path)

    assert not result.published
    assert result.failed == list(TRACKS)
    assert any(call[0] == "commit" for call in calls)
    assert (workspace / "analyses").exists()
    state = json.loads((tmp_path / "publication" / "state.json").read_text(encoding="utf-8"))
    assert {entry["status"] for entry in state["tracks"].values()} == {"failed"}


def test_retry_pushes_existing_local_commit_without_creating_another(monkeypatch, tmp_path: Path):
    _seed_completed_records(tmp_path)
    workspace = tmp_path / "publication" / "MusicDNA-Research"
    workspace.mkdir(parents=True)
    records, _incomplete, _unmatched = publication.discover_completed_analyses(tmp_path)
    transaction = publication._PackageTransaction(workspace)
    for record in records:
        publication._write_package(workspace, record, transaction)

    calls = _relation_git(monkeypatch, workspace, "ahead")

    def remote_fingerprint(_workspace, _branch, directory):
        return json.loads((directory / "status.json").read_text(encoding="utf-8"))["content_fingerprint"]

    monkeypatch.setattr(publication, "_remote_package_fingerprint", remote_fingerprint)
    result = publication.publish_pending_results(lambda _message: None, tmp_path)

    assert result.already_published == list(TRACKS)
    assert not result.published
    assert ["push", "origin", "main"] in calls
    assert not any(call[0] == "commit" for call in calls)


def test_unchanged_local_package_is_not_published_without_remote_match(monkeypatch, tmp_path: Path):
    _seed_completed_records(tmp_path)
    workspace = tmp_path / "publication" / "MusicDNA-Research"
    workspace.mkdir(parents=True)
    records, _incomplete, _unmatched = publication.discover_completed_analyses(tmp_path)
    transaction = publication._PackageTransaction(workspace)
    for record in records:
        publication._write_package(workspace, record, transaction)

    monkeypatch.setattr(publication, "_prepare_repository", lambda _config, _root=None: workspace)
    monkeypatch.setattr(publication, "_remote_package_fingerprint", lambda *_args: None)
    result = publication.publish_pending_results(lambda _message: None, tmp_path)

    assert not result.published
    assert not result.already_published
    assert result.failed == list(TRACKS)


def test_commit_failure_restores_generated_package_files(monkeypatch, tmp_path: Path):
    _seed_completed_records(tmp_path)
    workspace = tmp_path / "publication" / "MusicDNA-Research"
    workspace.mkdir(parents=True)

    monkeypatch.setattr(publication, "_prepare_repository", lambda _config, _root=None: workspace)

    def run_git(arguments: list[str], _cwd=None) -> str:
        if arguments[:2] == ["status", "--porcelain"]:
            return " M analyses" if len(arguments) > 2 else ""
        if arguments[0] == "commit":
            raise publication.PublicationError("commit failed")
        return ""

    monkeypatch.setattr(publication, "_run_git", run_git)
    result = publication.publish_pending_results(lambda _message: None, tmp_path)

    assert result.failed == list(TRACKS)
    assert not list((workspace / "analyses").rglob("*"))


def test_dirty_workspace_failure_marks_completed_tracks_failed(monkeypatch, tmp_path: Path):
    _seed_completed_records(tmp_path)
    monkeypatch.setattr(
        publication,
        "_prepare_repository",
        lambda _config, _root=None: (_ for _ in ()).throw(
            publication.PublicationError("workspace has uncommitted changes")
        ),
    )

    result = publication.publish_pending_results(lambda _message: None, tmp_path)

    assert result.failed == list(TRACKS)
    assert not result.published


def test_package_write_failure_restores_recoverable_workspace(monkeypatch, tmp_path: Path):
    _seed_completed_records(tmp_path)
    workspace = tmp_path / "publication" / "MusicDNA-Research"
    workspace.mkdir(parents=True)
    publication.load_publication_config(tmp_path)
    monkeypatch.setattr(publication, "_prepare_repository", lambda _config, _root=None: workspace)

    original_write = publication.write_json_atomic

    def fail_write(path, *args, **kwargs):
        if Path(path).name == "analysis.json":
            raise OSError("disk unavailable")
        return original_write(path, *args, **kwargs)

    monkeypatch.setattr(publication, "write_json_atomic", fail_write)
    result = publication.publish_pending_results(lambda _message: None, tmp_path)

    assert result.failed == list(TRACKS)
    assert not (workspace / "analyses").exists()


def test_repeated_successful_retry_is_idempotent_after_remote_verification(monkeypatch, tmp_path: Path):
    _seed_completed_records(tmp_path)
    _mock_repository(monkeypatch, tmp_path)

    first = publication.publish_pending_results(lambda _message: None, tmp_path)
    second = publication.publish_pending_results(lambda _message: None, tmp_path)

    assert first.published == list(TRACKS)
    assert second.already_published == list(TRACKS)
    assert not second.failed
