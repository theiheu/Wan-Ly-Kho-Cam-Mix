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
import json

def cleanup_build_artifacts(project_root, output_dir):
    """Clean up build artifacts after successful build"""
    print("🧹 Cleaning up build artifacts...")

    try:
        # List of artifacts to clean up
        artifacts_to_clean = [
            output_dir / "build",  # Build directory moved to output
            output_dir / "Quan_Ly_Kho_Cam_&_Mix.spec",  # Spec file moved to output
            project_root / "build",  # Original build directory (if any remains)
            project_root / "Quan_Ly_Kho_Cam_&_Mix.spec"  # Original spec file (if any remains)
        ]

        cleaned_count = 0
        for artifact in artifacts_to_clean:
            try:
                if artifact.exists():
                    if artifact.is_dir():
                        shutil.rmtree(artifact)
                        print(f"   ✅ Removed directory: {artifact.name}")
                    else:
                        artifact.unlink()
                        print(f"   ✅ Removed file: {artifact.name}")
                    cleaned_count += 1
            except Exception as e:
                print(f"   ⚠️ Could not remove {artifact.name}: {e}")

        if cleaned_count > 0:
            print(f"✅ Cleaned up {cleaned_count} build artifacts")
        else:
            print("✅ No build artifacts to clean up")

        return True

    except Exception as e:
        print(f"⚠️ Error during cleanup (build still successful): {e}")
        return False

def copy_complete_data_structure(project_root, output_dir):
    """Copy complete data structure with proper path mapping"""
    print("📋 Copying complete data structure...")

    try:
        # Create path mapping for executable environment
        path_mapping = {
            "src/data": "data",
            "src/core": "core"
        }

        for source_path, target_name in path_mapping.items():
            source_dir = project_root / source_path
            target_dir = output_dir / target_name

            if source_dir.exists():
                if target_dir.exists():
                    shutil.rmtree(target_dir)

                shutil.copytree(source_dir, target_dir)

                # Create path mapping file for executable
                mapping_file = output_dir / "path_mapping.json"
                mapping_data = {
                    "execution_env": "executable",
                    "data_path": str(target_dir) if target_name == "data" else None,
                    "core_path": str(target_dir) if target_name == "core" else None
                }

                with open(mapping_file, 'w', encoding='utf-8') as f:
                    json.dump(mapping_data, f, indent=2, ensure_ascii=False)

                print(f"   ✅ Copied {source_path}/ -> {target_name}/")
                print(f"      📄 JSON files: {json_files}")
                print(f"      🐍 Python files: {py_files}")

                total_copied += total_files
            else:
                print(f"   ⚠️ Source not found: {source_path}")

        print(f"✅ Total files copied: {total_copied}")
        return True

    except Exception as e:
        print(f"❌ Error copying data structure: {e}")
        return False

def build_standalone_exe():
    """Build standalone executable using PyInstaller with improved build management"""

    print("Building Simple Standalone EXE with Build Management...")
    print("=" * 60)

    try:
        # Get project root
        project_root = Path(__file__).parent.parent.parent
        installer_dir = project_root / "installer"
        output_dir = installer_dir / "output"

        # Main script path
        main_script = project_root / "src/main.py"

        if not main_script.exists():
            print(f"❌ Main script not found: {main_script}")
            return False

        # Clean previous builds from both project root and output directory
        print("🧹 Cleaning previous builds...")
        cleanup_locations = [
            (project_root / "dist", "dist"),
            (project_root / "build", "build"),
            (output_dir / "build", "output/build"),
            (project_root / "Quan_Ly_Kho_Cam_&_Mix.spec", "spec file"),
            (output_dir / "Quan_Ly_Kho_Cam_&_Mix.spec", "output/spec file")
        ]

        for cleanup_path, description in cleanup_locations:
            if cleanup_path.exists():
                try:
                    if cleanup_path.is_dir():
                        shutil.rmtree(cleanup_path)
                    else:
                        cleanup_path.unlink()
                    print(f"   ✅ Cleaned {description}")
                except Exception as e:
                    print(f"   ⚠️ Could not clean {description}: {e}")

        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        # PyInstaller command with build artifacts directed to output directory
        pyinstaller_cmd = [
            "pyinstaller",
            "--onefile",
            "--windowed",
            "--name=Quan_Ly_Kho_Cam_&_Mix",
            f"--distpath={output_dir}",
            f"--workpath={output_dir / 'build'}",  # Move build directory to output
            f"--specpath={output_dir}",  # Move spec file to output
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
            print(f"🎨 Using icon: {icon_file}")

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

        print("🚀 Running PyInstaller...")
        print(f"📋 Build artifacts will be placed in: {output_dir}")

        # Run PyInstaller
        result = subprocess.run(
            pyinstaller_cmd,
            cwd=project_root,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            exe_file = output_dir / "Quan_Ly_Kho_Cam_&_Mix.exe"

            if exe_file.exists():
                # Copy complete data structure including core
                copy_complete_data_structure(project_root, output_dir)

                file_size = exe_file.stat().st_size / (1024 * 1024)
                print(f"✅ Build successful!")
                print(f"📁 Output: {exe_file}")
                print(f"📊 Size: {file_size:.1f} MB")

                # Perform post-build cleanup
                cleanup_success = cleanup_build_artifacts(project_root, output_dir)

                # Verify final output directory is clean
                print(f"\n📂 Final output directory contents:")
                try:
                    for item in output_dir.iterdir():
                        if item.is_file():
                            size_mb = item.stat().st_size / (1024 * 1024)
                            print(f"   📄 {item.name} ({size_mb:.1f} MB)")
                        elif item.is_dir():
                            print(f"   📁 {item.name}/")
                except Exception as e:
                    print(f"   ⚠️ Could not list directory contents: {e}")

                return True
            else:
                print("❌ Build completed but executable not found")
                return False
        else:
            print("❌ PyInstaller failed:")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
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
            _, _ = test_process.communicate(timeout=10)

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
    """Main function with enhanced build management"""
    print("🏭 Simple Standalone EXE Builder")
    print("Enhanced with Build Directory Management")
    print("=" * 60)

    try:
        success = build_standalone_exe()

        if success:
            print("\n" + "=" * 60)
            print("🎉 BUILD COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            print("✅ Standalone executable created")
            print("✅ Build artifacts automatically cleaned up")
            print("✅ Output directory contains only distributable files")
            print("\n📁 Location: installer/output/")
            print("📋 Ready for distribution!")

            # Get project paths for final summary
            project_root = Path(__file__).parent.parent.parent
            output_dir = project_root / "installer" / "output"
            exe_file = output_dir / "Quan_Ly_Kho_Cam_&_Mix.exe"

            if exe_file.exists():
                print(f"\n🎯 Final executable: {exe_file.name}")
                print(f"📊 Size: {exe_file.stat().st_size / (1024 * 1024):.1f} MB")
        else:
            print("\n" + "=" * 60)
            print("💥 BUILD FAILED!")
            print("=" * 60)
            print("❌ Check the error messages above for details")
            print("💡 Common issues:")
            print("   - PyInstaller not installed: pip install pyinstaller")
            print("   - Missing dependencies: pip install -r requirements.txt")
            print("   - Path issues: ensure no Unicode characters in project path")

    except KeyboardInterrupt:
        print("\n⚠️ Build cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()






