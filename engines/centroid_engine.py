import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import sys
import numpy as np

from core.ffmpeg_engine import load_pcm, SR

FRAME=4096
HOP=2048

pcm=load_pcm(sys.argv[1])

print("="*60)
print("SPECTRAL CENTROID DNA")
print("="*60)

window=np.hanning(FRAME)

for i in range(0,len(pcm)-FRAME,HOP):

    frame=pcm[i:i+FRAME]*window

    spec=np.abs(np.fft.rfft(frame))

    freqs=np.fft.rfftfreq(FRAME,1/SR)

    if spec.sum()==0:
        continue

    centroid=(spec*freqs).sum()/spec.sum()

    t=i/SR

    print(f"{t:7.2f}s  {centroid:8.1f} Hz")
