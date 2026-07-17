import subprocess
import re
import sys

def analyze_energy(audio_file):
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-i", audio_file,
        "-af", "astats=metadata=1:reset=0.1",
        "-f", "null",
        "-"
    ]

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    rms = []

    for line in result.stderr.splitlines():
        if "RMS level dB:" in line:
            m = re.search(r'RMS level dB:\s*(-?\d+\.?\d*)', line)
            if m:
                rms.append(float(m.group(1)))

    print("=== ENERGY ENGINE ===")
    print(f"Próbek RMS: {len(rms)}")

    if rms:
        print(f"Min : {min(rms):.2f} dB")
        print(f"Max : {max(rms):.2f} dB")
        print(f"Avg : {sum(rms)/len(rms):.2f} dB")

        print("\nPierwszych 20 próbek:")
        for x in rms[:20]:
            print(x)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("python energy_engine.py <plik>")
        sys.exit(1)

    analyze_energy(sys.argv[1])
