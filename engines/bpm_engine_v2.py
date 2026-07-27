"""Tempo estimation from the dominant transient interval."""

from __future__ import annotations

import numpy as np

from core.ffmpeg_engine import load_pcm


SR = 48000
WINDOW = 1024
HOP = 512
MIN_INTERVAL_SECONDS = 0.30
MAX_INTERVAL_SECONDS = 1.00
INTERVAL_BIN_SECONDS = 0.02


def estimate_bpm_from_transients(positions: list[float]) -> tuple[float | None, float]:
    """Return tempo and support of the most frequent plausible beat interval."""

    intervals = np.diff(np.asarray(sorted(positions), dtype=float))
    intervals = intervals[(intervals >= MIN_INTERVAL_SECONDS) & (intervals <= MAX_INTERVAL_SECONDS)]
    if intervals.size == 0:
        return None, 0.0
    rounded = np.round(intervals / INTERVAL_BIN_SECONDS) * INTERVAL_BIN_SECONDS
    values, counts = np.unique(rounded, return_counts=True)
    winner = float(values[int(np.argmax(counts))])
    selected = intervals[np.abs(intervals - winner) <= INTERVAL_BIN_SECONDS / 2 + 1e-9]
    if selected.size == 0:
        return None, 0.0
    interval = float(np.median(selected))
    return 60.0 / interval, float(selected.size / intervals.size)


def detect_bpm(path: str, transient_positions: list[float] | None = None) -> float | None:
    """Estimate BPM from positions when available; retain a PCM fallback."""

    if transient_positions is not None:
        bpm, _confidence = estimate_bpm_from_transients(transient_positions)
        return bpm

    pcm = load_pcm(path)
    energy = np.array([np.sum(pcm[i:i + WINDOW].astype(np.float64) ** 2) for i in range(0, len(pcm) - WINDOW, HOP)])
    if energy.size < 2:
        return None
    onset = np.diff(energy)
    threshold = onset.mean() + onset.std() * 2
    positions = [index * HOP / SR for index, value in enumerate(onset) if value > threshold]
    bpm, _confidence = estimate_bpm_from_transients(positions)
    return bpm
