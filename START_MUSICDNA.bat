@echo off
setlocal
set "MUSICDNA_ROOT=%~dp0"

where pyw >nul 2>&1
if not errorlevel 1 (
    start "" pyw "%MUSICDNA_ROOT%START_MUSICDNA.pyw"
    exit /b 0
)

where pythonw >nul 2>&1
if not errorlevel 1 (
    start "" pythonw "%MUSICDNA_ROOT%START_MUSICDNA.pyw"
    exit /b 0
)

where python >nul 2>&1
if errorlevel 1 (
    echo MusicDNA could not find Python. Re-run the MusicDNA setup instructions.
    pause
    exit /b 1
)

echo MusicDNA could not find pythonw. Opening the launcher with python instead.
echo Keep this window open while MusicDNA is running.
python "%MUSICDNA_ROOT%musicdna_launcher.py"
if errorlevel 1 pause
