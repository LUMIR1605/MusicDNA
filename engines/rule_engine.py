import glob
import json
import os
from collections import defaultdict

MAP={
    "Reflection":"F001",
    "Story":"F002",
    "Longing":"F002",
    "Tension":"F003",
    "Hope":"F004",
    "Release":"F005"
}

rules=defaultdict(lambda:{"yes":0,"no":0})

files=sorted(glob.glob("dna/*.json"))

for file in files:

    dna=json.load(open(file,encoding="utf-8"))
    title=os.path.basename(file)

    instrumental="Tiësto" in title

    funcs=set()

    for j in dna["journey"]:
        f=MAP.get(j["emotion"])
        if f:
            funcs.add(f)

    for f in ["F001","F002","F003","F004","F005"]:

        key=("instrumental",f)

        if instrumental and f in funcs:
            rules[key]["yes"]+=1
        elif instrumental:
            rules[key]["no"]+=1

        key=("vocal",f)

        if (not instrumental) and f in funcs:
            rules[key]["yes"]+=1
        elif not instrumental:
            rules[key]["no"]+=1

print("="*70)
print("RULE ENGINE")
print("="*70)

for (cond,f),v in sorted(rules.items()):

    total=v["yes"]+v["no"]

    if total==0:
        continue

    conf=100*v["yes"]/total

    print()
    print(f"IF {cond}")
    print(f"THEN {f}")
    print(f"Confidence : {conf:.1f}%")
