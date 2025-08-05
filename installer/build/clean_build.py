#!/usr/bin/env python3
"""
Clean Build Script - Handles file locks and permissions
"""

import os
import sys
import subprocess
import shutil
import time
from pathlib import Path

def kill_process_by_name(process_name):
    """Kill process by name if running"""
    try:
        subprocess.run(['taskkill', '/F', '/IM', process_name], 
                      capture_output=True, check=False)
        print(f"✅ Terminated {process_name}")
        time.sleep(2)  # Wait for process to fully terminate
    except Exception as e:
        print(f"⚠️ Could not terminate {process_name}: {e}")

def force_remove_file(file_path):
    """Force remove a file even if locked"""
    try:
        if file_path.exists():
            # Try to remove file attributes that might prevent deletion
            os.chmod(file_path, 0o777)
            file_path.unlink()
            print(f"✅ Removed {file_path}")
            return True
    except Exception as e:
        print(f"❌ Could not remove {file_path}: {e}")
        return False

def clean_build():
    """Clean build with proper file handling"""
    
    print("🧹 Clean Build Process")
    print("=" * 40)
    
    # Get paths
    project_root = Path(__file__).parent.parent.parent
    output_dir = project_root / "installer" / "output"
    
    # Kill any running instances
    print("🔄 Stopping running processes...")
    kill_process_by_name("ChickenFarmManager.exe")
    kill_process_by_name("python.exe")  # In case it's running in Python
    
    # Clean output directory
    print("🧹 Cleaning output directory...")
    exe_file = output_dir / "ChickenFarmManager.exe"
    
    if exe_file.exists():
        if not force_remove_file(exe_file):
            print("❌ Cannot remove existing executable. Please:")
            print("   1. Close the application if it's running")
            print("   2. Check if antivirus is scanning the file")
            print("   3. Run this script as Administrator")
            input("Press Enter after fixing the issue...")
            
            # Try again
            if not force_remove_file(exe_file):
                print("❌ Still cannot remove file. Aborting.")
                return False
    
    # Clean build directories
    for cleanup_dir in ["dist", "build"]:
        cleanup_path = project_root / cleanup_dir
        if cleanup_path.exists():
            print(f"🧹 Cleaning {cleanup_dir}...")
            try:
                shutil.rmtree(cleanup_path)
            except Exception as e:
                print(f"⚠️ Could not fully clean {cleanup_dir}: {e}")
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    return True

def build_executable():
    """Build the executable"""
    
    print("🔨 Building executable...")
    
    project_root = Path(__file__).parent.parent.parent
    main_script = project_root / "main.py"
    output_dir = project_root / "installer" / "output"
    
    if not main_script.exists():
        print(f"❌ Main script not found: {main_script}")
        return False
    
    # Simple PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=ChickenFarmManager",
        f"--distpath={output_dir}",
        "--clean",
        "--noconfirm",
        f"--add-data={project_root / 'src'};src",
        str(main_script)
    ]
    
    # Add icon if available
    icon_file = project_root / "installer" / "resources" / "app_icon.ico"
    if icon_file.exists():
        cmd.extend(["--icon", str(icon_file)])
    
    print(f"Command: {' '.join(cmd)}")
    
    # Run build
    result = subprocess.run(cmd, cwd=project_root)
    
    if result.returncode == 0:
        exe_file = output_dir / "ChickenFarmManager.exe"
        if exe_file.exists():
            size_mb = exe_file.stat().st_size / (1024 * 1024)
            print(f"✅ Build successful!")
            print(f"📦 File: {exe_file}")
            print(f"📏 Size: {size_mb:.1f} MB")
            return True
    
    print("❌ Build failed!")
    return False

def main():
    """Main function"""
    try:
        # Clean first
        if not clean_build():
            print("❌ Clean failed!")
            input("Press Enter to exit...")
            return
        
        # Build
        if build_executable():
            print("\n🎉 BUILD COMPLETED SUCCESSFULLY!")
        else:
            print("\n💥 BUILD FAILED!")
            
    except KeyboardInterrupt:
        print("\n⚠️ Build cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()