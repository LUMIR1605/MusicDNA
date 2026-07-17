import json
from pathlib import Path

DB = Path.home() / "music_dna" / "knowledge.json"


def analyze():

    if not DB.exists():
        print("Brak knowledge.json")
        return

    songs = json.loads(DB.read_text())

    if len(songs) < 2:
        print("Potrzeba minimum dwóch utworów.")
        return

    src = songs[0]
    dst = songs[1]

    print("=" * 60)
    print("ADVISOR ENGINE")
    print("=" * 60)
    print()

    if src["harmony"]["mode"] != dst["harmony"]["mode"]:
        print("• Zmień tryb:", src["harmony"]["mode"], "→", dst["harmony"]["mode"])

    if src["harmony"]["key"] != dst["harmony"]["key"]:
        print("• Zmień tonację:", src["harmony"]["key"], "→", dst["harmony"]["key"])

    diff = dst["energy"]["avg"] - src["energy"]["avg"]

    if abs(diff) > 300:
        if diff > 0:
            print(f"• Zwiększ energię o około {diff:.0f}")
        else:
            print(f"• Zmniejsz energię o około {abs(diff):.0f}")

    missing = (
        set(dst["emotion"]["labels"]) -
        set(src["emotion"]["labels"])
    )

    if missing:
        print("• Dodaj emocje:", ", ".join(sorted(missing)))

    extra = (
        set(src["emotion"]["labels"]) -
        set(dst["emotion"]["labels"])
    )

    if extra:
        print("• Ogranicz emocje:", ", ".join(sorted(extra)))

    print()
    print("Analiza zakończona.")


if __name__ == "__main__":
    analyze()
