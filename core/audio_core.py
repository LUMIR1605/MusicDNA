import subprocess
import json
import sys

def analyze_audio(path):
    cmd = [
        "ffprobe",
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(result.stderr)

    data = json.loads(result.stdout)

    stream = data["streams"][0]
    fmt = data["format"]

    print("\n=== AUDIO CORE ===")
    print(f"Nazwa: {fmt['filename']}")
    print(f"Czas: {fmt['duration']} s")
    print(f"Bitrate: {fmt['bit_rate']} bps")
    print(f"Format: {fmt['format_name']}")
    print(f"Sample Rate: {stream['sample_rate']} Hz")
    print(f"Kanały: {stream['channels']}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Użycie:")
        print("python audio_core.py <plik>")
        sys.exit(1)

    analyze_audio(sys.argv[1])
