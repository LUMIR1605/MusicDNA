import json
from pathlib import Path
from collections import Counter

DB = Path.home() / "music_dna" / "knowledge.json"
REPORT = Path("research/discovery_report.json")

def analyze():
    if not DB.exists():
        print("Brak knowledge.json")
        return

    songs = json.loads(DB.read_text(encoding="utf-8"))

    emotions = Counter()
    rules = Counter()
    keys = Counter()

    for song in songs:
        for e in song.get("emotion", {}).get("labels", []):
            emotions[e] += 1

        for r in song.get("rules", []):
            rules[r] += 1

        harmony = song.get("harmony", {})
        key = harmony.get("key")
        mode = harmony.get("mode")

        if key and mode:
            keys[f"{key} {mode}"] += 1

    facts = [
        {"name": "songs_analyzed", "value": len(songs)},
        {"name": "top_emotions", "value": emotions.most_common(10)},
        {"name": "top_rules", "value": rules.most_common(10)},
        {"name": "top_keys", "value": keys.most_common(10)}
    ]

    patterns = []

    if emotions:
        e, c = emotions.most_common(1)[0]
        patterns.append(f'Najczęściej występująca emocja to "{e}" ({c} utworów).')

    if rules:
        r, c = rules.most_common(1)[0]
        patterns.append(f'Najczęściej wykrywana reguła: "{r}" ({c} utworów).')

    if keys:
        k, c = keys.most_common(1)[0]
        patterns.append(f'Najczęstsza tonacja: {k} ({c} utworów).')

    hypotheses = [
        "Zweryfikować zależność między tonacją a emocjami.",
        "Sprawdzić wpływ energii na wykrywane reguły.",
        "Porównać strukturę utworów między gatunkami.",
        "Zbadać wpływ metadanych YouTube na cechy muzyczne."
    ]

    report = {
        "facts": facts,
        "patterns": patterns,
        "hypotheses": hypotheses
    }

    REPORT.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print("=== DISCOVERY ENGINE v3 ===")
    print()
    print(f"Przeanalizowano: {len(songs)} utworów")
    print(f"Raport zapisany do: {REPORT}")

if __name__ == "__main__":
    analyze()
