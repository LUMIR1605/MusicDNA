import glob
import subprocess
import os

files = sorted(glob.glob("samples/*.mp3"))

print("="*70)
print("MUSIC DNA - ANALYZE ALL")
print("="*70)
print("Songs found:", len(files))
print()

for i, f in enumerate(files, 1):

    print("="*70)
    print(f"[{i}/{len(files)}] {os.path.basename(f)}")
    print("="*70)

    subprocess.run(
        ["python", "-m", "brain.pipeline", f],
        check=False
    )

print()
print("="*70)
print("REBUILD KNOWLEDGE")
print("="*70)

engines = [
    "engines/knowledge_graph_engine.py",
    "engines/research_engine.py",
    "engines/scientific_engine.py",
    "engines/counter_evidence_engine.py",
    "engines/cross_song_engine.py",
    "engines/statistical_discovery_engine.py"
]

for e in engines:
    print()
    print("Running:", e)
    subprocess.run(["python", e], check=False)

print()
print("="*70)
print("DONE")
print("="*70)
