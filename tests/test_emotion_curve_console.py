from __future__ import annotations

import sys

from engines.emotion_curve_engine import analyze


class Cp1250Stdout:
    """Minimal stdout replacement that rejects text unsupported by Windows cp1250."""

    encoding = "cp1250"

    def __init__(self) -> None:
        self.parts: list[str] = []

    def write(self, text: str) -> int:
        text.encode(self.encoding)
        self.parts.append(text)
        return len(text)

    def flush(self) -> None:
        pass


def test_emotion_curve_console_output_is_safe_for_cp1250(monkeypatch):
    stdout = Cp1250Stdout()
    monkeypatch.setattr(sys, "stdout", stdout)
    dna = {
        "energy": {"avg": 4000},
        "structure": [
            {"type": "UNKNOWN", "start": 0.0, "end": 1.0, "status": "uncertain"},
            {"type": "UNKNOWN", "start": 1.0, "end": 2.0, "status": "uncertain"},
        ],
    }

    curve = analyze(dna)

    assert curve == [
        {
            "start": 0.0,
            "end": 1.0,
            "score": None,
            "status": "unavailable",
            "confidence": 0.0,
            "reason": "Structure measurement is uncertain; no emotion curve is inferred.",
        },
        {
            "start": 1.0,
            "end": 2.0,
            "score": None,
            "status": "unavailable",
            "confidence": 0.0,
            "reason": "Structure measurement is uncertain; no emotion curve is inferred.",
        },
    ]
    assert "#" not in "".join(stdout.parts)
