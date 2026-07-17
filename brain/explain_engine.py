import json
from pathlib import Path

DB = Path.home() / "music_dna" / "knowledge.json"


def explain(a, b):

    score = 0

    print("=" * 60)
    print("EXPLAIN ENGINE")
    print("=" * 60)
    print()

    emotions = set(a["emotion"]["labels"]) & set(b["emotion"]["labels"])

    if emotions:
        pts = len(emotions) * 15
        score += pts
        print(f"+{pts}  Wspólne emocje: {', '.join(emotions)}")
    else:
        print("+0   Brak wspólnych emocji")

    if a["harmony"]["mode"] == b["harmony"]["mode"]:
        score += 20
        print("+20 Ten sam tryb:", a["harmony"]["mode"])
    else:
        print("+0  Inny tryb")

    diff = abs(
        a["energy"]["avg"] -
        b["energy"]["avg"]
    )

    if diff < 500:
        score += 20
        print("+20 Podobna energia")
    elif diff < 1500:
        score += 10
        print("+10 Umiarkowanie podobna energia")
    else:
        print("+0  Duża różnica energii")

    if a["harmony"]["key"] == b["harmony"]["key"]:
        score += 20
        print("+20 Ta sama tonacja")
    else:
        print("+0  Inna tonacja")

    print()
    print("=" * 60)
    print(f"WYNIK KOŃCOWY: {score}%")
    print("=" * 60)


def analyze():

    if not DB.exists():
        print("Brak knowledge.json")
        return

    songs = json.loads(DB.read_text())

    if len(songs) < 2:
        print("Potrzeba minimum dwóch utworów.")
        return

    explain(songs[0], songs[1])


if __name__ == "__main__":
    analyze()
