from __future__ import annotations

import json
from pathlib import Path

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
