import json
import sys

dna=json.load(open(sys.argv[1],encoding="utf-8"))

print("="*60)
print("LAYER DNA")
print("="*60)

for s in dna["structure"]:

    t=s["type"]

    if t=="INTRO":
        print(f"{s['start']:6.1f}s Piano ON")
        print(f"{s['start']:6.1f}s Pads ON")

    elif t=="VERSE":
        print(f"{s['start']:6.1f}s Kick ON")
        print(f"{s['start']:6.1f}s Bass ON")
        print(f"{s['start']:6.1f}s Vocal ON")

    elif t=="BUILD":
        print(f"{s['start']:6.1f}s Riser ON")
        print(f"{s['start']:6.1f}s Filter OPEN")

    elif t=="CHORUS":
        print(f"{s['start']:6.1f}s Full Drums")
        print(f"{s['start']:6.1f}s Strings")
        print(f"{s['start']:6.1f}s Lead Synth")
        print(f"{s['start']:6.1f}s Vocal Stack")
