import subprocess
import numpy as np

def analyze(path):
    cmd = [
        "ffmpeg","-hide_banner","-loglevel","error",
        "-i",path,
        "-f","s16le",
        "-ac","1",
        "-ar","22050",
        "-"
    ]

    pcm=subprocess.check_output(cmd)
    audio=np.frombuffer(pcm,dtype=np.int16).astype(np.float32)

    frame=2048
    hop=512

    energy=[]

    for i in range(0,len(audio)-frame,hop):
        energy.append(np.mean(np.abs(audio[i:i+frame])))

    energy=np.array(energy)

    diff=np.diff(energy)
    pulse=float(np.std(diff))
    groove=float(np.mean(np.abs(diff)))

    print("=== GROOVE DNA ===")
    print("Groove :",round(groove,2))
    print("Pulse  :",round(pulse,2))

    return {
        "groove":groove,
        "pulse":pulse
    }

if __name__=="__main__":
    import sys
    analyze(sys.argv[1])
