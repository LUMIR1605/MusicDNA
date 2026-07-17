import subprocess
import re

def value(pattern, text):
    m = re.search(pattern, text)
    return float(m.group(1)) if m else None

def analyze(audio):

    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-i", audio,
        "-af",
        "ebur128,astats=metadata=1:reset=0,aspectralstats=measure=centroid",
        "-f",
        "null",
        "-"
    ]

    r = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    log = r.stderr

    lufs = value(r"I:\s*(-?[0-9.]+)\s*LUFS", log)
    crest = value(r"Crest factor:\s*([0-9.]+)", log)
    dynamic = value(r"Dynamic range:\s*([0-9.]+)", log)
    centroid = value(r"Centroid:\s*([0-9.]+)", log)

    print("=== PRODUCTION DNA v2 ===")
    print(f"LUFS      : {lufs}")
    print(f"Crest     : {crest}")
    print(f"Dynamic   : {dynamic}")
    print(f"Centroid  : {centroid}")

    return {
        "lufs": lufs,
        "crest": crest,
        "dynamic_range": dynamic,
        "spectral_centroid": centroid
    }

if __name__ == "__main__":
    import sys
    analyze(sys.argv[1])
