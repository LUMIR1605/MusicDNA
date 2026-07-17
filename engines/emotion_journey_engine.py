import sys

def analyze(dna):

    print("=== EMOTION JOURNEY ENGINE v1 ===")
    print()

    journey = []

    structure = dna.get("structure", [])
    energy = dna.get("energy", {})
    harmony = dna.get("harmony", {})
    emotions = dna.get("emotion", {}).get("labels", [])

    avg_energy = energy.get("avg", 0)
    mode = harmony.get("mode")

    for section in structure:

        part = section["type"]

        if part == "INTRO":
            state = "Reflection"

        elif part == "VERSE":
            if "Longing" in emotions:
                state = "Longing"
            else:
                state = "Story"

        elif part == "BUILD":
            state = "Tension"

        elif part == "CHORUS":
            if avg_energy > 3500:
                state = "Release"
            else:
                state = "Hope"

        else:
            state = "Unknown"

        journey.append({
            "start": section["start"],
            "end": section["end"],
            "emotion": state
        })

    print("Emotional Journey")
    print()

    for j in journey:
        print(
            f'{j["start"]:6.1f}s - {j["end"]:6.1f}s   {j["emotion"]}'
        )

    return journey


if __name__ == "__main__":
    print("Emotion Journey działa jako moduł dna_builder.")
