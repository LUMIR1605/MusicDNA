import subprocess
import numpy as np
import sys

SR = 48000
WINDOW = 5
TOP = 5

cmd = [
    "ffmpeg",
    "-i", sys.argv[1],
    "-f", "s16le",
    "-acodec", "pcm_s16le",
    "-ac", "1",
    "-ar", str(SR),
    "-"
]

p = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.DEVNULL
)

samples_per_window = SR * WINDOW

print("=== SPECTRUM MAP v2 ===")
print()

sec = 0

while True:

    raw = p.stdout.read(samples_per_window * 2)

    if len(raw) < samples_per_window * 2:
        break

    samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32)

    samples *= np.hanning(len(samples))

    fft = np.fft.rfft(samples)
    amp = np.abs(fft)
    freq = np.fft.rfftfreq(len(samples), 1 / SR)

    idx = np.argsort(amp)[-TOP:][::-1]

    print(f"{sec:3d}-{sec+WINDOW:3d}s")

    for i in idx:
        print(f"    {freq[i]:8.1f} Hz   {amp[i]:12.0f}")

    print()

    sec += WINDOW
