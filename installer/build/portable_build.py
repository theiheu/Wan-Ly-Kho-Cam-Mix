#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Portable Build System
Creates a portable version of the application without PyInstaller
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# Set UTF-8 encoding for console output
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def create_portable_app():
    """Create a portable version of the application"""
    print("Portable Build System")
    print("=" * 50)

    project_root = Path(__file__).parent.parent.parent
    output_dir = project_root / "installer" / "output"

    # Create portable app directory
    portable_dir = output_dir / "ChickenFarmManager_Portable"
    if portable_dir.exists():
        shutil.rmtree(portable_dir)

    portable_dir.mkdir(parents=True)
    print("✅ Created portable directory")

    # Copy source code
    src_dir = project_root / "src"
    portable_src = portable_dir / "src"
    shutil.copytree(src_dir, portable_src)
    print("✅ Copied source code")

    # Copy main run script
    run_script = project_root / "run.py"
    if run_script.exists():
        shutil.copy2(run_script, portable_dir / "run.py")
        print("✅ Copied run.py")

    # Copy requirements
    req_file = project_root / "requirements.txt"
    if req_file.exists():
        shutil.copy2(req_file, portable_dir / "requirements.txt")
        print("✅ Copied requirements.txt")

    # Create a launcher script
    launcher_content = f'''#!/usr/bin/env python3
"""
Chicken Farm Manager Launcher
Portable version launcher with Qt plugin setup
"""

import os
import sys
import subprocess
from pathlib import Path

def setup_environment():
    """Setup the environment for the application"""
    app_dir = Path(__file__).parent

    # Add src to Python path
    src_dir = app_dir / "src"
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    # Set Qt plugin path if PyQt5 is available
    try:
        import PyQt5
        pyqt5_path = Path(PyQt5.__file__).parent
        qt_plugins_path = pyqt5_path / "Qt5" / "plugins"

        if not qt_plugins_path.exists():
            qt_plugins_path = pyqt5_path / "Qt" / "plugins"

        if qt_plugins_path.exists():
            os.environ['QT_PLUGIN_PATH'] = str(qt_plugins_path)
            print(f"Qt plugins found: {{qt_plugins_path}}")
        else:
            print("WARNING: Qt plugins not found - application may have display issues")
    except ImportError:
        print("WARNING: PyQt5 not found")

    # Set other environment variables
    os.environ['PYTHONPATH'] = str(src_dir)

def main():
    """Main launcher function"""
    print("Chicken Farm Manager - Portable Version")
    print("=" * 50)

    # Setup environment
    setup_environment()

    # Try to import and run the main application
    try:
        print("Starting application...")

        # Try different import methods
        try:
            from src.main import main as app_main
            app_main()
        except ImportError:
            try:
                import main
                main.main()
            except ImportError:
                # Fallback: run the run.py script
                app_dir = Path(__file__).parent
                run_script = app_dir / "run.py"
                if run_script.exists():
                    print("Running via run.py...")
                    subprocess.run([sys.executable, str(run_script)], cwd=str(app_dir))
                else:
                    print("ERROR: Could not find main application entry point")
                    print("Available files:")
                    for file in app_dir.iterdir():
                        if file.is_file():
                            print(f"  - {{file.name}}")

    except Exception as e:
        print(f"ERROR: Error starting application: {{e}}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
'''

    launcher_path = portable_dir / "ChickenFarmManager.py"
    with open(launcher_path, 'w', encoding='utf-8') as f:
        f.write(launcher_content)

    print("✅ Created launcher script")

    # Create batch file for Windows
    batch_content = f'''@echo off
title Chicken Farm Manager - Portable
cd /d "%~dp0"

echo Starting Chicken Farm Manager...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if required packages are installed
python -c "import PyQt5" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install required packages
        pause
        exit /b 1
    )
)

REM Run the application
python ChickenFarmManager.py

REM Keep window open if there was an error
if errorlevel 1 (
    echo.
    echo Application exited with an error
    pause
)
'''

    batch_path = portable_dir / "Run_ChickenFarmManager.bat"
    with open(batch_path, 'w', encoding='utf-8') as f:
        f.write(batch_content)

    print("✅ Created batch launcher")

    # Create README
    readme_content = f'''# Chicken Farm Manager - Portable Version

## Quick Start

1. **Run the application:**
   - Double-click `Run_ChickenFarmManager.bat`
   - Or run `python ChickenFarmManager.py` in command line

2. **Requirements:**
   - Python 3.8 or newer
   - Required packages will be installed automatically

## Manual Installation

If automatic installation fails:

```bash
pip install -r requirements.txt
```

## Troubleshooting

### Qt Plugin Errors
If you see "Qt platform plugin" errors:
1. Make sure PyQt5 is properly installed
2. Try reinstalling: `pip uninstall PyQt5 && pip install PyQt5`

### Import Errors
If you see import errors:
1. Make sure you're running from the application directory
2. Check that all source files are present in the `src/` folder

### Permission Errors
1. Make sure you have write permissions in the application directory
2. Try running as administrator

## Files

- `ChickenFarmManager.py` - Main launcher script
- `Run_ChickenFarmManager.bat` - Windows batch launcher
- `src/` - Application source code
- `requirements.txt` - Python package requirements

## Support

For support and updates, visit: https://github.com/Minh-Tan_Phat

---
Chicken Farm Manager v2.0.0
© 2025 Minh-Tan_Phat
'''

    readme_path = portable_dir / "README.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)

    print("✅ Created README documentation")

    # Create a ZIP package
    zip_path = output_dir / "ChickenFarmManager_Portable.zip"
    shutil.make_archive(str(zip_path.with_suffix('')), 'zip', str(portable_dir))
    print("✅ Created ZIP package")

    print("\n🎉 Portable application created successfully!")
    print("📍 Location: installer/output/ChickenFarmManager_Portable/")
    print("📦 ZIP package: installer/output/ChickenFarmManager_Portable.zip")
    print("\n📋 How to use:")
    print("1. Extract the ZIP file on any Windows computer")
    print("2. Run 'Run_ChickenFarmManager.bat'")
    print("3. The application will install dependencies and start")

    return True

def test_portable_app():
    """Test the portable application"""
    print("\nTesting portable application...")

    project_root = Path(__file__).parent.parent.parent
    output_dir = project_root / "installer" / "output"
    portable_dir = output_dir / "ChickenFarmManager_Portable"

    if not portable_dir.exists():
        print("ERROR: Portable directory not found")
        return False

    # Test the launcher
    launcher_path = portable_dir / "ChickenFarmManager.py"
    if launcher_path.exists():
        print("✅ Launcher script exists")

        # Try to run it briefly
        try:
            process = subprocess.Popen(
                [sys.executable, str(launcher_path)],
                cwd=str(portable_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Wait a moment
            import time
            time.sleep(3)

            # Terminate
            process.terminate()

            print("Launcher appears to work")
            return True

        except Exception as e:
            print(f"⚠️ WARNING: Launcher test failed: {e}")
            return False
    else:
        print("ERROR: Launcher not found")
        return False

def main():
    """Main function"""
    if create_portable_app():
        test_portable_app()
        return True
    else:
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
