from __future__ import annotations

from pathlib import Path

import musicdna_launcher


def test_close_decision_allows_idle_launcher_to_close():
    assert musicdna_launcher.can_close_launcher(job_running=False)


def test_close_decision_keeps_active_job_open_by_default():
    assert not musicdna_launcher.can_close_launcher(job_running=True)


def test_close_decision_allows_explicit_active_job_cancellation():
    assert musicdna_launcher.can_close_launcher(job_running=True, cancellation_confirmed=True)


def test_open_report_uses_windows_default_handler(monkeypatch, tmp_path: Path):
    report = tmp_path / "summary.txt"
    report.write_text("summary", encoding="utf-8")
    opened: list[str] = []

    monkeypatch.setattr(musicdna_launcher.sys, "platform", "win32")
    monkeypatch.setattr(musicdna_launcher.os, "startfile", opened.append, raising=False)

    musicdna_launcher.open_report(report)

    assert opened == [str(report.resolve())]


def test_batch_launcher_uses_repository_relative_gui_entry_point():
    launcher = Path(__file__).resolve().parents[1] / "START_MUSICDNA.bat"
    content = launcher.read_text(encoding="utf-8")

    assert "MUSICDNA_ROOT=%~dp0" in content
    assert "pythonw" in content
    assert "START_MUSICDNA.pyw" in content
