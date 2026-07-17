import glob
import json
from statistics import mean, median, stdev

songs=[]

for file in sorted(glob.glob("dna/*.json")):

    dna=json.load(open(file,encoding="utf-8"))

    duration=dna["journey"][-1]["end"]

    release=sum(1 for j in dna["journey"] if j["emotion"]=="Release")
    tension=sum(1 for j in dna["journey"] if j["emotion"]=="Tension")
    reflection=sum(1 for j in dna["journey"] if j["emotion"]=="Reflection")
    longing=sum(1 for j in dna["journey"] if j["emotion"]=="Longing")

    songs.append({
        "title":file.split("/")[-1].replace(".json",""),
        "reward_density":release/(duration/60),
        "tension_density":tension/(duration/60),
        "reward_ratio":release/max(tension,1),
        "release":release,
        "tension":tension
    })

def report(name):
    values=[s[name] for s in songs]

    print(f"\n{name.upper()}")
    print("-"*50)
    print("Mean   :",round(mean(values),3))
    print("Median :",round(median(values),3))

    if len(values)>1:
        print("StdDev :",round(stdev(values),3))

    print("Min    :",round(min(values),3))
    print("Max    :",round(max(values),3))

print("="*70)
print("STATISTICAL DISCOVERY ENGINE")
print("="*70)

print("Songs analysed:",len(songs))

report("reward_density")
report("tension_density")
report("reward_ratio")

print("\nTOP REWARD RATIO")
print("-"*50)

for s in sorted(songs,key=lambda x:x["reward_ratio"],reverse=True):
    print(f"{s['reward_ratio']:.2f}  {s['title']}")
