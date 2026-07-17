import sys
import numpy as np

from core.ffmpeg_engine import load_pcm

SR = 48000
WINDOW = 4096
HOP = 2048


def analyze_pitch(path):

    pcm = load_pcm(path)

    pitches = []

    print("=== PITCH ENGINE v2 ===")
    print()

    for i in range(0, len(pcm) - WINDOW, HOP):

        block = pcm[i:i + WINDOW]
        block = block * np.hanning(len(block))

        fft = np.fft.rfft(block)
        amp = np.abs(fft)

        idx = np.argmax(amp)
        freq = idx * SR / WINDOW

        if 50 <= freq <= 2000:
            pitches.append(freq)

    print("Próbek:", len(pitches))

    if pitches:
        print("Min :", round(min(pitches), 2))
        print("Max :", round(max(pitches), 2))
        print("Avg :", round(sum(pitches) / len(pitches), 2))

    return {
        "frames": len(pitches),
        "min": min(pitches) if pitches else 0,
        "max": max(pitches) if pitches else 0,
        "avg": sum(pitches) / len(pitches) if pitches else 0,
        "values": pitches[:200]
    }


if __name__ == "__main__":
    analyze_pitch(sys.argv[1])
