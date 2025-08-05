#!/usr/bin/env python3
"""
Windows Setup Script - Automatic installation and data setup
"""

import os
import sys
import shutil
import winreg
from pathlib import Path

def install_to_program_files():
    """Install application to Program Files with complete data structure"""
    print("🏗️ Installing to Program Files...")

    app_name = "Quan_Ly_Kho_Cam_&_Mix"
    program_files = Path(os.environ.get('PROGRAMFILES', 'C:\\Program Files'))
    install_dir = program_files / app_name

    try:
        # Create installation directory
        install_dir.mkdir(parents=True, exist_ok=True)

        # Copy executable
        current_dir = Path(__file__).parent
        exe_file = current_dir / f"{app_name}.exe"

        if exe_file.exists():
            shutil.copy2(exe_file, install_dir / f"{app_name}.exe")
            print(f"   ✅ Installed executable")

        # Copy complete data structure (core + data)
        data_directories = ["core", "data"]

        for dir_name in data_directories:
            source_dir = current_dir / dir_name
            target_dir = install_dir / dir_name

            if source_dir.exists():
                if target_dir.exists():
                    shutil.rmtree(target_dir)
                shutil.copytree(source_dir, target_dir)

                # Count files by type
                json_files = len(list(target_dir.rglob("*.json")))
                py_files = len(list(target_dir.rglob("*.py")))

                print(f"   ✅ Installed {dir_name}/ directory:")
                print(f"      📄 JSON files: {json_files}")
                if py_files > 0:
                    print(f"      🐍 Python files: {py_files}")

        # Create desktop shortcut
        create_desktop_shortcut(install_dir / f"{app_name}.exe")

        # Register in Windows
        register_application(install_dir)

        print(f"✅ Installation completed: {install_dir}")
        return install_dir

    except PermissionError:
        print("❌ Permission denied. Please run as Administrator.")
        return None
    except Exception as e:
        print(f"❌ Installation failed: {e}")
        return None

def create_desktop_shortcut(exe_path):
    """Create desktop shortcut"""
    try:
        import win32com.client

        desktop = Path.home() / "Desktop"
        shortcut_path = desktop / "Quản lý Cám - Trại Gà.lnk"

        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(str(shortcut_path))
        shortcut.Targetpath = str(exe_path)
        shortcut.WorkingDirectory = str(exe_path.parent)
        shortcut.IconLocation = str(exe_path)
        shortcut.save()

        print("   ✅ Created desktop shortcut")

    except ImportError:
        print("   ⚠️ Could not create shortcut (pywin32 not available)")
    except Exception as e:
        print(f"   ⚠️ Could not create shortcut: {e}")

def register_application(install_dir):
    """Register application in Windows registry"""
    try:
        app_name = "Quan_Ly_Kho_Cam_&_Mix"
        reg_path = f"Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{app_name}"

        with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
            winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ,
                            "Phần mềm Quản lý Cám - Trại Gà")
            winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, "2.0.0")
            winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, "Minh-Tan_Phat")
            winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, str(install_dir))
            winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ,
                            f'"{install_dir}\\uninstall.exe"')

        print("   ✅ Registered in Windows")

    except PermissionError:
        print("   ⚠️ Could not register (need admin rights)")
    except Exception as e:
        print(f"   ⚠️ Registration failed: {e}")

if __name__ == "__main__":
    print("🏗️ Windows Setup - Chicken Farm Manager")
    print("=" * 50)

    if install_to_program_files():
        print("\n✅ Setup completed successfully!")
        print("🎯 Application installed and ready to use")
    else:
        print("\n❌ Setup failed!")

    input("Press Enter to exit...")
