#!/usr/bin/env python3
"""
Application Launcher with Environment Setup
Ensures proper environment setup before launching main application
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def setup_environment():
    """Setup environment variables for AppData paths"""
    app_name = "Quan_Ly_Kho_Cam_&_Mix"
    appdata_path = Path(os.environ.get('APPDATA', '')) / app_name

    # Always use AppData regardless of installation location
    env_vars = {
        'CFM_INSTALLATION_MODE': 'professional',
        'CFM_DATA_PATH': str(appdata_path / "data"),
        'CFM_CONFIG_PATH': str(appdata_path / "data" / "config"),
        'CFM_LOGS_PATH': str(appdata_path / "logs"),
        'CFM_REPORTS_PATH': str(appdata_path / "reports"),
        'CFM_EXPORTS_PATH': str(appdata_path / "exports"),
        'CFM_BACKUPS_PATH': str(appdata_path / "backups")
    }

    for var_name, var_value in env_vars.items():
        os.environ[var_name] = str(var_value)
        # Create directory with proper permissions
        Path(var_value).mkdir(parents=True, exist_ok=True)

    print("🔧 Environment configured for AppData usage")
    print(f"   📁 Data path: {appdata_path}")

def setup_data_directories():
    """Setup complete data directories including core"""
    print("📁 Setting up complete data directories...")

    app_name = "Quan_Ly_Kho_Cam_&_Mix"
    appdata_path = Path(os.environ.get('APPDATA', '')) / app_name

    # Create complete directory structure
    data_structure = {
        # Core data directories
        'core': appdata_path / "core",
        'data': appdata_path / "data",
        'data/business': appdata_path / "data" / "business",
        'data/config': appdata_path / "data" / "config",
        'data/reports': appdata_path / "data" / "reports",
        'data/exports': appdata_path / "data" / "exports",
        'data/daily_consumption': appdata_path / "data" / "daily_consumption",
        'data/presets': appdata_path / "data" / "presets",
        'data/presets/feed': appdata_path / "data" / "presets" / "feed",
        'data/presets/mix': appdata_path / "data" / "presets" / "mix",

        # Additional directories
        'logs': appdata_path / "logs",
        'backups': appdata_path / "backups"
    }

    for dir_name, dir_path in data_structure.items():
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"   ✅ Created: {dir_name}")

    # Copy data from installation directory
    launcher_dir = Path(__file__).parent

    # Copy core directory (Python modules and data)
    copy_directory_structure(launcher_dir / "core", appdata_path / "core", "core")

    # Copy data directory (JSON configs and business data)
    copy_directory_structure(launcher_dir / "data", appdata_path / "data", "data")

    return data_structure

def copy_directory_structure(source_dir, target_dir, dir_name):
    """Copy directory structure preserving subdirectories"""
    if not source_dir.exists():
        print(f"   ⚠️ Source {dir_name} not found: {source_dir}")
        return

    copied_files = 0

    # Copy all files recursively
    for source_file in source_dir.rglob("*"):
        if source_file.is_file():
            # Calculate relative path
            relative_path = source_file.relative_to(source_dir)
            target_file = target_dir / relative_path

            # Create parent directories
            target_file.parent.mkdir(parents=True, exist_ok=True)

            # Copy file if it doesn't exist or is newer
            if not target_file.exists() or source_file.stat().st_mtime > target_file.stat().st_mtime:
                shutil.copy2(source_file, target_file)
                copied_files += 1
                print(f"   ✅ Copied {dir_name}: {relative_path}")

    if copied_files == 0:
        print(f"   ℹ️ {dir_name} directory up to date")

def main():
    """Enhanced launcher that ensures AppData usage"""
    print("🚀 Starting application with AppData configuration...")

    # Setup environment first
    setup_environment()

    # Get the directory where this launcher is located
    launcher_dir = Path(__file__).parent

    # Find the main executable
    main_exe = launcher_dir / "Quan_Ly_Kho_Cam_&_Mix_Main.exe"

    if main_exe.exists():
        # Launch with configured environment
        subprocess.run([str(main_exe)], env=os.environ)
    else:
        print(f"❌ Main application not found: {main_exe}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()




