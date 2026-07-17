import math
import sys
import numpy as np

from core.ffmpeg_engine import load_pcm

SR = 48000
WINDOW = int(SR * 0.1)


def rms(block):
    if len(block) == 0:
        return 0.0

    return math.sqrt(np.mean(block.astype(np.float64) ** 2))


def analyze(path):

    pcm = load_pcm(path)

    values = []

    for i in range(0, len(pcm), WINDOW):

        block = pcm[i:i + WINDOW]

        if len(block) < WINDOW:
            break

        values.append(rms(block))

    print("=== ENERGY PCM ===")
    print("Próbek:", len(values))

    if values:
        print("Min :", round(min(values), 2))
        print("Max :", round(max(values), 2))
        print("Avg :", round(sum(values) / len(values), 2))

    return values


if __name__ == "__main__":
    analyze(sys.argv[1])
