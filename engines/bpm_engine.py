import sys
import numpy as np

from core.ffmpeg_engine import load_pcm

SR = 48000
WINDOW = 1024
HOP = 512


def detect_transients(path):

    pcm = load_pcm(path)

    energy = []

    for i in range(0, len(pcm) - WINDOW, HOP):
        block = pcm[i:i + WINDOW]
        value = np.sum(block.astype(np.float64) ** 2)
        energy.append(value)

    energy = np.array(energy)

    diff = np.diff(energy)

    threshold = diff.mean() + diff.std() * 2

    transients = []

    for i, d in enumerate(diff):
        if d > threshold:
            t = (i * HOP) / SR
            transients.append(t)

    merged = []

    for t in transients:

        if not merged:
            merged.append(t)
            continue

        if t - merged[-1] > 0.05:
            merged.append(t)

    print("=== BEAT ENGINE v2 ===")
    print()

    print("Transjenty surowe :", len(transients))
    print("Po scaleniu       :", len(merged))
    print()

    for t in merged[:50]:
        print(f"{t:.3f}s")

    return merged


if __name__ == "__main__":
    detect_transients(sys.argv[1])
