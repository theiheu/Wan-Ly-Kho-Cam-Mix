#!/usr/bin/env python3
"""
cx_Freeze Build System
Alternative to PyInstaller using cx_Freeze
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_cx_freeze():
    """Install cx_Freeze if not available"""
    try:
        import cx_Freeze
        print("✅ cx_Freeze is available")
        return True
    except ImportError:
        print("📦 Installing cx_Freeze...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "cx_Freeze"], 
                         check=True, capture_output=True)
            print("✅ cx_Freeze installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install cx_Freeze: {e}")
            return False

def create_cx_freeze_setup():
    """Create setup.py for cx_Freeze"""
    project_root = Path(__file__).parent.parent.parent
    
    setup_content = f'''#!/usr/bin/env python3
"""
cx_Freeze setup script for Chicken Farm Manager
"""

import sys
from cx_Freeze import setup, Executable
from pathlib import Path

# Project root
project_root = Path(__file__).parent

# Build options
build_options = {{
    "packages": [
        "PyQt5.QtCore",
        "PyQt5.QtGui", 
        "PyQt5.QtWidgets",
        "PyQt5.QtPrintSupport",
        "pandas",
        "matplotlib",
        "matplotlib.backends.backend_qt5agg",
        "openpyxl",
        "PIL",
        "pkg_resources",
        "sip",
    ],
    "excludes": [
        "tkinter",
        "unittest",
        "test",
        "distutils",
        "PyQt5.QtWebKit",
        "PyQt5.QtWebKitWidgets",
        "PyQt5.QtWebEngine",
        "PyQt5.QtWebEngineWidgets",
    ],
    "include_files": [
        (str(project_root / "src"), "src"),
    ],
    "optimize": 1,
}}

# Executable options
executable_options = {{
    "script": str(project_root / "run.py"),
    "base": "Win32GUI" if sys.platform == "win32" else None,
    "target_name": "ChickenFarmManager.exe",
    "icon": str(project_root / "installer" / "resources" / "app_icon.ico") if (project_root / "installer" / "resources" / "app_icon.ico").exists() else None,
}}

# Create executable
executables = [Executable(**executable_options)]

# Setup
setup(
    name="ChickenFarmManager",
    version="2.0.0",
    description="Chicken Farm Management System",
    author="Minh-Tan_Phat",
    options={{"build_exe": build_options}},
    executables=executables,
)
'''
    
    setup_path = project_root / "setup_cx_freeze.py"
    with open(setup_path, 'w', encoding='utf-8') as f:
        f.write(setup_content)
    
    print(f"✅ Created cx_Freeze setup: {setup_path}")
    return setup_path

def build_with_cx_freeze():
    """Build executable using cx_Freeze"""
    print("🔨 Building with cx_Freeze")
    print("=" * 40)
    
    project_root = Path(__file__).parent.parent.parent
    output_dir = project_root / "installer" / "output"
    
    # Install cx_Freeze
    if not install_cx_freeze():
        return False
    
    # Create setup script
    setup_path = create_cx_freeze_setup()
    
    # Clean previous builds
    build_dir = project_root / "build"
    if build_dir.exists():
        shutil.rmtree(build_dir)
    
    # Build command
    cmd = [
        sys.executable, str(setup_path), 
        "build_exe",
        "--build-exe", str(output_dir / "ChickenFarmManager_cx_Freeze")
    ]
    
    print("🔨 Running cx_Freeze build...")
    
    try:
        # Change to project root
        original_cwd = os.getcwd()
        os.chdir(project_root)
        
        # Run cx_Freeze
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        print("✅ cx_Freeze build completed")
        
        # Check if executable was created
        exe_dir = output_dir / "ChickenFarmManager_cx_Freeze"
        exe_path = exe_dir / "ChickenFarmManager.exe"
        
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"✅ Executable created: {exe_path} ({size_mb:.1f} MB)")
            
            # Copy Qt plugins manually
            copy_qt_plugins_cx_freeze(exe_dir)
            
            return True
        else:
            print("❌ Executable not found after build")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ cx_Freeze build failed: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False
    finally:
        os.chdir(original_cwd)

def copy_qt_plugins_cx_freeze(exe_dir):
    """Copy Qt plugins for cx_Freeze build"""
    try:
        import PyQt5
        pyqt5_path = Path(PyQt5.__file__).parent
        qt_plugins_path = pyqt5_path / "Qt5" / "plugins"
        
        if not qt_plugins_path.exists():
            qt_plugins_path = pyqt5_path / "Qt" / "plugins"
        
        if not qt_plugins_path.exists():
            print("⚠️ Qt plugins not found")
            return
        
        # Create Qt plugins directory in executable directory
        exe_qt_dir = exe_dir / "lib" / "PyQt5" / "Qt" / "plugins"
        exe_qt_dir.mkdir(parents=True, exist_ok=True)
        
        # Essential plugins
        essential_plugins = {
            'platforms': ['qwindows.dll', 'qminimal.dll'],
            'imageformats': ['qico.dll', 'qjpeg.dll', 'qgif.dll'],
            'iconengines': ['qsvgicon.dll'],
        }
        
        copied_count = 0
        
        for plugin_dir, plugin_files in essential_plugins.items():
            plugin_src_dir = qt_plugins_path / plugin_dir
            plugin_dst_dir = exe_qt_dir / plugin_dir
            plugin_dst_dir.mkdir(exist_ok=True)
            
            if plugin_src_dir.exists():
                for plugin_file in plugin_files:
                    plugin_src = plugin_src_dir / plugin_file
                    plugin_dst = plugin_dst_dir / plugin_file
                    
                    if plugin_src.exists():
                        shutil.copy2(plugin_src, plugin_dst)
                        print(f"  ✅ Copied Qt plugin: {plugin_dir}/{plugin_file}")
                        copied_count += 1
        
        # Create qt.conf
        qt_conf_content = """[Paths]
Plugins = lib/PyQt5/Qt/plugins
"""
        qt_conf_path = exe_dir / "qt.conf"
        with open(qt_conf_path, 'w') as f:
            f.write(qt_conf_content)
        
        print(f"✅ Copied {copied_count} Qt plugins for cx_Freeze build")
        
    except Exception as e:
        print(f"⚠️ Could not copy Qt plugins: {e}")

def test_cx_freeze_executable():
    """Test the cx_Freeze executable"""
    print("\n🔍 Testing cx_Freeze executable...")
    
    project_root = Path(__file__).parent.parent.parent
    output_dir = project_root / "installer" / "output"
    exe_path = output_dir / "ChickenFarmManager_cx_Freeze" / "ChickenFarmManager.exe"
    
    if not exe_path.exists():
        print("❌ cx_Freeze executable not found")
        return False
    
    try:
        # Try to run the executable briefly
        process = subprocess.Popen(
            [str(exe_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait a moment
        import time
        time.sleep(5)
        
        # Check if it's still running
        if process.poll() is None:
            print("✅ cx_Freeze executable started successfully!")
            process.terminate()
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"⚠️ cx_Freeze executable exited with code: {process.returncode}")
            if stderr:
                print(f"Error: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ Could not test cx_Freeze executable: {e}")
        return False

def main():
    """Main function"""
    print("🚀 cx_Freeze Build System")
    print("=" * 50)
    
    if build_with_cx_freeze():
        print("\n🎉 cx_Freeze build completed!")
        
        if test_cx_freeze_executable():
            print("\n✅ cx_Freeze executable test passed!")
            print("\n📋 cx_Freeze provides an alternative to PyInstaller")
            print("   This may work better with your PyQt5 installation")
        else:
            print("\n⚠️ cx_Freeze executable test had issues")
        
        return True
    else:
        print("\n❌ cx_Freeze build failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
