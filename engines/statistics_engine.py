import json
from pathlib import Path
from statistics import mean

DB = Path.home() / "music_dna" / "knowledge.json"

def analyze():

    print("=== STATISTICS ENGINE ===\n")

    if not DB.exists():
        print("Brak knowledge.json")
        return

    songs = json.loads(DB.read_text())

    if not songs:
        print("Baza jest pusta.")
        return

    energies = [s["energy"]["avg"] for s in songs if "energy" in s]
    beats = [s["beats"]["count"] for s in songs if "beats" in s]

    print(f"Liczba utworów : {len(songs)}")
    print(f"Średnia energia: {mean(energies):.1f}")
    print(f"Średnia liczba beatów: {mean(beats):.1f}")

