import sys
import numpy as np

from core.ffmpeg_engine import load_pcm

SR = 48000
WINDOW = 4096
HOP = 2048


def analyze_lead(path):

    pcm = load_pcm(path)

    print("=== LEAD ENGINE v1 ===")
    print()

    previous = None
    stable = 0

    for i in range(0, len(pcm) - WINDOW, HOP):

        block = pcm[i:i + WINDOW]
        block *= np.hanning(len(block))

        fft = np.fft.rfft(block)
        amp = np.abs(fft)

        idx = np.argmax(amp)
        freq = idx * SR / WINDOW

        if not (80 <= freq <= 2000):
            continue

        if previous is not None:

            if abs(freq - previous) < 15:
                stable += 1
            else:
                stable = 0

        previous = freq

        if stable >= 5:

            print(f"{i/SR:8.3f}s   {freq:8.2f} Hz   STABLE")
