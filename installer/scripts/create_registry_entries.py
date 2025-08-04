#!/usr/bin/env python3
"""
Create Windows registry entries for proper uninstall support
"""

import winreg
import os
from pathlib import Path

def create_uninstall_registry_entry():
    """Create registry entry for Add/Remove Programs"""
    
    app_name = "Quan_Ly_Kho_Cam_&_Mix"
    display_name = "Phần mềm Quản lý Kho Cám & Mix"
    version = "2.0.0"
    publisher = "Minh-Tan_Phat"
    
    # Installation directory
    install_dir = Path(os.environ.get('PROGRAMFILES', 'C:\\Program Files')) / app_name
    
    # Registry key path
    reg_path = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\Quan_Ly_Kho_Cam_Mix"
    
    try:
        # Create registry key
        with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
            # Required values
            winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, display_name)
            winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, version)
            winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, publisher)
            winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, 
                            str(install_dir / "Uninstall.exe"))
            winreg.SetValueEx(key, "QuietUninstallString", 0, winreg.REG_SZ, 
                            str(install_dir / "Uninstall.exe") + " /S")
            
            # Optional values
            winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, 
                            str(install_dir / f"{app_name}.exe"))
            winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, str(install_dir))
            winreg.SetValueEx(key, "URLInfoAbout", 0, winreg.REG_SZ, 
                            "https://github.com/Minh-Tan_Phat")
            
            # Prevent modification
            winreg.SetValueEx(key, "NoModify", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, "NoRepair", 0, winreg.REG_DWORD, 1)
            
            # Estimated size (in KB)
            winreg.SetValueEx(key, "EstimatedSize", 0, winreg.REG_DWORD, 50000)  # ~50MB
            
        print("✅ Registry entries created successfully")
        return True
        
    except PermissionError:
        print("❌ Permission denied. Run as Administrator.")
        return False
    except Exception as e:
        print(f"❌ Error creating registry entries: {e}")
        return False

if __name__ == "__main__":
    create_uninstall_registry_entry()