from __future__ import annotations

import numpy as np

from engines import bpm_engine, bpm_engine_v2, rhythm_engine


def synthetic_click_track(bpm: float = 120.0, seconds: float = 6.0, sample_rate: int = 48000):
    pcm = np.zeros(int(seconds * sample_rate), dtype=np.float32)
    interval = int((60.0 / bpm) * sample_rate)
    for start in range(interval, len(pcm), interval):
        pcm[start:start + 256] = 30000.0
    return pcm


def test_synthetic_click_track_has_separate_rhythm_measurements(monkeypatch):
    pcm = synthetic_click_track()
    monkeypatch.setattr(bpm_engine, "load_pcm", lambda _: pcm)
    monkeypatch.setattr(bpm_engine_v2, "load_pcm", lambda _: pcm)

    rhythm = rhythm_engine.analyze("synthetic.wav")

    assert rhythm["transients"]["status"] == "measured"
    assert rhythm["transients"]["count"] >= 8
    assert rhythm["beat_positions"]["status"] == "estimated"
    assert rhythm["beat_positions"]["positions_seconds"] == rhythm["transients"]["positions_seconds"]
    assert rhythm["bpm"]["status"] == "estimated"
    assert abs(rhythm["bpm"]["value"] - 120.0) <= 3.0


def test_insufficient_transients_returns_unavailable_bpm(monkeypatch):
    monkeypatch.setattr(rhythm_engine, "detect_transients", lambda _: [0.5])

    rhythm = rhythm_engine.analyze("synthetic.wav")

    assert rhythm["bpm"]["value"] is None
    assert rhythm["bpm"]["status"] == "unavailable"
    assert rhythm["beat_positions"]["count"] == 1


def test_transient_failure_is_not_reported_as_empty_measurement(monkeypatch):
    def fail(_):
        raise RuntimeError("decoder unavailable")

    monkeypatch.setattr(rhythm_engine, "detect_transients", fail)

    rhythm = rhythm_engine.analyze("synthetic.wav")

    assert rhythm["transients"]["status"] == "unavailable"
    assert rhythm["transients"]["count"] == 0
    assert "RuntimeError" in rhythm["transients"]["reason"]
