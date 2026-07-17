"""Canonical rhythm contract built from the existing transient and BPM engines."""

from __future__ import annotations

import math
from typing import Any

from engines.bpm_engine import detect_transients
from engines.bpm_engine_v2 import detect_bpm


def _unavailable(reason: str) -> dict[str, Any]:
    return {
        "transients": {
            "positions_seconds": [],
            "count": 0,
            "status": "unavailable",
            "method": "energy_difference",
            "reason": reason,
        },
        "beat_positions": {
            "positions_seconds": [],
            "count": 0,
            "status": "unavailable",
            "method": "transient_candidates",
            "reason": reason,
        },
        "bpm": {
            "value": None,
            "status": "unavailable",
            "method": "autocorrelation",
            "reason": reason,
        },
    }


def analyze(audio_file: str) -> dict[str, Any]:
    """Return explicit transient, beat-position estimate, and BPM fields.

    The current beat positions are explicitly marked as estimates derived from
    transient candidates. No result is presented as a confirmed beat grid.
    """

    try:
        positions = [float(position) for position in detect_transients(audio_file)]
    except Exception as error:
        return _unavailable(f"Transient measurement unavailable: {type(error).__name__}")

    transients = {
        "positions_seconds": positions,
        "count": len(positions),
        "status": "measured",
        "method": "energy_difference",
    }
    beat_positions = {
        "positions_seconds": positions,
        "count": len(positions),
        "status": "estimated",
        "method": "transient_candidates",
    }

    if len(positions) < 2:
        return {
            "transients": transients,
            "beat_positions": beat_positions,
            "bpm": {
                "value": None,
                "status": "unavailable",
                "method": "autocorrelation",
                "reason": "Insufficient transient candidates for tempo estimation",
            },
        }

    try:
        bpm = float(detect_bpm(audio_file))
    except Exception as error:
        return {
            "transients": transients,
            "beat_positions": beat_positions,
            "bpm": {
                "value": None,
                "status": "unavailable",
                "method": "autocorrelation",
                "reason": f"Tempo measurement unavailable: {type(error).__name__}",
            },
        }

    if not math.isfinite(bpm) or bpm <= 0:
        return {
            "transients": transients,
            "beat_positions": beat_positions,
            "bpm": {
                "value": None,
                "status": "unavailable",
                "method": "autocorrelation",
                "reason": "Tempo measurement did not produce a finite positive value",
            },
        }

    return {
        "transients": transients,
        "beat_positions": beat_positions,
        "bpm": {
            "value": bpm,
            "status": "estimated",
            "method": "autocorrelation",
        },
    }
