import json
import sys

dna=json.load(open(sys.argv[1],encoding="utf-8"))

print("="*60)
print("CAUSE & EFFECT ENGINE")
print("="*60)

mapping={
    "Reflection":(
        "Reduce musical information",
        "Increase curiosity"
    ),
    "Story":(
        "Create emotional attachment",
        "Increase empathy"
    ),
    "Tension":(
        "Delay reward",
        "Increase expectation"
    ),
    "Release":(
        "Deliver emotional payoff",
        "Reward prediction"
    )
}

for j in dna["journey"]:

    cause,effect=mapping[j["emotion"]]

    print(f"\n{j['start']:6.1f}s - {j['end']:6.1f}s")
    print(f"CAUSE  : {cause}")
    print(f"EFFECT : {effect}")

print("\nMASTER PRINCIPLE")
print("Every musical decision should change the listener's psychological state.")
