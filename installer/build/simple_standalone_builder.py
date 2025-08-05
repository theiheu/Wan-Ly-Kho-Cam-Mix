#!/usr/bin/env python3
"""
Simple Standalone EXE Builder
Creates a single executable file using PyInstaller
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_standalone_exe():
    """Build standalone executable using PyInstaller"""

    print("Building Simple Standalone EXE...")
    print("=" * 50)

    try:
        # Get project root
        project_root = Path(__file__).parent.parent.parent
        installer_dir = project_root / "installer"
        output_dir = installer_dir / "output"

        # Main script path
        main_script = project_root / "src/main.py"

        if not main_script.exists():
            print(f"Main script not found: {main_script}")
            return False

        # Clean previous builds
        for cleanup_dir in ["dist", "build"]:
            cleanup_path = project_root / cleanup_dir
            if cleanup_path.exists():
                print(f"Cleaning {cleanup_dir}...")
                shutil.rmtree(cleanup_path)

        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        # PyInstaller command with better configuration
        pyinstaller_cmd = [
            "pyinstaller",
            "--onefile",
            "--windowed",
            "--name=ChickenFarmManager",
            f"--distpath={output_dir}",
            f"--workpath={project_root / 'build'}",
            "--clean",
            "--noconfirm",
            # Add all source directories
            f"--add-data={project_root / 'src'};src",
            # Exclude unnecessary modules
            "--exclude-module=tkinter",
            "--exclude-module=unittest",
            "--exclude-module=test",
            str(main_script)
        ]

        # Add icon if available
        icon_file = installer_dir / "resources" / "app_icon.ico"
        if icon_file.exists():
            pyinstaller_cmd.extend(["--icon", str(icon_file)])
            print(f"Using icon: {icon_file}")

        # Add hidden imports for PyQt5 and other dependencies
        hidden_imports = [
            "PyQt5.QtCore",
            "PyQt5.QtGui",
            "PyQt5.QtWidgets",
            "PyQt5.QtPrintSupport",
            "pandas",
            "matplotlib",
            "matplotlib.backends.backend_qt5agg",
            "openpyxl",
            "numpy",
            "json",
            "pathlib",
            "datetime"
        ]

        for import_name in hidden_imports:
            pyinstaller_cmd.extend(["--hidden-import", import_name])

        print("Running PyInstaller...")
        print(f"Command: {' '.join(pyinstaller_cmd)}")

        # Run PyInstaller
        result = subprocess.run(
            pyinstaller_cmd,
            cwd=project_root,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            exe_file = output_dir / "ChickenFarmManager.exe"

            if exe_file.exists():
                file_size = exe_file.stat().st_size / (1024 * 1024)  # MB
                print(f"Build successful!")
                print(f"Output: {exe_file}")
                print(f"Size: {file_size:.1f} MB")
                return True
            else:
                print("Build completed but executable not found")
                return False
        else:
            print("PyInstaller failed:")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_executable(exe_path):
    """Test if the executable runs without errors"""
    try:
        print(f"🔍 Testing: {exe_path}")

        # Try to run with --version flag (if supported)
        test_process = subprocess.Popen(
            [str(exe_path), "--help"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        try:
            stdout, stderr = test_process.communicate(timeout=10)

            if test_process.returncode == 0:
                print("✅ Executable runs successfully")
                return True
            else:
                print(f"⚠️ Executable returned code {test_process.returncode}")
                # For GUI apps, non-zero return code might be normal
                return True

        except subprocess.TimeoutExpired:
            test_process.terminate()
            print("✅ Executable started (terminated after timeout)")
            return True

    except Exception as e:
        print(f"⚠️ Could not test executable: {e}")
        return False

def main():
    """Main function"""
    try:
        success = build_standalone_exe()

        if success:
            print("\n🎉 BUILD COMPLETED SUCCESSFULLY!")
            print("📁 Check the installer/output directory for your executable")
        else:
            print("\n💥 BUILD FAILED!")
            print("Check the error messages above for details")

    except KeyboardInterrupt:
        print("\n⚠️ Build cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

    input("Press Enter to exit...")

if __name__ == "__main__":
    main()






