import numpy as np
from core.ffmpeg_engine import load_pcm

SR = 48000
WINDOW = 1024
HOP = 512


def detect_bpm(path):

    pcm = load_pcm(path)

    energy = []

    for i in range(0, len(pcm) - WINDOW, HOP):
        block = pcm[i:i + WINDOW]
        energy.append(np.sum(block.astype(np.float64) ** 2))

    energy = np.array(energy)

    diff = np.diff(energy)
    diff[diff < 0] = 0

    ac = np.correlate(diff, diff, mode="full")
    ac = ac[len(ac)//2:]

    min_bpm = 60
    max_bpm = 200

    min_lag = int((60 / max_bpm) * SR / HOP)
    max_lag = int((60 / min_bpm) * SR / HOP)

    lag = np.argmax(ac[min_lag:max_lag]) + min_lag

    bpm = 60 * SR / (lag * HOP)

    print("=== BPM ENGINE V2 ===")
    print(f"BPM: {bpm:.1f}")

    return bpm


if __name__ == "__main__":
    import sys
    detect_bpm(sys.argv[1])
