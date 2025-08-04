
import os
import sys
from pathlib import Path

# Setup environment for standalone executable
if getattr(sys, 'frozen', False):
    app_name = "Quan_Ly_Kho_Cam_&_Mix"
    exe_dir = Path(sys.executable).parent

    # Check if professional install (Program Files)
    use_professional = 'Program Files' in str(exe_dir)

    if use_professional:
        # Professional paths
        appdata = Path(os.environ.get('APPDATA', '')) / app_name
        documents = Path(os.environ.get('USERPROFILE', '')) / 'Documents' / app_name

        paths = {
            'CFM_DATA_PATH': str(appdata / "data"),
            'CFM_CONFIG_PATH': str(appdata / "config"),
            'CFM_LOGS_PATH': str(appdata / "logs"),
            'CFM_REPORTS_PATH': str(documents / "reports"),
            'CFM_EXPORTS_PATH': str(documents / "exports"),
            'CFM_BACKUPS_PATH': str(documents / "backups")
        }
    else:
        # Portable paths
        paths = {
            'CFM_DATA_PATH': str(exe_dir / "data"),
            'CFM_CONFIG_PATH': str(exe_dir / "config"),
            'CFM_LOGS_PATH': str(exe_dir / "logs"),
            'CFM_REPORTS_PATH': str(exe_dir / "reports"),
            'CFM_EXPORTS_PATH': str(exe_dir / "exports"),
            'CFM_BACKUPS_PATH': str(exe_dir / "backups")
        }

    # Set environment and create directories
    for var, path in paths.items():
        os.environ[var] = path
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
        except:
            pass
