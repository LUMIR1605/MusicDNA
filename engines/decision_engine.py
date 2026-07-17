import json
import sys

dna=json.load(open(sys.argv[1],encoding="utf-8"))

print("="*60)
print("PRODUCER DECISION DNA")
print("="*60)

for s,e in zip(dna["structure"], dna["journey"]):

    print(f"\n{s['start']:6.1f}s")

    if s["type"]=="INTRO":
        print("Decision : Delay gratification.")
        print("Reason   : Build curiosity before revealing the song.")

    elif s["type"]=="VERSE":
        print("Decision : Tell the story.")
        print("Reason   : Create emotional attachment.")

    elif s["type"]=="BUILD":
        print("Decision : Increase anticipation.")
        print("Reason   : The brain expects a reward.")

    elif s["type"]=="CHORUS":
        print("Decision : Deliver emotional reward.")
        print("Reason   : Maximum emotional payoff after tension.")

print("\nEND")
