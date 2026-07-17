import json
from pathlib import Path

from core.paths import dna_output_directory, write_text_atomic


def save(name, dna, output_directory=None):
    directory = Path(output_directory) if output_directory is not None else dna_output_directory()
    filename = directory / (Path(name).stem + ".json")
    write_text_atomic(filename, json.dumps(dna, indent=2, ensure_ascii=False))
    print(f"DNA zapisane: {filename}")
    return filename

if __name__ == "__main__":
    print("DNA Store v1")
