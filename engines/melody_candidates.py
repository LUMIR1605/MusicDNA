import sys
import numpy as np

from core.ffmpeg_engine import load_pcm

SR = 48000
WINDOW = 4096
HOP = 2048
TOP = 8


def analyze(path):

    pcm = load_pcm(path)

    print("=== MELODY CANDIDATES v1 ===")
    print()

    for pos in range(0, len(pcm) - WINDOW, HOP):

        block = pcm[pos:pos + WINDOW]
        block = block * np.hanning(len(block))

        fft = np.fft.rfft(block)
        amp = np.abs(fft)
        freq = np.fft.rfftfreq(len(block), 1 / SR)

        idx = np.argsort(amp)[-TOP:][::-1]

        print(f"\n{pos/SR:8.3f}s")

        for i in idx:
            if 80 <= freq[i] <= 2000:
                print(f"    {freq[i]:8.2f} Hz    {amp[i]:12.0f}")


if __name__ == "__main__":
    analyze(sys.argv[1])
