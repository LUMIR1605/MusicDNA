# MusicDNA input usage

The ingestion command accepts one URL supported by yt-dlp or one local WAV, MP3, FLAC, M4A, OGG, OPUS, WEBM, or MP4 file. It downloads only the requested URL, normalizes all sources to mono 48 kHz PCM WAV, runs the existing MusicDNA builder, updates knowledge, and writes a short text summary.

## Setup

Install dependencies into the same Python environment that will run MusicDNA and make `ffmpeg` available on PATH:

```text
py -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.venv\Scripts\python.exe -m pip install -e .
.venv\Scripts\python.exe -c "import sys, yt_dlp; print(sys.executable); print(yt_dlp.version.__version__)"
ffmpeg -version
```

## Usage

```text
musicdna add "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
musicdna add "C:\Music\Suno exports\my song.mp3"
```

If the editable command has not been installed, run:

```text
.venv\Scripts\python.exe musicdna.py add "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

For URL inputs, yt-dlp receives the supplied URL with `--no-playlist`; it is not limited to YouTube. It stores data under `MUSICDNA_DATA_DIR` when configured; otherwise it uses the cross-platform MusicDNA data root. There, temporary URL downloads are placed in `downloads/`, normalized samples in `samples/`, DNA in `dna/`, ingestion state in `ingestion/state.json`, and summaries in `reports/`.

Re-running a completed URL or file reports it as a duplicate. Interrupted URL downloads use yt-dlp continuation and previously normalized samples resume at the analysis step. Files with identical normalized SHA-256 are deduplicated even if their names or source locations differ.
