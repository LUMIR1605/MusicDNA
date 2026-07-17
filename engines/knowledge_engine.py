import json
from pathlib import Path

from core.paths import knowledge_database_path, write_json_atomic

def analyze(title, dna, metadata=None, database_path=None):

    database_file = Path(database_path) if database_path is not None else knowledge_database_path()

    print("=== KNOWLEDGE ENGINE v1 ===")
    print()

    if database_file.exists():
        database = json.loads(database_file.read_text(encoding="utf-8"))
    else:
        database = []

    entry = {
        "title": title,
        "youtube": metadata or {},
        **dna
    }

    database = [x for x in database if Path(x.get("title","")).name != Path(title).name]
    database.append(entry)

    write_json_atomic(database_file, database)

    print(f"Zapisano utworów: {len(database)}")

    return database


if __name__ == "__main__":
    print("Knowledge Engine działa jako moduł dna_builder.")
