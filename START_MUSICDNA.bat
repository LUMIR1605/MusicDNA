@echo off
setlocal
set "MUSICDNA_ROOT=%~dp0"
if exist "%MUSICDNA_ROOT%.venv\Scripts\ffmpeg.exe" set "PATH=%MUSICDNA_ROOT%.venv\Scripts;%PATH%"
call :configure_ffmpeg

if exist "%MUSICDNA_ROOT%.venv\Scripts\pythonw.exe" (
    start "" "%MUSICDNA_ROOT%.venv\Scripts\pythonw.exe" "%MUSICDNA_ROOT%START_MUSICDNA.pyw"
    exit /b 0
)

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
set "MUSICDNA_EXIT=%ERRORLEVEL%"
if not "%MUSICDNA_EXIT%"=="0" pause
exit /b %MUSICDNA_EXIT%

:configure_ffmpeg
set MUSICDNA_FFMPEG_DIR=
for /f "delims=" %%F in ('where ffmpeg.exe 2^>nul') do if not defined MUSICDNA_FFMPEG_DIR set "MUSICDNA_FFMPEG_DIR=%%~dpF"
if not defined MUSICDNA_FFMPEG_DIR if exist "C:\Program Files\ffmpeg\bin\ffmpeg.exe" set "MUSICDNA_FFMPEG_DIR=C:\Program Files\ffmpeg\bin\"
if not defined MUSICDNA_FFMPEG_DIR if exist "C:\Program Files\Gyan.FFmpeg\bin\ffmpeg.exe" set "MUSICDNA_FFMPEG_DIR=C:\Program Files\Gyan.FFmpeg\bin\"
if not defined MUSICDNA_FFMPEG_DIR if exist "C:\ffmpeg\bin\ffmpeg.exe" set "MUSICDNA_FFMPEG_DIR=C:\ffmpeg\bin\"
if not defined MUSICDNA_FFMPEG_DIR for /f "delims=" %%F in ('dir /b /s "%LOCALAPPDATA%\Microsoft\WinGet\Packages\ffmpeg.exe" 2^>nul') do set "MUSICDNA_FFMPEG_DIR=%%~dpF"
if defined MUSICDNA_FFMPEG_DIR set "PATH=%MUSICDNA_FFMPEG_DIR%;%PATH%"
exit /b 0
