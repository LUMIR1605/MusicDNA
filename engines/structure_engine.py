import sys
import numpy as np

from engines.energy_pcm import analyze as energy_analyze


SR = 48000
FRAME_TIME = 0.1


def analyze(path):

    print("=== STRUCTURE ENGINE ===")
    print()

    energy = energy_analyze(path)

    energy = np.array(energy, dtype=float)

    if len(energy) == 0:
        return []

    smooth = np.convolve(energy, np.ones(25) / 25, mode="same")

    maximum = smooth.max()

    sections = []

    current = None
    start = 0

    for i, value in enumerate(smooth):

        ratio = value / maximum

        if ratio < 0.20:
            label = "INTRO"

        elif ratio < 0.45:
            label = "VERSE"

        elif ratio < 0.70:
            label = "BUILD"

        else:
            label = "CHORUS"

        if current is None:
            current = label
            start = i
            continue

        if label != current:

            sections.append({
                "type": current,
                "start": start * FRAME_TIME,
                "end": i * FRAME_TIME
            })

            current = label
            start = i

    sections.append({
        "type": current,
        "start": start * FRAME_TIME,
        "end": len(smooth) * FRAME_TIME
    })

    for s in sections:
        print(
            f"{s['start']:7.1f}s - "
            f"{s['end']:7.1f}s   "
            f"{s['type']}"
        )

    return sections


if __name__ == "__main__":
    analyze(sys.argv[1])
