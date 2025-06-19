#!/usr/bin/env python3
"""
Build script for creating a standalone executable of the Pano Splitter GUI
"""

import subprocess
import os
import sys
from pathlib import Path


def build_executable():
    """Build the standalone executable using uv and PyInstaller"""

    # Get the current directory
    current_dir = Path(__file__).parent

    # Define paths
    gui_script = current_dir / "pano_splitter_gui.py"
    icon_path = None  # You can add an icon file here if you have one

    # PyInstaller arguments
    pyinstaller_args = [
        str(gui_script),
        "--onefile",  # Create a single executable file
        "--windowed",  # Don't show console window (for GUI apps)
        "--name=PanoSplitter",  # Name of the executable
        "--add-data=pano_splitter:pano_splitter",  # Include the pano_splitter module
        "--hidden-import=numpy",
        "--hidden-import=cv2",
        "--hidden-import=PIL",
        "--hidden-import=PIL.Image",
        "--hidden-import=PIL.ImageTk",
        "--hidden-import=tkinter",
        "--hidden-import=tkinter.ttk",
        "--hidden-import=tkinter.filedialog",
        "--hidden-import=tkinter.messagebox",
        "--hidden-import=tkinter.scrolledtext",
        "--hidden-import=concurrent.futures",
        "--hidden-import=threading",
        "--hidden-import=queue",
        "--hidden-import=multiprocessing",
        "--collect-all=cv2",
        "--collect-all=numpy",
        "--collect-all=PIL",
        "--noconfirm",  # Don't ask for confirmation to overwrite
        "--clean",  # Clean PyInstaller cache
    ]

    # Add icon if available
    if icon_path and icon_path.exists():
        pyinstaller_args.extend(["--icon", str(icon_path)])

    # Add console flag for debugging (remove --windowed and add --console)
    # Uncomment the next two lines for debugging
    # pyinstaller_args.remove('--windowed')
    # pyinstaller_args.append('--console')

    print("Building Pano Splitter GUI executable...")
    print(f"GUI script: {gui_script}")
    print(f"Current directory: {current_dir}")
    print()

    try:
        # Run PyInstaller using uv
        cmd = ["uv", "run", "pyinstaller"] + pyinstaller_args
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)

        print("\n✅ Build completed successfully!")
        print("📦 Executable location: dist/PanoSplitter")
        print("\n📝 Build Information:")
        print("   - Single file executable created")
        print("   - All dependencies included")
        print("   - GUI mode (no console window)")
        print("   - Compatible with current OS")

        # Check if executable was created
        if sys.platform.startswith("win"):
            exe_path = current_dir / "dist" / "PanoSplitter.exe"
        else:
            exe_path = current_dir / "dist" / "PanoSplitter"

        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"   - Executable size: {size_mb:.1f} MB")

        print("\n🚀 You can now distribute the executable in the 'dist' folder!")

    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Build failed: {str(e)}")
        return False

    return True


def create_installer_script():
    """Create a simple installer script for different platforms"""

    current_dir = Path(__file__).parent

    # Windows batch script
    win_script = """@echo off
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
"""

    # Unix shell script
    unix_script = """#!/bin/bash
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
"""

    # Write installer scripts
    with open(current_dir / "install_windows.bat", "w") as f:
        f.write(win_script)

    with open(current_dir / "install_unix.sh", "w") as f:
        f.write(unix_script)

    # Make Unix script executable
    os.chmod(current_dir / "install_unix.sh", 0o755)

    print("📝 Created installer scripts:")
    print("   - install_windows.bat (for Windows)")
    print("   - install_unix.sh (for Linux/macOS)")


if __name__ == "__main__":
    print("🔧 Pano Splitter GUI Build Tool")
    print("=" * 40)

    # Create installer scripts
    create_installer_script()
    print()

    # Build executable
    success = build_executable()

    if success:
        print("\n🎉 Ready to use!")
        print("Run the executable from the 'dist' folder or distribute it to users.")
    else:
        print("\n❌ Build failed. Please check the error messages above.")
        sys.exit(1)
