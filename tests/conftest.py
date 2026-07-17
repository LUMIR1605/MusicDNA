"""Shared fixtures for the MusicDNA baseline tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))


@pytest.fixture
def valid_rhythm():
    return {
        "transients": {
            "positions_seconds": [0.5, 1.0],
            "count": 2,
            "status": "measured",
            "method": "energy_difference",
        },
        "beat_positions": {
            "positions_seconds": [0.5, 1.0],
            "count": 2,
            "status": "estimated",
            "method": "transient_candidates",
        },
        "bpm": {
            "value": 120.0,
            "status": "estimated",
            "method": "autocorrelation",
        },
    }
