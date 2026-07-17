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

    timeline=[]

    for i in range(0,len(audio)-frame,hop):

        x=audio[i:i+frame]

        rms=np.sqrt(np.mean(x*x))

        active=np.sum(np.abs(x)>2500)

        if rms<400:
            stage="Silence"

        elif active<20000:
            stage="Intro"

        elif active<50000:
            stage="Build"

        elif active<90000:
            stage="Verse"

        else:
            stage="Full"

        sec=i/22050

        timeline.append((round(sec,1),stage))

    print("=== ARRANGEMENT DNA ===")

    for t,s in timeline:
        print(f"{t:6.1f}s   {s}")

    return timeline


if __name__=="__main__":
    import sys
    analyze(sys.argv[1])
