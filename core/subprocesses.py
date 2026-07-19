"""Subprocess helpers that keep console tools behind the MusicDNA GUI."""

from __future__ import annotations

import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any


def _hidden_window_options() -> dict[str, Any]:
    if sys.platform != "win32":
        return {}

    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = subprocess.SW_HIDE
    return {
        "creationflags": subprocess.CREATE_NO_WINDOW,
        "startupinfo": startupinfo,
    }


def run_process(command: Sequence[str], **kwargs: Any) -> subprocess.CompletedProcess[Any]:
    """Run a console helper without creating a visible Windows console window."""

    options = _hidden_window_options()
    if "creationflags" in kwargs and "creationflags" in options:
        options["creationflags"] |= kwargs.pop("creationflags")
    options.update(kwargs)
    return subprocess.run(command, **options)


def console_python_executable(executable: str | None = None) -> str:
    """Return the console Python paired with a Windows GUI Python executable."""

    selected = Path(executable or sys.executable)
    if sys.platform != "win32":
        return str(selected)

    replacements = {"pythonw.exe": "python.exe", "pyw.exe": "py.exe"}
    replacement = replacements.get(selected.name.lower())
    if replacement is None:
        return str(selected)
    console_python = selected.with_name(replacement)
    return str(console_python) if console_python.is_file() else str(selected)
