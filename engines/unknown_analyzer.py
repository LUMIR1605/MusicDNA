import glob
import json
from collections import Counter

MAP={
    "Reflection":"F001",
    "Story":"F002",
    "Longing":"F002",
    "Tension":"F003",
    "Release":"F005"
}

unknown=Counter()

for file in sorted(glob.glob("dna/*.json")):

    dna=json.load(open(file,encoding="utf-8"))

    print("\n"+"="*60)
    print(file)

    for j in dna["journey"]:

        if j["emotion"] not in MAP:

            unknown[j["emotion"]]+=1

            print(
                f"{j['start']:6.1f}s",
                j["emotion"]
            )

print("\n"+"="*60)
print("UNKNOWN SUMMARY")
print("="*60)

for k,v in unknown.items():
    print(k,":",v)
