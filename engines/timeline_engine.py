import json
import sys
from pathlib import Path

def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

dna=load(sys.argv[1])

print("="*60)
print("MUSIC DNA TIMELINE")
print("="*60)

structure=dna.get("structure",[])
journey=dna.get("journey",[])
curve=dna.get("curve",[])
production=dna.get("production",{})

n=max(len(structure),len(journey),len(curve))

for i in range(n):

    line=[]

    if i<len(structure):
        line.append(f"SECTION={structure[i]}")

    if i<len(journey):
        line.append(f"EMOTION={journey[i]}")

    if i<len(curve):
        line.append(f"LEVEL={curve[i]}")

    print(" | ".join(line))

print()
print("=== PRODUCTION ===")

for k,v in production.items():
    print(f"{k}: {v}")

print()
print("=== END ===")
