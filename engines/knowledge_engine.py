import json
from pathlib import Path

DB = Path.home() / "music_dna" / "knowledge.json"

def analyze(title, dna, metadata=None):

    print("=== KNOWLEDGE ENGINE v1 ===")
    print()

    if DB.exists():
        database = json.loads(DB.read_text())
    else:
        database = []

    entry = {
        "title": title,
        "youtube": metadata or {},
        **dna
    }

    database = [x for x in database if Path(x.get("title","")).name != Path(title).name]
    database.append(entry)

    DB.write_text(json.dumps(database, indent=2))

    print(f"Zapisano utworów: {len(database)}")

    return database


if __name__ == "__main__":
    print("Knowledge Engine działa jako moduł dna_builder.")
