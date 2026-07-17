import json
import sys

dna=json.load(open(sys.argv[1],encoding="utf-8"))

print("="*60)
print("SIGNAL ENGINE v1")
print("="*60)

journey=dna["journey"]

events=[]

for i in range(1,len(journey)):

    prev=journey[i-1]
    cur=journey[i]

    if prev["emotion"]!=cur["emotion"]:

        events.append({
            "time":cur["start"],
            "from":prev["emotion"],
            "to":cur["emotion"]
        })

for e in events:

    print(f"\n{e['time']:6.1f}s")
    print(f"{e['from']}  --->  {e['to']}")

    if e["to"]=="Tension":
        print("SIGNAL : Emotional pressure increasing")

    elif e["to"]=="Release":
        print("SIGNAL : Emotional reward")

    elif e["to"]=="Story":
        print("SIGNAL : Emotional attachment")

    elif e["to"]=="Reflection":
        print("SIGNAL : Emotional breathing")

print("\nSUMMARY")

print(f"Transitions : {len(events)}")

reward=sum(1 for e in events if e["to"]=="Release")
tension=sum(1 for e in events if e["to"]=="Tension")

print(f"Reward events      : {reward}")
print(f"Anticipation events: {tension}")

if reward>0:
    print("\nHYPOTHESIS")
    print("The song is driven by repeated reward cycles.")
