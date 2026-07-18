# MusicDNA TASK-003 usage

The ingestion command accepts one YouTube video URL, downloads only that requested video, extracts a WAV sample, runs the existing MusicDNA builder, updates knowledge, and writes a short text summary.

## Setup

Install dependencies and make `ffmpeg` available on PATH:

```text
python -m pip install -r requirements.txt
python -m pip install -e .
```

## Usage

```text
musicdna add "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

If the editable command has not been installed, run:

```text
python musicdna.py add "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

The command rejects playlists and channels. It stores data under `MUSICDNA_DATA_DIR` when configured; otherwise it uses the cross-platform MusicDNA data root. There, samples are placed in `samples/`, DNA in `dna/`, ingestion state in `ingestion/state.json`, and summaries in `reports/`.

Re-running a completed URL reports it as a duplicate. Interrupted downloads use yt-dlp continuation and previously downloaded samples resume at the analysis step.
