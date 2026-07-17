import subprocess

FIELDS = [
    "id",
    "title",
    "uploader",
    "channel_id",
    "webpage_url",
    "duration",
    "view_count",
    "like_count",
    "upload_date",
    "categories",
    "tags",
    "description"
]

def collect(url):
    print("=== YOUTUBE COLLECTOR ===")
    print()

    fmt = "|".join(f"%({f})s" for f in FIELDS)

    cmd = [
        "yt-dlp",
        "--skip-download",
        "--print",
        fmt,
        url
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(result.stderr)
        return None

    values = result.stdout.rstrip().split("|", len(FIELDS)-1)
    info = dict(zip(FIELDS, values))

    for k, v in info.items():
        if len(str(v)) > 120:
            print(f"{k:12}: {str(v)[:120]}...")
        else:
            print(f"{k:12}: {v}")

    return info

if __name__ == "__main__":
    import sys
    collect(sys.argv[1])
