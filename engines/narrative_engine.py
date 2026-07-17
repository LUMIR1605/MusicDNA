import subprocess
import sys

def detect_changes(audio_file):
    cmd = [
        "aubioonset",
        "-i",
        audio_file
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(result.stderr)

    points = []

    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue

        try:
            points.append(float(line))
        except ValueError:
            pass

    print("=== NARRATIVE ENGINE ===")
    print(f"Wykryto {len(points)} punktów zmian\n")

    print("Pierwsze 30 zmian:")

    for p in points[:30]:
        print(f"{p:.3f} s")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("python narrative_engine.py <plik>")
        sys.exit(1)

    detect_changes(sys.argv[1])
