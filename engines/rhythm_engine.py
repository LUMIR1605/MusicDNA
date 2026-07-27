"""Canonical rhythm contract built from transient candidates."""

from __future__ import annotations

import math
from typing import Any

from engines.bpm_engine import detect_transients
from engines.bpm_engine_v2 import detect_bpm, estimate_bpm_from_transients


def _unavailable(reason: str) -> dict[str, Any]:
    return {
        "transients": {"positions_seconds": [], "count": 0, "status": "unavailable", "method": "energy_difference", "reason": reason},
        "beat_positions": {"positions_seconds": [], "count": 0, "status": "unavailable", "method": "transient_candidates", "reason": reason},
        "bpm": {"value": None, "status": "unavailable", "confidence": 0.0, "method": "dominant_transient_interval", "reason": reason},
    }


def analyze(audio_file: str) -> dict[str, Any]:
    """Estimate BPM only from the most-supported plausible transient interval."""

    try:
        positions = [float(position) for position in detect_transients(audio_file)]
    except Exception as error:
        return _unavailable(f"Transient measurement unavailable: {type(error).__name__}")
    transients = {"positions_seconds": positions, "count": len(positions), "status": "measured", "method": "energy_difference"}
    beat_positions = {"positions_seconds": positions, "count": len(positions), "status": "estimated", "method": "transient_candidates"}
    if len(positions) < 2:
        return {"transients": transients, "beat_positions": beat_positions, "bpm": {"value": None, "status": "unavailable", "confidence": 0.0, "method": "dominant_transient_interval", "reason": "Insufficient transient candidates for tempo estimation"}}

    bpm, confidence = estimate_bpm_from_transients(positions)
    if bpm is None:
        return {"transients": transients, "beat_positions": beat_positions, "bpm": {"value": None, "status": "unavailable", "confidence": 0.0, "method": "dominant_transient_interval", "reason": "No plausible dominant transient interval"}}
    if not math.isfinite(bpm) or bpm <= 0:
        return _unavailable("Tempo measurement did not produce a finite positive value")
    status = "estimated" if confidence >= 0.40 else "uncertain"
    measurement: dict[str, Any] = {"value": bpm, "status": status, "confidence": confidence, "method": "dominant_transient_interval"}
    if status == "uncertain":
        measurement["reason"] = "No single transient interval has sufficient support for a reliable tempo claim."
    return {"transients": transients, "beat_positions": beat_positions, "bpm": measurement}
