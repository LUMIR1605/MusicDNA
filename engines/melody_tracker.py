"""Melody candidates restricted to the tonal frames accepted by measurement."""

from __future__ import annotations

from engines.tonal_measurement import estimate_tonal_frames


def analyze(path: str) -> dict[str, object]:
    frames, segments, total_frames = estimate_tonal_frames(path)
    notes: list[dict[str, object]] = []
    previous: float | None = None
    for frame in frames:
        frequency = float(frame["freq"])
        move = "START" if previous is None else "STABLE" if abs(frequency - previous) < 8 else "UP" if frequency > previous else "DOWN"
        notes.append({"time": frame["time"], "freq": frequency, "move": move, "confidence": frame["confidence"]})
        previous = frequency
    coverage = len(notes) / total_frames if total_frames else 0.0
    certainty = coverage * (sum(float(note["confidence"]) for note in notes) / len(notes)) if notes else 0.0
    result: dict[str, object] = {
        "frames": len(notes),
        "total_frames": total_frames,
        "tonal_segments": segments,
        "first": notes[0] if notes else None,
        "last": notes[-1] if notes else None,
        "values": notes[:200],
        "confidence": certainty,
        "status": "estimated" if notes and certainty >= 0.40 else "uncertain",
    }
    if result["status"] == "uncertain":
        result["reason"] = "No sufficiently long tonal sequence remains after frame rejection."
    return result
