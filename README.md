# MusicDNA

MusicDNA analyzes one source at a time without changing the existing analysis engines. `musicdna add` and the Windows launcher accept:

- one `http` or `https` URL supported by yt-dlp (including a single YouTube link);
- one local `WAV`, `MP3`, `FLAC`, `M4A`, `OGG`, `OPUS`, `WEBM`, or `MP4` file, including Suno exports.

Every source is normalized with ffmpeg to mono, 48 kHz PCM WAV before it reaches the existing engines. URL download, WAV normalization, analysis, SHA-256 duplicate detection, resumable state, report workspace, and private publication are separate stages.

## Setup and checks

Use the same Python environment for the launcher and the command line. On Windows, an isolated environment is the most reliable setup:

```text
py -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.venv\Scripts\python.exe -m pip install -e .
```

Install ffmpeg and make `ffmpeg.exe` available on `PATH`, then verify the exact runtime used by MusicDNA:

```text
.venv\Scripts\python.exe -c "import sys, yt_dlp; print(sys.executable); print(yt_dlp.version.__version__)"
ffmpeg -version
```

`START_MUSICDNA.bat` prefers `.venv\Scripts\pythonw.exe` when it exists, so the GUI uses that same environment.

## Analyze a link or Suno file

```text
musicdna add "https://youtu.be/H1HdZFgR-aA"
musicdna add "C:\Music\Suno exports\Mój utwór.mp3"
```

If the editable command has not been installed, replace `musicdna` with `.venv\Scripts\python.exe musicdna.py`. To use the GUI, double-click `START_MUSICDNA.bat`, paste a URL or select **CHOOSE LOCAL FILE**, then press **START**.

Re-running the same source resumes from the persisted stage. Different URLs or local files with the same normalized SHA-256 are not analyzed twice. Local file paths are kept out of the desktop workspace and the `MusicDNA-Research` publication package.

## Troubleshooting URL downloads

The `yt-dlp` command can work while MusicDNA fails if they are installed in different Python environments. MusicDNA intentionally runs `python -m yt_dlp` with its own interpreter, so `yt_dlp` must be installed in that interpreter. Run the first verification command above; it shows both the interpreter path and the module version. A missing `ffmpeg` is reported separately at normalization time.

## Private research publication

Successful analyses are published automatically to the private `LUMIR1605/MusicDNA-Research` repository after local DNA, Knowledge, and summary persistence complete. MusicDNA creates a credential-free local publication configuration under its application data directory on first use; GitHub authentication remains managed by Git Credential Manager, GitHub CLI, or an SSH agent.

Use `musicdna publish-pending` to retry completed local analyses without downloading or analyzing them again. See `TASK-005_USAGE.md` for the publication layout and recovery steps.

## Windows desktop launcher

After normal setup, double-click `START_MUSICDNA.bat` to open the MusicDNA desktop launcher without a terminal. `START_MUSICDNA.pyw` is also available when the Python file association points at the environment with MusicDNA installed. See `TASK-004_USAGE.md` for setup and desktop shortcut instructions.

## Historical note

The Lumir OS text below is retained as historical repository context. It is not MusicDNA setup or operating guidance.

# LUMIR OS

Jeżeli jesteś nowym modelem AI:

Przeczytaj kolejno:

1. PRIORITY.md
2. LUMIR_OS.md
3. MONEY_ENGINE.md
4. NEXT_ACTION.md
5. TOOLS.md
6. MIND_OS.md

Po przeczytaniu:

Nie proponuj nowych projektów.

Najpierw sprawdź aktualny priorytet.

Pomagaj kończyć rozpoczęte projekty.

Szukaj najlepszych możliwości monetyzacji.

Chroń czas użytkownika.

Myśl strategicznie.

Działaj jak partner projektu.
