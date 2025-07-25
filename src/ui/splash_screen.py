"""
Splash Screen for the Chicken Farm App
"""

from PyQt5.QtWidgets import QSplashScreen, QProgressBar, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter

from src.ui.logo import create_splash_image

class SplashScreen(QSplashScreen):
    """Custom splash screen with progress bar"""

    def __init__(self, width=500, height=350):
        """Initialize the splash screen

        Args:
            width: Width of the splash screen
            height: Height of the splash screen
        """
        # Create splash image
        splash_pixmap = create_splash_image(width, height)

        # Initialize splash screen
        super().__init__(splash_pixmap)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

        # Create progress bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(width//10, height - height//6, width - width//5, height//20)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid white;
                border-radius: 5px;
                background-color: transparent;
                color: white;
                text-align: center;
            }

            QProgressBar::chunk {
                background-color: white;
                width: 10px;
                margin: 0.5px;
            }
        """)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        # Initialize progress
        self.progress = 0

    def progress_event(self):
        """Update progress bar"""
        self.progress += 10
        self.progress_bar.setValue(self.progress)

    def start_progress(self, app, main_window):
        """Start progress animation and launch main window when done

        Args:
            app: QApplication instance
            main_window: Main window to show when splash screen is done
        """
        self.show()

        # Process events to ensure splash screen is displayed
        app.processEvents()

        # Create timer to update progress
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.progress_event)
        self.timer.start(150)  # Update every 150ms

        # Create timer to finish splash screen
        self.finish_timer = QTimer(self)
        self.finish_timer.setSingleShot(True)
        self.finish_timer.timeout.connect(lambda: self.finish_splash(main_window))
        self.finish_timer.start(1500)  # Finish after 1.5 seconds

    def finish_splash(self, main_window):
        """Finish splash screen and show main window

        Args:
            main_window: Main window to show
        """
        # Stop progress timer
        self.timer.stop()

        # Set progress to 100%
        self.progress_bar.setValue(100)

        # Show main window and close splash screen
        main_window.show()
        self.finish(main_window)

    def drawContents(self, painter):
        """Draw splash screen contents

        Args:
            painter: QPainter instance
        """
        super().drawContents(painter)