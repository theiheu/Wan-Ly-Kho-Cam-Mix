#!/usr/bin/env python3
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
            print(f"Qt plugins found: {qt_plugins_path}")
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
                            print(f"  - {file.name}")

    except Exception as e:
        print(f"ERROR: Error starting application: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
