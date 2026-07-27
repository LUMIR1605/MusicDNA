"""Emotion labels guarded by upstream measurement confidence."""

from __future__ import annotations


LABELS = ["Calm", "Hope", "Longing", "Dark", "Epic", "Power"]


def analyze(dna: dict) -> dict:
    energy = dna.get("energy", {})
    pitch = dna.get("pitch", {})
    beats = dna.get("beats", {})
    harmony = dna.get("harmony", {})
    dependencies = (pitch, harmony)
    if any(item.get("status") != "estimated" for item in dependencies):
        return {
            "labels": [],
            "scores": {},
            "status": "uncertain",
            "confidence": 0.0,
            "reason": "Pitch or harmony is not reliable enough to derive emotion labels.",
        }

    score = {label: 0.0 for label in LABELS}
    avg_energy = float(energy.get("avg", 0))
    beat_count = int(beats.get("count", 0))
    avg_pitch = float(pitch.get("avg", 0))
    mode = harmony.get("mode")
    if avg_energy > 5000:
        score["Power"] += 2
        score["Epic"] += 1
    elif avg_energy > 2500:
        score["Hope"] += 1
    else:
        score["Calm"] += 2
    if beat_count > 220:
        score["Power"] += 1
        score["Epic"] += 1
    else:
        score["Calm"] += 1
    if avg_pitch > 350:
        score["Hope"] += 1
    elif avg_pitch < 180:
        score["Dark"] += 1
        score["Longing"] += 1
    if mode == "minor":
        score["Dark"] += 2
        score["Longing"] += 2
    elif mode == "major":
        score["Hope"] += 2
    else:
        return {"labels": [], "scores": score, "status": "uncertain", "confidence": 0.0, "reason": "Harmony mode is unavailable."}
    confidence = min(float(pitch.get("confidence", 0.0)), float(harmony.get("confidence", 0.0)))
    if confidence < 0.40:
        return {"labels": [], "scores": score, "status": "uncertain", "confidence": confidence, "reason": "Upstream confidence is below the emotion reporting threshold."}
    labels = [label for label, value in sorted(score.items(), key=lambda item: item[1], reverse=True) if value > 0][:3]
    return {"labels": labels, "scores": score, "status": "estimated", "confidence": confidence}
