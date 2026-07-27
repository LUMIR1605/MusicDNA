"""Production measurements parsed from final EBU R128 output only."""

from __future__ import annotations

import re
import subprocess

import numpy as np

from core.ffmpeg_engine import load_pcm
from core.runtime import require_binary
from core.subprocesses import run_process


def _summary_value(label: str, text: str) -> float | None:
    match = re.search(label, text, re.DOTALL)
    return float(match.group(1)) if match else None


def parse_production_log(log: str) -> tuple[float | None, float | None, float | None]:
    """Read only the final EBU R128 summary, never transient frame lines."""

    lufs = _summary_value(r"Integrated loudness:\s*I:\s*(-?[0-9.]+)\s*LUFS", log)
    loudness_range = _summary_value(r"Loudness range:\s*LRA:\s*(-?[0-9.]+)\s*LU", log)
    crest = _summary_value(r"Crest factor:\s*([0-9.]+)", log)
    return lufs, loudness_range, crest


def _spectral_centroid(audio: str) -> tuple[float | None, float]:
    pcm = load_pcm(audio)
    window = 4096
    hop = 4096
    if len(pcm) < window:
        return None, 0.0
    starts = range(0, len(pcm) - window, hop)
    frames = [pcm[start:start + window] for start in starts]
    rms = np.asarray([np.sqrt(np.mean(frame.astype(float) ** 2)) for frame in frames])
    threshold = max(100.0, float(np.percentile(rms, 95)) * 0.05)
    frequencies = np.fft.rfftfreq(window, 1 / 48000)
    centroids: list[float] = []
    for frame, level in zip(frames, rms):
        if level < threshold:
            continue
        magnitude = np.abs(np.fft.rfft(frame * np.hanning(window)))
        total = float(magnitude.sum())
        if total:
            centroids.append(float(np.dot(frequencies, magnitude) / total))
    return (float(np.median(centroids)) if centroids else None, len(centroids) / len(frames))


def analyze(audio: str) -> dict[str, object]:
    command = [require_binary("ffmpeg"), "-hide_banner", "-nostats", "-i", audio, "-af", "ebur128=peak=true,astats=metadata=1:reset=0", "-f", "null", "-"]
    result = run_process(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
    lufs, loudness_range, crest = parse_production_log(result.stderr) if result.returncode == 0 else (None, None, None)
    centroid, centroid_coverage = _spectral_centroid(audio)
    complete = all(value is not None for value in (lufs, loudness_range, crest, centroid))
    confidence = centroid_coverage if complete else 0.0
    output: dict[str, object] = {
        "lufs": lufs,
        "crest": crest,
        "dynamic_range": loudness_range,
        "dynamic_range_unit": "LU (EBU R128 loudness range)",
        "spectral_centroid": centroid,
        "spectral_centroid_unit": "Hz",
        "status": "estimated" if complete else "uncertain",
        "confidence": confidence,
    }
    if not complete:
        output["reason"] = "One or more production measurements could not be derived from final programme statistics."
    return output
