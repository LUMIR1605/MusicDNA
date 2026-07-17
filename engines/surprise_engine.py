import json
import sys

dna=json.load(open(sys.argv[1],encoding="utf-8"))

print("="*60)
print("SURPRISE DNA")
print("="*60)

previous=None

for sec in dna["structure"]:

    t=sec["start"]
    typ=sec["type"]

    if previous=="BUILD" and typ=="CHORUS":
        surprise=15
        result="Expected payoff"

    elif previous=="BUILD" and typ!="CHORUS":
        surprise=95
        result="Delayed payoff"

    elif typ=="INTRO":
        surprise=35
        result="Slow reveal"

    elif typ=="VERSE":
        surprise=45
        result="Story development"

    else:
        surprise=25
        result="Natural continuation"

    print(f"{t:6.1f}s")
    print(f"Surprise : {surprise}%")
    print(f"Result   : {result}")
    print()

    previous=typ
