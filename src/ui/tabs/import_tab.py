"""
Import Tab for the Chicken Farm App
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel,
                           QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
                           QComboBox, QDoubleSpinBox, QDateEdit, QLineEdit)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont

from src.ui.widgets.custom_spinbox import CustomDoubleSpinBox
from src.utils.formatting import format_number

class ImportTab(QWidget):
    """Tab for importing feed and mix ingredients"""

    def __init__(self, parent=None):
        """Initialize the import tab"""
        super().__init__(parent)
        self.parent = parent  # Reference to main window

        # UI elements
        self.tabs = None
        self.feed_combo = None
        self.feed_amount_spin = None
        self.feed_date_edit = None
        self.feed_note_edit = None
        self.feed_import_history_table = None

        self.mix_combo = None
        self.mix_amount_spin = None
        self.mix_date_edit = None
        self.mix_note_edit = None
        self.mix_import_history_table = None

        # Initialize UI
        self.init_ui()

    def init_ui(self):
        """Initialize the UI components"""
        layout = QVBoxLayout()

        # Create tabs for feed and mix import
        self.tabs = QTabWidget()

        # Feed import tab
        feed_tab = QWidget()
        feed_layout = QVBoxLayout()

        # Feed import form
        feed_form_layout = QHBoxLayout()

        # Feed ingredient selection
        feed_form_layout.addWidget(QLabel("Thành phần:"))
        self.feed_combo = QComboBox()
        feed_form_layout.addWidget(self.feed_combo)

        # Feed amount
        feed_form_layout.addWidget(QLabel("Số lượng:"))
        self.feed_amount_spin = CustomDoubleSpinBox()
        self.feed_amount_spin.setRange(0, 1000000)
        self.feed_amount_spin.setDecimals(2)
        self.feed_amount_spin.setSingleStep(1)
        feed_form_layout.addWidget(self.feed_amount_spin)

        # Feed date
        feed_form_layout.addWidget(QLabel("Ngày:"))
        self.feed_date_edit = QDateEdit()
        self.feed_date_edit.setDate(QDate.currentDate())
        self.feed_date_edit.setCalendarPopup(True)
        feed_form_layout.addWidget(self.feed_date_edit)

        # Feed note
        feed_form_layout.addWidget(QLabel("Ghi chú:"))
        self.feed_note_edit = QLineEdit()
        feed_form_layout.addWidget(self.feed_note_edit)

        # Feed import button
        feed_import_button = QPushButton("Nhập")
        feed_import_button.clicked.connect(self.parent.import_feed)
        feed_form_layout.addWidget(feed_import_button)

        feed_layout.addLayout(feed_form_layout)

        # Feed import history table
        self.feed_import_history_table = QTableWidget(0, 5)
        self.feed_import_history_table.setHorizontalHeaderLabels(["Thành phần", "Số lượng", "Đơn vị", "Ngày", "Ghi chú"])

        # Set column widths
        header = self.feed_import_history_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Stretch)

        feed_layout.addWidget(self.feed_import_history_table)

        feed_tab.setLayout(feed_layout)

        # Mix import tab
        mix_tab = QWidget()
        mix_layout = QVBoxLayout()

        # Mix import form
        mix_form_layout = QHBoxLayout()

        # Mix ingredient selection
        mix_form_layout.addWidget(QLabel("Thành phần:"))
        self.mix_combo = QComboBox()
        mix_form_layout.addWidget(self.mix_combo)

        # Mix amount
        mix_form_layout.addWidget(QLabel("Số lượng:"))
        self.mix_amount_spin = CustomDoubleSpinBox()
        self.mix_amount_spin.setRange(0, 1000000)
        self.mix_amount_spin.setDecimals(2)
        self.mix_amount_spin.setSingleStep(1)
        mix_form_layout.addWidget(self.mix_amount_spin)

        # Mix date
        mix_form_layout.addWidget(QLabel("Ngày:"))
        self.mix_date_edit = QDateEdit()
        self.mix_date_edit.setDate(QDate.currentDate())
        self.mix_date_edit.setCalendarPopup(True)
        mix_form_layout.addWidget(self.mix_date_edit)

        # Mix note
        mix_form_layout.addWidget(QLabel("Ghi chú:"))
        self.mix_note_edit = QLineEdit()
        mix_form_layout.addWidget(self.mix_note_edit)

        # Mix import button
        mix_import_button = QPushButton("Nhập")
        mix_import_button.clicked.connect(self.parent.import_mix)
        mix_form_layout.addWidget(mix_import_button)

        mix_layout.addLayout(mix_form_layout)

        # Mix import history table
        self.mix_import_history_table = QTableWidget(0, 5)
        self.mix_import_history_table.setHorizontalHeaderLabels(["Thành phần", "Số lượng", "Đơn vị", "Ngày", "Ghi chú"])

        # Set column widths
        header = self.mix_import_history_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Stretch)

        mix_layout.addWidget(self.mix_import_history_table)

        mix_tab.setLayout(mix_layout)

        # Add tabs
        self.tabs.addTab(feed_tab, "Cám")
        self.tabs.addTab(mix_tab, "Hỗn hợp")

        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def update_feed_combo(self, feed_items):
        """Update feed combo box with available feed items"""
        current_text = self.feed_combo.currentText()
        self.feed_combo.clear()

        # Add feed items
        for item in feed_items:
            self.feed_combo.addItem(item["name"])

        # Try to restore previous selection
        index = self.feed_combo.findText(current_text)
        if index >= 0:
            self.feed_combo.setCurrentIndex(index)

    def update_mix_combo(self, mix_items):
        """Update mix combo box with available mix items"""
        current_text = self.mix_combo.currentText()
        self.mix_combo.clear()

        # Add mix items
        for item in mix_items:
            self.mix_combo.addItem(item["name"])

        # Try to restore previous selection
        index = self.mix_combo.findText(current_text)
        if index >= 0:
            self.mix_combo.setCurrentIndex(index)

    def update_feed_import_history(self, history):
        """Update the feed import history table"""
        self.feed_import_history_table.setRowCount(0)

        # Add rows for each history item
        for item in history:
            if item["type"] != "feed":
                continue

            row = self.feed_import_history_table.rowCount()
            self.feed_import_history_table.insertRow(row)

            # Add item name
            name_item = QTableWidgetItem(item["ingredient"])
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
            self.feed_import_history_table.setItem(row, 0, name_item)

            # Add amount
            amount_item = QTableWidgetItem(format_number(item["amount"]))
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            amount_item.setFlags(amount_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
            self.feed_import_history_table.setItem(row, 1, amount_item)

            # Add unit (assuming kg for feed)
            unit_item = QTableWidgetItem("kg")
            unit_item.setFlags(unit_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
            self.feed_import_history_table.setItem(row, 2, unit_item)

            # Add date
            date_item = QTableWidgetItem(item["date"])
            date_item.setFlags(date_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
            self.feed_import_history_table.setItem(row, 3, date_item)

            # Add note
            note_item = QTableWidgetItem(item.get("note", ""))
            note_item.setFlags(note_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
            self.feed_import_history_table.setItem(row, 4, note_item)

    def update_mix_import_history(self, history):
        """Update the mix import history table"""
        self.mix_import_history_table.setRowCount(0)

        # Add rows for each history item
        for item in history:
            if item["type"] != "mix":
                continue

            row = self.mix_import_history_table.rowCount()
            self.mix_import_history_table.insertRow(row)

            # Add item name
            name_item = QTableWidgetItem(item["ingredient"])
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
            self.mix_import_history_table.setItem(row, 0, name_item)

            # Add amount
            amount_item = QTableWidgetItem(format_number(item["amount"]))
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            amount_item.setFlags(amount_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
            self.mix_import_history_table.setItem(row, 1, amount_item)

            # Add unit (assuming kg for mix)
            unit_item = QTableWidgetItem("kg")
            unit_item.setFlags(unit_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
            self.mix_import_history_table.setItem(row, 2, unit_item)

            # Add date
            date_item = QTableWidgetItem(item["date"])
            date_item.setFlags(date_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
            self.mix_import_history_table.setItem(row, 3, date_item)

            # Add note
            note_item = QTableWidgetItem(item.get("note", ""))
            note_item.setFlags(note_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
            self.mix_import_history_table.setItem(row, 4, note_item)