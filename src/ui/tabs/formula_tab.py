"""
Formula Tab for the Chicken Farm App
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel,
                           QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
                           QComboBox, QDoubleSpinBox, QLineEdit, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from src.ui.widgets.custom_spinbox import CustomDoubleSpinBox
from src.utils.formatting import format_number

class FormulaTab(QWidget):
    """Tab for managing feed and mix formulas"""

    def __init__(self, parent=None):
        """Initialize the formula tab"""
        super().__init__(parent)
        self.parent = parent  # Reference to main window

        # UI elements
        self.tabs = None
        self.feed_formula_table = None
        self.feed_formula_name_edit = None
        self.feed_preset_combo = None

        self.mix_formula_table = None
        self.mix_formula_name_edit = None
        self.mix_preset_combo = None

        # Initialize UI
        self.init_ui()

    def init_ui(self):
        """Initialize the UI components"""
        layout = QVBoxLayout()

        # Create tabs for feed and mix formulas
        self.tabs = QTabWidget()

        # Feed formula tab
        feed_tab = QWidget()
        feed_layout = QVBoxLayout()

        # Feed formula name
        feed_name_layout = QHBoxLayout()
        feed_name_layout.addWidget(QLabel("Tên công thức:"))
        self.feed_formula_name_edit = QLineEdit()
        feed_name_layout.addWidget(self.feed_formula_name_edit)
        feed_layout.addLayout(feed_name_layout)

        # Feed formula table
        self.feed_formula_table = QTableWidget(0, 3)
        self.feed_formula_table.setHorizontalHeaderLabels(["Thành phần", "Tỷ lệ (%)", "Đơn vị"])

        # Set column widths
        header = self.feed_formula_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

        feed_layout.addWidget(self.feed_formula_table)

        # Feed formula buttons
        feed_buttons_layout = QHBoxLayout()

        # Feed formula save button
        feed_save_button = QPushButton("Lưu")
        feed_save_button.clicked.connect(self.parent.save_feed_formula)
        feed_buttons_layout.addWidget(feed_save_button)

        # Feed formula preset management
        feed_buttons_layout.addWidget(QLabel("Công thức có sẵn:"))
        self.feed_preset_combo = QComboBox()
        feed_buttons_layout.addWidget(self.feed_preset_combo)

        # Feed preset load button
        feed_load_button = QPushButton("Tải")
        feed_load_button.clicked.connect(self.parent.load_feed_preset)
        feed_buttons_layout.addWidget(feed_load_button)

        # Feed preset save button
        feed_save_preset_button = QPushButton("Lưu thành...")
        feed_save_preset_button.clicked.connect(self.parent.save_as_feed_preset)
        feed_buttons_layout.addWidget(feed_save_preset_button)

        # Feed preset delete button
        feed_delete_preset_button = QPushButton("Xóa")
        feed_delete_preset_button.clicked.connect(self.parent.delete_feed_preset)
        feed_buttons_layout.addWidget(feed_delete_preset_button)

        feed_layout.addLayout(feed_buttons_layout)

        feed_tab.setLayout(feed_layout)

        # Mix formula tab
        mix_tab = QWidget()
        mix_layout = QVBoxLayout()

        # Mix formula name
        mix_name_layout = QHBoxLayout()
        mix_name_layout.addWidget(QLabel("Tên công thức:"))
        self.mix_formula_name_edit = QLineEdit()
        mix_name_layout.addWidget(self.mix_formula_name_edit)
        mix_layout.addLayout(mix_name_layout)

        # Mix formula table
        self.mix_formula_table = QTableWidget(0, 3)
        self.mix_formula_table.setHorizontalHeaderLabels(["Thành phần", "Tỷ lệ (%)", "Đơn vị"])

        # Set column widths
        header = self.mix_formula_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

        mix_layout.addWidget(self.mix_formula_table)

        # Mix formula buttons
        mix_buttons_layout = QHBoxLayout()

        # Mix formula save button
        mix_save_button = QPushButton("Lưu")
        mix_save_button.clicked.connect(self.parent.save_mix_formula)
        mix_buttons_layout.addWidget(mix_save_button)

        # Mix formula preset management
        mix_buttons_layout.addWidget(QLabel("Công thức có sẵn:"))
        self.mix_preset_combo = QComboBox()
        mix_buttons_layout.addWidget(self.mix_preset_combo)

        # Mix preset load button
        mix_load_button = QPushButton("Tải")
        mix_load_button.clicked.connect(self.parent.load_mix_preset)
        mix_buttons_layout.addWidget(mix_load_button)

        # Mix preset save button
        mix_save_preset_button = QPushButton("Lưu thành...")
        mix_save_preset_button.clicked.connect(self.parent.save_as_mix_preset)
        mix_buttons_layout.addWidget(mix_save_preset_button)

        # Mix preset delete button
        mix_delete_preset_button = QPushButton("Xóa")
        mix_delete_preset_button.clicked.connect(self.parent.delete_mix_preset)
        mix_buttons_layout.addWidget(mix_delete_preset_button)

        mix_layout.addLayout(mix_buttons_layout)

        mix_tab.setLayout(mix_layout)

        # Add tabs
        self.tabs.addTab(feed_tab, "Cám")
        self.tabs.addTab(mix_tab, "Hỗn hợp")

        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def update_feed_formula_table(self, formula_items):
        """Update the feed formula table with current formula data"""
        self.feed_formula_table.setRowCount(0)

        # Add rows for each formula item
        for item in formula_items:
            row = self.feed_formula_table.rowCount()
            self.feed_formula_table.insertRow(row)

            # Add item name
            name_item = QTableWidgetItem(item["name"])
            self.feed_formula_table.setItem(row, 0, name_item)

            # Add ratio
            ratio_spin = CustomDoubleSpinBox()
            ratio_spin.setRange(0, 100)
            ratio_spin.setDecimals(2)
            ratio_spin.setSingleStep(0.1)
            ratio_spin.setValue(item["ratio"])
            self.feed_formula_table.setCellWidget(row, 1, ratio_spin)

            # Add unit
            unit_item = QTableWidgetItem(item["unit"])
            unit_item.setFlags(unit_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
            self.feed_formula_table.setItem(row, 2, unit_item)

    def update_mix_formula_table(self, formula_items):
        """Update the mix formula table with current formula data"""
        self.mix_formula_table.setRowCount(0)

        # Add rows for each formula item
        for item in formula_items:
            row = self.mix_formula_table.rowCount()
            self.mix_formula_table.insertRow(row)

            # Add item name
            name_item = QTableWidgetItem(item["name"])
            self.mix_formula_table.setItem(row, 0, name_item)

            # Add ratio
            ratio_spin = CustomDoubleSpinBox()
            ratio_spin.setRange(0, 100)
            ratio_spin.setDecimals(2)
            ratio_spin.setSingleStep(0.1)
            ratio_spin.setValue(item["ratio"])
            self.mix_formula_table.setCellWidget(row, 1, ratio_spin)

            # Add unit
            unit_item = QTableWidgetItem(item["unit"])
            unit_item.setFlags(unit_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
            self.mix_formula_table.setItem(row, 2, unit_item)

    def update_feed_preset_combo(self, presets):
        """Update the feed preset combo box with available presets"""
        current_text = self.feed_preset_combo.currentText()
        self.feed_preset_combo.clear()

        # Add presets
        for preset in presets:
            # Check if preset is a string (preset name) or a dictionary
            if isinstance(preset, dict):
                self.feed_preset_combo.addItem(preset["name"])
            else:
                self.feed_preset_combo.addItem(preset)

        # Try to restore previous selection
        index = self.feed_preset_combo.findText(current_text)
        if index >= 0:
            self.feed_preset_combo.setCurrentIndex(index)

    def update_mix_preset_combo(self, presets):
        """Update the mix preset combo box with available presets"""
        current_text = self.mix_preset_combo.currentText()
        self.mix_preset_combo.clear()

        # Add presets
        for preset in presets:
            # Check if preset is a string (preset name) or a dictionary
            if isinstance(preset, dict):
                self.mix_preset_combo.addItem(preset["name"])
            else:
                self.mix_preset_combo.addItem(preset)

        # Try to restore previous selection
        index = self.mix_preset_combo.findText(current_text)
        if index >= 0:
            self.mix_preset_combo.setCurrentIndex(index)