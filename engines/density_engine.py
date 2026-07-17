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

    frame=4096
    hop=2048

    density=[]

    for i in range(0,len(audio)-frame,hop):
        x=audio[i:i+frame]
        density.append(np.sum(np.abs(x)>2000))

    density=np.array(density)

    print("=== DENSITY DNA ===")
    print("Average :",round(float(np.mean(density)),2))
    print("Peak    :",int(np.max(density)))
    print("StdDev  :",round(float(np.std(density)),2))

    return{
        "average":float(np.mean(density)),
        "peak":int(np.max(density)),
        "variation":float(np.std(density))
    }

if __name__=="__main__":
    import sys
    analyze(sys.argv[1])
