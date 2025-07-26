"""
Styles for the Chicken Farm App
"""

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt

def apply_stylesheet(app):
    """Apply stylesheet to the application"""
    # Set fusion style for a modern look
    app.setStyle("Fusion")

    # Set application-wide stylesheet
    app.setStyleSheet("""
        /* General styles */
        QWidget {
            font-family: Arial, sans-serif;
            font-size: 16px;
        }

        /* Main window */
        QMainWindow {
            background-color: #f5f5f5;
        }

        /* Labels */
        QLabel {
            padding: 5px;
        }

        /* Headers */
        QLabel[header=true] {
            font-size: 20px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px;
            background-color: #ecf0f1;
            border-radius: 5px;
        }

        /* Buttons */
        QPushButton {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 5px;
            font-weight: bold;
            min-height: 40px;
            min-width: 120px;
        }

        QPushButton:hover {
            background-color: #2980b9;
        }

        QPushButton:pressed {
            background-color: #1c6ea4;
        }

        QPushButton:disabled {
            background-color: #bdc3c7;
            color: #7f8c8d;
        }

        /* Tables */
        QTableWidget {
            gridline-color: #bdc3c7;
            background-color: white;
            border: 1px solid #bdc3c7;
            border-radius: 5px;
            selection-background-color: #d6eaf8;
        }

        QTableWidget::item {
            padding: 5px;
        }

        QTableWidget::item:selected {
            background-color: #3498db;
            color: white;
        }

        QHeaderView::section {
            background-color: #34495e;
            color: white;
            padding: 8px;
            border: 1px solid #2c3e50;
            font-weight: bold;
        }

        QHeaderView::section:horizontal {
            border-top: 0;
        }

        QHeaderView::section:vertical {
            border-left: 0;
        }

        /* Tabs */
        QTabWidget::pane {
            border: 1px solid #bdc3c7;
            background: white;
            border-radius: 5px;
        }

        QTabBar::tab {
            background: #ecf0f1;
            border: 1px solid #bdc3c7;
            padding: 10px 15px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }

        QTabBar::tab:selected {
            background: #3498db;
            color: white;
            border-bottom-color: white;
        }

        QTabBar::tab:!selected {
            margin-top: 2px;
        }

        /* Combo boxes */
        QComboBox {
            border: 1px solid #bdc3c7;
            border-radius: 5px;
            padding: 5px 10px;
            min-height: 30px;
            background: white;
        }

        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 25px;
            border-left: 1px solid #bdc3c7;
        }

        QComboBox::down-arrow {
            image: url(:/icons/down_arrow.png);
        }

        QComboBox QAbstractItemView {
            border: 1px solid #bdc3c7;
            selection-background-color: #3498db;
            selection-color: white;
        }

        /* Spin boxes */
        QSpinBox, QDoubleSpinBox {
            border: 1px solid #bdc3c7;
            border-radius: 5px;
            padding: 5px;
            min-height: 30px;
            background: white;
        }

        QSpinBox::up-button, QDoubleSpinBox::up-button {
            subcontrol-origin: border;
            subcontrol-position: top right;
            width: 20px;
            border-left: 1px solid #bdc3c7;
            border-bottom: 1px solid #bdc3c7;
        }

        QSpinBox::down-button, QDoubleSpinBox::down-button {
            subcontrol-origin: border;
            subcontrol-position: bottom right;
            width: 20px;
            border-left: 1px solid #bdc3c7;
            border-top: 1px solid #bdc3c7;
        }

        /* Group boxes */
        QGroupBox {
            border: 1px solid #bdc3c7;
            border-radius: 5px;
            margin-top: 20px;
            font-weight: bold;
            background-color: #f9f9f9;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 10px;
            padding: 0 5px;
            background-color: #f9f9f9;
        }

        /* Scroll bars */
        QScrollBar:vertical {
            border: none;
            background: #f0f0f0;
            width: 15px;
            margin: 15px 0 15px 0;
            border-radius: 5px;
        }

        QScrollBar::handle:vertical {
            background: #bdc3c7;
            min-height: 30px;
            border-radius: 5px;
        }

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            border: none;
            background: none;
            height: 15px;
        }

        QScrollBar:horizontal {
            border: none;
            background: #f0f0f0;
            height: 15px;
            margin: 0 15px 0 15px;
            border-radius: 5px;
        }

        QScrollBar::handle:horizontal {
            background: #bdc3c7;
            min-width: 30px;
            border-radius: 5px;
        }

        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            border: none;
            background: none;
            width: 15px;
        }

        /* Status bar */
        QStatusBar {
            background-color: #ecf0f1;
            color: #2c3e50;
            border-top: 1px solid #bdc3c7;
        }

        /* Menu bar */
        QMenuBar {
            background-color: #34495e;
            color: white;
        }

        QMenuBar::item {
            background-color: transparent;
            padding: 8px 15px;
        }

        QMenuBar::item:selected {
            background-color: #2c3e50;
        }

        QMenu {
            background-color: white;
            border: 1px solid #bdc3c7;
        }

        QMenu::item {
            padding: 8px 30px 8px 20px;
        }

        QMenu::item:selected {
            background-color: #3498db;
            color: white;
        }

        /* Tool bar */
        QToolBar {
            background-color: #ecf0f1;
            border: 1px solid #bdc3c7;
            spacing: 5px;
            padding: 5px;
        }

        QToolButton {
            background-color: transparent;
            border-radius: 5px;
            padding: 5px;
        }

        QToolButton:hover {
            background-color: #d6eaf8;
        }

        QToolButton:pressed {
            background-color: #aed6f1;
        }
    """)

    # Set palette colors
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(245, 245, 245))
    palette.setColor(QPalette.WindowText, QColor(44, 62, 80))
    palette.setColor(QPalette.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.AlternateBase, QColor(245, 245, 245))
    palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ToolTipText, QColor(44, 62, 80))
    palette.setColor(QPalette.Text, QColor(44, 62, 80))
    palette.setColor(QPalette.Button, QColor(236, 240, 241))
    palette.setColor(QPalette.ButtonText, QColor(44, 62, 80))
    palette.setColor(QPalette.BrightText, QColor(255, 255, 255))
    palette.setColor(QPalette.Link, QColor(41, 128, 185))
    palette.setColor(QPalette.Highlight, QColor(52, 152, 219))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))

    # Set the palette
    app.setPalette(palette)