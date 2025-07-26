"""
Error handling and logging module for the Chicken Farm App.
This module provides functions to handle errors and log events.
"""

import os
import sys
import traceback
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from functools import wraps

# Use conditional import for PyQt5 to avoid errors if it's not available
try:
    from PyQt5.QtWidgets import QMessageBox
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False


# Set up logging
def setup_logging(log_dir: str = "logs", log_level: int = logging.INFO) -> logging.Logger:
    """
    Set up logging configuration.

    Args:
        log_dir: Directory to store log files
        log_level: Logging level (default: INFO)

    Returns:
        Logger instance
    """
    try:
        # Create log directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)

        # Create logger
        logger = logging.getLogger("ChickenFarmApp")
        logger.setLevel(log_level)

        # Check if handlers already exist to avoid duplicates
        if not logger.handlers:
            # Create file handler
            log_file = os.path.join(log_dir, f"app_{datetime.now().strftime('%Y%m%d')}.log")
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(log_level)

            # Create console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)

            # Create formatter
            formatter = logging.Formatter(
                "[%(asctime)s] %(levelname)s [%(filename)s:%(lineno)d] - %(message)s"
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)

            # Add handlers to logger
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)

        return logger
    except Exception as e:
        # If logging setup fails, create a simple logger that only prints to console
        print(f"Warning: Could not set up logging to file: {e}")
        logger = logging.getLogger("ChickenFarmApp")
        logger.setLevel(log_level)

        # Check if handlers already exist
        if not logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)
            formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s")
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        return logger


# Create logger instance
try:
    logger = setup_logging()
except Exception as e:
    # Fallback logger if setup fails completely
    print(f"Critical error setting up logger: {e}")
    logger = logging.getLogger("ChickenFarmApp")
    handler = logging.StreamHandler()
    logger.addHandler(handler)


def log_exception(exc_info):
    """
    Log an exception.

    Args:
        exc_info: Exception info from sys.exc_info()
    """
    try:
        exc_type, exc_value, exc_traceback = exc_info
        tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        tb_text = "".join(tb_lines)
        logger.error(f"Unhandled exception: {tb_text}")
    except Exception as e:
        print(f"Error logging exception: {e}")
        print(f"Original exception: {''.join(traceback.format_exception(*exc_info))}")


def handle_exception(exc_type, exc_value, exc_traceback):
    """
    Global exception handler.

    Args:
        exc_type: Exception type
        exc_value: Exception value
        exc_traceback: Exception traceback
    """
    # Log the exception
    log_exception((exc_type, exc_value, exc_traceback))

    # Show error message if PyQt is available
    if PYQT_AVAILABLE:
        try:
            error_message = f"Đã xảy ra lỗi: {exc_type.__name__}: {exc_value}"
            QMessageBox.critical(None, "Lỗi", error_message)
        except Exception as e:
            print(f"Could not show error dialog: {e}")
    else:
        print(f"Error: {exc_type.__name__}: {exc_value}")


# Set global exception handler
sys.excepthook = handle_exception


def try_except(func):
    """
    Decorator to handle exceptions in functions.

    Args:
        func: Function to decorate

    Returns:
        Decorated function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Log the exception
            logger.error(f"Exception in {func.__name__}: {str(e)}")
            logger.error(traceback.format_exc())

            # Show error message if PyQt is available
            if PYQT_AVAILABLE:
                try:
                    error_message = f"Lỗi trong {func.__name__}: {str(e)}"
                    QMessageBox.critical(None, "Lỗi", error_message)
                except Exception as dialog_error:
                    logger.error(f"Could not show error dialog: {dialog_error}")
            else:
                print(f"Error in {func.__name__}: {str(e)}")

            # Return None or a default value
            return None
    return wrapper


def log_function_call(func):
    """
    Decorator to log function calls.

    Args:
        func: Function to decorate

    Returns:
        Decorated function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            logger.debug(f"Calling {func.__name__} with args: {args}, kwargs: {kwargs}")
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} returned: {result}")
            return result
        except Exception as e:
            logger.error(f"Error logging function call {func.__name__}: {e}")
            return func(*args, **kwargs)  # Still call the function even if logging fails
    return wrapper


def log_event(event_type: str, event_data: Dict[str, Any]) -> None:
    """
    Log an application event.

    Args:
        event_type: Type of event
        event_data: Event data
    """
    try:
        logger.info(f"Event: {event_type} - {json.dumps(event_data, ensure_ascii=False)}")
    except Exception as e:
        logger.error(f"Error logging event: {e}")


def show_error_dialog(title: str, message: str) -> None:
    """
    Show an error dialog.

    Args:
        title: Dialog title
        message: Error message
    """
    try:
        logger.error(f"Error dialog: {title} - {message}")
        if PYQT_AVAILABLE:
            QMessageBox.critical(None, title, message)
        else:
            print(f"ERROR: {title} - {message}")
    except Exception as e:
        print(f"Failed to show error dialog: {e}")
        print(f"Original error: {title} - {message}")


def show_warning_dialog(title: str, message: str) -> None:
    """
    Show a warning dialog.

    Args:
        title: Dialog title
        message: Warning message
    """
    try:
        logger.warning(f"Warning dialog: {title} - {message}")
        if PYQT_AVAILABLE:
            QMessageBox.warning(None, title, message)
        else:
            print(f"WARNING: {title} - {message}")
    except Exception as e:
        print(f"Failed to show warning dialog: {e}")
        print(f"Original warning: {title} - {message}")


def show_info_dialog(title: str, message: str) -> None:
    """
    Show an information dialog.

    Args:
        title: Dialog title
        message: Information message
    """
    try:
        logger.info(f"Info dialog: {title} - {message}")
        if PYQT_AVAILABLE:
            QMessageBox.information(None, title, message)
        else:
            print(f"INFO: {title} - {message}")
    except Exception as e:
        print(f"Failed to show info dialog: {e}")
        print(f"Original info: {title} - {message}")


def confirm_dialog(title: str, message: str) -> bool:
    """
    Show a confirmation dialog.

    Args:
        title: Dialog title
        message: Confirmation message

    Returns:
        bool: True if confirmed, False otherwise
    """
    try:
        logger.info(f"Confirm dialog: {title} - {message}")
        if PYQT_AVAILABLE:
            reply = QMessageBox.question(
                None,
                title,
                message,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            return reply == QMessageBox.Yes
        else:
            # Default to False if no UI is available
            print(f"CONFIRM: {title} - {message} (defaulting to No)")
            return False
    except Exception as e:
        print(f"Failed to show confirmation dialog: {e}")
        print(f"Original confirmation: {title} - {message}")
        return False