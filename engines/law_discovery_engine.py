import json
import sys

dna=json.load(open(sys.argv[1],encoding="utf-8"))

print("="*60)
print("LAW DISCOVERY ENGINE v1")
print("="*60)

journey=dna["journey"]

last=None

for j in journey:

    e=j["emotion"]

    if last is not None:

        if last=="Reflection" and e!="Reflection":
            print("\nLAW")
            print("Curiosity is created before emotional attachment.")

        elif last=="Story" and e=="Tension":
            print("\nLAW")
            print("Emotional attachment precedes anticipation.")

        elif last=="Tension" and e=="Release":
            print("\nLAW")
            print("Reward appears only after expectation.")

        elif last=="Release" and e=="Tension":
            print("\nLAW")
            print("Expectation is rebuilt immediately after reward.")

    last=e

print("\nSUMMARY")
print("- Curiosity precedes attachment.")
print("- Attachment precedes anticipation.")
print("- Anticipation precedes reward.")
print("- Reward immediately creates new anticipation.")
print("- Emotional journey is cyclical, not linear.")
