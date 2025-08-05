#!/usr/bin/env python3
"""
Cleanup Utility
Forcefully cleans build directories and closes processes
"""

import os
import sys
import subprocess
import shutil
import time
from pathlib import Path

def force_cleanup():
    """Force cleanup of build directories"""
    print("🧹 Force Cleanup Utility")
    print("=" * 40)
    
    project_root = Path(__file__).parent.parent.parent
    
    # Directories to clean
    clean_dirs = [
        project_root / "dist",
        project_root / "build", 
        project_root / "installer" / "output"
    ]
    
    # Kill any running processes
    processes_to_kill = [
        "ChickenFarmManager.exe",
        "ChickenFarmManager_Setup.exe"
    ]
    
    print("🔪 Killing running processes...")
    for process in processes_to_kill:
        try:
            result = subprocess.run(['taskkill', '/F', '/IM', process], 
                                  capture_output=True, check=False)
            if result.returncode == 0:
                print(f"  ✅ Killed: {process}")
            else:
                print(f"  ℹ️ Not running: {process}")
        except Exception as e:
            print(f"  ⚠️ Error killing {process}: {e}")
    
    # Wait for processes to close
    print("⏳ Waiting for processes to close...")
    time.sleep(3)
    
    # Clean directories
    print("🗑️ Cleaning directories...")
    for dir_path in clean_dirs:
        if dir_path.exists():
            print(f"  Cleaning: {dir_path}")
            
            # Try multiple cleanup methods
            success = False
            
            # Method 1: Python shutil
            try:
                shutil.rmtree(dir_path)
                print(f"    ✅ Cleaned with shutil")
                success = True
            except Exception as e:
                print(f"    ❌ shutil failed: {e}")
            
            # Method 2: Windows rmdir command
            if not success:
                try:
                    result = subprocess.run(['rmdir', '/S', '/Q', str(dir_path)], 
                                          capture_output=True, check=False, shell=True)
                    if result.returncode == 0:
                        print(f"    ✅ Cleaned with rmdir")
                        success = True
                    else:
                        print(f"    ❌ rmdir failed: {result.stderr}")
                except Exception as e:
                    print(f"    ❌ rmdir error: {e}")
            
            # Method 3: Manual file-by-file removal
            if not success and dir_path.exists():
                try:
                    print(f"    🔧 Trying manual cleanup...")
                    
                    # Remove files first
                    for root, dirs, files in os.walk(dir_path, topdown=False):
                        for file in files:
                            file_path = Path(root) / file
                            try:
                                file_path.chmod(0o777)
                                file_path.unlink()
                            except:
                                pass
                        
                        for dir_name in dirs:
                            dir_to_remove = Path(root) / dir_name
                            try:
                                dir_to_remove.rmdir()
                            except:
                                pass
                    
                    # Remove main directory
                    dir_path.rmdir()
                    print(f"    ✅ Manual cleanup successful")
                    success = True
                    
                except Exception as e:
                    print(f"    ❌ Manual cleanup failed: {e}")
            
            if not success:
                print(f"    ⚠️ Could not fully clean {dir_path}")
                print(f"       You may need to close Windows Explorer and try again")
        else:
            print(f"  ℹ️ Not found: {dir_path}")
    
    # Recreate output directory
    output_dir = project_root / "installer" / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Recreated: {output_dir}")
    
    print("\n🎉 Cleanup completed!")
    print("You can now run the build script again.")

if __name__ == "__main__":
    force_cleanup()
