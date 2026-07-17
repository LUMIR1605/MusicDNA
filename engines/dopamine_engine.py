import json
import sys

dna=json.load(open(sys.argv[1],encoding="utf-8"))

print("="*60)
print("DOPAMINE DNA")
print("="*60)

expectation=0

for sec in dna["structure"]:

    typ=sec["type"]
    t=sec["start"]

    if typ=="INTRO":
        expectation=20
        dopamine=15
        state="Curiosity"

    elif typ=="VERSE":
        expectation=45
        dopamine=40
        state="Attachment"

    elif typ=="BUILD":
        expectation=95
        dopamine=85
        state="Anticipation"

    elif typ=="CHORUS":
        expectation=10
        dopamine=100
        state="Reward"

    else:
        dopamine=50
        state="Neutral"

    print(f"{t:6.1f}s")
    print(f"Brain State : {state}")
    print(f"Expectation : {expectation}%")
    print(f"Dopamine    : {dopamine}%")
    print()

