import json
import sys

dna=json.load(open(sys.argv[1],encoding="utf-8"))

print("="*60)
print("DISCOVERED PRINCIPLES")
print("="*60)

journey=dna["journey"]

for j in journey:
    e=j["emotion"]

    print(f"\n{j['start']:6.1f}s - {j['end']:6.1f}s")

    if e=="Reflection":
        print("Principle:")
        print("Create emotional space before giving information.")
        print("The listener must become curious.")

    elif e=="Story":
        print("Principle:")
        print("Build emotional attachment before increasing intensity.")

    elif e=="Tension":
        print("Principle:")
        print("Increase desire.")
        print("Do NOT satisfy the listener yet.")

    elif e=="Release":
        print("Principle:")
        print("Reward accumulated expectation.")
        print("Deliver maximum emotional payoff.")

print("\nGLOBAL PRINCIPLES")
print("- Curiosity before attachment.")
print("- Attachment before tension.")
print("- Tension before reward.")
print("- Every reward must be earned.")
print("- Never reveal everything too early.")
print("- Finish with emotional resolution.")
