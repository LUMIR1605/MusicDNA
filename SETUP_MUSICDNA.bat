@echo off
setlocal
set "MUSICDNA_ROOT=%~dp0"
pushd "%MUSICDNA_ROOT%" >nul || goto :root_error

if exist ".venv\Scripts\python.exe" goto :venv_ready
where py >nul 2>&1
if not errorlevel 1 py -3 -m venv .venv
if not errorlevel 1 goto :venv_created
where python >nul 2>&1
if errorlevel 1 goto :python_missing
python -m venv .venv
if errorlevel 1 goto :venv_error
:venv_created
set "MUSICDNA_VENV_CREATED=1"
echo [INFO] Utworzono srodowisko .venv.
:venv_ready
set "MUSICDNA_VENV_PYTHON=%CD%\.venv\Scripts\python.exe"
if not exist "%MUSICDNA_VENV_PYTHON%" goto :venv_error
if not defined MUSICDNA_VENV_CREATED echo [INFO] Uzywam istniejacego srodowiska .venv.

"%MUSICDNA_VENV_PYTHON%" -m pip install -r requirements-dev.txt
if errorlevel 1 goto :requirements_error
"%MUSICDNA_VENV_PYTHON%" -m pip install -e .
if errorlevel 1 goto :project_error
"%MUSICDNA_VENV_PYTHON%" -c "import numpy, yt_dlp; print('Python packages: numpy OK, yt_dlp OK')"
if errorlevel 1 goto :python_package_error

"%MUSICDNA_VENV_PYTHON%" -c "import imageio_ffmpeg, shutil, sys; source=imageio_ffmpeg.get_ffmpeg_exe(); target=__import__('pathlib').Path(sys.executable).parent / 'ffmpeg.exe'; shutil.copy2(source, target) if not target.exists() else None; print('ffmpeg:', target)"
if errorlevel 1 goto :ffmpeg_missing
set "PATH=%CD%\.venv\Scripts;%PATH%"

call :configure_ffmpeg
if not defined MUSICDNA_FFMPEG_DIR goto :ffmpeg_missing
ffmpeg -version >nul 2>&1
if errorlevel 1 goto :ffmpeg_missing

echo.
echo [GOTOWE] MusicDNA jest zainstalowane.
echo [GOTOWE] numpy i yt_dlp sa dostepne w .venv.
echo [GOTOWE] ffmpeg: %MUSICDNA_FFMPEG_DIR%ffmpeg.exe
echo Uruchom MusicDNA przez START_MUSICDNA.bat.
popd >nul
exit /b 0

:root_error
echo [BLAD] Nie mozna otworzyc folderu MusicDNA.
goto :failed
:python_missing
echo [BLAD] Nie znaleziono Pythona. Zainstaluj Python 3.10 lub nowszy i uruchom ten plik ponownie.
goto :failed
:venv_error
echo [BLAD] Nie udalo sie utworzyc .venv.
goto :failed
:requirements_error
echo [BLAD] Nie udalo sie zainstalowac requirements-dev.txt. Sprawdz polaczenie z internetem i uruchom ponownie.
goto :failed
:project_error
echo [BLAD] Nie udalo sie zainstalowac projektu MusicDNA.
goto :failed
:python_package_error
echo [BLAD] Brakuje numpy lub yt_dlp w .venv.
goto :failed
:ffmpeg_missing
echo [BLAD] Nie udalo sie przygotowac ffmpeg.exe w .venv ani znalezc go w systemie.
echo Sprawdz polaczenie z internetem, a nastepnie uruchom ponownie SETUP_MUSICDNA.bat.
goto :failed
:failed
popd >nul
pause
exit /b 2

:configure_ffmpeg
set MUSICDNA_FFMPEG_DIR=
for /f "delims=" %%F in ('where ffmpeg.exe 2^>nul') do if not defined MUSICDNA_FFMPEG_DIR set "MUSICDNA_FFMPEG_DIR=%%~dpF"
if not defined MUSICDNA_FFMPEG_DIR if exist "C:\Program Files\ffmpeg\bin\ffmpeg.exe" set "MUSICDNA_FFMPEG_DIR=C:\Program Files\ffmpeg\bin\"
if not defined MUSICDNA_FFMPEG_DIR if exist "C:\Program Files\Gyan.FFmpeg\bin\ffmpeg.exe" set "MUSICDNA_FFMPEG_DIR=C:\Program Files\Gyan.FFmpeg\bin\"
if not defined MUSICDNA_FFMPEG_DIR if exist "C:\ffmpeg\bin\ffmpeg.exe" set "MUSICDNA_FFMPEG_DIR=C:\ffmpeg\bin\"
if not defined MUSICDNA_FFMPEG_DIR for /f "delims=" %%F in ('dir /b /s "%LOCALAPPDATA%\Microsoft\WinGet\Packages\ffmpeg.exe" 2^>nul') do set "MUSICDNA_FFMPEG_DIR=%%~dpF"
if defined MUSICDNA_FFMPEG_DIR set "PATH=%MUSICDNA_FFMPEG_DIR%;%PATH%"
exit /b 0
