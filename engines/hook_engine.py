import json
import sys

dna=json.load(open(sys.argv[1],encoding="utf-8"))

print("="*60)
print("HOOK DNA")
print("="*60)

for s,c in zip(dna["structure"],dna["curve"]):

    if s["type"]=="CHORUS" and c["score"]>=90:

        print(f"{s['start']:6.1f}s")
        print("HOOK FOUND")
        print("Repeat main melodic idea")
        print("Strong vocal")
        print("Maximum emotional release")
        print("Highest memorability\n")
