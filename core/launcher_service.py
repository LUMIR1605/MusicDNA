"""Thin desktop-launcher adapter for the existing ingestion pipeline."""

from __future__ import annotations

from typing import Callable

from core.ingestion import IngestionResult, ingest, validate_youtube_url


def validate_add_url(url: str) -> str:
    """Validate a pasted URL before the desktop launcher starts work."""

    return validate_youtube_url(url.strip())


def run_add(url: str, progress: Callable[[str], None]) -> IngestionResult:
    """Delegate directly to the same pipeline used by ``musicdna add``."""

    validate_add_url(url)
    return ingest(url.strip(), progress)
