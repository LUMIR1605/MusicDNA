import matplotlib.pyplot as plt
from energy_pcm import analyze

values = analyze("/storage/emulated/0/Download/Whitney Houston - I Will Always Love You (Official 4K Video).mp3")

plt.figure(figsize=(12,4))
plt.plot(values)
plt.title("Energy Curve")
plt.xlabel("Window (100 ms)")
plt.ylabel("RMS")
plt.grid(True)
plt.savefig("/storage/emulated/0/Download/energy_curve.png", dpi=200)

print("✓ Zapisano:")
print("/storage/emulated/0/Download/energy_curve.png")
