import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
from core.ffmpeg_engine import load_pcm, SR

FRAME = 4096
HOP = 2048

def analyze(path):

    pcm = load_pcm(path)

    timeline=[]

    for i in range(0,len(pcm)-FRAME,HOP):

        frame=pcm[i:i+FRAME]

        spec=np.abs(np.fft.rfft(frame*np.hanning(FRAME)))

        freqs=np.fft.rfftfreq(FRAME,1/SR)

        centroid=np.sum(freqs*spec)/(np.sum(spec)+1e-9)

        if centroid<900:
            label="Dark"
        elif centroid<1800:
            label="Warm"
        elif centroid<3500:
            label="Bright"
        else:
            label="Very Bright"

        timeline.append({
            "time":round(i/SR,2),
            "centroid":round(float(centroid),1),
            "label":label
        })

    return {
        "frames":len(timeline),
        "timeline":timeline
    }

if __name__=="__main__":
    from pprint import pprint
    pprint(analyze(sys.argv[1]))
