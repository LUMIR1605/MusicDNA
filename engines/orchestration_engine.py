import json
import sys

dna=json.load(open(sys.argv[1],encoding="utf-8"))

print("="*60)
print("ORCHESTRATION DNA")
print("="*60)

for s,e,c in zip(dna["structure"],dna["journey"],dna["curve"]):

    level=c["score"]

    if level<40:
        layers=2
    elif level<60:
        layers=4
    elif level<80:
        layers=6
    else:
        layers=8

    print(f"\n{s['start']:6.1f}s -> {s['end']:6.1f}s")
    print(f"Section : {s['type']}")
    print(f"Emotion : {e['emotion']}")
    print(f"Energy  : {level}")
    print(f"Layers  : {layers}")

    if s["type"]=="INTRO":
        print("Pads")
        print("Piano")
    elif s["type"]=="VERSE":
        print("Pads")
        print("Bass")
        print("Kick")
        print("Vocal")
    elif s["type"]=="BUILD":
        print("Snare Roll")
        print("Risers")
        print("Filter Automation")
    elif s["type"]=="CHORUS":
        print("Full Drums")
        print("Sub Bass")
        print("Lead Synth")
        print("Strings")
        print("Vocal Stack")
