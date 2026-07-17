import json
import glob
from collections import defaultdict

print("="*60)
print("MUSIC DNA RESEARCH ENGINE")
print("="*60)

rules=defaultdict(int)
songs=0

for file in glob.glob("dna/*.json"):
    songs+=1

    dna=json.load(open(file,encoding="utf-8"))

    for rule in dna.get("rules",[]):
        rules[rule]+=1

print()

for rule,count in sorted(rules.items(),key=lambda x:x[1],reverse=True):

    confidence=round(count/songs*100,1)

    if confidence>=90:
        level="UNIVERSAL CANDIDATE"
    elif confidence>=70:
        level="STRONG"
    elif confidence>=50:
        level="MODERATE"
    else:
        level="WEAK"

    print(f"{confidence:5.1f}%   {level:20}   {rule}")

print()
print("Songs analysed:",songs)
