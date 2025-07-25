"""
Styles for the Chicken Farm App
"""

from PyQt5.QtGui import QColor, QFont, QPalette, QBrush, QLinearGradient
from PyQt5.QtCore import Qt

# Color scheme
COLORS = {
    "primary": "#4a86e8",
    "secondary": "#6aa84f",
    "background": "#f5f5f5",
    "text": "#333333",
    "light_text": "#666666",
    "success": "#6aa84f",
    "warning": "#e69138",
    "error": "#cc0000",
    "header_bg": "#e8eaf6",
    "table_header_bg": "#e3f2fd",
    "table_row_odd": "#ffffff",
    "table_row_even": "#f5f5f5",
    "button_hover": "#3d76cc",
    "button_pressed": "#2d5699"
}

# Font settings
FONTS = {
    "default": QFont("Arial", 10),
    "header": QFont("Arial", 12, QFont.Bold),
    "title": QFont("Arial", 14, QFont.Bold),
    "button": QFont("Arial", 10, QFont.Bold),
    "table_header": QFont("Arial", 10, QFont.Bold),
    "table_cell": QFont("Arial", 10)
}

# Stylesheet definitions
STYLESHEET = f"""
QMainWindow, QDialog {{
    background-color: {COLORS["background"]};
}}

QTabWidget::pane {{
    border: 1px solid #cccccc;
    background-color: white;
    border-radius: 4px;
}}

QTabBar::tab {{
    background-color: #e0e0e0;
    color: {COLORS["text"]};
    border: 1px solid #cccccc;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    padding: 6px 12px;
    margin-right: 2px;
}}

QTabBar::tab:selected {{
    background-color: white;
    border-bottom: 1px solid white;
}}

QTabBar::tab:hover {{
    background-color: #f0f0f0;
}}

QPushButton {{
    background-color: {COLORS["primary"]};
    color: white;
    border: none;
    border-radius: 4px;
    padding: 6px 12px;
    min-width: 80px;
}}

QPushButton:hover {{
    background-color: {COLORS["button_hover"]};
}}

QPushButton:pressed {{
    background-color: {COLORS["button_pressed"]};
}}

QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {{
    border: 1px solid #cccccc;
    border-radius: 4px;
    padding: 4px;
    background-color: white;
}}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {{
    border: 1px solid {COLORS["primary"]};
}}

QTableWidget {{
    border: 1px solid #cccccc;
    border-radius: 4px;
    background-color: white;
    gridline-color: #e0e0e0;
}}

QTableWidget::item {{
    padding: 4px;
}}

QTableWidget::item:selected {{
    background-color: {COLORS["primary"]};
    color: white;
}}

QHeaderView::section {{
    background-color: {COLORS["table_header_bg"]};
    color: {COLORS["text"]};
    padding: 6px;
    border: 1px solid #cccccc;
    font-weight: bold;
}}

QGroupBox {{
    border: 1px solid #cccccc;
    border-radius: 4px;
    margin-top: 12px;
    padding-top: 12px;
    background-color: white;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 0 5px;
    color: {COLORS["primary"]};
    font-weight: bold;
}}

QLabel {{
    color: {COLORS["text"]};
}}

QMessageBox {{
    background-color: white;
}}

QMessageBox QPushButton {{
    min-width: 60px;
}}
"""

def apply_stylesheet(app):
    """Apply the stylesheet to the application"""
    app.setStyleSheet(STYLESHEET)

def set_dark_palette(app):
    """Set a dark palette for the application (alternative theme)"""
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(dark_palette)