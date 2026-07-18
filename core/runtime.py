"""Runtime capability checks for the supported MusicDNA analysis path."""

from __future__ import annotations

from dataclasses import dataclass
from importlib.util import find_spec
from shutil import which
from typing import Callable, Iterable


CORE_PYTHON_MODULES = ("numpy", "jsonschema")
CORE_BINARIES = ("ffmpeg",)
OPTIONAL_BINARIES = ("ffprobe", "yt-dlp", "aubioonset")
INGESTION_PYTHON_MODULES = ("yt_dlp",)


@dataclass(frozen=True)
class CapabilityReport:
    """Result of checking the capabilities required by one runtime profile."""

    missing_python_modules: tuple[str, ...]
    missing_binaries: tuple[str, ...]

    @property
    def ready(self) -> bool:
        return not self.missing_python_modules and not self.missing_binaries


class RuntimeCapabilityError(RuntimeError):
    """Raised when a required local capability is unavailable."""

    def __init__(self, report: CapabilityReport):
        self.report = report
        parts: list[str] = []
        if report.missing_python_modules:
            parts.append(
                "Missing Python packages: " + ", ".join(report.missing_python_modules)
            )
        if report.missing_binaries:
            parts.append("Missing local tools: " + ", ".join(report.missing_binaries))
        super().__init__("; ".join(parts))


def check_capabilities(
    python_modules: Iterable[str] = (),
    binaries: Iterable[str] = (),
    module_finder: Callable[[str], object | None] = find_spec,
    binary_finder: Callable[[str], str | None] = which,
) -> CapabilityReport:
    """Check named Python modules and local executable commands without running them."""

    missing_python_modules = tuple(
        name for name in python_modules if module_finder(name) is None
    )
    missing_binaries = tuple(name for name in binaries if binary_finder(name) is None)
    return CapabilityReport(missing_python_modules, missing_binaries)


def require_core_capabilities() -> CapabilityReport:
    """Require only the packages and binary needed by the active audio builder."""

    report = check_capabilities(CORE_PYTHON_MODULES, CORE_BINARIES)
    if not report.ready:
        raise RuntimeCapabilityError(report)
    return report


def require_ingestion_capabilities() -> CapabilityReport:
    """Require the local dependencies used by the YouTube ingestion command."""

    report = check_capabilities(
        (*CORE_PYTHON_MODULES, *INGESTION_PYTHON_MODULES), CORE_BINARIES
    )
    if not report.ready:
        raise RuntimeCapabilityError(report)
    return report


def require_binary(name: str) -> str:
    """Return a binary path or raise the same structured capability error."""

    binary_path = which(name)
    if binary_path is None:
        raise RuntimeCapabilityError(CapabilityReport((), (name,)))
    return binary_path
