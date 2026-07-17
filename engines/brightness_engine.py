import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
from core.ffmpeg_engine import load_pcm, SR

FRAME = 4096
HOP = 2048

pcm = load_pcm(sys.argv[1])

print("="*60)
print("BRIGHTNESS DNA")
print("="*60)

for i in range(0, len(pcm)-FRAME, HOP):

    frame = pcm[i:i+FRAME]

    spec = np.abs(np.fft.rfft(frame*np.hanning(FRAME)))

    freqs = np.fft.rfftfreq(FRAME,1/SR)

    centroid = np.sum(freqs*spec)/(np.sum(spec)+1e-9)

    t = i/SR

    if int(t)%5==0 and abs((t%5))<0.05:

        if centroid<900:
            label="Dark"

        elif centroid<1800:
            label="Warm"

        elif centroid<3500:
            label="Bright"

        else:
            label="Very Bright"

        print(f"{t:6.1f}s  {centroid:7.0f} Hz   {label}")
