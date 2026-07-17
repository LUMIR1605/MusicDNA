import json
from pathlib import Path

OUT = Path("dna")

OUT.mkdir(exist_ok=True)

def save(name, dna):
    filename = OUT / (Path(name).stem + ".json")
    filename.write_text(
        json.dumps(dna, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    print(f"DNA zapisane: {filename}")
    return filename

if __name__ == "__main__":
    print("DNA Store v1")
