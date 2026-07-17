import sys
import numpy as np

from core.ffmpeg_engine import load_pcm

SR = 48000
WINDOW = 4096
HOP = 2048

NOTE_NAMES = [
    "C", "C#", "D", "D#", "E", "F",
    "F#", "G", "G#", "A", "A#", "B"
]


def analyze(path):

    pcm = load_pcm(path)

    chroma = np.zeros(12, dtype=np.float64)

    for i in range(0, len(pcm) - WINDOW, HOP):

        block = pcm[i:i + WINDOW]

        block = block * np.hanning(len(block))

        fft = np.fft.rfft(block)

        amp = np.abs(fft)

        freq = np.fft.rfftfreq(len(block), 1 / SR)

        for f, a in zip(freq, amp):

            if f < 40 or f > 5000:
                continue

            midi = int(round(69 + 12 * np.log2(f / 440.0)))

            chroma[midi % 12] += a

    idx = int(np.argmax(chroma))

    key = NOTE_NAMES[idx]

    total = float(np.sum(chroma))

    confidence = 0.0

    if total > 0:
        confidence = float(chroma[idx] / total)

    mode = "major"

    if chroma[(idx + 3) % 12] > chroma[(idx + 4) % 12]:
        mode = "minor"

    print("=== HARMONY ENGINE v1 ===")
    print()
    print("Key        :", key)
    print("Mode       :", mode)
    print("Confidence :", round(confidence, 3))

    return {
        "key": key,
        "mode": mode,
        "confidence": confidence,
        "chroma": chroma.tolist()
    }


if __name__ == "__main__":
    analyze(sys.argv[1])
