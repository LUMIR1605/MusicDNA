"""Validation boundary for the active versioned DNA output contract."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft202012Validator

from core.paths import to_json_compatible


SCHEMA_PATH = Path(__file__).with_name("dna_output_v1.json")


class DNASchemaValidationError(ValueError):
    """Raised when a DNA payload does not match the canonical output contract."""


@lru_cache(maxsize=1)
def load_schema() -> dict[str, Any]:
    with SCHEMA_PATH.open(encoding="utf-8") as schema_file:
        return json.load(schema_file)


def validate_dna(payload: Mapping[str, Any]) -> dict[str, Any]:
    normalized_payload = to_json_compatible(dict(payload))
    validator = Draft202012Validator(load_schema())
    errors = sorted(
        validator.iter_errors(normalized_payload), key=lambda error: list(error.path)
    )
    if not errors:
        return normalized_payload

    first_error = errors[0]
    location = ".".join(str(item) for item in first_error.path) or "root"
    raise DNASchemaValidationError(f"DNA schema validation failed at {location}: {first_error.message}")
