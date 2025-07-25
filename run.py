#!/usr/bin/env python3
"""
Run script for the Chicken Farm App
"""

import sys
import os
from PyQt5.QtWidgets import QApplication

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the main window class
from src.ui.main_window import ChickenFarmApp
from src.ui.styles import apply_stylesheet
from src.ui.splash_screen import SplashScreen
from src.ui.logo import create_app_logo

def main():
    """Main function to run the application"""
    # Create application
    app = QApplication(sys.argv)

    # Set application icon
    app.setWindowIcon(create_app_logo())

    # Apply stylesheet
    apply_stylesheet(app)

    # Create main window (but don't show it yet)
    window = ChickenFarmApp()

    # Create and show splash screen
    splash = SplashScreen()
    splash.start_progress(app, window)

    # Run the application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()