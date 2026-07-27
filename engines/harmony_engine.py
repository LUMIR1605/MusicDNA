"""Conservative chroma-based key candidate measurement."""

from __future__ import annotations

import sys

import numpy as np

from core.ffmpeg_engine import load_pcm


SR = 48000
WINDOW = 4096
HOP = 2048
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
MIN_DOMINANCE = 0.20
MIN_MODE_MARGIN = 0.03


def analyze(path: str) -> dict[str, object]:
    pcm = load_pcm(path)
    chroma = np.zeros(12, dtype=np.float64)
    frequencies = np.fft.rfftfreq(WINDOW, 1 / SR)
    valid = (frequencies >= 40) & (frequencies <= 5000)
    midi = np.rint(69 + 12 * np.log2(frequencies[valid] / 440.0)).astype(int) % 12
    for index in range(0, len(pcm) - WINDOW, HOP):
        block = pcm[index:index + WINDOW]
        if float(np.sqrt(np.mean(block.astype(float) ** 2))) < 100.0:
            continue
        amplitudes = np.abs(np.fft.rfft(block * np.hanning(WINDOW)))[valid]
        np.add.at(chroma, midi, amplitudes)

    total = float(chroma.sum())
    candidate_index = int(np.argmax(chroma)) if total else 0
    dominance = float(chroma[candidate_index] / total) if total else 0.0
    minor_strength = float(chroma[(candidate_index + 3) % 12] / total) if total else 0.0
    major_strength = float(chroma[(candidate_index + 4) % 12] / total) if total else 0.0
    candidate_mode = "minor" if minor_strength > major_strength else "major"
    mode_margin = abs(minor_strength - major_strength)
    status = "estimated" if dominance >= MIN_DOMINANCE and mode_margin >= MIN_MODE_MARGIN else "uncertain"
    result: dict[str, object] = {
        "key": NOTE_NAMES[candidate_index] if status == "estimated" else None,
        "mode": candidate_mode if status == "estimated" else None,
        "candidate_key": NOTE_NAMES[candidate_index],
        "candidate_mode": candidate_mode,
        "confidence": dominance,
        "status": status,
        "chroma": chroma.tolist(),
    }
    if status == "uncertain":
        result["reason"] = "Chroma dominance or major/minor separation is below the reporting threshold."
    print("=== HARMONY ENGINE ===")
    print("Candidate  :", f"{result['candidate_key']} {result['candidate_mode']}")
    print("Confidence :", round(dominance, 3), status)
    return result
