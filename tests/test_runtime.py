from __future__ import annotations

import pytest

from core import runtime
from core.runtime import CapabilityReport, RuntimeCapabilityError, check_capabilities


def test_capability_check_reports_missing_module_and_binary():
    report = check_capabilities(
        python_modules=("numpy", "missing_module"),
        binaries=("ffmpeg", "missing_binary"),
        module_finder=lambda name: object() if name == "numpy" else None,
        binary_finder=lambda name: "C:/tools/ffmpeg.exe" if name == "ffmpeg" else None,
    )

    assert report.missing_python_modules == ("missing_module",)
    assert report.missing_binaries == ("missing_binary",)
    assert not report.ready


def test_capability_error_is_actionable_without_traceback_details():
    report = CapabilityReport(("numpy",), ("ffmpeg",))

    with pytest.raises(RuntimeCapabilityError, match="Missing Python packages: numpy") as error:
        raise RuntimeCapabilityError(report)

    assert "Missing local tools: ffmpeg" in str(error.value)


def test_require_binary_reports_missing_ffmpeg_when_no_system_or_venv_binary(monkeypatch):
    monkeypatch.setattr(runtime, "which", lambda _name: None)
    monkeypatch.setattr(runtime, "_venv_binary", lambda _name: None)

    with pytest.raises(RuntimeCapabilityError, match="Missing local tools: ffmpeg"):
        runtime.require_binary("ffmpeg")


def test_require_binary_uses_venv_tool_and_exposes_it_to_unchanged_engines(monkeypatch):
    monkeypatch.setattr(runtime, "which", lambda _name: None)
    monkeypatch.setattr(runtime, "_venv_binary", lambda _name: "C:/MusicDNA/.venv/Scripts/ffmpeg.exe")
    monkeypatch.setenv("PATH", "C:/Windows/System32")

    assert runtime.require_binary("ffmpeg") == "C:/MusicDNA/.venv/Scripts/ffmpeg.exe"
    assert runtime.os.environ["PATH"].split(runtime.os.pathsep)[0] == "C:\\MusicDNA\\.venv\\Scripts"
