"""
History Tab for the Chicken Farm App
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel,
                           QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
                           QComboBox, QDateEdit, QGroupBox, QRadioButton)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QColor

from src.utils.formatting import format_number

class HistoryTab(QWidget):
    """Tab for viewing history data"""

    def __init__(self, parent=None):
        """Initialize the history tab"""
        super().__init__(parent)
        self.parent = parent  # Reference to main window

        # UI elements
        self.tabs = None
        self.date_combo = None
        self.compare_date_combo = None
        self.date_radio = None
        self.custom_date_radio = None
        self.date_edit = None

        self.usage_table = None
        self.feed_table = None
        self.mix_table = None

        # Initialize UI
        self.init_ui()

    def init_ui(self):
        """Initialize the UI components"""
        layout = QVBoxLayout()

        # Date selection
        date_layout = QHBoxLayout()

        # Date selection group
        date_group = QGroupBox("Chọn ngày")
        date_group_layout = QHBoxLayout()

        # Date selection radio buttons
        self.date_radio = QRadioButton("Ngày có sẵn:")
        self.date_radio.setChecked(True)
        date_group_layout.addWidget(self.date_radio)

        # Date combo box
        self.date_combo = QComboBox()
        date_group_layout.addWidget(self.date_combo)

        # Custom date radio button
        self.custom_date_radio = QRadioButton("Ngày tùy chọn:")
        date_group_layout.addWidget(self.custom_date_radio)

        # Date edit
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        date_group_layout.addWidget(self.date_edit)

        # Load button
        load_button = QPushButton("Tải")
        load_button.clicked.connect(self.parent.fill_table_by_date)
        date_group_layout.addWidget(load_button)

        # Connect radio buttons
        def toggle_date_source():
            self.date_combo.setEnabled(self.date_radio.isChecked())
            self.date_edit.setEnabled(self.custom_date_radio.isChecked())

        self.date_radio.toggled.connect(toggle_date_source)
        self.custom_date_radio.toggled.connect(toggle_date_source)

        # Apply initial state
        toggle_date_source()

        date_group.setLayout(date_group_layout)
        date_layout.addWidget(date_group)

        # Comparison group
        compare_group = QGroupBox("So sánh với")
        compare_layout = QHBoxLayout()

        # Compare date combo box
        self.compare_date_combo = QComboBox()
        self.compare_date_combo.addItem("Không so sánh")
        compare_layout.addWidget(self.compare_date_combo)

        # Compare button
        compare_button = QPushButton("So sánh")
        compare_button.clicked.connect(self.parent.compare_history_data)
        compare_layout.addWidget(compare_button)

        compare_group.setLayout(compare_layout)
        date_layout.addWidget(compare_group)

        # Export button
        export_button = QPushButton("Xuất Excel")
        export_button.clicked.connect(self.parent.export_history_to_excel)
        date_layout.addWidget(export_button)

        # Visualize button
        visualize_button = QPushButton("Biểu đồ")
        visualize_button.clicked.connect(self.parent.visualize_history_data)
        date_layout.addWidget(visualize_button)

        layout.addLayout(date_layout)

        # Create tabs for different history types
        self.tabs = QTabWidget()

        # Usage history tab
        usage_tab = QWidget()
        usage_layout = QVBoxLayout()

        # Usage history table
        self.usage_table = QTableWidget(0, 6)
        self.usage_table.setHorizontalHeaderLabels(["Khu", "Ca", "Công thức", "Số lượng", "Đơn vị", "Thành phần"])

        # Set column widths
        header = self.usage_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.Stretch)

        usage_layout.addWidget(self.usage_table)
        usage_tab.setLayout(usage_layout)

        # Feed import history tab
        feed_tab = QWidget()
        feed_layout = QVBoxLayout()

        # Feed import history table
        self.feed_table = QTableWidget(0, 5)
        self.feed_table.setHorizontalHeaderLabels(["Thành phần", "Số lượng", "Đơn vị", "Ngày", "Ghi chú"])

        # Set column widths
        header = self.feed_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Stretch)

        feed_layout.addWidget(self.feed_table)
        feed_tab.setLayout(feed_layout)

        # Mix import history tab
        mix_tab = QWidget()
        mix_layout = QVBoxLayout()

        # Mix import history table
        self.mix_table = QTableWidget(0, 5)
        self.mix_table.setHorizontalHeaderLabels(["Thành phần", "Số lượng", "Đơn vị", "Ngày", "Ghi chú"])

        # Set column widths
        header = self.mix_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Stretch)

        mix_layout.addWidget(self.mix_table)
        mix_tab.setLayout(mix_layout)

        # Add tabs
        self.tabs.addTab(usage_tab, "Sử dụng")
        self.tabs.addTab(feed_tab, "Nhập cám")
        self.tabs.addTab(mix_tab, "Nhập hỗn hợp")

        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def update_date_combos(self, dates):
        """Update date combo boxes with available dates"""
        # Save current selections
        current_date = self.date_combo.currentText()
        current_compare_date = self.compare_date_combo.currentText()

        # Clear and refill date combo
        self.date_combo.clear()
        for date in dates:
            self.date_combo.addItem(date)

        # Try to restore previous selection
        index = self.date_combo.findText(current_date)
        if index >= 0:
            self.date_combo.setCurrentIndex(index)

        # Clear and refill compare date combo
        self.compare_date_combo.clear()
        self.compare_date_combo.addItem("Không so sánh")
        for date in dates:
            self.compare_date_combo.addItem(date)

        # Try to restore previous selection
        index = self.compare_date_combo.findText(current_compare_date)
        if index >= 0:
            self.compare_date_combo.setCurrentIndex(index)

    def update_usage_table(self, usage_data, compare_data=None):
        """Update the usage history table"""
        self.usage_table.setRowCount(0)

        # Add rows for each usage item
        for item in usage_data:
            row = self.usage_table.rowCount()
            self.usage_table.insertRow(row)

            # Add area
            area_item = QTableWidgetItem(f"Khu {item['area'] + 1}")
            area_item.setFlags(area_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
            self.usage_table.setItem(row, 0, area_item)

            # Add shift
            shift_item = QTableWidgetItem(item["shift"])
            shift_item.setFlags(shift_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
            self.usage_table.setItem(row, 1, shift_item)

            # Add formula
            formula_item = QTableWidgetItem(item["formula"])
            formula_item.setFlags(formula_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
            self.usage_table.setItem(row, 2, formula_item)

            # Add amount
            amount_item = QTableWidgetItem(format_number(item["amount"]))
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            amount_item.setFlags(amount_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
            self.usage_table.setItem(row, 3, amount_item)

            # Add unit
            unit_item = QTableWidgetItem(item["unit"])
            unit_item.setFlags(unit_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
            self.usage_table.setItem(row, 4, unit_item)

            # Add ingredients
            ingredients_item = QTableWidgetItem(item.get("ingredients", ""))
            ingredients_item.setFlags(ingredients_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
            self.usage_table.setItem(row, 5, ingredients_item)

        # Apply comparison highlighting if compare data is provided
        if compare_data:
            self.highlight_usage_comparison(usage_data, compare_data)

    def update_feed_table(self, feed_data, compare_data=None):
        """Update the feed import history table"""
        self.feed_table.setRowCount(0)

        # Add rows for each feed import item
        for item in feed_data:
            row = self.feed_table.rowCount()
            self.feed_table.insertRow(row)

            # Add item name
            name_item = QTableWidgetItem(item["ingredient"])
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
            self.feed_table.setItem(row, 0, name_item)

            # Add amount
            amount_item = QTableWidgetItem(format_number(item["amount"]))
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            amount_item.setFlags(amount_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
            self.feed_table.setItem(row, 1, amount_item)

            # Add unit (assuming kg for feed)
            unit_item = QTableWidgetItem("kg")
            unit_item.setFlags(unit_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
            self.feed_table.setItem(row, 2, unit_item)

            # Add date
            date_item = QTableWidgetItem(item["date"])
            date_item.setFlags(date_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
            self.feed_table.setItem(row, 3, date_item)

            # Add note
            note_item = QTableWidgetItem(item.get("note", ""))
            note_item.setFlags(note_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
            self.feed_table.setItem(row, 4, note_item)

        # Apply comparison highlighting if compare data is provided
        if compare_data:
            self.highlight_feed_comparison(feed_data, compare_data)

    def update_mix_table(self, mix_data, compare_data=None):
        """Update the mix import history table"""
        self.mix_table.setRowCount(0)

        # Add rows for each mix import item
        for item in mix_data:
            row = self.mix_table.rowCount()
            self.mix_table.insertRow(row)

            # Add item name
            name_item = QTableWidgetItem(item["ingredient"])
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
            self.mix_table.setItem(row, 0, name_item)

            # Add amount
            amount_item = QTableWidgetItem(format_number(item["amount"]))
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            amount_item.setFlags(amount_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
            self.mix_table.setItem(row, 1, amount_item)

            # Add unit (assuming kg for mix)
            unit_item = QTableWidgetItem("kg")
            unit_item.setFlags(unit_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
            self.mix_table.setItem(row, 2, unit_item)

            # Add date
            date_item = QTableWidgetItem(item["date"])
            date_item.setFlags(date_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
            self.mix_table.setItem(row, 3, date_item)

            # Add note
            note_item = QTableWidgetItem(item.get("note", ""))
            note_item.setFlags(note_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
            self.mix_table.setItem(row, 4, note_item)

        # Apply comparison highlighting if compare data is provided
        if compare_data:
            self.highlight_mix_comparison(mix_data, compare_data)

    def highlight_usage_comparison(self, current_data, compare_data):
        """Highlight differences between current and comparison usage data"""
        # Create dictionaries for easier comparison
        current_dict = {}
        for item in current_data:
            key = f"{item['area']}_{item['shift']}_{item['formula']}"
            current_dict[key] = item

        compare_dict = {}
        for item in compare_data:
            key = f"{item['area']}_{item['shift']}_{item['formula']}"
            compare_dict[key] = item

        # Highlight rows based on comparison
        for row in range(self.usage_table.rowCount()):
            area = int(self.usage_table.item(row, 0).text().replace("Khu ", "")) - 1
            shift = self.usage_table.item(row, 1).text()
            formula = self.usage_table.item(row, 2).text()
            key = f"{area}_{shift}_{formula}"

            if key in compare_dict:
                # Item exists in both datasets, compare amounts
                current_amount = float(self.usage_table.item(row, 3).text().replace(",", ""))
                compare_amount = compare_dict[key]["amount"]

                if current_amount > compare_amount:
                    # Increased - highlight green
                    for col in range(self.usage_table.columnCount()):
                        self.usage_table.item(row, col).setBackground(QColor(200, 255, 200))
                elif current_amount < compare_amount:
                    # Decreased - highlight red
                    for col in range(self.usage_table.columnCount()):
                        self.usage_table.item(row, col).setBackground(QColor(255, 200, 200))
            else:
                # New item - highlight blue
                for col in range(self.usage_table.columnCount()):
                    self.usage_table.item(row, col).setBackground(QColor(200, 200, 255))

    def highlight_feed_comparison(self, current_data, compare_data):
        """Highlight differences between current and comparison feed data"""
        # Create dictionaries for easier comparison
        current_dict = {}
        for item in current_data:
            key = item["ingredient"]
            current_dict[key] = item

        compare_dict = {}
        for item in compare_data:
            key = item["ingredient"]
            compare_dict[key] = item

        # Highlight rows based on comparison
        for row in range(self.feed_table.rowCount()):
            ingredient = self.feed_table.item(row, 0).text()
            key = ingredient

            if key in compare_dict:
                # Item exists in both datasets, compare amounts
                current_amount = float(self.feed_table.item(row, 1).text().replace(",", ""))
                compare_amount = compare_dict[key]["amount"]

                if current_amount > compare_amount:
                    # Increased - highlight green
                    for col in range(self.feed_table.columnCount()):
                        self.feed_table.item(row, col).setBackground(QColor(200, 255, 200))
                elif current_amount < compare_amount:
                    # Decreased - highlight red
                    for col in range(self.feed_table.columnCount()):
                        self.feed_table.item(row, col).setBackground(QColor(255, 200, 200))
            else:
                # New item - highlight blue
                for col in range(self.feed_table.columnCount()):
                    self.feed_table.item(row, col).setBackground(QColor(200, 200, 255))

    def highlight_mix_comparison(self, current_data, compare_data):
        """Highlight differences between current and comparison mix data"""
        # Create dictionaries for easier comparison
        current_dict = {}
        for item in current_data:
            key = item["ingredient"]
            current_dict[key] = item

        compare_dict = {}
        for item in compare_data:
            key = item["ingredient"]
            compare_dict[key] = item

        # Highlight rows based on comparison
        for row in range(self.mix_table.rowCount()):
            ingredient = self.mix_table.item(row, 0).text()
            key = ingredient

            if key in compare_dict:
                # Item exists in both datasets, compare amounts
                current_amount = float(self.mix_table.item(row, 1).text().replace(",", ""))
                compare_amount = compare_dict[key]["amount"]

                if current_amount > compare_amount:
                    # Increased - highlight green
                    for col in range(self.mix_table.columnCount()):
                        self.mix_table.item(row, col).setBackground(QColor(200, 255, 200))
                elif current_amount < compare_amount:
                    # Decreased - highlight red
                    for col in range(self.mix_table.columnCount()):
                        self.mix_table.item(row, col).setBackground(QColor(255, 200, 200))
            else:
                # New item - highlight blue
                for col in range(self.mix_table.columnCount()):
                    self.mix_table.item(row, col).setBackground(QColor(200, 200, 255))
