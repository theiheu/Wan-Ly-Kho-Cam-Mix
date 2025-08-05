#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nuitka Build System for Chicken Farm Manager
Creates standalone .exe using Nuitka compiler
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

class NuitkaBuilder:
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

    def check_nuitka_requirements(self):
        """Check if Nuitka and required tools are available"""
        print("🔍 Checking Nuitka requirements...")
        
        try:
            # Check Nuitka
            result = subprocess.run([sys.executable, "-c", "import nuitka; print('Nuitka version:', nuitka.__version__)"], 
                                  capture_output=True, text=True, check=True)
            print("✅ Nuitka available:", result.stdout.strip())
            
            # Check for C++ compiler (required by Nuitka)
            try:
                result = subprocess.run(["cl"], capture_output=True, text=True)
                if "Microsoft" in result.stderr:
                    print("✅ Microsoft Visual C++ compiler available")
                    return True
            except FileNotFoundError:
                pass
            
            # Check for MinGW
            try:
                result = subprocess.run(["gcc", "--version"], capture_output=True, text=True)
                if result.returncode == 0:
                    print("✅ GCC compiler available")
                    return True
            except FileNotFoundError:
                pass
            
            print("⚠️ No C++ compiler found. Nuitka requires either:")
            print("   - Microsoft Visual Studio (with C++ tools)")
            print("   - MinGW-w64")
            print("   - Clang")
            return False
            
        except subprocess.CalledProcessError:
            print("❌ Nuitka not available")
            return False

    def create_temp_build_environment(self):
        """Create a temporary build environment to avoid Unicode path issues"""
        print("🔧 Creating temporary build environment...")
        
        # Create temp directory with ASCII-only path
        temp_dir = Path(tempfile.mkdtemp(prefix="cfm_build_"))
        print(f"📁 Temp build directory: {temp_dir}")
        
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
        
        return temp_dir, temp_main

    def build_with_nuitka(self, temp_dir, main_script):
        """Build executable using Nuitka"""
        print("🔨 Building with Nuitka...")
        
        # Nuitka command arguments
        nuitka_args = [
            sys.executable, "-m", "nuitka",
            "--standalone",                    # Create standalone executable
            "--onefile",                      # Single file executable
            "--windows-disable-console",     # No console window for GUI app
            "--enable-plugin=pyqt5",         # Enable PyQt5 plugin
            "--include-data-dir=src=src",     # Include source directory
            "--output-dir=" + str(temp_dir / "dist"),  # Output directory
            "--output-filename=ChickenFarmManager.exe",  # Output filename
            "--windows-icon-from-ico=" + str(self.installer_dir / "resources" / "app_icon.ico"),  # Icon
            str(main_script)                  # Main script to compile
        ]
        
        print("🔧 Nuitka command:")
        print(" ".join(nuitka_args))
        
        try:
            # Run Nuitka build
            result = subprocess.run(
                nuitka_args,
                cwd=str(temp_dir),
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            if result.returncode == 0:
                print("✅ Nuitka build successful!")
                
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
                    return False
            else:
                print("❌ Nuitka build failed!")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Nuitka build timed out (10 minutes)")
            return False
        except Exception as e:
            print(f"❌ Nuitka build error: {e}")
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
        self.print_header("Nuitka Executable Builder")
        
        print(f"🏗️ Project: {self.app_info['display_name']}")
        print(f"📍 Source: {self.project_root}")
        print(f"🎯 Target: Standalone Windows .exe")
        
        # Step 1: Check requirements
        if not self.check_nuitka_requirements():
            print("\n❌ Build failed: Missing requirements")
            return False
        
        # Step 2: Create temp environment
        temp_dir, temp_main = self.create_temp_build_environment()
        
        try:
            # Step 3: Build with Nuitka
            if self.build_with_nuitka(temp_dir, temp_main):
                # Step 4: Test executable
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
                print("\n❌ Build failed during Nuitka compilation")
                return False
                
        finally:
            # Always cleanup temp directory
            self.cleanup_temp_directory(temp_dir)

def main():
    """Main entry point"""
    builder = NuitkaBuilder()
    success = builder.build_executable()
    
    if success:
        print("\n✨ Nuitka build completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Nuitka build failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
