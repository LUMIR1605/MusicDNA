import sys
import subprocess
from pathlib import Path

if len(sys.argv) < 2:
    print("Usage: python -m brain.research_pipeline <dna.json>")
    sys.exit(1)

dna = Path(sys.argv[1])

ENGINES = [
    "engines/fact_engine.py",
    "engines/feature_engine.py",
    "engines/hypothesis_generator.py",
    "engines/psychological_function_engine.py",
    "engines/sequence_engine.py",
    "engines/grammar_engine.py",
    "engines/function_validator.py",
    "engines/music_genome_engine.py",
]

print("="*70)
print("RESEARCH PIPELINE")
print("="*70)
print(dna.name)
print()

for engine in ENGINES:
    print("▶", engine)

    result = subprocess.run([
        "python",
        engine,
        str(dna)
    ])

    if result.returncode != 0:
        print(f"❌ {engine} failed")
        sys.exit(result.returncode)

print()
print("="*70)
print("RESEARCH COMPLETE")
print("="*70)
