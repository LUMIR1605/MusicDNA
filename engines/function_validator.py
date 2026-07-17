import glob
import json

MAP={
    "Reflection":"F001",
    "Story":"F002",
    "Longing":"F002",
    "Tension":"F003",
    "Hope":"F004",
    "Release":"F005"
}

stats={}
songs=sorted(glob.glob("dna/*.json"))

for file in songs:

    dna=json.load(open(file,encoding="utf-8"))

    used=set()

    for j in dna["journey"]:
        f=MAP.get(j["emotion"])
        if f:
            used.add(f)

    print("\n"+file)

    for f in sorted(used):
        print(" ",f)

    for f in used:
        stats[f]=stats.get(f,0)+1

coverage={}

print("\n"+"="*60)
print("FUNCTION COVERAGE")
print("="*60)

for f in sorted(stats):

    c=round(stats[f]*100/len(songs),1)
    coverage[f]=c

    print(f"{f}: {stats[f]}/{len(songs)} ({c}%)")

json.dump(
    coverage,
    open("function_coverage.json","w",encoding="utf-8"),
    indent=2
)

print("\nSaved: function_coverage.json")
