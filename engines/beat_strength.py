import sys
import numpy as np

from core.ffmpeg_engine import load_pcm

SR = 48000
WINDOW = 1024
HOP = 512

pcm = load_pcm(sys.argv[1])

energy = []

for i in range(0, len(pcm) - WINDOW, HOP):
    block = pcm[i:i+WINDOW]
    energy.append(np.sum(block.astype(np.float64)**2))

energy = np.array(energy)

diff = np.diff(energy)

threshold = diff.mean() + diff.std() * 2

print("=== BEAT STRENGTH ===")
print()

for i, d in enumerate(diff):

    if d > threshold:

        t = (i * HOP) / SR

        print(f"{t:8.3f}s   {d:14.0f}")
