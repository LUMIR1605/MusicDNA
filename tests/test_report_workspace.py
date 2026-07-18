from __future__ import annotations

import json
from pathlib import Path

from core.paths import desktop_directory, desktop_reports_directory
from core.report_workspace import PACKAGE_VERSION, create_report_workspace


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
