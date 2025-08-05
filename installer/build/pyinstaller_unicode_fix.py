#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyInstaller Unicode Path Fix for Chicken Farm Manager
Creates standalone .exe using PyInstaller with Unicode path workaround
"""

import os
import sys
import shutil
import subprocess
import tempfile
from pathlib import Path

# Set UTF-8 encoding for console output
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

class PyInstallerUnicodeFix:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.installer_dir = self.project_root / "installer"
        self.build_dir = self.installer_dir / "build"
        self.output_dir = self.installer_dir / "output"
        self.src_dir = self.project_root / "src"
        self.main_script = self.project_root / "run.py"

        # Application information
        self.app_info = {
            "name": "ChickenFarmManager",
            "display_name": "Chicken Farm Manager",
            "version": "2.0.0",
            "description": "Professional Chicken Farm Management System",
            "company": "Minh-Tan_Phat"
        }

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def print_header(self, title):
        """Print formatted header"""
        print(f"\n{'='*60}")
        print(f"🚀 {title}")
        print(f"{'='*60}")

    def check_pyinstaller_requirements(self):
        """Check if PyInstaller is available"""
        print("🔍 Checking PyInstaller requirements...")

        try:
            result = subprocess.run([sys.executable, "-c", "import PyInstaller; print('PyInstaller version:', PyInstaller.__version__)"],
                                  capture_output=True, text=True, check=True)
            print("✅ PyInstaller available:", result.stdout.strip())
            return True

        except subprocess.CalledProcessError:
            print("❌ PyInstaller not available")
            return False

    def create_temp_build_environment(self):
        """Create a temporary build environment with ASCII-only paths"""
        print("🔧 Creating temporary build environment...")

        # Create temp directory with ASCII-only path
        temp_dir = Path(tempfile.mkdtemp(prefix="cfm_build_", dir="C:\\temp"))
        print(f"📁 Temp build directory: {temp_dir}")

        # Ensure temp directory exists
        temp_dir.mkdir(parents=True, exist_ok=True)

        # Copy source files to temp directory
        temp_src = temp_dir / "src"
        shutil.copytree(self.src_dir, temp_src)
        print("✅ Copied source files")

        # Copy main script
        temp_main = temp_dir / "run.py"
        shutil.copy2(self.main_script, temp_main)
        print("✅ Copied main script")

        # Copy requirements
        req_file = self.project_root / "requirements.txt"
        if req_file.exists():
            shutil.copy2(req_file, temp_dir / "requirements.txt")
            print("✅ Copied requirements.txt")

        # Copy icon if available
        icon_file = self.installer_dir / "resources" / "app_icon.ico"
        if icon_file.exists():
            shutil.copy2(icon_file, temp_dir / "app_icon.ico")
            print("✅ Copied application icon")

        return temp_dir, temp_main

    def create_pyinstaller_spec(self, temp_dir, main_script):
        """Create a PyInstaller spec file with proper configuration"""
        print("📝 Creating PyInstaller spec file...")

        # Convert paths to forward slashes for spec file
        temp_dir_str = str(temp_dir).replace('\\', '/')
        main_script_str = str(main_script).replace('\\', '/')
        src_dir_str = str(temp_dir / "src").replace('\\', '/')
        icon_path_str = str(temp_dir / "app_icon.ico").replace('\\', '/')

        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# Add source directory to path
src_path = Path(r"{temp_dir_str}") / "src"
sys.path.insert(0, str(src_path))

a = Analysis(
    [r'{main_script_str}'],
    pathex=[r'{temp_dir_str}'],
    binaries=[],
    datas=[
        (r'{src_dir_str}', 'src'),
    ],
    hiddenimports=[
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'pandas',
        'numpy',
        'matplotlib',
        'openpyxl',
        'PIL',
        'src.main',
        'src.ui.main_window',
        'src.controllers',
        'src.models',
        'src.services',
        'src.utils',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ChickenFarmManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=r'{icon_path_str}' if Path(r'{icon_path_str}').exists() else None,
)
'''

        spec_file = temp_dir / "ChickenFarmManager.spec"
        with open(spec_file, 'w', encoding='utf-8') as f:
            f.write(spec_content)

        print(f"✅ Created spec file: {spec_file}")
        return spec_file

    def build_with_pyinstaller(self, temp_dir, spec_file):
        """Build executable using PyInstaller"""
        print("🔨 Building with PyInstaller...")

        # PyInstaller command arguments
        pyinstaller_args = [
            sys.executable, "-m", "PyInstaller",
            "--clean",                        # Clean cache and remove temporary files
            "--noconfirm",                   # Replace output directory without confirmation
            "--log-level=INFO",              # Set log level
            str(spec_file)                   # Use spec file
        ]

        print("🔧 PyInstaller command:")
        print(" ".join(pyinstaller_args))

        try:
            # Run PyInstaller build
            result = subprocess.run(
                pyinstaller_args,
                cwd=str(temp_dir),
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout
                env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}
            )

            if result.returncode == 0:
                print("✅ PyInstaller build successful!")

                # Find the generated executable
                dist_dir = temp_dir / "dist"
                exe_file = dist_dir / "ChickenFarmManager.exe"

                if exe_file.exists():
                    # Copy to output directory
                    output_exe = self.output_dir / "ChickenFarmManager.exe"
                    shutil.copy2(exe_file, output_exe)
                    print(f"✅ Executable copied to: {output_exe}")

                    # Get file size
                    size_mb = output_exe.stat().st_size / (1024 * 1024)
                    print(f"📦 Executable size: {size_mb:.2f} MB")

                    return True
                else:
                    print("❌ Executable not found in dist directory")
                    print("Available files in dist:")
                    if dist_dir.exists():
                        for file in dist_dir.iterdir():
                            print(f"  - {file.name}")
                    return False
            else:
                print("❌ PyInstaller build failed!")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                return False

        except subprocess.TimeoutExpired:
            print("❌ PyInstaller build timed out (10 minutes)")
            return False
        except Exception as e:
            print(f"❌ PyInstaller build error: {e}")
            return False

    def test_executable(self):
        """Test the generated executable"""
        print("🧪 Testing executable...")

        exe_file = self.output_dir / "ChickenFarmManager.exe"
        if not exe_file.exists():
            print("❌ Executable not found")
            return False

        try:
            # Try to run the executable briefly
            process = subprocess.Popen(
                [str(exe_file)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Wait a moment then terminate
            import time
            time.sleep(3)
            process.terminate()

            print("✅ Executable appears to work")
            return True

        except Exception as e:
            print(f"⚠️ Executable test failed: {e}")
            return False

    def cleanup_temp_directory(self, temp_dir):
        """Clean up temporary build directory"""
        try:
            shutil.rmtree(temp_dir)
            print("🧹 Cleaned up temporary directory")
        except Exception as e:
            print(f"⚠️ Failed to clean temp directory: {e}")

    def build_executable(self):
        """Main build process"""
        self.print_header("PyInstaller Unicode Path Fix")

        print(f"🏗️ Project: {self.app_info['display_name']}")
        print(f"📍 Source: {self.project_root}")
        print(f"🎯 Target: Standalone Windows .exe")
        print(f"🔧 Method: Temporary ASCII-only build environment")

        # Step 1: Check requirements
        if not self.check_pyinstaller_requirements():
            print("\n❌ Build failed: Missing requirements")
            return False

        # Step 2: Create temp environment
        temp_dir, temp_main = self.create_temp_build_environment()

        try:
            # Step 3: Create spec file
            spec_file = self.create_pyinstaller_spec(temp_dir, temp_main)

            # Step 4: Build with PyInstaller
            if self.build_with_pyinstaller(temp_dir, spec_file):
                # Step 5: Test executable
                if self.test_executable():
                    print("\n🎉 BUILD SUCCESSFUL!")
                    print(f"📦 Executable: {self.output_dir / 'ChickenFarmManager.exe'}")
                    print("\n📋 Next Steps:")
                    print("1. Test the .exe on a clean Windows system")
                    print("2. Distribute the single executable file")
                    print("3. No Python installation required for end users")
                    return True
                else:
                    print("\n⚠️ Build completed but executable test failed")
                    return False
            else:
                print("\n❌ Build failed during PyInstaller compilation")
                return False

        finally:
            # Always cleanup temp directory
            self.cleanup_temp_directory(temp_dir)

def main():
    """Main entry point"""
    builder = PyInstallerUnicodeFix()
    success = builder.build_executable()

    if success:
        print("\n✨ PyInstaller Unicode fix build completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 PyInstaller Unicode fix build failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
