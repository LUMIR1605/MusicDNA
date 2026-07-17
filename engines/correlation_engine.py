import json
import sys

dna=json.load(open(sys.argv[1],encoding="utf-8"))

print("="*60)
print("CORRELATION ENGINE v1")
print("="*60)

journey=dna["journey"]

last=None

stats={
    "Reflection->Story":0,
    "Story->Tension":0,
    "Tension->Release":0,
    "Release->Tension":0,
    "Release->Reflection":0
}

for j in journey:

    cur=j["emotion"]

    if last is not None:

        key=f"{last}->{cur}"

        if key in stats:
            stats[key]+=1

    last=cur

print()

for k,v in sorted(stats.items(),key=lambda x:x[1],reverse=True):

    print(f"{k:<24}{v}")

print("\nDISCOVERED RELATIONSHIPS")

for k,v in sorted(stats.items(),key=lambda x:x[1],reverse=True):

    if v>0:
        print(f"- {k} repeated {v} times.")
