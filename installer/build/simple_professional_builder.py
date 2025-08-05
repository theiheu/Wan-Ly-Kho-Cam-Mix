#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Professional Installer Builder
Creates a self-installing executable with data persistence
"""

import os
import sys
import shutil
import subprocess
import tempfile
from pathlib import Path

def create_install_manager():
    """Create installation manager script content"""
    return '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import shutil
import subprocess
from pathlib import Path

class InstallationManager:
    def __init__(self):
        self.app_name = "ChickenFarmManager"
        self.display_name = "Chicken Farm Manager"
        self.program_files = Path(os.environ.get('PROGRAMFILES', 'C:/Program Files'))
        self.install_path = self.program_files / self.app_name
        self.appdata_path = Path(os.environ.get('APPDATA', '')) / self.app_name
        self.documents_path = Path(os.environ.get('USERPROFILE', '')) / 'Documents' / self.app_name
        self.installed_exe = self.install_path / f"{self.app_name}.exe"

    def is_installed(self):
        return self.install_path.exists() and self.installed_exe.exists()

    def is_running_from_install_location(self):
        current_exe = Path(sys.executable if getattr(sys, 'frozen', False) else __file__)
        return current_exe.parent == self.install_path

    def install(self):
        print("🔧 Installing application...")
        try:
            # Create directories
            self.install_path.mkdir(parents=True, exist_ok=True)
            self.appdata_path.mkdir(parents=True, exist_ok=True)
            self.documents_path.mkdir(parents=True, exist_ok=True)
            (self.appdata_path / "data").mkdir(exist_ok=True)
            (self.appdata_path / "config").mkdir(exist_ok=True)
            (self.documents_path / "reports").mkdir(exist_ok=True)

            # Copy executable
            current_exe = Path(sys.executable if getattr(sys, 'frozen', False) else __file__)
            if current_exe != self.installed_exe:
                shutil.copy2(current_exe, self.installed_exe)

            # Create desktop shortcut
            desktop = Path(os.environ.get('USERPROFILE', '')) / 'Desktop'
            shortcut = desktop / f"{self.display_name}.bat"
            with open(shortcut, 'w') as f:
                f.write(f'@echo off\\n')
                f.write(f'cd /d "{self.install_path}"\\n')
                f.write(f'start "" "{self.installed_exe}"\\n')

            # Save installation config
            config_file = self.appdata_path / "installation.conf"
            with open(config_file, 'w') as f:
                f.write(f"INSTALL_PATH={self.install_path}\\n")
                f.write(f"APPDATA_PATH={self.appdata_path}\\n")
                f.write(f"DOCUMENTS_PATH={self.documents_path}\\n")

            print("✅ Installation completed!")
            return True
        except Exception as e:
            print(f"❌ Installation failed: {e}")
            return False

    def launch_installed(self):
        if self.installed_exe.exists():
            subprocess.Popen([str(self.installed_exe)], cwd=str(self.install_path))
            return True
        return False

def create_data_manager():
    """Create data path manager script content"""
    return '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from pathlib import Path

class DataPathManager:
    def __init__(self):
        self.app_name = "ChickenFarmManager"
        self.appdata_path = Path(os.environ.get('APPDATA', '')) / self.app_name
        self.documents_path = Path(os.environ.get('USERPROFILE', '')) / 'Documents' / self.app_name
        self.ensure_directories()

    def ensure_directories(self):
        directories = [
            self.appdata_path / "data",
            self.appdata_path / "config",
            self.documents_path / "reports",
            self.documents_path / "exports"
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def get_data_path(self):
        return self.appdata_path / "data"

    def get_config_path(self):
        return self.appdata_path / "config"

    def get_reports_path(self):
        return self.documents_path / "reports"

    def get_exports_path(self):
        return self.documents_path / "exports"

data_path_manager = DataPathManager()
'''

def create_modified_run():
    """Create modified run.py content"""
    project_root = Path(__file__).parent.parent.parent
    run_py = project_root / "run.py"

    with open(run_py, 'r', encoding='utf-8') as f:
        original_content = f.read()

    modified_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys

# Fix console encoding for Windows (safe for executable)
if sys.platform == "win32":
    try:
        import codecs
        if hasattr(sys.stdout, 'buffer') and sys.stdout.buffer is not None:
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        if hasattr(sys.stderr, 'buffer') and sys.stderr.buffer is not None:
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    except (AttributeError, TypeError):
        pass

# Import installation manager
try:
    from install_manager import main as install_main
    install_main()
except ImportError:
    pass

# Import data path manager
try:
    from data_path_manager import data_path_manager
    os.environ['CFM_DATA_PATH'] = str(data_path_manager.get_data_path())
    os.environ['CFM_CONFIG_PATH'] = str(data_path_manager.get_config_path())
    os.environ['CFM_REPORTS_PATH'] = str(data_path_manager.get_reports_path())
    os.environ['CFM_EXPORTS_PATH'] = str(data_path_manager.get_exports_path())
except ImportError:
    pass

''' + original_content

    return modified_content

def build_professional_exe():
    """Build the professional self-installing executable"""
    print("🚀 Building Professional Self-Installing Executable")

    project_root = Path(__file__).parent.parent.parent
    output_dir = project_root / "installer" / "output"
    src_dir = project_root / "src"

    # Create clean build environment
    clean_base = Path("C:/temp/cfm_professional")
    if clean_base.exists():
        shutil.rmtree(clean_base)
    clean_base.mkdir(parents=True, exist_ok=True)

    try:
        # Create project copy
        project_copy = clean_base / "project"
        project_copy.mkdir()

        # Copy source files
        shutil.copytree(src_dir, project_copy / "src")

        # Create installation components
        with open(project_copy / "install_manager.py", 'w', encoding='utf-8') as f:
            f.write(create_install_manager())

        with open(project_copy / "data_path_manager.py", 'w', encoding='utf-8') as f:
            f.write(create_data_manager())

        with open(project_copy / "run.py", 'w', encoding='utf-8') as f:
            f.write(create_modified_run())

        # Copy requirements and resources
        req_file = project_root / "requirements.txt"
        if req_file.exists():
            shutil.copy2(req_file, project_copy / "requirements.txt")

        icon_file = project_root / "installer" / "resources" / "app_icon.ico"
        if icon_file.exists():
            shutil.copy2(icon_file, project_copy / "app_icon.ico")

        # Create virtual environment
        venv_dir = clean_base / "venv"
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)

        python_exe = venv_dir / "Scripts" / "python.exe"
        pip_exe = venv_dir / "Scripts" / "pip.exe"

        # Install dependencies
        subprocess.run([str(pip_exe), "install", "pyinstaller"], check=True)
        if req_file.exists():
            subprocess.run([str(pip_exe), "install", "-r", str(project_copy / "requirements.txt")], check=True)

        # Build with PyInstaller
        pyinstaller_args = [
            str(python_exe), "-m", "PyInstaller",
            "--onefile",
            "--windowed",
            "--name=ChickenFarmManager_Professional",
            "--distpath=" + str(project_copy / "dist"),
            "--clean",
            "--noconfirm",
            "--add-data=" + str(project_copy / "src") + ";src",
            "--add-data=" + str(project_copy / "install_manager.py") + ";.",
            "--add-data=" + str(project_copy / "data_path_manager.py") + ";.",
            str(project_copy / "run.py")
        ]

        if (project_copy / "app_icon.ico").exists():
            pyinstaller_args.extend([f"--icon={project_copy / 'app_icon.ico'}"])

        print("🔧 Building executable...")
        result = subprocess.run(pyinstaller_args, cwd=str(project_copy), timeout=600)

        if result.returncode == 0:
            exe_file = project_copy / "dist" / "ChickenFarmManager_Professional.exe"
            if exe_file.exists():
                output_exe = output_dir / "ChickenFarmManager_Professional.exe"
                shutil.copy2(exe_file, output_exe)

                size_mb = output_exe.stat().st_size / (1024 * 1024)
                print(f"✅ Professional executable created: {output_exe}")
                print(f"📦 Size: {size_mb:.2f} MB")
                return True

        print("❌ Build failed")
        return False

    except Exception as e:
        print(f"❌ Build error: {e}")
        return False
    finally:
        try:
            shutil.rmtree(clean_base)
        except:
            pass

def create_installation_script():
    """Create installation script that sets up environment variables"""

    install_script = output_dir / "install_setup.py"

    script_content = '''#!/usr/bin/env python3
"""
Professional Installation Setup Script
Sets up environment variables and creates proper directory structure
"""

import os
import sys
import winreg
from pathlib import Path

def setup_environment_variables():
    """Set up environment variables for professional installation"""

    app_name = "Quan_Ly_Kho_Cam_&_Mix"

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
        # Set environment variables in registry for current user
        reg_path = r"Environment"

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_SET_VALUE) as key:
            for var_name, var_value in env_vars.items():
                winreg.SetValueEx(key, var_name, 0, winreg.REG_EXPAND_SZ, var_value)
                print(f"✅ Set {var_name} = {var_value}")

        # Create directories
        for path_str in env_vars.values():
            path = Path(path_str)
            path.mkdir(parents=True, exist_ok=True)
            print(f"📁 Created directory: {path}")

        print("✅ Environment setup completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Error setting up environment: {e}")
        return False

def create_desktop_shortcut():
    """Create desktop shortcut"""
    try:
        import win32com.client

        desktop = Path.home() / "Desktop"
        shortcut_path = desktop / "Quan Ly Kho Cam & Mix.lnk"

        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(str(shortcut_path))

        # Get installation directory
        install_dir = Path(os.environ.get('PROGRAMFILES', 'C:\\\\Program Files')) / "Quan_Ly_Kho_Cam_&_Mix"
        exe_path = install_dir / "Quan_Ly_Kho_Cam_&_Mix.exe"

        shortcut.Targetpath = str(exe_path)
        shortcut.WorkingDirectory = str(install_dir)
        shortcut.Description = "Phần mềm Quản lý Kho Cám & Mix"
        shortcut.save()

        print(f"✅ Desktop shortcut created: {shortcut_path}")
        return True

    except Exception as e:
        print(f"⚠️ Could not create desktop shortcut: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Setting up Quan Ly Kho Cam & Mix...")

    # Setup environment
    if setup_environment_variables():
        print("✅ Environment variables configured")
    else:
        print("❌ Failed to configure environment variables")
        sys.exit(1)

    # Create desktop shortcut
    create_desktop_shortcut()

    print("🎉 Installation setup completed!")
    input("Press Enter to continue...")
'''

    with open(install_script, 'w', encoding='utf-8') as f:
        f.write(script_content)

    print(f"✅ Installation script created: {install_script}")
    return install_script

def main():
    """Main entry point"""
    success = build_professional_exe()

    if success:
        print("\n🎉 PROFESSIONAL BUILD SUCCESSFUL!")
        print("📦 Features:")
        print("   ✅ Automatic installation to Program Files")
        print("   ✅ Persistent data storage")
        print("   ✅ Desktop shortcut creation")
        print("   ✅ Professional user experience")

        # Create installation script
        install_script = create_installation_script()

        return True
    else:
        print("\n❌ PROFESSIONAL BUILD FAILED!")
        return False

if __name__ == "__main__":
    main()

'''

