import json
from pathlib import Path

DB = Path.home() / "music_dna" / "knowledge.json"

def analyze():
    print("=" * 60)
    print("BPM REASONING")
    print("=" * 60)
    print()

    if not DB.exists():
        print("Brak knowledge.json")
        return

    songs = json.loads(DB.read_text())

    bpms = []

    for song in songs:
        bpm = song.get("bpm")
        if bpm:
            bpms.append((song["title"], bpm))

    if not bpms:
        print("Brak danych BPM.")
        return

    for title, bpm in bpms:
        print(f"{Path(title).name}")
        print(f"  BPM: {bpm:.1f}")
        print()

    avg = sum(b for _, b in bpms) / len(bpms)

    print("-" * 60)
    print(f"Średnie BPM bazy: {avg:.1f}")

if __name__ == "__main__":
    analyze()
