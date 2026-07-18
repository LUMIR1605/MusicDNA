# MusicDNA private publication

MusicDNA publishes completed analyses to the private `LUMIR1605/MusicDNA-Research` repository. No environment variables, tokens, or passwords are stored by MusicDNA.

## First use

On first publication attempt, MusicDNA creates this local configuration file:

```text
Windows: %LOCALAPPDATA%\MusicDNA\publication\config.json
Termux: ~/.local/share/musicdna/publication/config.json
```

It contains only the enabled flag, repository URL, and branch. Git uses the existing Git Credential Manager, authenticated GitHub CLI session, or SSH agent.

## Automatic publication

After local DNA, Knowledge, and summary persistence succeed, `musicdna add "<url>"` publishes the completed result automatically. A failed publication never invalidates the local result and never restarts audio download or analysis.

## Retry and backfill

Run this command to publish every completed local record, including records created before publication was enabled:

```text
musicdna publish-pending
```

The desktop launcher offers the same action through **PUBLISH PENDING RESULTS**.

## Published files

Each track is written to:

```text
analyses/<video-id>_<safe-track-name>/
  analysis.json
  metadata.json
  status.json
  summary.md
```

MusicDNA never publishes WAV, MP3, downloaded media, local file paths, diagnostic logs, credentials, tokens, or temporary files.
