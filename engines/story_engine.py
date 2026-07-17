from energy_pcm import analyze

values = analyze("/storage/emulated/0/Download/Whitney Houston - I Will Always Love You (Official 4K Video).mp3")

m = max(values)

print("\n=== STORY ENGINE ===\n")

state = "low"

for i,v in enumerate(values):

    p = v/m

    if state=="low" and p>0.30:
        print(f"▲ START BUILD      {i*0.1:7.1f}s")
        state="build"

    elif state=="build" and p>0.70:
        print(f"🔥 CLIMAX          {i*0.1:7.1f}s")
        state="high"

    elif state=="high" and p<0.40:
        print(f"▼ RELEASE         {i*0.1:7.1f}s")
        state="low"

print("\nAnaliza zakończona.")
