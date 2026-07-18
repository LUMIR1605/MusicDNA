# MusicDNA desktop launcher

## One-time setup

From the MusicDNA repository directory:

```text
python -m pip install -r requirements.txt
python -m pip install -e .
```

Install FFmpeg and open a new PowerShell window before the first run, as described in the setup notes.

## Start MusicDNA without a terminal

Double-click either file in the repository directory:

- `START_MUSICDNA.pyw` is the preferred Windows launcher and opens no terminal.
- `START_MUSICDNA.bat` first uses `pyw` or `pythonw`. If neither is available, it opens the GUI through `python` and explains why its small command window remains open.

To add a desktop shortcut, right-click `START_MUSICDNA.pyw` in File Explorer and choose **Show more options** then **Send to > Desktop (create shortcut)**.

The launcher uses the same ingestion pipeline as `musicdna add`. It writes samples, DNA, knowledge, import state, and reports only through the existing MusicDNA data-path policy. It does not use OneDrive-specific paths.
