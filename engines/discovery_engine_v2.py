import json
import sys

dna=json.load(open(sys.argv[1],encoding="utf-8"))

print("="*60)
print("DISCOVERY ENGINE v2")
print("="*60)

journey=dna["journey"]

laws=[]

for i in range(len(journey)-1):

    a=journey[i]["emotion"]
    b=journey[i+1]["emotion"]

    laws.append((a,b))

counts={}

for law in laws:
    counts[law]=counts.get(law,0)+1

print("\nDISCOVERED RELATIONSHIPS\n")

for (a,b),n in sorted(counts.items(),key=lambda x:x[1],reverse=True):
    print(f"{a:12} -> {b:12} {n}")

print("\nCANDIDATE LAWS\n")

total=len(laws)

for (a,b),n in sorted(counts.items(),key=lambda x:x[1],reverse=True):

    confidence=100*n/total

    if confidence>=20:

        print(f"LAW : {a} -> {b}")
        print(f"Evidence   : {n}/{total}")
        print(f"Confidence : {confidence:.1f}%")
        print()
