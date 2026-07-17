import json
import sys

dna=json.load(open(sys.argv[1],encoding="utf-8"))

print("="*60)
print("EXPECTATION DNA")
print("="*60)

for sec,emo in zip(dna["structure"],dna["journey"]):

    t=sec["start"]
    typ=sec["type"]

    if typ=="INTRO":
        exp=20
        reason="Curiosity"

    elif typ=="VERSE":
        exp=45
        reason="Story"

    elif typ=="BUILD":
        exp=95
        reason="Brain expects emotional payoff"

    elif typ=="CHORUS":
        exp=15
        reason="Expectation released"

    else:
        exp=50
        reason="Neutral"

    print(f"{t:6.1f}s")
    print(f"Expectation : {exp}%")
    print(f"Reason      : {reason}")
    print()
