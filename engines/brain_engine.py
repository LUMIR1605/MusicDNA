import json
import sys

dna=json.load(open(sys.argv[1],encoding="utf-8"))

print("="*60)
print("BRAIN ENGINE")
print("="*60)

energy=dna["energy"]["avg"]
key=dna["harmony"]["key"]
mode=dna["harmony"]["mode"]
emo=", ".join(dna["emotion"]["labels"])

print("PRIMARY EMOTION")
print(emo)
print()

print("MUSICAL GOAL")

if mode=="major":
    print("Lead the listener from curiosity to hope.")
else:
    print("Lead the listener from uncertainty to emotional release.")

print()

print("PRODUCER STRATEGY")

print("- Delay gratification.")
print("- Build anticipation gradually.")
print("- Repeat one memorable hook.")
print("- Increase arrangement step by step.")
print("- Earn every climax.")
print("- Never begin at maximum intensity.")
print("- Finish with emotional resolution.")

print()

print("DO NOT LOSE")

print("- Emotional hook")
print("- Progressive dynamics")
print("- Contrast between tension and release")
print("- Atmospheric intro")
print("- Reflective outro")

print()

print("AI INSTRUCTION")

print("Compose a completely original song.")
print("Copy no melody.")
print("Copy no harmony.")
print("Recreate only the emotional architecture.")
