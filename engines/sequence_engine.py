import json
from collections import Counter

data=json.load(open("psychological_functions.json",encoding="utf-8"))

seq=[x["function"].split()[0] for x in data]

pairs=Counter()

for i in range(len(seq)-1):
    pairs[(seq[i],seq[i+1])]+=1

triples=Counter()

for i in range(len(seq)-2):
    triples[(seq[i],seq[i+1],seq[i+2])]+=1

quads=Counter()

for i in range(len(seq)-3):
    quads[(seq[i],seq[i+1],seq[i+2],seq[i+3])]+=1

print("="*70)
print("SEQUENCE ENGINE")
print("="*70)

print("\nTOP PAIRS")
for k,v in pairs.most_common(10):
    print(" → ".join(k),":",v)

print("\nTOP TRIPLES")
for k,v in triples.most_common(10):
    print(" → ".join(k),":",v)

print("\nTOP QUADS")
for k,v in quads.most_common(10):
    print(" → ".join(k),":",v)
