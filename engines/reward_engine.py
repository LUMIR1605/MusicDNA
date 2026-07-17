import json
import sys

dna=json.load(open(sys.argv[1],encoding="utf-8"))

print("="*60)
print("REWARD DNA")
print("="*60)

expectation=0

for sec in dna["structure"]:

    typ=sec["type"]
    t=sec["start"]

    if typ=="INTRO":
        expectation=20
        reward=0

    elif typ=="VERSE":
        expectation=50
        reward=20

    elif typ=="BUILD":
        expectation=95
        reward=5

    elif typ=="CHORUS":
        reward=100
        expectation=10

    else:
        reward=40

    print(f"{t:6.1f}s")
    print(f"Expectation : {expectation}%")
    print(f"Reward      : {reward}%")
    print()
