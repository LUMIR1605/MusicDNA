import json
import subprocess
import os
from pathlib import Path

from collectors.youtube_collector import collect

QUEUE = Path.home() / "lumir_air_v14" / "data" / "music_queue.json"


def load():
    return json.loads(QUEUE.read_text())


def save(data):
    QUEUE.write_text(json.dumps(data, indent=2))


os.makedirs("tmp", exist_ok=True)

queue = load()

for i, track in enumerate(queue, 1):

    if track["status"] != "waiting":
        continue

    print("=" * 60)
    print(f"[{i}/{len(queue)}]")
    print("Tytuł :", track["title"])
    print("Autor :", track["artist"])
    print()

    query = track.get("url","") or f'ytsearch1:{track["artist"]} {track["title"]}'
    metadata = collect(query)

    download = subprocess.run([
        "yt-dlp",
        "-x",
        "--audio-format", "mp3",
        "-o", "tmp/%(id)s.%(ext)s",
        query
    ])

    if download.returncode != 0:
        print("❌ Błąd pobierania")
        track["status"] = "error"
        save(queue)
        continue

    video_id = metadata["id"]
    audio = f"tmp/{video_id}.mp3"

    analyze = subprocess.run([
        "python",
        "-m",
        "brain.pipeline",
        audio,
        track["title"],
        json.dumps(metadata or {})
    ])

    if analyze.returncode != 0:
        print("❌ Błąd analizy")
        track["status"] = "error"
    else:
        track["status"] = "done"

    save(queue)

    if os.path.exists(audio):
        os.remove(audio)
        print("🗑 Usunięto plik audio")

    print("✓ GOTOWE\n")

print("=" * 60)
print("KOLEJKA ZAKOŃCZONA")
print("=" * 60)
