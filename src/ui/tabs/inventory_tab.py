"""
Inventory Tab for the Chicken Farm App
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel,
                           QPushButton, QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from src.utils.formatting import format_number

class InventoryTab(QWidget):
    """Tab for managing inventory"""

    def __init__(self, parent=None):
        """Initialize the inventory tab"""
        super().__init__(parent)
        self.parent = parent  # Reference to main window

        # UI elements
        self.tabs = None
        self.feed_inventory_table = None
        self.mix_inventory_table = None

        # Initialize UI
        self.init_ui()

    def init_ui(self):
        """Initialize the UI components"""
        layout = QVBoxLayout()

        # Create tabs for feed and mix inventory
        self.tabs = QTabWidget()

        # Feed inventory tab
        feed_tab = QWidget()
        feed_layout = QVBoxLayout()

        # Feed inventory table
        self.feed_inventory_table = QTableWidget(0, 3)
        self.feed_inventory_table.setHorizontalHeaderLabels(["Thành phần", "Số lượng", "Đơn vị"])

        # Set column widths
        header = self.feed_inventory_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

        feed_layout.addWidget(self.feed_inventory_table)

        # Add update button
        update_feed_button = QPushButton("Cập nhật")
        update_feed_button.clicked.connect(lambda: self.parent.update_inventory("feed"))
        feed_layout.addWidget(update_feed_button)

        feed_tab.setLayout(feed_layout)

        # Mix inventory tab
        mix_tab = QWidget()
        mix_layout = QVBoxLayout()

        # Mix inventory table
        self.mix_inventory_table = QTableWidget(0, 3)
        self.mix_inventory_table.setHorizontalHeaderLabels(["Thành phần", "Số lượng", "Đơn vị"])

        # Set column widths
        header = self.mix_inventory_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

        mix_layout.addWidget(self.mix_inventory_table)

        # Add update button
        update_mix_button = QPushButton("Cập nhật")
        update_mix_button.clicked.connect(lambda: self.parent.update_inventory("mix"))
        mix_layout.addWidget(update_mix_button)

        mix_tab.setLayout(mix_layout)

        # Add tabs
        self.tabs.addTab(feed_tab, "Cám")
        self.tabs.addTab(mix_tab, "Hỗn hợp")

        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def update_feed_inventory_table(self, inventory):
        """Update the feed inventory table with current inventory data"""
        self.feed_inventory_table.setRowCount(0)

        # Add rows for each inventory item
        for item in inventory:
            row = self.feed_inventory_table.rowCount()
            self.feed_inventory_table.insertRow(row)

            # Add item name
            name_item = QTableWidgetItem(item["name"])
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
            self.feed_inventory_table.setItem(row, 0, name_item)

            # Add amount
            amount_item = QTableWidgetItem(format_number(item["amount"]))
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.feed_inventory_table.setItem(row, 1, amount_item)

            # Add unit
            unit_item = QTableWidgetItem(item["unit"])
            unit_item.setFlags(unit_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
            self.feed_inventory_table.setItem(row, 2, unit_item)

    def update_mix_inventory_table(self, inventory):
        """Update the mix inventory table with current inventory data"""
        self.mix_inventory_table.setRowCount(0)

        # Add rows for each inventory item
        for item in inventory:
            row = self.mix_inventory_table.rowCount()
            self.mix_inventory_table.insertRow(row)

            # Add item name
            name_item = QTableWidgetItem(item["name"])
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
            self.mix_inventory_table.setItem(row, 0, name_item)

            # Add amount
            amount_item = QTableWidgetItem(format_number(item["amount"]))
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.mix_inventory_table.setItem(row, 1, amount_item)

            # Add unit
            unit_item = QTableWidgetItem(item["unit"])
            unit_item.setFlags(unit_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
            self.mix_inventory_table.setItem(row, 2, unit_item)