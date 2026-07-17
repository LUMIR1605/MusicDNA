import sys
import numpy as np

from core.ffmpeg_engine import load_pcm

SR = 48000
WINDOW = SR * 5


def analyze(path):

    pcm = load_pcm(path)

    block = pcm[:WINDOW]

    if len(block) < WINDOW:
        raise RuntimeError("Plik jest za krótki.")

    block = block * np.hanning(len(block))

    fft = np.fft.rfft(block)
    freq = np.fft.rfftfreq(len(block), 1 / SR)
    amp = np.abs(fft)

    idx = np.argsort(amp)[-20:][::-1]

    print("=== SPECTRUM ENGINE ===")
    print()

    for i in idx:
        print(f"{freq[i]:8.1f} Hz   {amp[i]:12.1f}")

    peaks = []

    for i in idx:
        peaks.append({
            "freq": float(freq[i]),
            "amp": float(amp[i])
        })

    return {
        "peaks": peaks
    }


if __name__ == "__main__":
    analyze(sys.argv[1])
