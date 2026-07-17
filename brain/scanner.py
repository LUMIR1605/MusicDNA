from pathlib import Path

EXTENSIONS = {
    ".mp3",
    ".wav",
    ".flac",
    ".m4a",
    ".ogg"
}


def scan(folder):

    folder = Path(folder)

    files = []

    for ext in EXTENSIONS:
        files.extend(folder.rglob(f"*{ext}"))

    files = sorted(files)

    print(f"Znaleziono {len(files)} plików.")

    return files
