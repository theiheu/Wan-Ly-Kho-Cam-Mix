#!/usr/bin/env python3
"""
Simple EXE Builder - Clean Implementation
Creates a standalone executable using PyInstaller
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def main():
    """Build standalone executable"""

    print("🏭 Simple EXE Builder")
    print("=" * 40)

    try:
        # Project paths
        project_root = Path(__file__).parent.parent.parent
        main_script = project_root / "main.py"
        output_dir = project_root / "installer" / "output"

        # Validate main script
        if not main_script.exists():
            print(f"❌ Main script not found: {main_script}")
            input("Press Enter to exit...")
            return

        print(f"📁 Project root: {project_root}")
        print(f"🎯 Main script: {main_script}")
        print(f"📦 Output directory: {output_dir}")

        # Clean previous builds
        for cleanup_dir in ["dist", "build"]:
            cleanup_path = project_root / cleanup_dir
            if cleanup_path.exists():
                print(f"🧹 Cleaning {cleanup_dir}...")
                shutil.rmtree(cleanup_path)

        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        # Build command
        cmd = [
            "pyinstaller",
            "--onefile",
            "--windowed",
            "--name=ChickenFarmManager",
            f"--distpath={output_dir}",
            "--clean",
            "--noconfirm",
            str(main_script)
        ]

        # Add icon if available
        icon_path = project_root / "installer" / "resources" / "app_icon.ico"
        if icon_path.exists():
            cmd.extend(["--icon", str(icon_path)])

        print("🔨 Building executable...")
        print(f"Command: {' '.join(cmd)}")

        # Run build
        result = subprocess.run(cmd, cwd=project_root)

        # Check result
        exe_file = output_dir / "ChickenFarmManager.exe"

        if result.returncode == 0 and exe_file.exists():
            size_mb = exe_file.stat().st_size / (1024 * 1024)
            print(f"✅ Build successful!")
            print(f"📦 File: {exe_file}")
            print(f"📏 Size: {size_mb:.1f} MB")
        else:
            print("❌ Build failed!")

    except Exception as e:
        print(f"❌ Error: {e}")

    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
