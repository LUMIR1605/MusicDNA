# MusicDNA

MusicDNA can ingest one user-requested YouTube video through the command-line pipeline documented in `TASK-003_USAGE.md`.

Quick start after installing dependencies and `ffmpeg`:

```text
musicdna add "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

Use `python musicdna.py add "<url>"` when the local command entry point has not been installed yet.

## Private research publication

Successful analyses are published automatically to the private `LUMIR1605/MusicDNA-Research` repository after local DNA, Knowledge, and summary persistence complete. MusicDNA creates a credential-free local publication configuration under its application data directory on first use; GitHub authentication remains managed by Git Credential Manager, GitHub CLI, or an SSH agent.

Use `musicdna publish-pending` to retry completed local analyses without downloading or analyzing them again. See `TASK-005_USAGE.md` for the publication layout and recovery steps.

## Windows desktop launcher

After normal setup, double-click `START_MUSICDNA.pyw` to open the MusicDNA desktop launcher without a terminal. `START_MUSICDNA.bat` is also provided for Windows systems where the Python file association is unavailable. See `TASK-004_USAGE.md` for setup and desktop shortcut instructions.

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
