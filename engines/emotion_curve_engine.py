import math

def analyze(dna):

    print("=== EMOTION CURVE ENGINE v1 ===")
    print()

    curve = []

    energy = dna.get("energy", {})
    structure = dna.get("structure", [])

    avg = energy.get("avg", 0)

    for s in structure:

        value = 40

        if s["type"] == "INTRO":
            value -= 15

        elif s["type"] == "VERSE":
            value += 0

        elif s["type"] == "BUILD":
            value += 25

        elif s["type"] == "CHORUS":
            value += 40

        if avg > 3500:
            value += 10

        value = max(0, min(100, value))

        curve.append({
            "start": s["start"],
            "end": s["end"],
            "score": value
        })

    for c in curve:

        bar = "#" * (c["score"] // 5)

        print(
            f'{c["start"]:6.1f}s {c["score"]:3d} {bar}'
        )

    return curve


if __name__ == "__main__":
    print("Emotion Curve działa jako moduł dna_builder.")
