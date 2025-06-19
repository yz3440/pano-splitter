#!/usr/bin/env python3
"""
Script to prepare release assets and generate checksums for GitHub release
"""

import hashlib
import zipfile
import tarfile
import shutil
from pathlib import Path
import sys
import platform


def calculate_sha256(file_path):
    """Calculate SHA256 hash of a file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


def get_file_size_mb(file_path):
    """Get file size in MB"""
    return round(file_path.stat().st_size / (1024 * 1024), 1)


def create_release_assets():
    """Create release assets from the built executable"""

    current_dir = Path(__file__).parent
    dist_dir = current_dir / "dist"
    release_dir = current_dir / "release"

    # Create release directory
    release_dir.mkdir(exist_ok=True)

    # Check if executable exists
    executable_path = dist_dir / "PanoSplitter"
    if not executable_path.exists():
        print("❌ Executable not found. Please run 'uv run python build_gui.py' first.")
        return False

    # Determine platform
    current_platform = platform.system().lower()

    if current_platform == "darwin":
        platform_name = "macos"
        archive_name = f"PanoSplitter-{platform_name}.zip"

        # Create ZIP for macOS
        with zipfile.ZipFile(
            release_dir / archive_name, "w", zipfile.ZIP_DEFLATED
        ) as zipf:
            zipf.write(executable_path, "PanoSplitter")
            # Add .app if it exists
            app_path = dist_dir / "PanoSplitter.app"
            if app_path.exists():
                for file_path in app_path.rglob("*"):
                    if file_path.is_file():
                        arcname = file_path.relative_to(dist_dir)
                        zipf.write(file_path, arcname)

    elif current_platform == "windows":
        platform_name = "windows"
        archive_name = f"PanoSplitter-{platform_name}.exe"

        # For Windows, just copy the .exe
        exe_path = dist_dir / "PanoSplitter.exe"
        if exe_path.exists():
            shutil.copy2(exe_path, release_dir / archive_name)
        else:
            shutil.copy2(executable_path, release_dir / archive_name)

    else:  # Linux
        platform_name = "linux"
        archive_name = f"PanoSplitter-{platform_name}.tar.gz"

        # Create TAR.GZ for Linux
        with tarfile.open(release_dir / archive_name, "w:gz") as tarf:
            tarf.add(executable_path, arcname="PanoSplitter")

    # Calculate checksums and sizes
    asset_path = release_dir / archive_name
    sha256 = calculate_sha256(asset_path)
    size_mb = get_file_size_mb(asset_path)

    print(f"✅ Created release asset: {archive_name}")
    print(f"📦 Size: {size_mb} MB")
    print(f"🔐 SHA256: {sha256}")

    # Create checksums file
    checksums_file = release_dir / "checksums.txt"
    with open(checksums_file, "w") as f:
        f.write(f"{sha256}  {archive_name}\n")

    print(f"📝 Checksums saved to: {checksums_file}")

    # Update the release notes with actual values
    update_release_notes(platform_name, archive_name, size_mb, sha256)

    return True


def update_release_notes(platform_name, archive_name, size_mb, sha256):
    """Update the release notes with actual values"""

    release_notes_path = Path(__file__).parent / "RELEASE_NOTES.md"

    if not release_notes_path.exists():
        return

    with open(release_notes_path, "r") as f:
        content = f.read()

    # Platform mapping for display
    platform_display = {
        "macos": "macOS (Intel/Apple Silicon)",
        "windows": "Windows (64-bit)",
        "linux": "Linux (64-bit)",
    }

    # Replace placeholder values
    old_line = f"| {platform_display.get(platform_name, platform_name)} | `PanoSplitter-{platform_name}.zip` | ~60MB | `[hash]` |"
    new_line = f"| {platform_display.get(platform_name, platform_name)} | `{archive_name}` | {size_mb}MB | `{sha256[:16]}...` |"

    if platform_name == "windows":
        old_line = f"| {platform_display.get(platform_name, platform_name)} | `PanoSplitter-windows.exe` | ~65MB | `[hash]` |"
    elif platform_name == "linux":
        old_line = f"| {platform_display.get(platform_name, platform_name)} | `PanoSplitter-linux.tar.gz` | ~58MB | `[hash]` |"

    content = content.replace(old_line, new_line)

    with open(release_notes_path, "w") as f:
        f.write(content)

    print(f"📝 Updated release notes for {platform_name}")


def create_github_action_info():
    """Create information for GitHub Actions release"""

    info = {
        "tag_name": "v0.0.1",
        "release_name": "Pano Splitter GUI v0.0.1 - Complete Panoramic Image Converter",
        "body": "See RELEASE_NOTES.md for full details",
        "draft": True,
        "prerelease": False,
    }

    return info


if __name__ == "__main__":
    print("🔧 Preparing Release Assets")
    print("=" * 40)

    if create_release_assets():
        print("\n✅ Release preparation complete!")
        print("\nNext steps:")
        print("1. Review the generated assets in the 'release/' folder")
        print("2. Copy the content from RELEASE_NOTES.md for your GitHub release")
        print("3. Upload the assets to GitHub releases")
        print("4. Use the SHA256 checksums for security verification")

        # Show GitHub CLI command if available
        print("\nOptional: If you have GitHub CLI installed:")
        print(
            "gh release create v0.0.1 release/* --title 'Pano Splitter GUI v0.0.1' --notes-file RELEASE_NOTES.md"
        )

    else:
        print("\n❌ Release preparation failed!")
        sys.exit(1)
