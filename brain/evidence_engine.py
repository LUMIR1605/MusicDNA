import json
from pathlib import Path
from collections import Counter

DB = Path.home() / "music_dna" / "knowledge.json"


def analyze():

    print("=== EVIDENCE ENGINE v1 ===")
    print()

    if not DB.exists():
        print("Brak knowledge.json")
        return {}

    songs = json.loads(DB.read_text())

    evidence = {
        "tracks": len(songs),
        "modes": Counter(),
        "emotions": Counter(),
        "rules": Counter(),
    }

    for song in songs:

        mode = song.get("harmony", {}).get("mode")
        if mode:
            evidence["modes"][mode] += 1

        for emotion in song.get("emotion", {}).get("labels", []):
            evidence["emotions"][emotion] += 1

        for rule in song.get("rules", []):
            evidence["rules"][rule] += 1

    print("Liczba utworów:", evidence["tracks"])
    print()

    print("Najczęstsze emocje:")
    for k, v in evidence["emotions"].most_common():
        print(f"{k}: {v}")

    print()

    print("Najczęstsze reguły:")
    for k, v in evidence["rules"].most_common():
        print(f"{k}: {v}")

    return evidence


if __name__ == "__main__":
    analyze()
