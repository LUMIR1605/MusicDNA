import glob
import json

MAP={
    "Reflection":"F001",
    "Story":"F002",
    "Longing":"F002",
    "Tension":"F003",
    "Release":"F005"
}

RULE=("F002","F003","F005")

print("="*70)
print("FALSIFICATION ENGINE")
print("="*70)

supported=[]
failed=[]

for file in sorted(glob.glob("dna/*.json")):

    dna=json.load(open(file,encoding="utf-8"))

    seq=[MAP.get(x["emotion"]) for x in dna["journey"]]
    seq=[x for x in seq if x]

    ok=False

    for i in range(len(seq)-2):
        if tuple(seq[i:i+3])==RULE:
            ok=True
            break

    title=file.split("/")[-1].replace(".json","")

    if ok:
        supported.append(title)
    else:
        failed.append(title)

print("\nSUPPORTED")
for s in supported:
    print("✓",s)

print("\nFAILED")
for s in failed:
    print("✗",s)

print("\nSupport :",len(supported))
print("Failed  :",len(failed))

confidence=100*len(supported)/(len(supported)+len(failed))
print(f"\nConfidence : {confidence:.1f}%")
