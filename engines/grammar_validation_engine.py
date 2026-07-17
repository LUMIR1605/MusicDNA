import glob
import json
from collections import Counter

global_patterns=Counter()
song_count={}

for file in sorted(glob.glob("dna/*.json")):

    dna=json.load(open(file,encoding="utf-8"))

    MAP={
        "Reflection":"F001",
        "Story":"F002",
        "Longing":"F002",
        "Tension":"F003",
        "Release":"F005"
    }

    seq=[MAP.get(x["emotion"]) for x in dna["journey"]]
    seq=[x for x in seq if x]

    local=set()

    for n in range(2,5):
        for i in range(len(seq)-n+1):
            p=tuple(seq[i:i+n])
            local.add(p)

    for p in local:
        global_patterns[p]+=1

songs=len(glob.glob("dna/*.json"))

print("="*70)
print("GRAMMAR VALIDATION ENGINE")
print("="*70)

for p,c in sorted(global_patterns.items(),key=lambda x:(-x[1],-len(x[0]))):

    confidence=100*c/songs

    print()
    print("Pattern    :", " → ".join(p))
    print("Songs      :", c,"/",songs)
    print(f"Confidence : {confidence:.1f}%")
