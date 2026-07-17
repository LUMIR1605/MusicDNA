import json
import sys

dna=json.load(open(sys.argv[1],encoding="utf-8"))

print("="*60)
print("STATE ENGINE v1")
print("="*60)

mapping={
    "Reflection":"Curiosity",
    "Story":"Attachment",
    "Tension":"Expectation",
    "Release":"Reward"
}

journey=dna["journey"]

states=[]

for j in journey:
    states.append(mapping[j["emotion"]])

transitions={}

for i in range(len(states)-1):

    a=states[i]
    b=states[i+1]

    transitions.setdefault(a,{})
    transitions[a][b]=transitions[a].get(b,0)+1

print("\nSTATE TIMELINE\n")

for j,s in zip(journey,states):
    print(f"{j['start']:6.1f}s   {s}")

print("\nSTATE TRANSITIONS\n")

for a in transitions:

    total=sum(transitions[a].values())

    for b,count in transitions[a].items():

        p=100*count/total

        print(f"{a:<15} -> {b:<15} {count:2d} ({p:5.1f}%)")

print("\nDISCOVERED MODEL\n")

for a in transitions:

    best=max(transitions[a],key=transitions[a].get)

    print(f"{a}  →  {best}")

print("\nSUMMARY")

print("This song behaves like a state machine.")
