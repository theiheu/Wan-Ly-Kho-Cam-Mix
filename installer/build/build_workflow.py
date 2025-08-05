#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Streamlined Build Workflow for Chicken Farm Manager
Optimized build process focusing on working solutions
"""

import os
import sys
import shutil
import subprocess
import time
from pathlib import Path

# Set UTF-8 encoding for console output
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

class OptimizedBuildWorkflow:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.installer_dir = self.project_root / "installer"
        self.build_dir = self.installer_dir / "build"
        self.output_dir = self.installer_dir / "output"

        # Application information
        self.app_info = {
            "name": "ChickenFarmManager",
            "display_name": "Phần mềm Quản lý Cám - Trại Gà",
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

    def print_step(self, step, description):
        """Print formatted step"""
        print(f"\n📋 Step {step}: {description}")
        print("-" * 40)

    def check_dependencies(self):
        """Check if required dependencies are available"""
        self.print_step(1, "Checking Dependencies")

        try:
            result = subprocess.run([
                sys.executable,
                str(self.build_dir / "test_dependencies.py")
            ], capture_output=True, text=True, check=True, encoding='utf-8')

            if "All dependencies are available" in result.stdout:
                print("✅ All dependencies verified")
                return True
            else:
                print("❌ Some dependencies missing")
                print(result.stdout)
                return False

        except subprocess.CalledProcessError as e:
            print("❌ Dependency check failed")
            return False

    def build_portable_application(self):
        """Build the portable application (primary method)"""
        self.print_step(2, "Building Portable Application")

        try:
            result = subprocess.run([
                sys.executable,
                str(self.build_dir / "portable_build.py")
            ], capture_output=True, text=True, check=True, encoding='utf-8')

            print("✅ Portable application built successfully")
            if result.stdout and "Portable application created successfully!" in result.stdout:
                success_part = result.stdout.split("Portable application created successfully!")[1].strip()
                if success_part:
                    print(success_part)
            return True

        except subprocess.CalledProcessError as e:
            print("❌ Portable build failed")
            return False

    def try_standalone_exe_build(self):
        """Try standalone .exe build (recommended for .exe distribution)"""
        self.print_step(3, "Building Standalone .exe")

        print("🎯 Creating true standalone executable with clean environment")

        try:
            result = subprocess.run([
                sys.executable,
                str(self.build_dir / "standalone_exe_builder.py")
            ], capture_output=True, text=True, timeout=600, encoding='utf-8')

            if result.returncode == 0:
                print("✅ Standalone .exe build successful")
                # Check if executable exists and get size
                exe_file = self.output_dir / "ChickenFarmManager.exe"
                if exe_file.exists():
                    size_mb = exe_file.stat().st_size / (1024 * 1024)
                    print(f"📦 Executable size: {size_mb:.2f} MB")
                return True
            else:
                print("❌ Standalone .exe build failed")
                return False

        except subprocess.TimeoutExpired:
            print("❌ Standalone .exe build timed out")
            return False
        except Exception as e:
            print("❌ Standalone .exe build error")
            return False

    def try_alternative_build(self):
        """Try cx_Freeze as alternative (fallback method)"""
        self.print_step(4, "Trying Alternative Build (cx_Freeze)")

        print("⚠️ Note: cx_Freeze may fail due to PyQt5 compatibility issues")

        try:
            result = subprocess.run([
                sys.executable,
                str(self.build_dir / "cx_freeze_build.py")
            ], capture_output=True, text=True, timeout=120, encoding='utf-8')

            if result.returncode == 0:
                print("✅ cx_Freeze build successful")
                return True
            else:
                print("❌ cx_Freeze build failed (expected)")
                print("This is normal - PyQt5 compatibility issues")
                return False

        except subprocess.TimeoutExpired:
            print("❌ cx_Freeze build timed out")
            return False
        except Exception as e:
            print("❌ cx_Freeze build error")
            return False

    def validate_output(self):
        """Validate the build output"""
        self.print_step(5, "Validating Build Output")

        validation_results = {}

        # Check portable application
        portable_zip = self.output_dir / "ChickenFarmManager_Portable.zip"
        portable_dir = self.output_dir / "ChickenFarmManager_Portable"

        if portable_zip.exists() and portable_dir.exists():
            print("✅ Portable application files found")

            # Check key files in portable directory
            key_files = [
                "Run_ChickenFarmManager.bat",
                "ChickenFarmManager.py",
                "README.md",
                "requirements.txt",
                "src"
            ]

            missing_files = []
            for file in key_files:
                if not (portable_dir / file).exists():
                    missing_files.append(file)

            if missing_files:
                print(f"❌ Missing portable files: {', '.join(missing_files)}")
                validation_results["portable"] = False
            else:
                print("✅ All portable files present")
                size_mb = portable_zip.stat().st_size / (1024 * 1024)
                print(f"📦 Portable package size: {size_mb:.2f} MB")
                validation_results["portable"] = True
        else:
            print("❌ Portable application not found")
            validation_results["portable"] = False

        # Check standalone executable
        exe_file = self.output_dir / "ChickenFarmManager.exe"
        if exe_file.exists():
            size_mb = exe_file.stat().st_size / (1024 * 1024)
            print(f"✅ Standalone executable found - Size: {size_mb:.2f} MB")
            validation_results["executable"] = True
        else:
            print("❌ Standalone executable not found")
            validation_results["executable"] = False

        return any(validation_results.values())

    def generate_report(self, success_steps):
        """Generate build report"""
        self.print_step(6, "Build Report")

        print(f"📊 Build Summary:")
        print(f"   Dependencies:     {'✅' if 1 in success_steps else '❌'}")
        print(f"   Portable App:     {'✅' if 2 in success_steps else '❌'}")
        print(f"   Standalone .exe:  {'✅' if 3 in success_steps else '❌'}")
        print(f"   Alternative:      {'✅' if 4 in success_steps else '❌'}")
        print(f"   Validation:       {'✅' if 5 in success_steps else '❌'}")

        # Check what was built successfully
        exe_file = self.output_dir / "ChickenFarmManager.exe"
        portable_zip = self.output_dir / "ChickenFarmManager_Portable.zip"

        if 5 in success_steps:
            print(f"\n🎉 BUILD SUCCESSFUL!")

            if exe_file.exists():
                size_mb = exe_file.stat().st_size / (1024 * 1024)
                print(f"📦 Standalone executable: ChickenFarmManager.exe ({size_mb:.2f} MB)")
                print(f"   ✅ True standalone - no Python installation required")
                print(f"   ✅ Double-click to run")
                print(f"   ✅ Professional user experience")

            if portable_zip.exists():
                size_mb = portable_zip.stat().st_size / (1024 * 1024)
                print(f"📦 Portable application: ChickenFarmManager_Portable.zip ({size_mb:.2f} MB)")
                print(f"   ✅ Extract and run")
                print(f"   ✅ Includes source code")
                print(f"   ✅ Automatic dependency installation")

            print(f"\n📋 Distribution Options:")
            if exe_file.exists():
                print(f"   1. Distribute ChickenFarmManager.exe for simple installation")
            if portable_zip.exists():
                print(f"   2. Distribute ChickenFarmManager_Portable.zip for portable use")
            print(f"   3. Test on clean Windows systems")
        else:
            print(f"\n❌ BUILD FAILED!")
            print(f"   Please check the error messages above")

    def run_complete_workflow(self):
        """Run the complete optimized build workflow"""
        self.print_header("Optimized Build Workflow - Chicken Farm Manager")

        print(f"🏗️ Project: {self.app_info['display_name']}")
        print(f"📍 Location: {self.project_root}")
        print(f"🎯 Target: Professional Windows Distribution")

        success_steps = []

        # Step 1: Check dependencies
        if self.check_dependencies():
            success_steps.append(1)

        # Step 2: Build portable application (primary)
        if self.build_portable_application():
            success_steps.append(2)

        # Step 3: Build standalone executable (recommended for .exe distribution)
        if self.try_standalone_exe_build():
            success_steps.append(3)

        # Step 4: Try alternative build (optional)
        if self.try_alternative_build():
            success_steps.append(4)

        # Step 5: Validate output
        if self.validate_output():
            success_steps.append(5)

        # Step 6: Generate report
        self.generate_report(success_steps)

        return 5 in success_steps  # Success if validation passes (either portable or exe)

def main():
    """Main entry point"""
    workflow = OptimizedBuildWorkflow()
    success = workflow.run_complete_workflow()

    if success:
        print(f"\n✨ Build workflow completed successfully!")
        sys.exit(0)
    else:
        print(f"\n💥 Build workflow failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
