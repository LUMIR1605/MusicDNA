import json
from pathlib import Path

DB = Path.home() / "music_dna" / "knowledge.json"


def analyze():

    print("=" * 60)
    print("MASTER BRAIN")
    print("=" * 60)
    print()

    if not DB.exists():
        print("Brak knowledge.json")
        return

    songs = json.loads(DB.read_text())

    if len(songs) < 2:
        print("Potrzeba minimum dwóch utworów.")
        return

    source = songs[0]
    target = songs[1]

    print("UTWÓR ŹRÓDŁOWY")
    print(Path(source["title"]).name)
    print()

    print("UTWÓR DOCELOWY")
    print(Path(target["title"]).name)
    print()

    print("PODSUMOWANIE")
    print("-" * 60)

    if source["harmony"]["mode"] != target["harmony"]["mode"]:
        print("✓ Zmień tryb:",
              source["harmony"]["mode"],
              "→",
              target["harmony"]["mode"])

    if source["harmony"]["key"] != target["harmony"]["key"]:
        print("✓ Zmień tonację:",
              source["harmony"]["key"],
              "→",
              target["harmony"]["key"])

    energy = target["energy"]["avg"] - source["energy"]["avg"]

    if abs(energy) > 300:
        print(f"✓ Korekta energii: {energy:+.0f}")

    add = set(target["emotion"]["labels"]) - set(source["emotion"]["labels"])
    remove = set(source["emotion"]["labels"]) - set(target["emotion"]["labels"])

    if add:
        print("✓ Dodaj emocje:", ", ".join(sorted(add)))

    if remove:
        print("✓ Ogranicz emocje:", ", ".join(sorted(remove)))

    print()
    print("Wniosek:")
    print("To pierwszy raport decyzyjny Music DNA.")


if __name__ == "__main__":
    analyze()
