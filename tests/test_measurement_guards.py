from __future__ import annotations

import subprocess

import numpy as np

from engines import (
    emotion_engine,
    emotion_journey_engine,
    harmony_engine,
    melody_tracker,
    pitch_engine,
    production_engine,
    rhythm_engine,
    structure_engine,
    tonal_measurement,
)


def test_structure_rejects_sub_two_second_energy_flicker(monkeypatch):
    energy = np.array([10.0] * 50 + [100.0] * 4 + [10.0] * 50)
    monkeypatch.setattr(structure_engine, "energy_analyze", lambda _: energy)

    sections = structure_engine.analyze("fixture.wav")

    assert sections
    assert all(section["end"] - section["start"] >= 2.0 for section in sections)
    assert all(section["type"] == "UNKNOWN" for section in sections)
    assert all(section["status"] == "uncertain" for section in sections)


def test_h1_like_transient_intervals_do_not_return_the_autocorrelation_subharmonic(monkeypatch):
    intervals = [0.64] * 124 + [0.79] * 74 + [0.46] * 56 + [0.33] * 58 + [0.55] * 45
    positions = list(np.cumsum([0.0, *intervals]))
    monkeypatch.setattr(rhythm_engine, "detect_transients", lambda _: positions)

    rhythm = rhythm_engine.analyze("fixture.wav")

    assert abs(rhythm["bpm"]["value"] - 93.75) < 1.0
    assert rhythm["bpm"]["status"] == "uncertain"
    assert rhythm["bpm"]["confidence"] < 0.40


def test_harmony_with_flat_chroma_is_not_reported_as_a_key(monkeypatch):
    noise = np.random.default_rng(3).normal(0, 1000, 48000 * 2).astype(np.float32)
    monkeypatch.setattr(harmony_engine, "load_pcm", lambda _: noise)

    harmony = harmony_engine.analyze("fixture.wav")

    assert harmony["status"] == "uncertain"
    assert harmony["key"] is None
    assert harmony["mode"] is None


def test_emotion_and_journey_do_not_label_uncertain_measurements():
    dna = {
        "energy": {"avg": 5000},
        "pitch": {"status": "estimated", "confidence": 0.8, "avg": 250},
        "harmony": {"status": "uncertain", "confidence": 0.118, "candidate_mode": "minor"},
        "beats": {"count": 300},
        "structure": [{"type": "UNKNOWN", "start": 0.0, "end": 4.0, "status": "uncertain"}],
    }
    emotion = emotion_engine.analyze(dna)
    dna["emotion"] = emotion

    assert emotion["status"] == "uncertain"
    assert emotion["labels"] == []
    journey = emotion_journey_engine.analyze(dna)
    assert journey[0]["emotion"] == "UNKNOWN"
    assert journey[0]["status"] == "unavailable"


def test_production_reads_final_ebu_summary_not_initial_silence_frame(monkeypatch):
    log = """
    t: 0.1 I: -70.0 LUFS
    Integrated loudness:
      I:         -17.5 LUFS
    Loudness range:
      LRA:         1.8 LU
    Overall
    Crest factor: 5.716167
    """
    monkeypatch.setattr(production_engine, "require_binary", lambda _: "ffmpeg")
    monkeypatch.setattr(production_engine, "run_process", lambda *_args, **_kwargs: subprocess.CompletedProcess([], 0, "", log))
    tone = np.sin(2 * np.pi * 440 * np.arange(48000 * 2) / 48000).astype(np.float32) * 10000
    monkeypatch.setattr(production_engine, "load_pcm", lambda _: tone)

    production = production_engine.analyze("fixture.wav")

    assert production["lufs"] == -17.5
    assert production["dynamic_range"] == 1.8
    assert production["spectral_centroid"] is not None
    assert abs(float(production["spectral_centroid"]) - 440) < 25
    assert production["status"] == "estimated"


def test_pitch_and_melody_reject_silence_and_broadband_percussion(monkeypatch):
    sample_rate = 48000
    seconds = np.arange(sample_rate) / sample_rate
    tone_a = 12000 * np.sin(2 * np.pi * 220 * seconds)
    noise = np.random.default_rng(12).normal(0, 3000, sample_rate)
    tone_b = 12000 * np.sin(2 * np.pi * 440 * seconds)
    pcm = np.concatenate([np.zeros(sample_rate), tone_a, noise, tone_b]).astype(np.float32)
    monkeypatch.setattr(tonal_measurement, "load_pcm", lambda _: pcm)

    pitch = pitch_engine.analyze_pitch("fixture.wav")
    melody = melody_tracker.analyze("fixture.wav")

    assert pitch["status"] == "estimated"
    assert len(pitch["tonal_segments"]) == 2
    assert all(abs(value - 220) < 20 or abs(value - 440) < 20 for value in pitch["values"])
    assert melody["status"] == "estimated"
    assert len(melody["tonal_segments"]) == 2
