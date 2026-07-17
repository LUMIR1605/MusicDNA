import sys
import numpy as np

from core.ffmpeg_engine import load_pcm

SR = 48000
WINDOW = 4096
HOP = 2048

def analyze(path):
    pcm = load_pcm(path)

    notes = []
    last = None

    for i in range(0, len(pcm) - WINDOW, HOP):
        block = pcm[i:i+WINDOW] * np.hanning(WINDOW)

        fft = np.fft.rfft(block)
        amp = np.abs(fft)

        idx = np.argmax(amp)
        freq = idx * SR / WINDOW

        if not (80 <= freq <= 2000):
            continue

        if last is None:
            move = "START"
        else:
            d = freq - last
            if abs(d) < 8:
                move = "→"
            elif d > 0:
                move = "↑"
            else:
                move = "↓"

        notes.append({
            "time": i / SR,
            "freq": float(freq),
            "move": move
        })

        last = freq

    print("=== MELODY TRACKER v2 ===")
    print("Próbek:", len(notes))

    return notes

if __name__ == "__main__":
    data = analyze(sys.argv[1])

    print("Pierwsze 20 nut:")
    for n in data[:20]:
        print(f"{n['time']:7.3f}s  {n['freq']:8.2f} Hz  {n['move']}")
