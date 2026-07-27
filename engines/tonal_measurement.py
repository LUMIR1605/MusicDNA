"""Shared conservative tonal-frame detector for pitch and melody measurements."""

from __future__ import annotations

import numpy as np

from core.ffmpeg_engine import load_pcm


SR = 48000
WINDOW = 4096
HOP = 2048
MIN_FREQUENCY = 65.0
MAX_FREQUENCY = 1000.0
MIN_TONAL_FRAMES = 4


def estimate_tonal_frames(path: str) -> tuple[list[dict[str, float]], list[dict[str, float]], int]:
    """Reject silence and broadband/percussive frames before reporting pitch."""

    pcm = load_pcm(path)
    starts = list(range(0, len(pcm) - WINDOW, HOP))
    if not starts:
        return [], [], 0
    rms = np.asarray([np.sqrt(np.mean(pcm[start:start + WINDOW].astype(float) ** 2)) for start in starts])
    threshold = max(100.0, float(np.percentile(rms, 95)) * 0.05)
    frequencies = np.fft.rfftfreq(WINDOW, 1 / SR)
    tonal_band = (frequencies >= MIN_FREQUENCY) & (frequencies <= MAX_FREQUENCY)
    broad_band = (frequencies >= MIN_FREQUENCY) & (frequencies <= 5000.0)
    candidates: list[dict[str, float]] = []
    for frame_index, start in enumerate(starts):
        if rms[frame_index] < threshold:
            continue
        magnitude = np.abs(np.fft.rfft(pcm[start:start + WINDOW] * np.hanning(WINDOW)))
        tonal = magnitude[tonal_band]
        broad = magnitude[broad_band] + 1e-12
        peak_index = int(np.argmax(tonal))
        peak = float(tonal[peak_index])
        median = float(np.median(tonal)) + 1e-12
        flatness = float(np.exp(np.mean(np.log(broad))) / np.mean(broad))
        peak_to_median = peak / median
        if flatness >= 0.35 or peak_to_median < 18.0:
            continue
        score = min(1.0, (peak_to_median / 80.0) * (1.0 - flatness))
        candidates.append(
            {
                "frame": float(frame_index),
                "time": start / SR,
                "freq": float(frequencies[tonal_band][peak_index]),
                "confidence": score,
            }
        )

    groups: list[list[dict[str, float]]] = []
    for candidate in candidates:
        if groups and int(candidate["frame"]) == int(groups[-1][-1]["frame"]) + 1:
            groups[-1].append(candidate)
        else:
            groups.append([candidate])
    groups = [group for group in groups if len(group) >= MIN_TONAL_FRAMES]
    accepted = [frame for group in groups for frame in group]
    segments = [
        {"start": group[0]["time"], "end": group[-1]["time"] + WINDOW / SR, "confidence": float(np.mean([item["confidence"] for item in group]))}
        for group in groups
    ]
    return accepted, segments, len(starts)
