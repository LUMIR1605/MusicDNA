import subprocess
import numpy as np

def analyze(path):

    cmd=[
        "ffmpeg","-hide_banner","-loglevel","error",
        "-i",path,
        "-f","s16le",
        "-ac","1",
        "-ar","22050",
        "-"
    ]

    pcm=subprocess.check_output(cmd)

    audio=np.frombuffer(pcm,dtype=np.int16).astype(np.float32)

    frame=22050*5
    hop=frame

    prev=None
    timeline=[]

    print("=== DELTA SPECTRUM DNA ===")

    for i in range(0,len(audio)-frame,hop):

        chunk=audio[i:i+frame]

        spec=np.abs(np.fft.rfft(chunk))

        spec=spec/(spec.sum()+1e-9)

        if prev is not None:

            delta=float(np.sum(np.abs(spec-prev)))

            sec=i/22050

            print(f"{sec:6.1f}s  Δ={delta:.4f}")

            timeline.append({
                "time":round(sec,1),
                "delta":delta
            })

        prev=spec

    return timeline

if __name__=="__main__":
    import sys
    analyze(sys.argv[1])
