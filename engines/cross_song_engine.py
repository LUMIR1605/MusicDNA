import glob
import json
from statistics import mean

songs=[]

for f in sorted(glob.glob("dna/*.json")):

    dna=json.load(open(f,encoding="utf-8"))

    duration=dna["journey"][-1]["end"]

    release=sum(1 for j in dna["journey"] if j["emotion"]=="Release")
    tension=sum(1 for j in dna["journey"] if j["emotion"]=="Tension")
    reflection=sum(1 for j in dna["journey"] if j["emotion"]=="Reflection")
    longing=sum(1 for j in dna["journey"] if j["emotion"]=="Longing")

    songs.append({
        "title":f.split("/")[-1].replace(".json",""),
        "duration":duration,
        "release":release,
        "tension":tension,
        "reflection":reflection,
        "longing":longing,
        "reward_density":release/(duration/60),
        "tension_density":tension/(duration/60),
        "reward_ratio":release/max(tension,1)
    })

print("="*70)
print("CROSS SONG DISCOVERY ENGINE")
print("="*70)

for s in songs:
    print()
    print(s["title"])
    print(f"Reward density : {s['reward_density']:.2f}")
    print(f"Tension density: {s['tension_density']:.2f}")
    print(f"Reward ratio   : {s['reward_ratio']:.2f}")

print()
print("="*70)
print("AVERAGES")
print("="*70)

print("Reward density :",round(mean(s["reward_density"] for s in songs),2))
print("Tension density:",round(mean(s["tension_density"] for s in songs),2))
print("Reward ratio   :",round(mean(s["reward_ratio"] for s in songs),2))

print()
print("Songs analysed :",len(songs))
