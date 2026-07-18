from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from engines import dna_builder
from schema.validation import DNASchemaValidationError, validate_dna


def valid_payload(rhythm):
    return {
        "schema_version": "dna-output-v1",
        "audio": {},
        "energy": {},
        "beats": {"count": 2, "first": 0.5, "last": 1.0},
        "rhythm": rhythm,
        "spectrum": {},
        "pitch": {},
        "melody": {},
        "structure": {},
        "harmony": {},
        "emotion": {},
        "journey": {},
        "curve": {},
        "production": {},
        "rules": {},
    }


def stub_builder_dependencies(monkeypatch, rhythm):
    monkeypatch.setattr(dna_builder, "require_core_capabilities", lambda: None)
    monkeypatch.setattr(dna_builder, "energy_analyze", lambda _: [1.0, 2.0])
    monkeypatch.setattr(dna_builder, "rhythm_analyze", lambda _: rhythm)
    monkeypatch.setattr(dna_builder, "spectrum_analyze", lambda _: {})
    monkeypatch.setattr(dna_builder, "structure_analyze", lambda _: {})
    monkeypatch.setattr(dna_builder, "analyze_pitch", lambda _: {})
    monkeypatch.setattr(dna_builder, "melody_analyze", lambda _: [])
    monkeypatch.setattr(dna_builder, "harmony_analyze", lambda _: {})
    monkeypatch.setattr(dna_builder, "emotion_analyze", lambda _: {})
    monkeypatch.setattr(dna_builder, "journey_analyze", lambda _: {})
    monkeypatch.setattr(dna_builder, "production_analyze", lambda _: {})
    monkeypatch.setattr(dna_builder, "curve_analyze", lambda _: {})
    monkeypatch.setattr(dna_builder, "rules_analyze", lambda _: {})
    monkeypatch.setattr(dna_builder, "knowledge_analyze", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(dna_builder, "save_dna", lambda *_args, **_kwargs: Path("fixture.json"))


def test_canonical_schema_accepts_valid_payload(valid_rhythm):
    validate_dna(valid_payload(valid_rhythm))


def test_canonical_schema_rejects_missing_rhythm_contract(valid_rhythm):
    payload = valid_payload(valid_rhythm)
    payload.pop("rhythm")

    with pytest.raises(DNASchemaValidationError, match="rhythm"):
        validate_dna(payload)


def test_schema_normalizes_numpy_measurements_before_validation(valid_rhythm):
    numpy_rhythm = {
        "transients": dict(valid_rhythm["transients"], positions_seconds=np.array([0.5, 1.0]), count=np.int64(2)),
        "beat_positions": dict(valid_rhythm["beat_positions"], positions_seconds=np.array([0.5, 1.0]), count=np.int64(2)),
        "bpm": dict(valid_rhythm["bpm"], value=np.float32(120.0)),
    }
    payload = valid_payload(numpy_rhythm)
    payload["energy"] = {"avg": np.float64(1.25)}
    payload["beats"] = {"count": np.int64(2), "first": np.float64(0.5), "last": np.float32(1.0)}

    normalized = validate_dna(payload)

    assert isinstance(normalized["energy"]["avg"], float)
    assert isinstance(normalized["beats"]["count"], int)
    assert normalized["rhythm"]["transients"]["positions_seconds"] == [0.5, 1.0]


def test_builder_validates_versioned_payload_and_preserves_legacy_beats(monkeypatch, valid_rhythm):
    stub_builder_dependencies(monkeypatch, valid_rhythm)

    dna, output = dna_builder.build("fixture.wav")

    assert output == Path("fixture.json")
    assert dna["schema_version"] == "dna-output-v1"
    assert dna["rhythm"]["bpm"]["value"] == 120.0
    assert dna["beats"] == {"count": 2, "first": 0.5, "last": 1.0}


def test_builder_rejects_invalid_rhythm_before_persistence(monkeypatch, valid_rhythm):
    invalid_rhythm = dict(valid_rhythm)
    invalid_rhythm["bpm"] = dict(valid_rhythm["bpm"], status="invalid")
    stub_builder_dependencies(monkeypatch, invalid_rhythm)
    saved = []
    monkeypatch.setattr(dna_builder, "save_dna", lambda *_args, **_kwargs: saved.append(True))

    with pytest.raises(DNASchemaValidationError, match="status"):
        dna_builder.build("fixture.wav")

    assert saved == []
