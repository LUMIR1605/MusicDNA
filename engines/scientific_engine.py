import json
import glob
from collections import defaultdict

print("="*60)
print("SCIENTIFIC ENGINE")
print("="*60)

laws=defaultdict(list)

for file in sorted(glob.glob("dna/*.json")):

    dna=json.load(open(file,encoding="utf-8"))

    title=file.split("/")[-1].replace(".json","")

    for rule in dna.get("rules",[]):

        laws[rule].append(title)

print()

for rule,songs in sorted(laws.items(),key=lambda x:len(x[1]),reverse=True):

    n=len(songs)

    if n<5:
        level="OBSERVATION"
    elif n<20:
        level="HYPOTHESIS"
    elif n<50:
        level="CANDIDATE LAW"
    elif n<100:
        level="STRONG LAW"
    else:
        level="UNIVERSAL LAW"

    print("="*60)
    print(rule)
    print("Status :",level)
    print("Evidence:",n,"song(s)")
    print()

    for s in songs:
        print(" ✓",s)

print("\nTOTAL SONGS:",len(glob.glob("dna/*.json")))
