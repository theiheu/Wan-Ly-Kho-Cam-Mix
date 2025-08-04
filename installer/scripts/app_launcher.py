#!/usr/bin/env python3
"""
Application Launcher with Environment Setup
Ensures proper environment setup before launching main application
"""

import os
import sys
import subprocess
from pathlib import Path

def setup_environment():
    """Setup environment variables"""
    
    app_name = "Quan_Ly_Kho_Cam_&_Mix"
    
    # Define paths
    appdata_path = Path(os.environ.get('APPDATA', '')) / app_name
    documents_path = Path(os.environ.get('USERPROFILE', '')) / 'Documents' / app_name
    
    # Environment variables
    env_vars = {
        'CFM_DATA_PATH': str(appdata_path / "data"),
        'CFM_CONFIG_PATH': str(appdata_path / "config"),
        'CFM_LOGS_PATH': str(appdata_path / "logs"),
        'CFM_REPORTS_PATH': str(documents_path / "reports"),
        'CFM_EXPORTS_PATH': str(documents_path / "exports"),
        'CFM_BACKUPS_PATH': str(documents_path / "backups")
    }
    
    # Set environment variables
    for var_name, var_value in env_vars.items():
        os.environ[var_name] = var_value
        # Create directory
        Path(var_value).mkdir(parents=True, exist_ok=True)

def main():
    """Main launcher"""
    
    # Setup environment
    setup_environment()
    
    # Get the directory where this launcher is located
    launcher_dir = Path(__file__).parent
    
    # Find the main executable
    main_exe = launcher_dir / "Quan_Ly_Kho_Cam_&_Mix_Main.exe"
    
    if main_exe.exists():
        # Launch main application with environment
        subprocess.run([str(main_exe)], env=os.environ)
    else:
        print(f"❌ Main application not found: {main_exe}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()