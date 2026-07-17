import json
from pathlib import Path

DB = Path.home() / "music_dna" / "knowledge.json"


def similarity(a, b):

    score = 0

    if a["harmony"]["mode"] == b["harmony"]["mode"]:
        score += 25

    common = set(a["emotion"]["labels"]) & set(b["emotion"]["labels"])
    score += len(common) * 15

    ea = a["energy"]["avg"]
    eb = b["energy"]["avg"]

    diff = abs(ea - eb)

    if diff < 500:
        score += 30
    elif diff < 1500:
        score += 15

    return min(score, 100)


def analyze():

    songs = json.loads(DB.read_text())

    print("=== COMPARISON ENGINE ===\n")

    for i in range(len(songs)):
        for j in range(i + 1, len(songs)):

            a = songs[i]
            b = songs[j]

            s = similarity(a, b)

            print(Path(a["title"]).name)
            print("↕")
            print(Path(b["title"]).name)
            print(f"Podobieństwo: {s}%")
            print("-" * 60)


if __name__ == "__main__":
    analyze()
