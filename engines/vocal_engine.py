import sys
import numpy as np

from core.ffmpeg_engine import load_pcm

SR = 48000
WINDOW = 4096
HOP = 2048


def analyze(path):

    pcm = load_pcm(path)

    levels = []

    print("=== VOCAL ENGINE v1 ===")
    print()

    for i in range(0, len(pcm) - WINDOW, HOP):

        block = pcm[i:i + WINDOW]

        rms = np.sqrt(np.mean(block.astype(np.float64) ** 2))

        levels.append(float(rms))

    print(f"Próbek: {len(levels)}")
    print(f"Min : {min(levels):.2f}")
    print(f"Max : {max(levels):.2f}")
    print(f"Avg : {sum(levels)/len(levels):.2f}")

    return {
        "frames": len(levels),
        "min": min(levels),
        "max": max(levels),
        "avg": sum(levels) / len(levels)
    }


if __name__ == "__main__":
    analyze(sys.argv[1])
