@echo off
REM -----------------------------------------------------------------------------
REM IG2mp3 Windows helper
REM - Creates (if needed) a virtual environment in .venv
REM - Installs requirements
REM - Launches the Tkinter GUI
REM This avoids PowerShell execution-policy issues because it only uses CMD.
REM -----------------------------------------------------------------------------

setlocal enabledelayedexpansion

echo [IG2mp3] Preparing Python environment...

REM Detect Python launcher first, fallback to python on PATH
set "PYTHON_CMD="
where py >nul 2>&1
if %errorlevel%==0 (
    set "PYTHON_CMD=py -3"
) else (
    where python >nul 2>&1
    if %errorlevel%==0 (
        set "PYTHON_CMD=python"
    ) else (
        echo [IG2mp3] ERROR: Python 3.10+ not found. Install it from https://www.python.org/downloads/ and re-run this file.
        exit /b 1
    )
)

if not exist ".venv" (
    echo [IG2mp3] Creating virtual environment (.venv)...
    %PYTHON_CMD% -m venv .venv
    if %errorlevel% neq 0 (
        echo [IG2mp3] ERROR: Unable to create the virtual environment.
        exit /b 1
    )
)

set "VENV_PY=.venv\Scripts\python.exe"
if not exist "%VENV_PY%" (
    echo [IG2mp3] ERROR: Could not find %VENV_PY%. Delete the .venv folder and run this script again.
    exit /b 1
)

echo [IG2mp3] Upgrading pip (just in case)...
"%VENV_PY%" -m pip install --upgrade pip >nul

echo [IG2mp3] Installing required packages...
"%VENV_PY%" -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [IG2mp3] ERROR: Package installation failed.
    exit /b 1
)

echo [IG2mp3] Launching the app. Keep this window open to see logs.
"%VENV_PY%" reels_audio_box.py

echo [IG2mp3] App closed. You can close this window now.

endlocal
