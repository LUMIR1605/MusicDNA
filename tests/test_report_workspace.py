from __future__ import annotations

import json
from pathlib import Path

import pytest

from core import paths
from core.paths import desktop_directory, desktop_reports_directory
from core.report_workspace import (
    PACKAGE_VERSION,
    ReportWorkspaceError,
    create_report_workspace,
    is_valid_report_workspace,
)


VIDEO_ID = "dQw4w9WgXcQ"


def _metadata() -> dict[str, object]:
    return {
        "id": VIDEO_ID,
        "title": "Example / Song: Test",
        "webpage_url": f"https://www.youtube.com/watch?v={VIDEO_ID}",
        "uploader": "MusicDNA tests",
        "duration": 120,
    }


def _dna(bpm: float = 120.0) -> dict[str, object]:
    return {
        "schema_version": "dna-output-v1",
        "rhythm": {
            "transients": {"count": 4},
            "bpm": {"status": "estimated", "value": bpm},
        },
    }


def test_desktop_path_detection_uses_windows_user_profile(tmp_path: Path):
    desktop = desktop_directory(
        environ={"USERPROFILE": str(tmp_path / "profile")},
        home=tmp_path / "home",
        platform_name="win32",
    )

    assert desktop == tmp_path / "profile" / "Desktop"


def test_desktop_path_uses_configured_windows_redirection(monkeypatch, tmp_path: Path):
    redirected = tmp_path / "OneDrive" / "Desktop"
    monkeypatch.setattr(paths, "_windows_desktop_from_registry", lambda: redirected)

    assert desktop_directory(home=tmp_path / "home", platform_name="win32") == redirected


def test_invalid_windows_desktop_registry_value_uses_profile_fallback(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(paths, "_windows_desktop_from_registry", lambda: None)
    monkeypatch.setattr(paths.os, "environ", {"USERPROFILE": str(tmp_path / "profile")})

    desktop = desktop_directory(
        home=tmp_path / "home",
        platform_name="win32",
    )

    assert desktop == tmp_path / "profile" / "Desktop"


def test_first_report_creates_safe_desktop_package(tmp_path: Path):
    root = tmp_path / "Desktop" / "MusicDNA Reports"

    workspace = create_report_workspace(
        VIDEO_ID,
        _metadata(),
        _dna(),
        workspace_root=root,
        analysis_timestamp="2026-07-19T12:00:00+00:00",
    )

    assert workspace.directory == root / f"{VIDEO_ID}_Example_Song_Test"
    assert {item.name for item in workspace.directory.iterdir()} == {
        "summary.md",
        "analysis_package.json",
        "metadata.json",
    }
    package = json.loads(workspace.package_path.read_text(encoding="utf-8"))
    assert package["package_version"] == PACKAGE_VERSION
    assert package["schema_version"] == "dna-output-v1"
    assert package["ingestion_status"] == "completed"
    assert package["metadata"]["video_id"] == VIDEO_ID
    assert "Sample:" not in workspace.summary_path.read_text(encoding="utf-8")


def test_existing_report_folder_updates_without_duplicate(tmp_path: Path):
    root = tmp_path / "Desktop" / "MusicDNA Reports"
    first = create_report_workspace(VIDEO_ID, _metadata(), _dna(), workspace_root=root)
    second = create_report_workspace(VIDEO_ID, _metadata(), _dna(128.0), workspace_root=root)

    assert first.directory == second.directory
    assert len(list(root.iterdir())) == 1
    package = json.loads(second.package_path.read_text(encoding="utf-8"))
    assert package["dna"]["rhythm"]["bpm"]["value"] == 128.0
    assert is_valid_report_workspace(second.directory)


def test_missing_desktop_uses_local_data_fallback(tmp_path: Path):
    missing_desktop = tmp_path / "missing-desktop"
    root = desktop_reports_directory(missing_desktop, tmp_path / "data")

    workspace = create_report_workspace(VIDEO_ID, _metadata(), _dna(), workspace_root=root)

    assert workspace.directory.parent == tmp_path / "data" / "reports-workspace"
    assert workspace.directory.exists()


def test_workspace_never_copies_media_or_internal_paths(tmp_path: Path):
    root = tmp_path / "Desktop" / "MusicDNA Reports"
    source_media = tmp_path / "samples" / "private.wav"
    source_media.parent.mkdir(parents=True)
    source_media.write_bytes(b"audio")

    workspace = create_report_workspace(VIDEO_ID, _metadata(), _dna(), workspace_root=root)

    assert not any(path.suffix.lower() in {".wav", ".mp3"} for path in workspace.directory.iterdir())
    text = "\n".join(item.read_text(encoding="utf-8") for item in workspace.directory.iterdir())
    assert str(source_media) not in text
    for forbidden in ("sample_path", "dna_path", "report_path", "token", "credential", "launcher-errors.log"):
        assert forbidden not in text


def test_workspace_rejects_private_dna_or_arbitrary_metadata_paths(tmp_path: Path):
    root = tmp_path / "Desktop" / "MusicDNA Reports"
    metadata = {**_metadata(), "sample_path": r"C:\\Users\\private.wav", "uploader": {"path": r"C:\\Users"}}
    dna = {**_dna(), "audio": {"sample_path": r"C:\\Users\\private.wav"}}

    with pytest.raises(ReportWorkspaceError, match="private local data"):
        create_report_workspace(VIDEO_ID, metadata, dna, workspace_root=root)

    workspace = create_report_workspace(VIDEO_ID, metadata, _dna(), workspace_root=root)
    package = json.loads(workspace.package_path.read_text(encoding="utf-8"))
    assert "sample_path" not in package["metadata"]
    assert package["metadata"]["uploader"] == ""


def test_unsafe_video_id_and_title_cannot_escape_workspace(tmp_path: Path):
    root = tmp_path / "Desktop" / "MusicDNA Reports"
    unsafe_metadata = {**_metadata(), "title": "../../outside\\report"}

    with pytest.raises(ReportWorkspaceError, match="invalid video ID"):
        create_report_workspace("../../outside", unsafe_metadata, _dna(), workspace_root=root)

    workspace = create_report_workspace(VIDEO_ID, unsafe_metadata, _dna(), workspace_root=root)
    assert workspace.directory.parent == root
    assert ".." not in workspace.directory.name


def test_partial_write_failure_restores_existing_package(monkeypatch, tmp_path: Path):
    root = tmp_path / "Desktop" / "MusicDNA Reports"
    workspace = create_report_workspace(VIDEO_ID, _metadata(), _dna(), workspace_root=root)
    original = workspace.package_path.read_text(encoding="utf-8")

    def fail_metadata(*_args, **_kwargs):
        raise OSError("disk unavailable")

    monkeypatch.setattr("core.report_workspace.write_json_atomic", fail_metadata)
    with pytest.raises(ReportWorkspaceError, match="could not be written safely"):
        create_report_workspace(VIDEO_ID, _metadata(), _dna(128.0), workspace_root=root)

    assert workspace.package_path.read_text(encoding="utf-8") == original
    assert workspace.summary_path.exists()
    assert workspace.metadata_path.exists()


def test_existing_file_collision_is_rejected(tmp_path: Path):
    root = tmp_path / "Desktop" / "MusicDNA Reports"
    target = root / f"{VIDEO_ID}_Example_Song_Test"
    target.parent.mkdir(parents=True)
    target.write_text("not a directory", encoding="utf-8")

    with pytest.raises(ReportWorkspaceError, match="target is not a directory"):
        create_report_workspace(VIDEO_ID, _metadata(), _dna(), workspace_root=root)


def test_existing_workspace_symlink_is_rejected(tmp_path: Path):
    root = tmp_path / "Desktop" / "MusicDNA Reports"
    target = root / f"{VIDEO_ID}_Example_Song_Test"
    outside = tmp_path / "outside"
    outside.mkdir()
    target.parent.mkdir(parents=True)
    try:
        target.symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("This Windows environment does not permit symbolic links.")

    with pytest.raises(ReportWorkspaceError, match="target is not a directory"):
        create_report_workspace(VIDEO_ID, _metadata(), _dna(), workspace_root=root)
    assert not tuple(outside.iterdir())


@pytest.mark.parametrize(
    ("name", "content"),
    [
        ("stale.mp3", b"media"),
        ("stale.wav", b"media"),
        ("launcher-errors.log", b"log"),
        ("notes.txt", b"unrelated"),
    ],
)
def test_unexpected_file_rejects_refresh_without_changing_existing_package(
    tmp_path: Path, name: str, content: bytes
):
    root = tmp_path / "Desktop" / "MusicDNA Reports"
    workspace = create_report_workspace(VIDEO_ID, _metadata(), _dna(), workspace_root=root)
    before = {entry.name: entry.read_bytes() for entry in workspace.directory.iterdir()}
    stale = workspace.directory / name
    stale.write_bytes(content)

    with pytest.raises(ReportWorkspaceError, match="contains unexpected files"):
        create_report_workspace(VIDEO_ID, _metadata(), _dna(128.0), workspace_root=root)

    after = {entry.name: entry.read_bytes() for entry in workspace.directory.iterdir()}
    assert after == {**before, name: content}
    assert not is_valid_report_workspace(workspace.directory)


def test_nested_directory_rejects_refresh_without_deleting_it(tmp_path: Path):
    root = tmp_path / "Desktop" / "MusicDNA Reports"
    workspace = create_report_workspace(VIDEO_ID, _metadata(), _dna(), workspace_root=root)
    nested = workspace.directory / "cache"
    nested.mkdir()
    (nested / "artifact.txt").write_text("keep", encoding="utf-8")

    with pytest.raises(ReportWorkspaceError, match="contains unexpected files"):
        create_report_workspace(VIDEO_ID, _metadata(), _dna(128.0), workspace_root=root)

    assert (nested / "artifact.txt").read_text(encoding="utf-8") == "keep"
    assert not is_valid_report_workspace(workspace.directory)


def test_symlink_entry_rejects_refresh_without_touching_target(tmp_path: Path):
    root = tmp_path / "Desktop" / "MusicDNA Reports"
    workspace = create_report_workspace(VIDEO_ID, _metadata(), _dna(), workspace_root=root)
    outside = tmp_path / "outside.txt"
    outside.write_text("keep", encoding="utf-8")
    link = workspace.directory / "outside-link.txt"
    try:
        link.symlink_to(outside)
    except OSError:
        pytest.skip("This Windows environment does not permit symbolic links.")

    with pytest.raises(ReportWorkspaceError, match="contains unexpected files"):
        create_report_workspace(VIDEO_ID, _metadata(), _dna(128.0), workspace_root=root)

    assert outside.read_text(encoding="utf-8") == "keep"
    assert link.is_symlink()
    assert not is_valid_report_workspace(workspace.directory)


def test_first_write_failure_leaves_no_partial_required_package(monkeypatch, tmp_path: Path):
    root = tmp_path / "Desktop" / "MusicDNA Reports"

    def fail_package(*_args, **_kwargs):
        raise OSError("disk unavailable")

    monkeypatch.setattr("core.report_workspace.write_json_atomic", fail_package)
    with pytest.raises(ReportWorkspaceError, match="could not be written safely"):
        create_report_workspace(VIDEO_ID, _metadata(), _dna(), workspace_root=root)

    target = root / f"{VIDEO_ID}_Example_Song_Test"
    assert not target.exists()
