from __future__ import annotations

import subprocess
from pathlib import Path

from core import subprocesses


def test_run_process_hides_console_window_on_windows(monkeypatch):
    received = {}
    expected = subprocess.CompletedProcess(["ffmpeg"], 0)

    def fake_run(command, **kwargs):
        received["command"] = command
        received.update(kwargs)
        return expected

    monkeypatch.setattr(subprocesses.sys, "platform", "win32")
    monkeypatch.setattr(subprocesses.subprocess, "run", fake_run)

    result = subprocesses.run_process(["ffmpeg"], capture_output=True)

    assert result is expected
    assert received["command"] == ["ffmpeg"]
    assert received["capture_output"] is True
    assert received["creationflags"] & subprocess.CREATE_NO_WINDOW
    assert received["startupinfo"].dwFlags & subprocess.STARTF_USESHOWWINDOW
    assert received["startupinfo"].wShowWindow == subprocess.SW_HIDE


def test_run_process_preserves_non_windows_behavior(monkeypatch):
    received = {}

    def fake_run(command, **kwargs):
        received["command"] = command
        received.update(kwargs)
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(subprocesses.sys, "platform", "linux")
    monkeypatch.setattr(subprocesses.subprocess, "run", fake_run)

    subprocesses.run_process(["git", "status"], text=True)

    assert received == {"command": ["git", "status"], "text": True}


def test_run_process_combines_existing_creation_flags(monkeypatch):
    received = {}

    def fake_run(command, **kwargs):
        received.update(kwargs)
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(subprocesses.sys, "platform", "win32")
    monkeypatch.setattr(subprocesses.subprocess, "run", fake_run)

    subprocesses.run_process(["ffmpeg"], creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)

    assert received["creationflags"] & subprocess.CREATE_NO_WINDOW
    assert received["creationflags"] & subprocess.CREATE_NEW_PROCESS_GROUP


def test_console_python_executable_replaces_pythonw_on_windows(monkeypatch, tmp_path: Path):
    pythonw = tmp_path / "pythonw.exe"
    python = tmp_path / "python.exe"
    pythonw.touch()
    python.touch()
    monkeypatch.setattr(subprocesses.sys, "platform", "win32")

    assert subprocesses.console_python_executable(str(pythonw)) == str(python)


def test_console_python_executable_keeps_unpaired_executable(monkeypatch, tmp_path: Path):
    pythonw = tmp_path / "pythonw.exe"
    pythonw.touch()
    monkeypatch.setattr(subprocesses.sys, "platform", "win32")

    assert subprocesses.console_python_executable(str(pythonw)) == str(pythonw)
