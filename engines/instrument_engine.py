import subprocess

BANDS = {
    "Sub Bass": (20,60),
    "Bass": (60,250),
    "Low Mid": (250,500),
    "Mid": (500,2000),
    "Presence": (2000,6000),
    "Air": (6000,16000),
}

def analyze(audio):

    print("=== INSTRUMENT DNA v1 ===")
    print()

    result = {}

    for name,(low,high) in BANDS.items():

        cmd=[
            "ffmpeg",
            "-hide_banner",
            "-i",audio,
            "-af",f"bandpass=f={(low+high)//2}:width={high-low},volumedetect",
            "-f","null","-"
        ]

        r=subprocess.run(cmd,stderr=subprocess.PIPE,text=True)

        volume=None

        for line in r.stderr.splitlines():
            if "mean_volume:" in line:
                volume=float(line.split(":")[-1].replace(" dB","").strip())

        result[name]=volume
        print(f"{name:<10}: {volume}")

    return result

if __name__=="__main__":
    import sys
    analyze(sys.argv[1])
