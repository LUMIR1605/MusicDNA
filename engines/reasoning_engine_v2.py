import json
import sys

with open(sys.argv[1], encoding="utf-8") as f:
    dna=json.load(f)

structure=dna["structure"]
journey=dna["journey"]
curve=dna["curve"]

print("="*60)
print("MUSIC DNA REASONING")
print("="*60)

for s,e,c in zip(structure,journey,curve):

    section=s["type"]
    emotion=e["emotion"]
    level=c["score"]

    if section=="INTRO":
        goal="Build curiosity and emotional space."

    elif section=="VERSE":
        goal="Tell the emotional story."

    elif section=="BUILD":
        goal="Increase anticipation before reward."

    elif section=="CHORUS":
        goal="Deliver maximum emotional payoff."

    else:
        goal="Transition."

    print(f"""
{s['start']:6.1f}s - {s['end']:6.1f}s

SECTION : {section}
EMOTION : {emotion}
LEVEL   : {level}

GOAL
{goal}
""")
