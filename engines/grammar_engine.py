import json
from collections import Counter

seq=json.load(open("psychological_functions.json",encoding="utf-8"))
tokens=[x["function"].split()[0] for x in seq]

rules=Counter()

for n in range(2,7):
    for i in range(len(tokens)-n+1):
        rules[tuple(tokens[i:i+n])]+=1

print("="*70)
print("GRAMMAR ENGINE")
print("="*70)

for rule,count in sorted(rules.items(),key=lambda x:(-x[1],-len(x[0]))):

    if count<2:
        continue

    print()
    print("Pattern :", " → ".join(rule))
    print("Length  :", len(rule))
    print("Count   :", count)
