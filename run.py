#!/usr/bin/env python3
"""
Run script for the Chicken Farm App
"""

import sys
import os
import time
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox, QDesktopWidget
from PyQt5.QtCore import Qt, QTimer

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Simple error handling before modules are loaded
def simple_exception_handler(exc_type, exc_value, exc_traceback):
    """Simple exception handler for startup errors"""
    error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    print(f"ERROR: {error_msg}")

    # Try to show a message box
    try:
        app = QApplication.instance() or QApplication(sys.argv)
        QMessageBox.critical(None, "Lỗi khởi động",
                            f"Đã xảy ra lỗi khi khởi động ứng dụng:\n\n{exc_value}\n\n"
                            "Vui lòng cài đặt các gói phụ thuộc cần thiết:\n"
                            "pip install -r requirements.txt")
    except:
        pass

    return 1

# Set temporary exception handler
sys.excepthook = simple_exception_handler

def center_window(window, screen_fraction=0.75):
    """
    Center window on screen and resize to occupy given fraction of screen

    Args:
        window: Window to center and resize
        screen_fraction: Fraction of screen to occupy (0.0 to 1.0)
    """
    # Get desktop geometry
    desktop = QDesktopWidget().availableGeometry()

    # Calculate window size (75% of desktop)
    width = int(desktop.width() * screen_fraction)
    height = int(desktop.height() * screen_fraction)

    # Calculate position to center window
    x = (desktop.width() - width) // 2
    y = (desktop.height() - height) // 2

    # Set window size and position
    window.setGeometry(x, y, width, height)

    print(f"Window positioned at ({x}, {y}) with size {width}x{height}")
    print(f"Desktop size: {desktop.width()}x{desktop.height()}")

def main():
    """Main function to run the application"""
    try:
        # Create application
        app = QApplication(sys.argv)

        # Import the main window class
        from src.ui.main_window import ChickenFarmApp
        from src.ui.styles import apply_stylesheet
        from src.ui.logo import create_app_logo

        # Set application icon
        app.setWindowIcon(create_app_logo())

        # Apply stylesheet
        apply_stylesheet(app)

        # Try to import optimization modules
        try:
            from src.utils.app_initializer import app_initializer
            from src.utils.error_handler import logger, handle_exception

            # Set global exception handler
            sys.excepthook = handle_exception

            # Initialize the application with optimizations
            app_initializer.initialize(app)

            # Create main window
            window = ChickenFarmApp()

            # Show window first
            window.show()

            # Use QTimer to resize the window after it's shown
            QTimer.singleShot(100, lambda: center_window(window))

            # Close splash screen
            app_initializer.close_splash_screen()

            # Set up cleanup on exit
            app.aboutToQuit.connect(app_initializer.cleanup)

        except ImportError as e:
            print(f"Warning: Could not import optimization modules: {e}")
            print("Continuing without optimizations...")

            # Create main window without optimizations
            window = ChickenFarmApp()

            # Show window first
            window.show()

            # Use QTimer to resize the window after it's shown
            QTimer.singleShot(100, lambda: center_window(window))

        # Run the application
        return app.exec_()

    except Exception as e:
        print(f"Critical error in main: {e}")
        print(traceback.format_exc())

        # Show error message
        try:
            QMessageBox.critical(
                None,
                "Lỗi khởi động ứng dụng",
                f"Đã xảy ra lỗi khi khởi động ứng dụng: {str(e)}\n\n"
                "Vui lòng kiểm tra file log để biết thêm chi tiết."
            )
        except:
            pass

        return 1

if __name__ == "__main__":
    # Run the application
    exit_code = main()

    # Exit with the appropriate code
    sys.exit(exit_code)