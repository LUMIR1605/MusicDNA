from energy_pcm import analyze

values = analyze("/storage/emulated/0/Download/Whitney Houston - I Will Always Love You (Official 4K Video).mp3")

WINDOW = 50

smooth = []

for i in range(0, len(values), WINDOW):
    chunk = values[i:i+WINDOW]
    if chunk:
        smooth.append(sum(chunk)/len(chunk))

print("\n=== SMOOTH ENERGY ===\n")
print("Punktów:", len(smooth))
print()

for i,v in enumerate(smooth):
    sec = i * WINDOW * 0.1
    print(f"{sec:6.1f}s   {v:8.1f}")

