import json
from pathlib import Path
from collections import Counter

DB = Path.home() / "music_dna" / "knowledge.json"

def analyze():

    print("=== PATTERN ENGINE v1 ===")
    print()

    if not DB.exists():
        print("Brak knowledge.json")
        return []

    songs = json.loads(DB.read_text())

    patterns = Counter()

    for song in songs:

        mode = song.get("harmony", {}).get("mode", "unknown")

        emotions = tuple(sorted(
            song.get("emotion", {}).get("labels", [])
        ))

        energy = song.get("energy", {}).get("avg", 0)

        if energy < 3000:
            e = "LOW"
        elif energy < 7000:
            e = "MID"
        else:
            e = "HIGH"

        pattern = (mode, e, emotions)

        patterns[pattern] += 1

    print("Najczęstsze wzorce:\n")

    for pattern, count in patterns.most_common(20):
        print(f"{count:3}x  {pattern}")

    return patterns

if __name__ == "__main__":
    analyze()
