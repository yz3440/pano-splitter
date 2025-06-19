@echo off
echo Installing Pano Splitter GUI...
echo.

REM Check if uv is installed
uv --version >nul 2>&1
if errorlevel 1 (
    echo uv is not installed or not in PATH
    echo Please install uv from https://docs.astral.sh/uv/getting-started/installation/
    pause
    exit /b 1
)

echo Installing dependencies...
uv sync

echo Adding PyInstaller...
uv add pyinstaller

echo Building executable...
uv run python build_gui.py

echo.
echo Installation complete!
echo The executable is in the 'dist' folder
pause
