"""Do not emit a numeric emotion curve when structure is uncertain."""

from __future__ import annotations


def analyze(dna: dict) -> list[dict]:
    structure = dna.get("structure", [])
    usable = bool(structure) and all(section.get("status", "estimated") == "estimated" for section in structure)
    if not usable:
        return [
            {
                "start": section["start"],
                "end": section["end"],
                "score": None,
                "status": "unavailable",
                "confidence": 0.0,
                "reason": "Structure measurement is uncertain; no emotion curve is inferred.",
            }
            for section in structure
        ]
    return [
        {
            "start": section["start"],
            "end": section["end"],
            "score": None,
            "status": "uncertain",
            "confidence": 0.0,
            "reason": "No validated mapping from musical form to emotion score is available.",
        }
        for section in structure
    ]
