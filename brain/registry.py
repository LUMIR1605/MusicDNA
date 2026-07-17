import json
from pathlib import Path

REGISTRY = Path.home() / "music_dna" / "registry.json"


def load():
    if REGISTRY.exists():
        return json.loads(REGISTRY.read_text())
    return []


def save(data):
    REGISTRY.write_text(json.dumps(data, indent=2))


def exists(path):
    data = load()
    return path in data


def add(path):
    data = load()
    if path not in data:
        data.append(path)
        save(data)
