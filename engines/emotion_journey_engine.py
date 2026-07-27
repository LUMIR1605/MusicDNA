"""Do not narrate an emotional journey from uncertain structure."""

from __future__ import annotations


def analyze(dna: dict) -> list[dict]:
    structure = dna.get("structure", [])
    emotion = dna.get("emotion", {})
    usable = bool(structure) and emotion.get("status") == "estimated" and all(
        section.get("status", "estimated") == "estimated" for section in structure
    )
    if not usable:
        return [
            {
                "start": section["start"],
                "end": section["end"],
                "emotion": "UNKNOWN",
                "status": "unavailable",
                "confidence": 0.0,
                "reason": "Structure or emotion measurement is uncertain; no emotional journey is inferred.",
            }
            for section in structure
        ]
    # Kept as a conservative compatibility path for externally validated sections.
    return [
        {
            "start": section["start"],
            "end": section["end"],
            "emotion": "UNKNOWN",
            "status": "uncertain",
            "confidence": 0.0,
            "reason": "No validated mapping from musical form to emotion is available.",
        }
        for section in structure
    ]
