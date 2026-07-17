import json
import sys

dna=json.load(open(sys.argv[1],encoding="utf-8"))

print("="*60)
print("ROOT CAUSE ENGINE v1")
print("="*60)

journey=dna["journey"]

for i,e in enumerate(journey):

    if e["emotion"]!="Release":
        continue

    print(f"\nRELEASE @ {e['start']:.1f}s")

    prev=journey[max(0,i-3):i]

    if not prev:
        print("No previous events.")
        continue

    print("Previous chain:")

    for p in prev:
        print(f"  {p['emotion']:12} {p['start']:6.1f}s")

    print("\nCandidate causes:")

    found=False

    if any(x["emotion"]=="Tension" for x in prev):
        print(" ✓ Tension detected")
        found=True

    if any(x["emotion"]=="Story" for x in prev):
        print(" ✓ Emotional attachment detected")
        found=True

    if any(x["emotion"]=="Reflection" for x in prev):
        print(" ✓ Curiosity phase detected")
        found=True

    if not found:
        print(" No measurable cause found.")

print("\nIMPORTANT")
print("These are candidate causes only.")
print("Validation across many songs is required.")
