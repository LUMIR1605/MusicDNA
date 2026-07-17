from pathlib import Path

SUPPORTED = {".mp3", ".wav", ".flac", ".m4a", ".ogg"}

def load_audio(path):
    path = Path(path).expanduser()

    if not path.exists():
        raise FileNotFoundError(f"Nie znaleziono pliku: {path}")

    if path.suffix.lower() not in SUPPORTED:
        raise ValueError(f"Nieobsługiwany format: {path.suffix}")

    return {
        "path": str(path),
        "name": path.name,
        "extension": path.suffix.lower(),
        "size": path.stat().st_size
    }

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Użycie:")
        print("python file_loader.py <plik_audio>")
        raise SystemExit(1)

    info = load_audio(sys.argv[1])

    print("=== FILE INFO ===")
    for k, v in info.items():
        print(f"{k}: {v}")
