import json
import sys

dna=json.load(open(sys.argv[1],encoding="utf-8"))

MAP={
    "Reflection":"F001 Create Curiosity",
    "Story":"F002 Build Attachment",
    "Longing":"F002 Build Attachment",
    "Tension":"F003 Increase Anticipation",
    "Release":"F005 Deliver Reward",
    "Hope":"F004 Sustain Expectation"
}

print("="*70)
print("PSYCHOLOGICAL FUNCTION ENGINE")
print("="*70)

timeline=[]

for j in dna["journey"]:
    f=MAP.get(j["emotion"],"UNKNOWN")
    timeline.append({
        "time":round(j["start"],1),
        "function":f
    })
    print(f"{j['start']:6.1f}s  {f}")

json.dump(
    timeline,
    open("psychological_functions.json","w",encoding="utf-8"),
    indent=2,
    ensure_ascii=False
)

print()
print("Saved: psychological_functions.json")
