"""Energy segmentation with explicit limits on musical-form interpretation."""

from __future__ import annotations

import sys

import numpy as np

from engines.energy_pcm import analyze as energy_analyze


FRAME_TIME = 0.1
MIN_SEGMENT_SECONDS = 2.0
MIN_SEGMENT_FRAMES = int(MIN_SEGMENT_SECONDS / FRAME_TIME)


def _energy_band(ratio: float) -> str:
    if ratio < 0.20:
        return "low"
    if ratio < 0.45:
        return "medium_low"
    if ratio < 0.70:
        return "medium_high"
    return "high"


def _runs(labels: list[str], values: np.ndarray) -> list[dict[str, object]]:
    runs: list[dict[str, object]] = []
    start = 0
    current = labels[0]
    for index, label in enumerate(labels[1:], 1):
        if label == current:
            continue
        runs.append({"band": current, "start": start, "end": index, "mean": float(values[start:index].mean())})
        start, current = index, label
    runs.append({"band": current, "start": start, "end": len(labels), "mean": float(values[start:].mean())})
    return runs


def _merge_short_runs(runs: list[dict[str, object]]) -> list[dict[str, object]]:
    """Merge flicker shorter than two seconds into its closest neighbour."""

    runs = [dict(run) for run in runs]
    while len(runs) > 1:
        short_index = next(
            (index for index, run in enumerate(runs) if int(run["end"]) - int(run["start"]) < MIN_SEGMENT_FRAMES),
            None,
        )
        if short_index is None:
            break
        run = runs[short_index]
        if short_index == 0:
            target_index = 1
        elif short_index == len(runs) - 1:
            target_index = short_index - 1
        else:
            before = runs[short_index - 1]
            after = runs[short_index + 1]
            target_index = short_index - 1 if abs(float(run["mean"]) - float(before["mean"])) <= abs(float(run["mean"]) - float(after["mean"])) else short_index + 1
        target = runs[target_index]
        target["start"] = min(int(target["start"]), int(run["start"]))
        target["end"] = max(int(target["end"]), int(run["end"]))
        target["mean"] = (float(target["mean"]) + float(run["mean"])) / 2.0
        runs.pop(short_index)
        runs.sort(key=lambda item: int(item["start"]))
    return runs


def analyze(path: str) -> list[dict[str, object]]:
    """Return stable energy segments, never asserted verse/build/chorus labels.

    Energy alone cannot identify musical form. It is retained as an observable
    segmentation signal, but every output segment is explicitly uncertain and
    downstream emotional engines must not infer a narrative from it.
    """

    energy = np.asarray(energy_analyze(path), dtype=float)
    if energy.size == 0 or not np.isfinite(energy).all() or float(energy.max()) <= 0:
        return []
    smooth = np.convolve(energy, np.ones(25) / 25, mode="same")
    labels = [_energy_band(float(value / smooth.max())) for value in smooth]
    segments = _merge_short_runs(_runs(labels, smooth))

    result = [
        {
            "type": "UNKNOWN",
            "start": int(segment["start"]) * FRAME_TIME,
            "end": int(segment["end"]) * FRAME_TIME,
            "energy_band": segment["band"],
            "status": "uncertain",
            "confidence": 0.0,
            "reason": "Energy-only segmentation cannot identify musical form.",
        }
        for segment in segments
    ]

    print("=== STRUCTURE ENGINE ===")
    for segment in result:
        print(f"{segment['start']:7.1f}s - {segment['end']:7.1f}s   UNKNOWN (energy segment)")
    return result


if __name__ == "__main__":
    analyze(sys.argv[1])
