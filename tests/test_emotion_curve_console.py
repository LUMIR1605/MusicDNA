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
            {"type": "INTRO", "start": 0.0, "end": 1.0},
            {"type": "CHORUS", "start": 1.0, "end": 2.0},
        ],
    }

    curve = analyze(dna)

    assert curve == [
        {"start": 0.0, "end": 1.0, "score": 35},
        {"start": 1.0, "end": 2.0, "score": 90},
    ]
    assert "#######" in "".join(stdout.parts)
