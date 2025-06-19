#!/bin/bash
echo "Installing Pano Splitter GUI..."
echo

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "uv is not installed or not in PATH"
    echo "Please install uv from https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi

echo "Installing dependencies..."
uv sync

echo "Adding PyInstaller..."
uv add pyinstaller

echo "Building executable..."
uv run python build_gui.py

echo
echo "Installation complete!"
echo "The executable is in the 'dist' folder"
