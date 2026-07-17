import glob
import json
import os

MAP={
    "Reflection":"F001",
    "Story":"F002",
    "Longing":"F002",
    "Tension":"F003",
    "Hope":"F004",
    "Release":"F005"
}

print("="*70)
print("CONDITION ENGINE")
print("="*70)

for file in sorted(glob.glob("dna/*.json")):

    dna=json.load(open(file,encoding="utf-8"))

    title=os.path.basename(file).replace(".json","")

    instrumental = "Tiësto" in title
    vocal = not instrumental

    duration=dna["journey"][-1]["end"]

    functions=set()

    for j in dna["journey"]:
        f=MAP.get(j["emotion"])
        if f:
            functions.add(f)

    print()
    print(title)
    print("-"*60)

    print("Instrumental :",instrumental)
    print("Vocal        :",vocal)
    print("Duration     :",round(duration,1),"sec")
    print("Functions    :",", ".join(sorted(functions)))
