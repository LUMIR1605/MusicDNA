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
    timeline = []

    for i in range(0, len(pcm), WINDOW):

        block = pcm[i:i+WINDOW]

        if len(block) < WINDOW:
            break

        value = rms(block)

        values.append(value)

        timeline.append({
            "time": round(i / SR, 2),
            "value": round(value, 2)
        })

    return {
        "min": round(min(values),2),
        "max": round(max(values),2),
        "avg": round(sum(values)/len(values),2),
        "frames": len(values),
        "timeline": timeline
    }

if __name__ == "__main__":
    from pprint import pprint
    pprint(analyze(sys.argv[1]))
