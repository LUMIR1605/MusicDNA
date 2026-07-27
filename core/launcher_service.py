"""Thin desktop-launcher adapter for the existing ingestion pipeline."""

from __future__ import annotations

from typing import Callable

from core.audio_source import SourceError, parse_audio_source
from core.ingestion import IngestionError, IngestionResult, ingest


def validate_add_source(source: str) -> str:
    """Validate a pasted URL or selected local file before work starts."""

    try:
        return parse_audio_source(source.strip()).source_id
    except SourceError as error:
        raise IngestionError(str(error)) from error


def validate_add_url(url: str) -> str:
    """Backward-compatible name for callers that previously accepted only URLs."""

    return validate_add_source(url)


def run_add(source: str, progress: Callable[[str], None]) -> IngestionResult:
    """Delegate directly to the same pipeline used by ``musicdna add``."""

    validate_add_source(source)
    return ingest(source.strip(), progress)
