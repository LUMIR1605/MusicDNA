import json
import glob
from collections import defaultdict

print("="*60)
print("COUNTER EVIDENCE ENGINE")
print("="*60)

laws=defaultdict(lambda:{"yes":[],"no":[]})

files=sorted(glob.glob("dna/*.json"))

for file in files:

    dna=json.load(open(file,encoding="utf-8"))

    title=file.split("/")[-1].replace(".json","")

    present=set(dna.get("rules",[]))

    all_rules=set()

    for f in files:
        d=json.load(open(f,encoding="utf-8"))
        all_rules.update(d.get("rules",[]))

    for rule in all_rules:

        if rule in present:
            laws[rule]["yes"].append(title)
        else:
            laws[rule]["no"].append(title)

for rule,data in sorted(laws.items()):

    print("\n"+"="*60)
    print(rule)

    print("\nSUPPORTED :",len(data["yes"]))
    for s in data["yes"]:
        print(" ✓",s)

    print("\nNOT FOUND :",len(data["no"]))
    for s in data["no"]:
        print(" ✗",s)
