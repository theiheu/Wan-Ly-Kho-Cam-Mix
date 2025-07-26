"""
Application initializer for the Chicken Farm App.
This module initializes the application with optimizations and configurations.
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

from PyQt5.QtWidgets import QApplication, QSplashScreen, QMessageBox
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont
from PyQt5.QtCore import Qt, QTimer

# Try to import modules but don't fail if they're not available
try:
    from src.utils.error_handler import logger, setup_logging
except ImportError:
    # Create a simple logger if error_handler is not available
    import logging
    logger = logging.getLogger("ChickenFarmApp")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s"))
    logger.addHandler(handler)

    def setup_logging(log_dir="logs", log_level=logging.INFO):
        return logger

try:
    from src.utils.cache_manager import cache_manager
except ImportError:
    # Create a dummy cache manager if not available
    class DummyCacheManager:
        def get(self, key, use_disk=False): return None
        def set(self, key, value, ttl=300, use_disk=False): pass
        def clear(self): pass

    cache_manager = DummyCacheManager()

try:
    from src.utils.performance_monitor import performance_monitor
except ImportError:
    # Create a dummy performance monitor if not available
    class DummyPerformanceMonitor:
        def start_monitoring(self, interval=5.0): pass
        def stop_monitoring(self): pass
        def add_metric(self, name, value): pass
        def save_metrics(self, filename=None): return ""

    performance_monitor = DummyPerformanceMonitor()

try:
    from src.utils.optimizations import backup_data_files
except ImportError:
    # Create a dummy backup function if not available
    def backup_data_files(backup_dir="backups"):
        os.makedirs(backup_dir, exist_ok=True)
        return True


class AppInitializer:
    """Class to initialize the application with optimizations."""

    def __init__(self, app_name: str = "Chicken Farm App"):
        """
        Initialize the application initializer.

        Args:
            app_name: Application name
        """
        self.app_name = app_name
        self.start_time = time.time()
        self.config = {}
        self.splash = None

        # Set up logging
        try:
            setup_logging(log_level=20)  # INFO level
        except Exception as e:
            print(f"Warning: Could not set up logging: {e}")

        # Create necessary directories
        self._create_directories()

        # Load configuration
        self._load_config()

    def _create_directories(self) -> None:
        """Create necessary directories."""
        directories = [
            "src/data/cache",
            "src/data/config",
            "src/data/reports",
            "src/data/imports",
            "src/data/presets/feed",
            "src/data/presets/mix",
            "logs",
            "metrics",
            "backups"
        ]

        for directory in directories:
            try:
                os.makedirs(directory, exist_ok=True)
                logger.debug(f"Created directory: {directory}")
            except Exception as e:
                logger.warning(f"Could not create directory {directory}: {e}")

    def _load_config(self) -> None:
        """Load application configuration."""
        config_file = "src/data/config/app_config.json"

        # Default configuration
        default_config = {
            "performance_monitoring": True,
            "monitoring_interval": 10.0,
            "cache_enabled": True,
            "backup_on_start": True,
            "backup_on_exit": True,
            "auto_save_interval": 300,  # 5 minutes
            "ui_theme": "default",
            "font_size": 14,
            "table_row_height": 30
        }

        # Try to load existing configuration
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)

                # Merge with default config
                self.config = {**default_config, **loaded_config}
                logger.info(f"Loaded configuration from {config_file}")
            except Exception as e:
                logger.error(f"Error loading configuration: {e}")
                self.config = default_config
        else:
            # Create default configuration
            self.config = default_config
            try:
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, ensure_ascii=False, indent=2)
                logger.info(f"Created default configuration in {config_file}")
            except Exception as e:
                logger.error(f"Error creating configuration file: {e}")

    def show_splash_screen(self, app: QApplication, image_path: str = None) -> None:
        """
        Show a splash screen while the application is loading.

        Args:
            app: QApplication instance
            image_path: Path to splash screen image
        """
        try:
            # Create a default splash screen if no image is provided
            if image_path is None or not os.path.exists(image_path):
                # Create a pixmap
                pixmap = QPixmap(400, 300)
                pixmap.fill(QColor(240, 248, 255))  # Light blue background

                # Add text
                painter = QPainter(pixmap)
                painter.setFont(QFont("Arial", 20, QFont.Bold))
                painter.setPen(QColor(0, 100, 0))  # Dark green text
                painter.drawText(pixmap.rect(), Qt.AlignCenter, f"{self.app_name}\nĐang khởi động...")
                painter.end()
            else:
                # Load image from file
                pixmap = QPixmap(image_path)

            # Create splash screen
            self.splash = QSplashScreen(pixmap)
            self.splash.show()

            # Process events to show splash immediately
            app.processEvents()
        except Exception as e:
            logger.error(f"Error showing splash screen: {e}")
            self.splash = None

    def update_splash_message(self, message: str) -> None:
        """
        Update splash screen message.

        Args:
            message: Message to display
        """
        if self.splash:
            try:
                self.splash.showMessage(
                    message,
                    Qt.AlignBottom | Qt.AlignCenter,
                    QColor(0, 0, 0)
                )
                QApplication.processEvents()
            except Exception as e:
                logger.error(f"Error updating splash message: {e}")

    def close_splash_screen(self) -> None:
        """Close the splash screen."""
        if self.splash:
            try:
                self.splash.close()
            except Exception as e:
                logger.error(f"Error closing splash screen: {e}")
            self.splash = None

    def initialize(self, app: QApplication) -> None:
        """
        Initialize the application with optimizations.

        Args:
            app: QApplication instance
        """
        try:
            # Show splash screen
            self.show_splash_screen(app)
            self.update_splash_message("Đang khởi tạo ứng dụng...")

            # Set application style
            if self.config.get("ui_theme") == "dark":
                app.setStyle("Fusion")
                # Apply dark palette (could be implemented in a separate function)
            else:
                app.setStyle("Fusion")  # Default style

            # Create backup if enabled
            if self.config.get("backup_on_start", True):
                self.update_splash_message("Đang tạo bản sao lưu...")
                try:
                    backup_data_files()
                except Exception as e:
                    logger.error(f"Error creating backup: {e}")

            # Start performance monitoring if enabled
            if self.config.get("performance_monitoring", True):
                self.update_splash_message("Đang khởi động hệ thống giám sát hiệu suất...")
                try:
                    interval = self.config.get("monitoring_interval", 10.0)
                    performance_monitor.start_monitoring(interval)
                except Exception as e:
                    logger.error(f"Error starting performance monitoring: {e}")

            # Clear cache if needed
            if self.config.get("clear_cache_on_start", False):
                self.update_splash_message("Đang xóa bộ nhớ đệm...")
                try:
                    cache_manager.clear()
                except Exception as e:
                    logger.error(f"Error clearing cache: {e}")

            # Log initialization complete
            elapsed_time = time.time() - self.start_time
            logger.info(f"Application initialized in {elapsed_time:.2f} seconds")
            self.update_splash_message(f"Khởi tạo hoàn tất ({elapsed_time:.2f}s)")

            # Add a small delay to show the completion message
            time.sleep(0.5)
        except Exception as e:
            logger.error(f"Error during initialization: {e}")
            # Try to show error message to user
            try:
                QMessageBox.critical(None, "Lỗi khởi động", f"Đã xảy ra lỗi khi khởi động ứng dụng: {str(e)}")
            except:
                print(f"Critical error during initialization: {e}")

    def cleanup(self) -> None:
        """Clean up resources before application exit."""
        try:
            # Stop performance monitoring
            try:
                performance_monitor.stop_monitoring()

                # Save performance metrics
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                performance_monitor.save_metrics(f"exit_metrics_{timestamp}.json")
            except Exception as e:
                logger.error(f"Error stopping performance monitoring: {e}")

            # Create backup if enabled
            if self.config.get("backup_on_exit", True):
                try:
                    backup_data_files(backup_dir="backups/exit_backups")
                except Exception as e:
                    logger.error(f"Error creating exit backup: {e}")

            # Log cleanup complete
            logger.info("Application cleanup complete")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


# Create a global initializer instance
app_initializer = AppInitializer()