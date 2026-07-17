import json
import sys

dna=json.load(open(sys.argv[1],encoding="utf-8"))

print("="*60)
print("EVENT ENGINE v1")
print("="*60)

events=[]

for j in dna["journey"]:

    t=j["start"]
    emo=j["emotion"]

    if emo=="Reflection":
        events.append((t,"LOW_INFORMATION"))

    elif emo=="Story":
        events.append((t,"EMOTIONAL_ATTACHMENT"))

    elif emo=="Tension":
        events.append((t,"EXPECTATION_BUILD"))

    elif emo=="Release":
        events.append((t,"EMOTIONAL_REWARD"))

for s in dna.get("structure",[]):

    events.append((s["start"],"SECTION_"+s["type"]))

events.sort(key=lambda x:x[0])

last=None

for t,e in events:

    if last is None:
        print(f"{t:6.1f}s   {e}")
    else:
        print(f"{t:6.1f}s   {e}   (+{t-last:.1f}s)")
    last=t

print("\nSUMMARY")

counts={}

for _,e in events:
    counts[e]=counts.get(e,0)+1

for k,v in sorted(counts.items(),key=lambda x:x[1],reverse=True):
    print(f"{k:<28}{v}")
