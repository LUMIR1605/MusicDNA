import json
from pathlib import Path
from collections import Counter

DB = Path.home() / "music_dna" / "knowledge.json"


def analyze():
    print("=== REASONING ENGINE v1 ===\n")

    if not DB.exists():
        print("Brak knowledge.json")
        return

    songs = json.loads(DB.read_text())

    print(f"Przeanalizowano utworów: {len(songs)}\n")

    modes = Counter()
    emotions = Counter()
    intro_lengths = []

    for song in songs:
        mode = song.get("harmony", {}).get("mode")
        if mode:
            modes[mode] += 1

        for emotion in song.get("emotion", {}).get("labels", []):
            emotions[emotion] += 1

        structure = song.get("structure", [])
        if structure and structure[0]["type"] == "INTRO":
            intro_lengths.append(
                structure[0]["end"] - structure[0]["start"]
            )

    print("=== WNIOSKI ===\n")

    if modes:
        m, n = modes.most_common(1)[0]
        print(f"Najczęstszy tryb     : {m} ({n})")

    if emotions:
        e, n = emotions.most_common(1)[0]
        print(f"Najczęstsza emocja   : {e} ({n})")

    if intro_lengths:
        avg = sum(intro_lengths) / len(intro_lengths)
        print(f"Średnie intro        : {avg:.1f} s")


if __name__ == "__main__":
    analyze()
