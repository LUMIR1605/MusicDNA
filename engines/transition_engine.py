import json
import sys

dna=json.load(open(sys.argv[1],encoding="utf-8"))

print("="*60)
print("TRANSITION DNA")
print("="*60)

sections=dna["structure"]
curve=dna["curve"]

for s,c in zip(sections,curve):

    print(f"\n{s['start']:6.1f}s")

    if s["type"]=="INTRO":
        print("Introduce atmosphere")
        print("Hold back rhythm")
        print("Keep brightness low")

    elif s["type"]=="VERSE":
        print("Introduce groove")
        print("Reveal vocal")
        print("Small harmonic movement")

    elif s["type"]=="BUILD":
        print("Increase tension")
        print("Open filter")
        print("Increase brightness")
        print("Increase stereo width")
        print("Do NOT release yet")

    elif s["type"]=="CHORUS":
        print("Release energy")
        print("Full drums")
        print("Maximum width")
        print("Highest brightness")
        print("Strong hook")
