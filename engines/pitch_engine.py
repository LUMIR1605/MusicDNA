"""Pitch summary based only on contiguous tonal frames."""

from __future__ import annotations

from engines.tonal_measurement import estimate_tonal_frames


def analyze_pitch(path: str) -> dict[str, object]:
    frames, segments, total_frames = estimate_tonal_frames(path)
    values = [frame["freq"] for frame in frames]
    coverage = len(frames) / total_frames if total_frames else 0.0
    certainty = coverage * (sum(frame["confidence"] for frame in frames) / len(frames)) if frames else 0.0
    status = "estimated" if values and certainty >= 0.40 else "uncertain"
    result: dict[str, object] = {
        "frames": len(values),
        "total_frames": total_frames,
        "tonal_segments": segments,
        "min": min(values) if values else None,
        "max": max(values) if values else None,
        "avg": sum(values) / len(values) if values else None,
        "values": values[:200],
        "confidence": certainty,
        "status": status,
    }
    if status == "uncertain":
        result["reason"] = "Too few contiguous tonal frames after silence and percussive-frame rejection."
    return result
