from sys import argv
import json

from engines.dna_builder import build
from brain.evidence_engine import analyze as evidence


def analyze(audio_file, title=None, metadata=None):

    print("=" * 60)
    print("MUSIC DNA PIPELINE")
    print("=" * 60)

    if isinstance(metadata, str):
        metadata = json.loads(metadata)

    dna, dna_path = build(audio_file, title, metadata)

    print()
    print("[2/5] Evidence...")
    evidence()

    import subprocess

    subprocess.run([
        "python",
        "-m",
        "brain.research_pipeline",
        str(dna_path)
    ])

    print()
    print("✓ Pipeline zakończony.")

    return dna


if __name__ == "__main__":

    title = argv[2] if len(argv) > 2 else None

    metadata = None
    if len(argv) > 3:
        metadata = argv[3]

    analyze(argv[1], title, metadata)
