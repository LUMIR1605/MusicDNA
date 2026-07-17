import json
from pathlib import Path

DB = Path.home() / "music_dna" / "knowledge.json"


def analyze():

    print("=== INTELLIGENCE ENGINE v1 ===\n")

    if not DB.exists():
        print("Brak knowledge.json")
        return

    songs = json.loads(DB.read_text())

    print(f"Baza wiedzy: {len(songs)} utworów\n")

    for song in songs:

        title = Path(song["title"]).name
        mode = song.get("harmony", {}).get("mode", "?")
        key = song.get("harmony", {}).get("key", "?")
        emotions = ", ".join(song.get("emotion", {}).get("labels", []))
        energy = round(song.get("energy", {}).get("avg", 0), 1)

        print("=" * 60)
        print(title)
        print(f"Tonacja : {key} {mode}")
        print(f"Energia : {energy}")
        print(f"Emocje  : {emotions}")

    print("\n=== KONIEC ===")


if __name__ == "__main__":
    analyze()
