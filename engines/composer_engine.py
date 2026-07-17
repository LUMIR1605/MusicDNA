import json
import sys

with open(sys.argv[1], encoding="utf-8") as f:
    dna=json.load(f)

print("="*60)
print("COMPOSER INSTRUCTIONS")
print("="*60)

for section,emotion,curve in zip(
    dna["structure"],
    dna["journey"],
    dna["curve"]
):

    t1=round(section["start"],1)
    t2=round(section["end"],1)

    print(f"\n{t1}s - {t2}s")

    typ=section["type"]

    if typ=="INTRO":
        print("- Keep arrangement minimal.")
        print("- Introduce atmosphere slowly.")
        print("- Hide the main hook.")
        print("- Leave emotional space.")

    elif typ=="VERSE":
        print("- Tell the story.")
        print("- Keep groove controlled.")
        print("- Introduce new layers gradually.")

    elif typ=="BUILD":
        print("- Increase tension.")
        print("- Open filters.")
        print("- Add rhythmic energy.")
        print("- Delay the payoff.")

    elif typ=="CHORUS":
        print("- Open full arrangement.")
        print("- Maximum emotional impact.")
        print("- Wide stereo image.")
        print("- Strong vocal delivery.")
        print("- Full bass energy.")

print("\nEND")
