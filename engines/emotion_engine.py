import sys


LABELS = [
    "Calm",
    "Hope",
    "Longing",
    "Dark",
    "Epic",
    "Power"
]


def analyze(dna):

    energy = dna.get("energy", {})
    pitch = dna.get("pitch", {})
    beats = dna.get("beats", {})
    harmony = dna.get("harmony", {})

    score = {k: 0.0 for k in LABELS}

    avg_energy = float(energy.get("avg", 0))
    beat_count = int(beats.get("count", 0))
    avg_pitch = float(pitch.get("avg", 0))
    mode = harmony.get("mode", "major")

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
    else:
        score["Hope"] += 2

    result = sorted(
        score.items(),
        key=lambda x: x[1],
        reverse=True
    )

    emotions = [x[0] for x in result if x[1] > 0][:3]

    print("=== EMOTION ENGINE v1 ===")
    print()

    for e in emotions:
        print(e)

    return {
        "labels": emotions,
        "scores": score
    }


if __name__ == "__main__":
    print("Emotion Engine działa jako moduł dna_builder.")
