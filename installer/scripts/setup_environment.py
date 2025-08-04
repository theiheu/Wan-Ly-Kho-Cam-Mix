#!/usr/bin/env python3
"""
Environment Setup Script
Runs on first application startup to ensure proper environment setup
"""

import os
import sys
import winreg
from pathlib import Path

def setup_professional_environment():
    """Setup environment variables for professional installation"""

    app_name = "Quan_Ly_Kho_Cam_&_Mix"

    # Check if already set up
    if 'CFM_DATA_PATH' in os.environ:
        print("✅ Environment already configured")
        return True

    print("🔧 Setting up professional environment...")

    # Define paths
    appdata_path = Path(os.environ.get('APPDATA', '')) / app_name
    documents_path = Path(os.environ.get('USERPROFILE', '')) / 'Documents' / app_name

    # Environment variables to set
    env_vars = {
        'CFM_DATA_PATH': str(appdata_path / "data"),
        'CFM_CONFIG_PATH': str(appdata_path / "config"),
        'CFM_LOGS_PATH': str(appdata_path / "logs"),
        'CFM_REPORTS_PATH': str(documents_path / "reports"),
        'CFM_EXPORTS_PATH': str(documents_path / "exports"),
        'CFM_BACKUPS_PATH': str(documents_path / "backups")
    }

    try:
        # Set environment variables for current process
        for var_name, var_value in env_vars.items():
            os.environ[var_name] = var_value
            print(f"✅ Set {var_name} = {var_value}")

        # Try to set in registry for persistence (may fail without admin rights)
        try:
            reg_path = r"Environment"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_SET_VALUE) as key:
                for var_name, var_value in env_vars.items():
                    winreg.SetValueEx(key, var_name, 0, winreg.REG_EXPAND_SZ, var_value)
            print("✅ Environment variables saved to registry")
        except Exception as e:
            print(f"⚠️ Could not save to registry (will work for current session): {e}")

        # Create directories
        for path_str in env_vars.values():
            path = Path(path_str)
            path.mkdir(parents=True, exist_ok=True)
            print(f"📁 Created directory: {path}")

        return True

    except Exception as e:
        print(f"❌ Error setting up environment: {e}")
        return False

if __name__ == "__main__":
    setup_professional_environment()


