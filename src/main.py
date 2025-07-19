import sys
import os
import json
import subprocess
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout,
                            QHBoxLayout, QGridLayout, QLabel, QLineEdit, QPushButton,
                            QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
                            QMessageBox, QFileDialog, QSpinBox, QDoubleSpinBox, QInputDialog)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QColor

from src.core.formula_manager import FormulaManager
from src.core.inventory_manager import InventoryManager
from src.utils.default_formulas import PACKAGING_INFO
from src.utils.app_icon import create_app_icon

# Constants
AREAS = 5  # Number of areas
SHIFTS = ["Sáng", "Chiều"]  # Morning and afternoon shifts

# Định nghĩa các trại cho từng khu
FARMS = {
    0: ["T1", "T2", "T4", "T6"],          # Khu 1
    1: ["T1", "T2", "T4", "T6"],          # Khu 2
    2: ["1D", "2D", "4D", "2N"],          # Khu 3
    3: ["T2", "T4", "T6", "T8", "Trại 1 khu 4"],  # Khu 4
    4: ["Trống"]                           # Khu 5
}

# Helper function to format numbers (display integers without decimal places)
def format_number(value):
    """Format a number to display as integer if it has no decimal part, otherwise show 2 decimal places"""
    if value == int(value):
        return f"{int(value)}"
    else:
        return f"{value:.2f}"

class ChickenFarmApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Phần mềm Quản lý Cám - Trại Gà")

        # Lấy kích thước màn hình
        desktop = QApplication.desktop()
        screen_rect = desktop.availableGeometry()
        screen_width = screen_rect.width()
        screen_height = screen_rect.height()

        # Tính toán kích thước cửa sổ (75% kích thước màn hình)
        window_width = int(screen_width * 0.95)
        window_height = int(screen_height * 0.95)

        # Tính toán vị trí để cửa sổ xuất hiện ở giữa màn hình
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2

        # Thiết lập kích thước và vị trí cửa sổ
        self.setGeometry(x_position, y_position, window_width, window_height)

        # Set application icon
        self.setWindowIcon(create_app_icon())

        # Initialize managers
        self.formula_manager = FormulaManager()
        self.inventory_manager = InventoryManager()

        # Get formulas and inventory data
        self.feed_formula = self.formula_manager.get_feed_formula()
        self.mix_formula = self.formula_manager.get_mix_formula()
        self.inventory = self.inventory_manager.get_inventory()

        # Initialize UI
        self.init_ui()

    def init_ui(self):
        """Initialize the main UI components"""
        # Create main tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Create tabs
        self.feed_usage_tab = QWidget()
        self.inventory_tab = QWidget()
        self.formula_tab = QWidget()
        self.history_tab = QWidget()  # Tab mới cho lịch sử

        # Add tabs to widget
        self.tabs.addTab(self.feed_usage_tab, "Sử dụng Cám")
        self.tabs.addTab(self.inventory_tab, "Tồn Kho")
        self.tabs.addTab(self.formula_tab, "Công Thức")
        self.tabs.addTab(self.history_tab, "Lịch Sử")  # Thêm tab lịch sử

        # Create menu bar
        self.create_menu_bar()

        # Setup each tab
        self.setup_feed_usage_tab()
        self.setup_inventory_tab()
        self.setup_formula_tab()
        self.setup_history_tab()  # Thiết lập tab lịch sử

    def create_menu_bar(self):
        """Create the menu bar"""
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("Tệp")

        # Export action
        export_action = file_menu.addAction("Xuất Excel")
        export_action.triggered.connect(self.export_to_excel)

        file_menu.addSeparator()

        # Exit action
        exit_action = file_menu.addAction("Thoát")
        exit_action.triggered.connect(self.close)

        # Help menu
        help_menu = menu_bar.addMenu("Trợ giúp")

        # About action
        about_action = help_menu.addAction("Giới thiệu")
        about_action.triggered.connect(self.show_about_dialog)

    def show_about_dialog(self):
        """Show the about dialog"""
        QMessageBox.about(
            self,
            "Giới thiệu",
            """<h1>Phần mềm Quản lý Cám - Trại Gà</h1>
            <p>Phiên bản 1.0</p>
            <p>Phần mềm quản lý cám cho trại gà, giúp theo dõi lượng cám sử dụng hàng ngày và quản lý tồn kho.</p>
            <p>© 2023 Minh-Tan_Phat</p>"""
        )

    def setup_feed_usage_tab(self):
        """Setup the feed usage tab"""
        layout = QVBoxLayout()

        # Header section
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Báo Cáo Lượng Cám Sử Dụng Trong Ngày"))
        date_label = QLabel(f"Ngày: {QDate.currentDate().toString('dd/MM/yyyy')}")
        header_layout.addWidget(date_label)
        header_layout.addStretch()

        # Thêm phần chọn công thức cám mặc định
        default_formula_layout = QHBoxLayout()
        default_formula_layout.addWidget(QLabel("Công thức cám mặc định:"))

        self.default_formula_combo = QComboBox()
        # Lấy danh sách các công thức cám có sẵn
        presets = self.formula_manager.get_feed_presets()
        self.default_formula_combo.addItem("")  # Thêm lựa chọn trống
        for preset in presets:
            self.default_formula_combo.addItem(preset)
        default_formula_layout.addWidget(self.default_formula_combo)

        # Nút áp dụng công thức mặc định
        apply_default_button = QPushButton("Áp dụng cho tất cả")
        apply_default_button.clicked.connect(self.apply_default_formula)
        default_formula_layout.addWidget(apply_default_button)

        default_formula_layout.addStretch()

        # Create table for feed usage input
        self.feed_table = QTableWidget()

        # Calculate total number of farms
        total_farms = sum(len(farms) for farms in FARMS.values())

        # Tạo bảng với cấu trúc mới:
        # - Hàng đầu tiên: Khu (label)
        # - Hàng thứ hai: Trại
        # - Các hàng tiếp theo: Buổi (Sáng/Chiều)
        self.feed_table.setRowCount(len(SHIFTS) + 2)  # +2 cho hàng Khu và hàng Trại
        self.feed_table.setColumnCount(total_farms)  # Chỉ hiển thị các trại, bỏ cột nhãn

        # Ẩn header row (dãy số trên cùng)
        self.feed_table.horizontalHeader().setVisible(False)

        # Set row headers
        self.feed_table.setVerticalHeaderItem(0, QTableWidgetItem("Khu"))
        self.feed_table.setVerticalHeaderItem(1, QTableWidgetItem("Trại"))
        for i, shift in enumerate(SHIFTS):
            self.feed_table.setVerticalHeaderItem(i + 2, QTableWidgetItem(shift))

        # Populate table with farms and khu information
        col_index = 0  # Bắt đầu từ cột 0 vì đã bỏ cột nhãn
        for khu_idx, farms in FARMS.items():
            khu_name = f"Khu {khu_idx + 1}"

            for farm_idx, farm in enumerate(farms):
                # Set khu label in first row
                self.feed_table.setItem(0, col_index, QTableWidgetItem(khu_name))

                # Set farm name in second row
                self.feed_table.setItem(1, col_index, QTableWidgetItem(farm))

                # Create editable cells for feed usage for each shift
                for shift_idx in range(len(SHIFTS)):
                    # Tạo một widget container để chứa cả spinbox và combobox
                    container = QWidget()
                    container_layout = QHBoxLayout(container)
                    container_layout.setContentsMargins(2, 2, 2, 2)
                    container_layout.setSpacing(2)

                    # Tạo spinbox cho số lượng mẻ
                    spin_box = QDoubleSpinBox()
                    spin_box.setRange(0, 100)
                    spin_box.setSingleStep(0.5)
                    spin_box.setDecimals(1)

                    # Tạo combobox cho công thức cám
                    formula_combo = QComboBox()
                    # Lấy danh sách các công thức cám có sẵn
                    presets = self.formula_manager.get_feed_presets()
                    formula_combo.addItem("")  # Thêm lựa chọn trống
                    for preset in presets:
                        formula_combo.addItem(preset)

                    # Thêm các widget vào container
                    container_layout.addWidget(spin_box, 1)  # Tỷ lệ 1
                    container_layout.addWidget(formula_combo, 2)  # Tỷ lệ 2

                    # Lưu reference đến các widget con để truy cập sau này
                    container.spin_box = spin_box
                    container.formula_combo = formula_combo

                    # Kết nối sự kiện thay đổi giá trị spin_box để tự động chọn công thức mặc định
                    spin_box.valueChanged.connect(lambda value, combo=formula_combo: self.auto_select_default_formula(value, combo))

                    # Thêm container vào cell
                    self.feed_table.setCellWidget(shift_idx + 2, col_index, container)

                col_index += 1

        # Stretch columns to fill available space
        self.feed_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Calculate button
        calc_button = QPushButton("Tính Toán")
        calc_button.clicked.connect(self.calculate_feed_usage)

        # Results section
        self.results_label = QLabel("Kết quả tính toán sẽ hiển thị ở đây")
        self.results_label.setAlignment(Qt.AlignCenter)

        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(3)  # Ingredient, Amount, Bags
        self.results_table.setHorizontalHeaderLabels(["Thành phần", "Số lượng (kg)", "Số bao"])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Add widgets to layout
        layout.addLayout(header_layout)
        layout.addLayout(default_formula_layout)
        layout.addWidget(self.feed_table)
        layout.addWidget(calc_button)
        layout.addWidget(self.results_label)
        layout.addWidget(self.results_table)

        # Save and export buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Lưu Báo Cáo")
        save_button.clicked.connect(self.save_report)
        export_button = QPushButton("Xuất Excel")
        export_button.clicked.connect(self.export_to_excel)
        button_layout.addWidget(save_button)
        button_layout.addWidget(export_button)
        layout.addLayout(button_layout)

        self.feed_usage_tab.setLayout(layout)

    def apply_default_formula(self):
        """Áp dụng công thức cám mặc định cho tất cả các ô trong bảng"""
        default_formula = self.default_formula_combo.currentText()
        if not default_formula:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một công thức cám mặc định!")
            return

        # Áp dụng cho tất cả các ô trong bảng
        for col in range(self.feed_table.columnCount()):
            for row in range(2, 2 + len(SHIFTS)):
                cell_widget = self.feed_table.cellWidget(row, col)
                if cell_widget and hasattr(cell_widget, 'formula_combo'):
                    cell_widget.formula_combo.setCurrentText(default_formula)

        QMessageBox.information(self, "Thành công", f"Đã áp dụng công thức cám '{default_formula}' cho tất cả các ô!")

    def auto_select_default_formula(self, value, combo):
        """Tự động chọn công thức mặc định khi người dùng nhập số lượng mẻ"""
        # Nếu đã chọn công thức rồi thì không thay đổi
        if combo.currentText():
            return

        # Nếu người dùng nhập giá trị > 0 và chưa chọn công thức, tự động chọn công thức mặc định
        if value > 0:
            default_formula = self.default_formula_combo.currentText()
            if default_formula:
                combo.setCurrentText(default_formula)

    def setup_inventory_tab(self):
        """Setup the inventory management tab"""
        layout = QVBoxLayout()

        # Create tabs for Feed and Mix inventory
        inventory_tabs = QTabWidget()
        feed_inventory_tab = QWidget()
        mix_inventory_tab = QWidget()

        inventory_tabs.addTab(feed_inventory_tab, "Kho Cám")
        inventory_tabs.addTab(mix_inventory_tab, "Kho Mix")

        # Setup Feed Inventory tab
        feed_layout = QVBoxLayout()

        self.feed_inventory_table = QTableWidget()
        self.feed_inventory_table.setColumnCount(4)
        self.feed_inventory_table.setHorizontalHeaderLabels(["Thành phần", "Tồn kho (kg)", "Kích thước bao (kg)", "Số bao"])
        self.feed_inventory_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Populate feed inventory table
        self.update_feed_inventory_table()

        feed_layout.addWidget(self.feed_inventory_table)

        # Add update inventory buttons
        update_layout = QHBoxLayout()
        update_button = QPushButton("Cập nhật tồn kho")
        update_button.clicked.connect(lambda: self.update_inventory("feed"))
        update_layout.addWidget(update_button)
        feed_layout.addLayout(update_layout)

        feed_inventory_tab.setLayout(feed_layout)

        # Setup Mix Inventory tab
        mix_layout = QVBoxLayout()

        self.mix_inventory_table = QTableWidget()
        self.mix_inventory_table.setColumnCount(4)
        self.mix_inventory_table.setHorizontalHeaderLabels(["Thành phần", "Tồn kho (kg)", "Kích thước bao (kg)", "Số bao"])
        self.mix_inventory_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Populate mix inventory table
        self.update_mix_inventory_table()

        mix_layout.addWidget(self.mix_inventory_table)

        # Add update inventory buttons
        mix_update_layout = QHBoxLayout()
        mix_update_button = QPushButton("Cập nhật tồn kho")
        mix_update_button.clicked.connect(lambda: self.update_inventory("mix"))
        mix_update_layout.addWidget(mix_update_button)
        mix_layout.addLayout(mix_update_layout)

        mix_inventory_tab.setLayout(mix_layout)

        layout.addWidget(inventory_tabs)
        self.inventory_tab.setLayout(layout)

    def setup_formula_tab(self):
        """Setup the formula management tab"""
        layout = QVBoxLayout()

        # Create tabs for Feed and Mix formulas
        formula_tabs = QTabWidget()
        feed_formula_tab = QWidget()
        mix_formula_tab = QWidget()

        formula_tabs.addTab(feed_formula_tab, "Công thức Cám")
        formula_tabs.addTab(mix_formula_tab, "Công thức Mix")

        # Setup Feed Formula tab
        feed_layout = QVBoxLayout()

        # Add preset management
        feed_preset_layout = QHBoxLayout()
        feed_preset_layout.addWidget(QLabel("Công thức có sẵn:"))

        self.feed_preset_combo = QComboBox()
        self.update_feed_preset_combo()
        # Kết nối sự kiện thay đổi selection để tự động tải công thức
        self.feed_preset_combo.currentIndexChanged.connect(self.auto_load_feed_preset)
        feed_preset_layout.addWidget(self.feed_preset_combo)

        update_feed_preset_button = QPushButton("Cập nhật")
        update_feed_preset_button.clicked.connect(self.update_feed_preset)
        feed_preset_layout.addWidget(update_feed_preset_button)

        save_as_feed_preset_button = QPushButton("Lưu thành")
        save_as_feed_preset_button.clicked.connect(self.save_as_feed_preset)
        feed_preset_layout.addWidget(save_as_feed_preset_button)

        delete_feed_preset_button = QPushButton("Xóa")
        delete_feed_preset_button.clicked.connect(self.delete_feed_preset)
        feed_preset_layout.addWidget(delete_feed_preset_button)

        feed_layout.addLayout(feed_preset_layout)

        # Add mix formula link section
        mix_link_layout = QHBoxLayout()
        mix_link_layout.addWidget(QLabel("Công thức Mix cho Nguyên liệu tổ hợp:"))

        self.mix_link_combo = QComboBox()
        self.update_mix_link_combo()
        mix_link_layout.addWidget(self.mix_link_combo)

        set_mix_link_button = QPushButton("Gắn công thức")
        set_mix_link_button.clicked.connect(self.set_mix_formula_link)
        mix_link_layout.addWidget(set_mix_link_button)

        feed_layout.addLayout(mix_link_layout)

        self.feed_formula_table = QTableWidget()
        self.feed_formula_table.setColumnCount(2)
        self.feed_formula_table.setHorizontalHeaderLabels(["Thành phần", "Lượng (kg/mẻ)"])
        self.feed_formula_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Populate feed formula table
        self.update_feed_formula_table()

        feed_layout.addWidget(self.feed_formula_table)

        feed_formula_tab.setLayout(feed_layout)

        # Setup Mix Formula tab
        mix_layout = QVBoxLayout()

        # Add preset management
        mix_preset_layout = QHBoxLayout()
        mix_preset_layout.addWidget(QLabel("Công thức có sẵn:"))

        self.mix_preset_combo = QComboBox()
        self.update_mix_preset_combo()
        # Kết nối sự kiện thay đổi selection để tự động tải công thức
        self.mix_preset_combo.currentIndexChanged.connect(self.auto_load_mix_preset)
        mix_preset_layout.addWidget(self.mix_preset_combo)

        update_mix_preset_button = QPushButton("Cập nhật")
        update_mix_preset_button.clicked.connect(self.update_mix_preset)
        mix_preset_layout.addWidget(update_mix_preset_button)

        save_as_mix_preset_button = QPushButton("Lưu thành")
        save_as_mix_preset_button.clicked.connect(self.save_as_mix_preset)
        mix_preset_layout.addWidget(save_as_mix_preset_button)

        delete_mix_preset_button = QPushButton("Xóa")
        delete_mix_preset_button.clicked.connect(self.delete_mix_preset)
        mix_preset_layout.addWidget(delete_mix_preset_button)

        mix_layout.addLayout(mix_preset_layout)

        self.mix_formula_table = QTableWidget()
        self.mix_formula_table.setColumnCount(2)
        self.mix_formula_table.setHorizontalHeaderLabels(["Thành phần", "Lượng (kg/mẻ)"])
        self.mix_formula_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Populate mix formula table
        self.update_mix_formula_table()

        mix_layout.addWidget(self.mix_formula_table)

        mix_formula_tab.setLayout(mix_layout)

        layout.addWidget(formula_tabs)
        self.formula_tab.setLayout(layout)

    def setup_history_tab(self):
        """Setup the history tab to view past feed usage"""
        layout = QVBoxLayout()

        # Header section
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Lịch Sử Sử Dụng Cám"))
        header_layout.addStretch()

        # Date selection section
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Chọn ngày:"))

        self.history_date_combo = QComboBox()
        self.update_history_dates()
        date_layout.addWidget(self.history_date_combo)

        load_button = QPushButton("Tải Dữ Liệu")
        load_button.clicked.connect(self.load_history_data)
        date_layout.addWidget(load_button)

        # Add comparison section
        date_layout.addWidget(QLabel("So sánh với:"))

        self.compare_date_combo = QComboBox()
        self.compare_date_combo.addItem("Không so sánh", "")
        self.update_history_dates(self.compare_date_combo)
        date_layout.addWidget(self.compare_date_combo)

        compare_button = QPushButton("So Sánh")
        compare_button.clicked.connect(self.compare_history_data)
        date_layout.addWidget(compare_button)

        date_layout.addStretch()

        # Create tab widget for different history views
        self.history_tabs = QTabWidget()

        # Create tabs for different history views
        self.history_usage_tab = QWidget()
        self.history_feed_tab = QWidget()
        self.history_mix_tab = QWidget()

        self.history_tabs.addTab(self.history_usage_tab, "Sử Dụng Cám")
        self.history_tabs.addTab(self.history_feed_tab, "Thành Phần Cám")
        self.history_tabs.addTab(self.history_mix_tab, "Thành Phần Mix")

        # Setup each history tab
        self.setup_history_usage_tab()
        self.setup_history_feed_tab()
        self.setup_history_mix_tab()

        # Add widgets to layout
        layout.addLayout(header_layout)
        layout.addLayout(date_layout)
        layout.addWidget(self.history_tabs)

        # Visualization button
        button_layout = QHBoxLayout()

        visualize_button = QPushButton("Hiển Thị Biểu Đồ")
        visualize_button.clicked.connect(self.visualize_history_data)
        button_layout.addWidget(visualize_button)

        export_history_button = QPushButton("Xuất Excel")
        export_history_button.clicked.connect(self.export_history_to_excel)
        button_layout.addWidget(export_history_button)

        layout.addLayout(button_layout)

        self.history_tab.setLayout(layout)

    def setup_history_usage_tab(self):
        """Setup the history usage tab"""
        layout = QVBoxLayout()

        # Create table for historical feed usage
        self.history_usage_table = QTableWidget()

        # Calculate total number of farms
        total_farms = sum(len(farms) for farms in FARMS.values())

        # Tạo bảng với cấu trúc giống bảng ở dashboard:
        # - Hàng đầu tiên: Khu (label)
        # - Hàng thứ hai: Trại
        # - Các hàng tiếp theo: Buổi (Sáng/Chiều)
        self.history_usage_table.setRowCount(len(SHIFTS) + 2)  # +2 cho hàng Khu và hàng Trại
        self.history_usage_table.setColumnCount(total_farms)  # Chỉ hiển thị các trại, bỏ cột nhãn

        # Ẩn header row (dãy số trên cùng)
        self.history_usage_table.horizontalHeader().setVisible(False)

        # Set row headers
        self.history_usage_table.setVerticalHeaderItem(0, QTableWidgetItem("Khu"))
        self.history_usage_table.setVerticalHeaderItem(1, QTableWidgetItem("Trại"))
        for i, shift in enumerate(SHIFTS):
            self.history_usage_table.setVerticalHeaderItem(i + 2, QTableWidgetItem(shift))

        layout.addWidget(self.history_usage_table)
        self.history_usage_tab.setLayout(layout)

    def setup_history_feed_tab(self):
        """Setup the history feed ingredients tab"""
        layout = QVBoxLayout()

        # Create table for historical feed ingredients
        self.history_feed_table = QTableWidget()
        self.history_feed_table.setColumnCount(3)  # Thành phần, Số lượng (kg), Số bao
        self.history_feed_table.setHorizontalHeaderLabels(["Thành phần", "Số lượng (kg)", "Số bao"])
        self.history_feed_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.history_feed_table)
        self.history_feed_tab.setLayout(layout)

    def setup_history_mix_tab(self):
        """Setup the history mix ingredients tab"""
        layout = QVBoxLayout()

        # Create table for historical mix ingredients
        self.history_mix_table = QTableWidget()
        self.history_mix_table.setColumnCount(3)  # Thành phần, Số lượng (kg), Số bao
        self.history_mix_table.setHorizontalHeaderLabels(["Thành phần", "Số lượng (kg)", "Số bao"])
        self.history_mix_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.history_mix_table)
        self.history_mix_tab.setLayout(layout)

    def update_history_dates(self, combo_box=None):
        """Update the list of available report dates"""
        # Xác định combo box cần cập nhật
        combo_boxes = []
        if combo_box is None:
            combo_boxes.append(self.history_date_combo)
            if hasattr(self, 'compare_date_combo'):
                combo_boxes.append(self.compare_date_combo)
        else:
            combo_boxes.append(combo_box)

        # Xóa dữ liệu cũ
        for cb in combo_boxes:
            cb.clear()

        # Reports directory
        reports_dir = "reports"

        # Check if reports directory exists
        if not os.path.exists(reports_dir):
            for cb in combo_boxes:
                cb.addItem("Không có dữ liệu")
            return

        # Find all report files in the reports directory
        report_files = [os.path.join(reports_dir, f) for f in os.listdir(reports_dir)
                       if f.startswith('report_') and f.endswith('.json')]

        # Nếu không có file báo cáo
        if not report_files:
            for cb in combo_boxes:
                cb.addItem("Không có dữ liệu")
            return

        # Sort by date (newest first)
        report_files.sort(reverse=True)

        # Thêm option "Không so sánh" cho combo box so sánh
        if combo_box is None and hasattr(self, 'compare_date_combo'):
            self.compare_date_combo.addItem("Không so sánh", "")

        # Add to combo box
        for report_file in report_files:
            # Extract date from filename (format: reports/report_YYYYMMDD.json)
            date_str = os.path.basename(report_file)[7:-5]  # Remove 'report_' and '.json'
            try:
                # Format date as DD/MM/YYYY for display
                date = QDate.fromString(date_str, "yyyyMMdd")
                formatted_date = date.toString("dd/MM/yyyy")
                for cb in combo_boxes:
                    cb.addItem(formatted_date, report_file)
            except:
                # If date parsing fails, just add the filename
                for cb in combo_boxes:
                    cb.addItem(os.path.basename(report_file))

    def load_history_data(self):
        """Load historical data for the selected date"""
        # Get selected report file
        current_index = self.history_date_combo.currentIndex()
        if current_index < 0:
            QMessageBox.warning(self, "Lỗi", "Không có dữ liệu lịch sử để tải")
            return

        report_file = self.history_date_combo.itemData(current_index)
        if not report_file:
            QMessageBox.warning(self, "Lỗi", "Không tìm thấy file báo cáo")
            return

        try:
            # Load report data
            with open(report_file, 'r', encoding='utf-8') as f:
                report_data = json.load(f)

            # Update usage table
            self.update_history_usage_table(report_data)

            # Update feed ingredients table
            self.update_history_feed_table(report_data)

            # Update mix ingredients table
            self.update_history_mix_table(report_data)

            QMessageBox.information(self, "Thành công", f"Đã tải dữ liệu lịch sử ngày {self.history_date_combo.currentText()}")

        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể tải dữ liệu lịch sử: {str(e)}")

    def update_history_usage_table(self, report_data):
        """Update the history usage table with data from a report"""
        if "feed_usage" not in report_data:
            return

        # Xóa dữ liệu cũ
        self.history_usage_table.clearContents()

        # Populate table with farms and khu information
        col_index = 0  # Bắt đầu từ cột 0 vì đã bỏ cột nhãn
        for khu_idx, farms in FARMS.items():
            khu_name = f"Khu {khu_idx + 1}"

            for farm_idx, farm in enumerate(farms):
                # Set khu label in first row
                self.history_usage_table.setItem(0, col_index, QTableWidgetItem(khu_name))

                # Set farm name in second row
                self.history_usage_table.setItem(1, col_index, QTableWidgetItem(farm))

                # Set values for each shift
                if khu_name in report_data["feed_usage"] and farm in report_data["feed_usage"][khu_name]:
                    farm_data = report_data["feed_usage"][khu_name][farm]

                    # Kiểm tra xem có dữ liệu công thức không
                    has_formula_data = ("formula_usage" in report_data and
                                       khu_name in report_data["formula_usage"] and
                                       farm in report_data["formula_usage"][khu_name])

                    for shift_idx, shift in enumerate(SHIFTS):
                        if shift in farm_data:
                            value = farm_data[shift]

                            # Nếu có dữ liệu công thức, hiển thị cả số lượng và công thức
                            if has_formula_data and shift in report_data["formula_usage"][khu_name][farm]:
                                formula = report_data["formula_usage"][khu_name][farm][shift]
                                if formula:
                                    display_text = f"{format_number(value)} ({formula})"
                                else:
                                    display_text = format_number(value)
                            else:
                                display_text = format_number(value)

                            self.history_usage_table.setItem(shift_idx + 2, col_index,
                                                          QTableWidgetItem(display_text))

                col_index += 1

        # Calculate and display totals
        # Calculate total for each area
        for area_idx in range(AREAS):
            area_name = f"Khu {area_idx + 1}"
            farms = FARMS[area_idx]
            col_start = 0
            for idx in range(area_idx):
                col_start += len(FARMS[idx])

            # Calculate total for each shift
            for shift_idx, shift in enumerate(SHIFTS):
                total = 0
                for farm_idx in range(len(farms)):
                    col = col_start + farm_idx
                    item = self.history_usage_table.item(shift_idx + 2, col)
                    if item and item.text():
                        try:
                            # Trích xuất số từ văn bản (có thể có công thức trong ngoặc)
                            text = item.text()
                            if "(" in text:
                                text = text.split("(")[0].strip()
                            total += float(text.replace(',', '.'))
                        except ValueError:
                            pass

                # Add total to area totals row
                self.history_usage_table.setItem(shift_idx + 2 + len(SHIFTS), col_start,
                                              QTableWidgetItem(format_number(total)))

                # Merge cells for area total
                if len(farms) > 1:
                    self.history_usage_table.setSpan(shift_idx + 2 + len(SHIFTS), col_start, 1, len(farms))

    def update_history_feed_table(self, report_data):
        """Update the history feed ingredients table with data from the report"""
        if "feed_ingredients" not in report_data:
            return

        # Get feed ingredients
        feed_ingredients = report_data["feed_ingredients"]

        # Prepare data for table
        table_data = []
        total_amount = 0
        total_bags = 0

        for ingredient, amount in feed_ingredients.items():
            bags = self.inventory_manager.calculate_bags(ingredient, amount)
            table_data.append((ingredient, amount, bags))
            total_amount += amount
            total_bags += bags

        # Sort by amount (descending)
        table_data.sort(key=lambda x: x[1], reverse=True)

        # Update table with space for total row
        self.history_feed_table.setRowCount(len(table_data) + 1)

        for row, (ingredient, amount, bags) in enumerate(table_data):
            self.history_feed_table.setItem(row, 0, QTableWidgetItem(ingredient))
            self.history_feed_table.setItem(row, 1, QTableWidgetItem(format_number(amount)))
            self.history_feed_table.setItem(row, 2, QTableWidgetItem(format_number(bags)))

        # Add total row
        total_row = len(table_data)
        total_item = QTableWidgetItem("Tổng lượng Cám")
        total_item.setFont(QFont("Arial", weight=QFont.Bold))
        self.history_feed_table.setItem(total_row, 0, total_item)

        total_amount_item = QTableWidgetItem(format_number(total_amount))
        total_amount_item.setFont(QFont("Arial", weight=QFont.Bold))
        total_amount_item.setBackground(QColor(200, 230, 250))  # Light blue background
        self.history_feed_table.setItem(total_row, 1, total_amount_item)

        total_bags_item = QTableWidgetItem(format_number(total_bags))
        total_bags_item.setFont(QFont("Arial", weight=QFont.Bold))
        total_bags_item.setBackground(QColor(200, 230, 250))  # Light blue background
        self.history_feed_table.setItem(total_row, 2, total_bags_item)

    def update_history_mix_table(self, report_data):
        """Update the history mix ingredients table with data from the report"""
        if "mix_ingredients" not in report_data:
            return

        # Get mix ingredients
        mix_ingredients = report_data["mix_ingredients"]

        # Get linked mix formula name if available
        linked_mix_name = report_data.get("linked_mix_formula", "")
        tong_hop_amount = report_data.get("tong_hop_amount", 0)
        mix_total = report_data.get("mix_total", 0)

        # Set title with linked formula info if available
        if linked_mix_name:
            self.history_tabs.setTabText(2, f"Thành Phần Mix ({linked_mix_name})")
        else:
            self.history_tabs.setTabText(2, "Thành Phần Mix")

        # Prepare data for table
        table_data = []
        total_amount = 0
        total_bags = 0

        for ingredient, amount in mix_ingredients.items():
            bags = self.inventory_manager.calculate_bags(ingredient, amount)
            table_data.append((ingredient, amount, bags))
            total_amount += amount
            total_bags += bags

        # Sort by amount (descending)
        table_data.sort(key=lambda x: x[1], reverse=True)

        # Update table with space for total row
        self.history_mix_table.setRowCount(len(table_data) + 1)

        for row, (ingredient, amount, bags) in enumerate(table_data):
            self.history_mix_table.setItem(row, 0, QTableWidgetItem(ingredient))
            self.history_mix_table.setItem(row, 1, QTableWidgetItem(format_number(amount)))
            self.history_mix_table.setItem(row, 2, QTableWidgetItem(format_number(bags)))

        # Add total row
        total_row = len(table_data)
        total_item = QTableWidgetItem("Tổng lượng Mix")
        total_item.setFont(QFont("Arial", weight=QFont.Bold))
        self.history_mix_table.setItem(total_row, 0, total_item)

        total_amount_item = QTableWidgetItem(format_number(total_amount))
        total_amount_item.setFont(QFont("Arial", weight=QFont.Bold))
        total_amount_item.setBackground(QColor(230, 250, 200))  # Light green background
        self.history_mix_table.setItem(total_row, 1, total_amount_item)

        total_bags_item = QTableWidgetItem(format_number(total_bags))
        total_bags_item.setFont(QFont("Arial", weight=QFont.Bold))
        total_bags_item.setBackground(QColor(230, 250, 200))  # Light green background
        self.history_mix_table.setItem(total_row, 2, total_bags_item)

    def visualize_history_data(self):
        """Visualize historical data for the selected date"""
        # Get selected report file
        current_index = self.history_date_combo.currentIndex()
        if current_index < 0:
            QMessageBox.warning(self, "Lỗi", "Không có dữ liệu lịch sử để hiển thị")
            return

        report_file = self.history_date_combo.itemData(current_index)
        if not report_file:
            QMessageBox.warning(self, "Lỗi", "Không tìm thấy file báo cáo")
            return

        try:
            # Run visualization script with the report file
            subprocess.Popen([sys.executable, "visualize.py", report_file])
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể hiển thị biểu đồ: {str(e)}")

    def update_feed_formula_table(self):
        """Update the feed formula table with current formula"""
        self.feed_formula = self.formula_manager.get_feed_formula()

        # Tính tổng lượng cám (không bao gồm nguyên liệu tổ hợp)
        total_feed = 0
        for ingredient, amount in self.feed_formula.items():
            if ingredient != "Nguyên liệu tổ hợp":
                total_feed += amount

        # Get linked mix formula name for display
        current_preset = self.feed_preset_combo.currentText()
        linked_mix_name = ""

        if current_preset:
            # Nếu đang xem một preset, lấy liên kết cho preset đó
            linked_mix_name = self.formula_manager.get_linked_mix_formula_name(current_preset)
        else:
            # Nếu đang xem công thức hiện tại, lấy liên kết hiện tại
            linked_mix_name = self.formula_manager.get_linked_mix_formula_name()

        # Lấy công thức mix đã được liên kết
        mix_formula = None
        if linked_mix_name:
            if current_preset:
                mix_formula = self.formula_manager.get_linked_mix_formula(current_preset)
            else:
                mix_formula = self.formula_manager.get_linked_mix_formula()

        # Tính tổng lượng mix nếu có
        mix_total = 0
        if mix_formula:
            mix_total = self.formula_manager.calculate_mix_total(mix_formula)

        # Thêm hàng tổng cộng cho cám (không thêm hàng tổng mix)
        total_rows = len(self.feed_formula) + 1  # +1 cho hàng tổng cám
        self.feed_formula_table.setRowCount(total_rows)

        row = 0
        for ingredient, amount in self.feed_formula.items():
            # Ingredient name
            ingredient_name = ingredient
            if ingredient == "Nguyên liệu tổ hợp":
                if linked_mix_name:
                    ingredient_name = f"{ingredient} (Gắn với: {linked_mix_name})"

                    # Hiển thị tổng lượng mix thay vì giá trị nguyên liệu tổ hợp
                    amount_spin = QDoubleSpinBox()
                    amount_spin.setRange(0, 2000)
                    amount_spin.setValue(mix_total)
                    self.feed_formula_table.setCellWidget(row, 1, amount_spin)
                else:
                    # Nếu không có công thức mix được gắn, hiển thị giá trị bình thường
                    amount_spin = QDoubleSpinBox()
                    amount_spin.setRange(0, 2000)
                    amount_spin.setValue(amount)
                    self.feed_formula_table.setCellWidget(row, 1, amount_spin)
            else:
                # Các thành phần khác hiển thị bình thường
                amount_spin = QDoubleSpinBox()
                amount_spin.setRange(0, 2000)
                amount_spin.setValue(amount)
                self.feed_formula_table.setCellWidget(row, 1, amount_spin)

            self.feed_formula_table.setItem(row, 0, QTableWidgetItem(ingredient_name))
            row += 1

        # Thêm hàng tổng lượng cám
        total_item = QTableWidgetItem("Tổng lượng Cám")
        total_item.setFont(QFont("Arial", weight=QFont.Bold))
        self.feed_formula_table.setItem(row, 0, total_item)

        total_value = QTableWidgetItem(format_number(total_feed))
        total_value.setFont(QFont("Arial", weight=QFont.Bold))
        total_value.setBackground(QColor(200, 230, 250))  # Light blue background
        self.feed_formula_table.setItem(row, 1, total_value)

    def update_mix_formula_table(self):
        """Update the mix formula table with current formula"""
        self.mix_formula = self.formula_manager.get_mix_formula()

        # Tính tổng lượng mix
        mix_total = self.formula_manager.calculate_mix_total(self.mix_formula)

        # Thêm hàng tổng cộng
        self.mix_formula_table.setRowCount(len(self.mix_formula) + 1)

        for i, (ingredient, amount) in enumerate(self.mix_formula.items()):
            # Ingredient name
            self.mix_formula_table.setItem(i, 0, QTableWidgetItem(ingredient))

            # Amount input
            amount_spin = QDoubleSpinBox()
            amount_spin.setRange(0, 2000)
            amount_spin.setValue(amount)
            self.mix_formula_table.setCellWidget(i, 1, amount_spin)

        # Thêm hàng tổng lượng
        total_row = len(self.mix_formula)
        total_item = QTableWidgetItem("Tổng lượng Mix")
        total_item.setFont(QFont("Arial", weight=QFont.Bold))
        self.mix_formula_table.setItem(total_row, 0, total_item)

        total_value = QTableWidgetItem(format_number(mix_total))
        total_value.setFont(QFont("Arial", weight=QFont.Bold))
        total_value.setBackground(QColor(230, 250, 200))  # Light green background
        self.mix_formula_table.setItem(total_row, 1, total_value)

    def update_feed_inventory_table(self):
        """Update the feed inventory table"""
        # Get relevant ingredients from feed formula
        feed_ingredients = [k for k in self.feed_formula.keys() if k != "Nguyên liệu tổ hợp"]
        self.feed_inventory_table.setRowCount(len(feed_ingredients))

        # Update inventory from manager
        self.inventory = self.inventory_manager.get_inventory()

        for i, ingredient in enumerate(feed_ingredients):
            # Ingredient name
            self.feed_inventory_table.setItem(i, 0, QTableWidgetItem(ingredient))

            # Current inventory
            inventory_amount = self.inventory.get(ingredient, 0)
            self.feed_inventory_table.setItem(i, 1, QTableWidgetItem(str(inventory_amount)))

            # Bag size
            bag_size = self.inventory_manager.get_bag_size(ingredient)
            self.feed_inventory_table.setItem(i, 2, QTableWidgetItem(str(bag_size)))

            # Number of bags
            bags = self.inventory_manager.calculate_bags(ingredient, inventory_amount)
            self.feed_inventory_table.setItem(i, 3, QTableWidgetItem(format_number(bags)))

    def update_mix_inventory_table(self):
        """Update the mix inventory table"""
        mix_ingredients = list(self.mix_formula.keys())
        self.mix_inventory_table.setRowCount(len(mix_ingredients))

        # Update inventory from manager
        self.inventory = self.inventory_manager.get_inventory()

        for i, ingredient in enumerate(mix_ingredients):
            # Ingredient name
            self.mix_inventory_table.setItem(i, 0, QTableWidgetItem(ingredient))

            # Current inventory
            inventory_amount = self.inventory.get(ingredient, 0)
            self.mix_inventory_table.setItem(i, 1, QTableWidgetItem(str(inventory_amount)))

            # Bag size
            bag_size = self.inventory_manager.get_bag_size(ingredient)
            self.mix_inventory_table.setItem(i, 2, QTableWidgetItem(str(bag_size)))

            # Number of bags
            bags = self.inventory_manager.calculate_bags(ingredient, inventory_amount)
            self.mix_inventory_table.setItem(i, 3, QTableWidgetItem(format_number(bags)))

    def calculate_feed_usage(self):
        """Calculate feed usage based on input table"""
        total_batches = 0
        area_batches = {}
        farm_batches = {}

        # Dictionary để lưu số mẻ theo từng công thức cám
        formula_batches = {}

        # Dictionary để lưu thành phần cám theo từng công thức
        formula_ingredients = {}

        # Khởi tạo dữ liệu cho từng khu
        for area in range(AREAS):
            area_batches[f"Khu {area + 1}"] = 0

        # Tính tổng số mẻ cám sử dụng theo từng trại và từng khu
        col_index = 0 # Bắt đầu từ cột 0 vì đã bỏ cột nhãn
        for khu_idx, farms in FARMS.items():
            khu_name = f"Khu {khu_idx + 1}"

            for farm in farms:
                farm_name = farm
                farm_key = f"{khu_name}-{farm}"
                farm_batches[farm_key] = 0

                # Tính tổng mẻ cám cho trại này
                for shift_idx in range(len(SHIFTS)):
                    cell_widget = self.feed_table.cellWidget(shift_idx + 2, col_index)
                    if cell_widget:
                        # Lấy spinbox và combobox từ container
                        spin_box = cell_widget.spin_box
                        formula_combo = cell_widget.formula_combo

                        # Lấy giá trị nhập vào và công thức cám
                        input_value = spin_box.value()
                        formula_name = formula_combo.currentText()

                        # Nếu có nhập số lượng và chọn công thức
                        if input_value > 0 and formula_name:
                            # Chuyển đổi số lượng từ bảng thành số mẻ
                            # 0.5 tương đương với 1 mẻ, 1 tương đương với 2 mẻ
                            actual_batches = input_value * 2  # Nhân đôi giá trị nhập vào để có số mẻ thực tế

                            # Cập nhật số mẻ cho trại và khu
                            farm_batches[farm_key] += actual_batches
                            area_batches[khu_name] += actual_batches
                            total_batches += actual_batches

                            # Cộng dồn số mẻ theo công thức
                            if formula_name not in formula_batches:
                                formula_batches[formula_name] = 0
                            formula_batches[formula_name] += actual_batches

                col_index += 1

        # Tính toán thành phần cám sử dụng cho từng công thức
        # Dictionary để lưu tổng thành phần cám
        feed_ingredients = {}
        # Dictionary để lưu tổng thành phần mix
        mix_ingredients = {}

        for formula_name, batch_count in formula_batches.items():
            if not formula_name:
                continue

            # Lấy công thức cám
            feed_formula = self.formula_manager.load_feed_preset(formula_name)
            if not feed_formula:
                continue

            # Tính toán thành phần cám (không bao gồm mix)
            for ingredient, amount_per_batch in feed_formula.items():
                if ingredient != "Nguyên liệu tổ hợp":
                    feed_amount = amount_per_batch * batch_count

                    # Cộng dồn vào tổng thành phần cám
                    if ingredient in feed_ingredients:
                        feed_ingredients[ingredient] += feed_amount
                    else:
                        feed_ingredients[ingredient] = feed_amount

            # Lấy tên công thức mix được liên kết với preset cám hiện tại
            linked_mix_name = self.formula_manager.get_linked_mix_formula_name(formula_name)

            # Lấy dữ liệu công thức mix được liên kết
            mix_formula = self.formula_manager.get_linked_mix_formula(formula_name)

            # Lấy lượng nguyên liệu tổ hợp từ công thức cám
            tong_hop_amount = feed_formula.get("Nguyên liệu tổ hợp", 0)

            # Tính tổng lượng mix nếu có
            mix_total = 0
            if mix_formula:
                mix_total = self.formula_manager.calculate_mix_total(mix_formula)

            # Tính tỷ lệ giữa các thành phần mix
            mix_ratios = {}
            if mix_total > 0:
                for ingredient, amount in mix_formula.items():
                    mix_ratios[ingredient] = amount / mix_total

            # Tính toán thành phần mix dựa trên tỷ lệ
            for ingredient, ratio in mix_ratios.items():
                # Tính lượng mix theo tỷ lệ với tổng lượng mix và số mẻ
                mix_amount = ratio * tong_hop_amount * batch_count

                # Cộng dồn vào tổng thành phần mix
                if ingredient in mix_ingredients:
                    mix_ingredients[ingredient] += mix_amount
                else:
                    mix_ingredients[ingredient] = mix_amount

            # Lưu thông tin công thức và thành phần cho hiển thị chi tiết nếu cần
            formula_ingredients[formula_name] = {
                "batches": batch_count,
                "linked_mix_name": linked_mix_name,
                "tong_hop_amount": tong_hop_amount
            }

        # Tính tổng lượng cám và mix
        total_feed_amount = sum(feed_ingredients.values())
        total_mix_amount = sum(mix_ingredients.values())

        # Cập nhật bảng kết quả
        # Sắp xếp các thành phần để đưa bắp và nành lên đầu
        priority_ingredients = ["Bắp", "Nành"]
        sorted_feed_ingredients = {}

        # Thêm các thành phần ưu tiên trước
        for ingredient in priority_ingredients:
            if ingredient in feed_ingredients:
                sorted_feed_ingredients[ingredient] = feed_ingredients[ingredient]

        # Thêm các thành phần còn lại
        for ingredient, amount in feed_ingredients.items():
            if ingredient not in priority_ingredients:
                sorted_feed_ingredients[ingredient] = amount

        # Tính tổng số hàng cần thiết
        total_rows = len(sorted_feed_ingredients) + len(mix_ingredients) + 4  # +4 cho 2 tiêu đề và 2 tổng cộng
        self.results_table.setRowCount(total_rows)

        # Thêm tiêu đề kho cám
        row = 0
        feed_header = QTableWidgetItem("THÀNH PHẦN KHO CÁM")
        feed_header.setBackground(QColor(200, 230, 250))  # Light blue background
        font = QFont()
        font.setBold(True)
        feed_header.setFont(font)
        self.results_table.setItem(row, 0, feed_header)
        self.results_table.setSpan(row, 0, 1, 3)  # Merge cells across all columns
        row += 1

        # Thêm các thành phần cám
        for ingredient, amount in sorted_feed_ingredients.items():
            # Ingredient name with special marking for priority ingredients
            ingredient_name = ingredient
            if ingredient in priority_ingredients:
                ingredient_name = f"★ {ingredient}"

            item = QTableWidgetItem(ingredient_name)
            if ingredient in priority_ingredients:
                item.setBackground(QColor(255, 255, 200))  # Light yellow background for priority
            self.results_table.setItem(row, 0, item)

            # Amount used
            self.results_table.setItem(row, 1, QTableWidgetItem(format_number(amount)))

            # Number of bags
            bags = self.inventory_manager.calculate_bags(ingredient, amount)
            self.results_table.setItem(row, 2, QTableWidgetItem(format_number(bags)))

            row += 1

        # Thêm tổng lượng cám
        total_feed_item = QTableWidgetItem("Tổng lượng Cám")
        total_feed_item.setFont(QFont("Arial", weight=QFont.Bold))
        self.results_table.setItem(row, 0, total_feed_item)

        total_feed_value = QTableWidgetItem(format_number(total_feed_amount))
        total_feed_value.setFont(QFont("Arial", weight=QFont.Bold))
        total_feed_value.setBackground(QColor(200, 230, 250))  # Light blue background
        self.results_table.setItem(row, 1, total_feed_value)

        # Không hiển thị số bao cho tổng lượng
        self.results_table.setItem(row, 2, QTableWidgetItem(""))
        row += 1

        # Thêm tiêu đề kho mix
        mix_header = QTableWidgetItem("THÀNH PHẦN KHO MIX")
        mix_header.setBackground(QColor(230, 250, 200))  # Light green background
        mix_header.setFont(font)
        self.results_table.setItem(row, 0, mix_header)
        self.results_table.setSpan(row, 0, 1, 3)  # Merge cells across all columns
        row += 1

        # Thêm các thành phần kho mix
        for ingredient, amount in mix_ingredients.items():
            # Ingredient name
            self.results_table.setItem(row, 0, QTableWidgetItem(ingredient))

            # Amount used
            self.results_table.setItem(row, 1, QTableWidgetItem(format_number(amount)))

            # Number of bags
            bags = self.inventory_manager.calculate_bags(ingredient, amount)
            self.results_table.setItem(row, 2, QTableWidgetItem(format_number(bags)))

            row += 1

        # Thêm tổng lượng mix
        total_mix_item = QTableWidgetItem("Tổng lượng Mix")
        total_mix_item.setFont(QFont("Arial", weight=QFont.Bold))
        self.results_table.setItem(row, 0, total_mix_item)

        total_mix_value = QTableWidgetItem(format_number(total_mix_amount))
        total_mix_value.setFont(QFont("Arial", weight=QFont.Bold))
        total_mix_value.setBackground(QColor(230, 250, 200))  # Light green background
        self.results_table.setItem(row, 1, total_mix_value)

        # Không hiển thị số bao cho tổng lượng
        self.results_table.setItem(row, 2, QTableWidgetItem(""))

        # Update results label - hiển thị số mẻ thực tế
        results_text = f"Tổng số mẻ: {format_number(total_batches)} | "
        for area, batches in area_batches.items():
            results_text += f"{area}: {format_number(batches)} mẻ | "

        # Thêm thông tin số mẻ theo công thức
        results_text += "\nTheo công thức: "
        for formula_name, batches in formula_batches.items():
            if batches > 0:
                results_text += f"{formula_name}: {format_number(batches)} mẻ | "

        self.results_label.setText(results_text)

        # Update inventory after calculation
        all_ingredients = {**feed_ingredients, **mix_ingredients}
        self.update_inventory_after_usage(all_ingredients)

    def update_inventory_after_usage(self, ingredients_used):
        """Update inventory after feed usage"""
        # Use inventory manager to update inventory
        self.inventory = self.inventory_manager.use_ingredients(ingredients_used)

        # Update inventory tables
        self.update_feed_inventory_table()
        self.update_mix_inventory_table()

    def update_inventory(self, inventory_type):
        """Update inventory amounts"""
        table = self.feed_inventory_table if inventory_type == "feed" else self.mix_inventory_table
        updates = {}

        for row in range(table.rowCount()):
            ingredient = table.item(row, 0).text()
            try:
                new_amount = float(table.item(row, 1).text())
                updates[ingredient] = new_amount
            except (ValueError, AttributeError):
                pass

        # Update inventory using manager
        self.inventory_manager.update_multiple(updates)
        self.inventory = self.inventory_manager.get_inventory()

        # Update inventory tables
        self.update_feed_inventory_table()
        self.update_mix_inventory_table()

        QMessageBox.information(self, "Thành công", "Đã cập nhật tồn kho thành công!")

    def save_feed_formula(self):
        """Save the feed formula"""
        try:
            updated_formula = {}

            # Lấy danh sách các thành phần từ công thức hiện tại để đảm bảo không bỏ sót
            current_ingredients = list(self.feed_formula.keys())

            # Duyệt qua các hàng trong bảng
            for row in range(self.feed_formula_table.rowCount()):
                # Bỏ qua nếu không có item ở cột 0
                if self.feed_formula_table.item(row, 0) is None:
                    continue

                # Lấy tên thành phần
                ingredient = self.feed_formula_table.item(row, 0).text()

                # Kiểm tra xem hàng hiện tại có phải là hàng tổng cộng không
                if ingredient == "Tổng lượng Cám":
                    continue  # Bỏ qua hàng tổng cộng

                # Loại bỏ phần "(Gắn với: ...)" nếu có
                if " (Gắn với: " in ingredient:
                    ingredient = ingredient.split(" (Gắn với: ")[0]

                # Lấy giá trị
                try:
                    # Thử lấy giá trị từ spin box
                    amount_spin = self.feed_formula_table.cellWidget(row, 1)
                    if amount_spin is not None:
                        amount = amount_spin.value()
                    else:
                        # Nếu không có spin box, thử lấy giá trị từ item
                        item = self.feed_formula_table.item(row, 1)
                        if item is not None:
                            amount = float(item.text().replace(',', '.'))
                        else:
                            # Nếu không có item, sử dụng giá trị từ công thức hiện tại
                            amount = self.feed_formula.get(ingredient, 0)

                    # Đối với Nguyên liệu tổ hợp, lưu giá trị gốc nếu có công thức mix được gắn
                    if ingredient == "Nguyên liệu tổ hợp":
                        # Kiểm tra xem có công thức mix được gắn không
                        current_preset = self.feed_preset_combo.currentText()
                        linked_mix_name = ""

                        if current_preset:
                            linked_mix_name = self.formula_manager.get_linked_mix_formula_name(current_preset)
                        else:
                            linked_mix_name = self.formula_manager.get_linked_mix_formula_name()

                        if linked_mix_name:
                            # Nếu có công thức mix được gắn, lưu giá trị gốc từ feed_formula
                            amount = self.feed_formula.get(ingredient, 0)

                    updated_formula[ingredient] = amount

                    # Đánh dấu thành phần đã được xử lý
                    if ingredient in current_ingredients:
                        current_ingredients.remove(ingredient)
                except Exception as e:
                    print(f"Lỗi khi xử lý thành phần {ingredient}: {e}")

            # Thêm các thành phần còn lại từ công thức hiện tại (nếu có)
            for ingredient in current_ingredients:
                updated_formula[ingredient] = self.feed_formula[ingredient]

            # Save formula using manager
            self.formula_manager.set_feed_formula(updated_formula)
            self.feed_formula = updated_formula

            # Cập nhật lại bảng để hiển thị đúng
            self.update_feed_formula_table()

            QMessageBox.information(self, "Thành công", "Đã lưu công thức cám thành công!")
            return True
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể lưu công thức cám: {str(e)}")
            # In thông tin lỗi ra console để debug
            import traceback
            traceback.print_exc()
            return False

    def save_mix_formula(self):
        """Save the mix formula"""
        try:
            updated_formula = {}

            # Lấy danh sách các thành phần từ công thức hiện tại để đảm bảo không bỏ sót
            current_ingredients = list(self.mix_formula.keys())

            # Duyệt qua các hàng trong bảng
            for row in range(self.mix_formula_table.rowCount()):
                # Bỏ qua nếu không có item ở cột 0
                if self.mix_formula_table.item(row, 0) is None:
                    continue

                # Lấy tên thành phần
                ingredient = self.mix_formula_table.item(row, 0).text()

                # Kiểm tra xem hàng hiện tại có phải là hàng tổng cộng không
                if ingredient == "Tổng lượng Mix":
                    continue  # Bỏ qua hàng tổng cộng

                # Lấy giá trị
                try:
                    # Thử lấy giá trị từ spin box
                    amount_spin = self.mix_formula_table.cellWidget(row, 1)
                    if amount_spin is not None:
                        amount = amount_spin.value()
                    else:
                        # Nếu không có spin box, thử lấy giá trị từ item
                        item = self.mix_formula_table.item(row, 1)
                        if item is not None:
                            amount = float(item.text().replace(',', '.'))
                        else:
                            # Nếu không có item, sử dụng giá trị từ công thức hiện tại
                            amount = self.mix_formula.get(ingredient, 0)

                    updated_formula[ingredient] = amount

                    # Đánh dấu thành phần đã được xử lý
                    if ingredient in current_ingredients:
                        current_ingredients.remove(ingredient)
                except Exception as e:
                    print(f"Lỗi khi xử lý thành phần {ingredient}: {e}")

            # Thêm các thành phần còn lại từ công thức hiện tại (nếu có)
            for ingredient in current_ingredients:
                updated_formula[ingredient] = self.mix_formula[ingredient]

            # Save formula using manager
            self.formula_manager.set_mix_formula(updated_formula)
            self.mix_formula = updated_formula

            # Cập nhật lại bảng để hiển thị đúng
            self.update_mix_formula_table()

            QMessageBox.information(self, "Thành công", "Đã lưu công thức mix thành công!")
            return True
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể lưu công thức mix: {str(e)}")
            # In thông tin lỗi ra console để debug
            import traceback
            traceback.print_exc()
            return False

    def save_report(self):
        """Save the current feed usage report"""
        try:
            # Create reports directory if it doesn't exist
            reports_dir = "src/data/reports"
            os.makedirs(reports_dir, exist_ok=True)

            # Get current date
            current_date = QDate.currentDate().toString("yyyy-MM-dd")
            filename = os.path.join(reports_dir, f"report_{current_date}.json")

            # Collect data from the feed usage table
            feed_data = {}
            formula_data = {}  # Dữ liệu về công thức cám cho từng mẻ

            # Collect data for each area and farm
            col_index = 0
            for khu_idx, farms in FARMS.items():
                khu_name = f"Khu {khu_idx + 1}"
                feed_data[khu_name] = {}
                formula_data[khu_name] = {}

                for farm in farms:
                    farm_name = farm
                    feed_data[khu_name][farm_name] = {}
                    formula_data[khu_name][farm_name] = {}

                    for shift_idx, shift in enumerate(SHIFTS):
                        cell_widget = self.feed_table.cellWidget(shift_idx + 2, col_index)
                        if cell_widget:
                            # Lấy spinbox và combobox từ container
                            spin_box = cell_widget.spin_box
                            formula_combo = cell_widget.formula_combo

                            # Lưu giá trị nhập vào và công thức cám
                            feed_data[khu_name][farm_name][shift] = spin_box.value()
                            formula_data[khu_name][farm_name][shift] = formula_combo.currentText()

                    col_index += 1

            # Collect data from results table
            results_data = []
            for row in range(self.results_table.rowCount()):
                row_data = {}
                for col in range(self.results_table.columnCount()):
                    item = self.results_table.item(row, col)
                    if item:
                        header = self.results_table.horizontalHeaderItem(col).text()
                        row_data[header] = item.text()
                results_data.append(row_data)

            # Get feed formula data
            feed_formula_data = {}
            for row in range(self.feed_formula_table.rowCount()):
                ingredient_item = self.feed_formula_table.item(row, 0)
                if ingredient_item and ingredient_item.text():
                    ingredient = ingredient_item.text()
                    amount_item = self.feed_formula_table.item(row, 1)
                    if amount_item:
                        try:
                            amount = float(amount_item.text().replace(',', '.'))
                            feed_formula_data[ingredient] = amount
                        except ValueError:
                            pass

            # Get mix formula data
            mix_formula_data = {}
            for row in range(self.mix_formula_table.rowCount()):
                ingredient_item = self.mix_formula_table.item(row, 0)
                if ingredient_item and ingredient_item.text():
                    ingredient = ingredient_item.text()
                    amount_item = self.mix_formula_table.item(row, 1)
                    if amount_item:
                        try:
                            amount = float(amount_item.text().replace(',', '.'))
                            mix_formula_data[ingredient] = amount
                        except ValueError:
                            pass

            # Prepare data to save
            report_data = {
                "date": current_date,
                "feed_usage": feed_data,
                "formula_usage": formula_data,  # Dữ liệu về công thức cám cho từng mẻ
                "results": results_data,
                "feed_formula": feed_formula_data,
                "mix_formula": mix_formula_data
            }

            # Save to file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=4)

            QMessageBox.information(self, "Thành công", f"Đã lưu báo cáo vào file {filename}")

            # Refresh history tab if it exists
            if hasattr(self, 'history_date_combo'):
                self.update_history_dates()

            return True
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể lưu báo cáo: {str(e)}")
            return False

    def export_to_excel(self):
        """Export current report to Excel"""
        try:
            # Get date for filename
            date_str = QDate.currentDate().toString('yyyyMMdd')

            # Create reports directory if it doesn't exist
            reports_dir = "reports"
            if not os.path.exists(reports_dir):
                os.makedirs(reports_dir)

            filename = os.path.join(reports_dir, f"report_{date_str}.xlsx")

            # Create a pandas ExcelWriter object
            writer = pd.ExcelWriter(filename, engine='openpyxl')

            # Create feed usage by khu dataframe
            khu_data = []
            for khu_idx in range(AREAS):
                khu_name = f"Khu {khu_idx + 1}"
                row_data = {"Khu": khu_name}

                # Calculate total for each shift in this khu
                for shift_idx, shift in enumerate(SHIFTS):
                    total = 0
                    farms = FARMS.get(khu_idx, [])

                    # If this khu has farms, sum up their values
                    if farms:
                        col_start = 0 # Bắt đầu từ cột 0 vì đã bỏ cột nhãn
                        for prev_khu_idx in range(khu_idx):
                            col_start += len(FARMS.get(prev_khu_idx, []))

                        for farm_idx in range(len(farms)):
                            col = col_start + farm_idx
                            spin_box = self.feed_table.cellWidget(shift_idx + 2, col)
                            if spin_box:
                                total += spin_box.value()

                    row_data[shift] = total

                khu_data.append(row_data)

            khu_df = pd.DataFrame(khu_data)

            # Create feed usage by farm dataframe
            farm_data = []
            col_index = 0 # Bắt đầu từ cột 0 vì đã bỏ cột nhãn
            for khu_idx, farms in FARMS.items():
                khu_name = f"Khu {khu_idx + 1}"

                for farm in farms:
                    row_data = {"Khu": khu_name, "Trại": farm}

                    for shift_idx, shift in enumerate(SHIFTS):
                        spin_box = self.feed_table.cellWidget(shift_idx + 2, col_index)
                        if spin_box:
                            row_data[shift] = spin_box.value()

                    farm_data.append(row_data)
                    col_index += 1

            farm_df = pd.DataFrame(farm_data)

            # Tính tổng số mẻ
            total_batches = 0
            for row in farm_data:
                total_batches += sum([row[shift] for shift in SHIFTS])

            # Tính toán thành phần cám sử dụng (không bao gồm mix)
            feed_ingredients_data = []
            for ingredient, amount_per_batch in self.feed_formula.items():
                if ingredient != "Nguyên liệu tổ hợp":
                    amount = amount_per_batch * total_batches
                    bags = self.inventory_manager.calculate_bags(ingredient, amount)
                    feed_ingredients_data.append({
                        "Thành phần": ingredient,
                        "Số lượng (kg)": amount,
                        "Số bao": bags
                    })

            feed_ingredients_df = pd.DataFrame(feed_ingredients_data)

            # Tính toán thành phần mix sử dụng
            mix_ingredients_data = []
            for ingredient, amount_per_batch in self.mix_formula.items():
                amount = amount_per_batch * total_batches
                bags = self.inventory_manager.calculate_bags(ingredient, amount)
                mix_ingredients_data.append({
                    "Thành phần": ingredient,
                    "Số lượng (kg)": amount,
                    "Số bao": bags
                })

            mix_ingredients_df = pd.DataFrame(mix_ingredients_data)

            # Write to Excel
            khu_df.to_excel(writer, sheet_name='Sử dụng Cám theo Khu', index=False)
            farm_df.to_excel(writer, sheet_name='Sử dụng Cám theo Trại', index=False)
            feed_ingredients_df.to_excel(writer, sheet_name='Thành phần Kho Cám', index=False)
            mix_ingredients_df.to_excel(writer, sheet_name='Thành phần Kho Mix', index=False)

            # Save the Excel file
            writer.close()

            QMessageBox.information(self, "Thành công", f"Đã xuất báo cáo vào file {filename}!")

        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể xuất báo cáo: {str(e)}")

    def update_feed_preset_combo(self):
        """Update feed preset combo box with available presets"""
        self.feed_preset_combo.clear()
        presets = self.formula_manager.get_feed_presets()
        for preset in presets:
            self.feed_preset_combo.addItem(preset)

    def update_mix_preset_combo(self):
        """Update mix preset combo box with available presets"""
        self.mix_preset_combo.clear()
        presets = self.formula_manager.get_mix_presets()
        for preset in presets:
            self.mix_preset_combo.addItem(preset)

    def load_feed_preset(self):
        """Load selected feed preset"""
        preset_name = self.feed_preset_combo.currentText()
        if not preset_name:
            return

        preset_formula = self.formula_manager.load_feed_preset(preset_name)
        if preset_formula:
            self.formula_manager.set_feed_formula(preset_formula)
            self.feed_formula = preset_formula
            self.update_feed_formula_table()

            # Cập nhật combo box liên kết mix để hiển thị liên kết cho preset này
            self.update_mix_link_combo()

            QMessageBox.information(self, "Thành công", f"Đã tải công thức cám '{preset_name}'")

    def load_mix_preset(self):
        """Load selected mix preset"""
        preset_name = self.mix_preset_combo.currentText()
        if not preset_name:
            return

        preset_formula = self.formula_manager.load_mix_preset(preset_name)
        if preset_formula:
            self.formula_manager.set_mix_formula(preset_formula)
            self.mix_formula = preset_formula
            self.update_mix_formula_table()
            QMessageBox.information(self, "Thành công", f"Đã tải công thức mix '{preset_name}'")

    def save_as_feed_preset(self):
        """Save current feed formula as a preset"""
        preset_name, ok = QInputDialog.getText(self, "Lưu công thức", "Tên công thức:")
        if ok and preset_name:
            try:
                # Lưu công thức hiện tại trước
                if not self.save_feed_formula():
                    return

                # Lấy công thức đã lưu
                formula = self.feed_formula

                # Save as preset
                if self.formula_manager.save_preset("feed", preset_name, formula):
                    self.update_feed_preset_combo()

                    # Chọn preset mới tạo
                    index = self.feed_preset_combo.findText(preset_name)
                    if index >= 0:
                        self.feed_preset_combo.setCurrentIndex(index)

                    QMessageBox.information(self, "Thành công", f"Đã lưu công thức cám '{preset_name}'")
            except Exception as e:
                QMessageBox.warning(self, "Lỗi", f"Không thể lưu công thức cám: {str(e)}")
                # In thông tin lỗi ra console để debug
                import traceback
                traceback.print_exc()

    def save_as_mix_preset(self):
        """Save current mix formula as a preset"""
        preset_name, ok = QInputDialog.getText(self, "Lưu công thức", "Tên công thức:")
        if ok and preset_name:
            try:
                # Lưu công thức hiện tại trước
                if not self.save_mix_formula():
                    return

                # Lấy công thức đã lưu
                formula = self.mix_formula

                # Save as preset
                if self.formula_manager.save_preset("mix", preset_name, formula):
                    self.update_mix_preset_combo()

                    # Chọn preset mới tạo
                    index = self.mix_preset_combo.findText(preset_name)
                    if index >= 0:
                        self.mix_preset_combo.setCurrentIndex(index)

                    QMessageBox.information(self, "Thành công", f"Đã lưu công thức mix '{preset_name}'")
            except Exception as e:
                QMessageBox.warning(self, "Lỗi", f"Không thể lưu công thức mix: {str(e)}")
                # In thông tin lỗi ra console để debug
                import traceback
                traceback.print_exc()

    def delete_feed_preset(self):
        """Delete selected feed preset"""
        preset_name = self.feed_preset_combo.currentText()
        if not preset_name:
            return

        reply = QMessageBox.question(self, "Xác nhận xóa",
                                     f"Bạn có chắc chắn muốn xóa công thức cám '{preset_name}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            if self.formula_manager.delete_preset("feed", preset_name):
                self.update_feed_preset_combo()
                QMessageBox.information(self, "Thành công", f"Đã xóa công thức cám '{preset_name}'")

    def delete_mix_preset(self):
        """Delete selected mix preset"""
        preset_name = self.mix_preset_combo.currentText()
        if not preset_name:
            return

        reply = QMessageBox.question(self, "Xác nhận xóa",
                                     f"Bạn có chắc chắn muốn xóa công thức mix '{preset_name}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            if self.formula_manager.delete_preset("mix", preset_name):
                self.update_mix_preset_combo()
                QMessageBox.information(self, "Thành công", f"Đã xóa công thức mix '{preset_name}'")

    def compare_history_data(self):
        """Compare data between selected dates in history tab"""
        current_date_index = self.history_date_combo.currentIndex()
        compare_date_index = self.compare_date_combo.currentIndex()

        if current_date_index < 0:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn ngày để so sánh.")
            return

        current_report_file = self.history_date_combo.itemData(current_date_index)

        if not current_report_file:
            QMessageBox.warning(self, "Lỗi", "Không tìm thấy file báo cáo cho ngày hiện tại.")
            return

        try:
            # Tải dữ liệu ngày hiện tại
            with open(current_report_file, 'r', encoding='utf-8') as f:
                current_data = json.load(f)

            # Nếu không có ngày so sánh hoặc chọn "Không so sánh"
            if compare_date_index <= 0 or not self.compare_date_combo.itemData(compare_date_index):
                # Chỉ hiển thị dữ liệu ngày hiện tại
                self.update_history_usage_table(current_data)
                self.update_history_feed_table(current_data)
                self.update_history_mix_table(current_data)

                QMessageBox.information(self, "Thành công", f"Đã tải dữ liệu ngày {self.history_date_combo.currentText()}")
                return

            # Tải dữ liệu ngày so sánh
            compare_report_file = self.compare_date_combo.itemData(compare_date_index)
            with open(compare_report_file, 'r', encoding='utf-8') as f:
                compare_data = json.load(f)

            # Hiển thị dữ liệu so sánh
            self.update_history_usage_comparison(current_data, compare_data)
            self.update_history_feed_comparison(current_data, compare_data)
            self.update_history_mix_comparison(current_data, compare_data)

            QMessageBox.information(self, "Thành công",
                f"Đã so sánh dữ liệu giữa ngày {self.history_date_combo.currentText()} và {self.compare_date_combo.currentText()}")

        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể so sánh dữ liệu: {str(e)}")

    def update_history_usage_comparison(self, current_data, compare_data):
        """Update the history usage table with comparison data"""
        if "feed_usage" not in current_data or "feed_usage" not in compare_data:
            return

        # Populate table with farms and khu information
        col_index = 0  # Bắt đầu từ cột 0 vì đã bỏ cột nhãn
        for khu_idx, farms in FARMS.items():
            khu_name = f"Khu {khu_idx + 1}"

            for farm_idx, farm in enumerate(farms):
                # Set khu label in first row
                self.history_usage_table.setItem(0, col_index, QTableWidgetItem(khu_name))

                # Set farm name in second row
                self.history_usage_table.setItem(1, col_index, QTableWidgetItem(farm))

                # Fill in usage data for each shift
                for shift_idx, shift in enumerate(SHIFTS):
                    # Try to get the usage value from the current data
                    try:
                        current_usage = current_data["feed_usage"][khu_name][farm][shift]
                        item = QTableWidgetItem(format_number(current_usage))
                    except (KeyError, TypeError):
                        current_usage = 0

                    # Try to get the usage value from the compare data
                    try:
                        compare_usage = compare_data["feed_usage"][khu_name][farm][shift]
                    except (KeyError, TypeError):
                        compare_usage = 0

                    # Calculate difference
                    diff = current_usage - compare_usage

                    # Create item with the current usage value
                    item = QTableWidgetItem(format_number(current_usage))

                    # Set color based on difference
                    if diff > 0:
                        item.setForeground(QColor(0, 128, 0))  # Green for increase
                    elif diff < 0:
                        item.setForeground(QColor(255, 0, 0))  # Red for decrease

                    # Add tooltip with comparison information
                    item.setToolTip(f"Hiện tại: {format_number(current_usage)}, So sánh: {format_number(compare_usage)}, Chênh lệch: {format_number(diff)}")

                    self.history_usage_table.setItem(shift_idx + 2, col_index, item)

                col_index += 1

        # Stretch columns to fill available space
        self.history_usage_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def update_history_feed_comparison(self, current_data, compare_data):
        """Update the history feed ingredients table with comparison data"""
        if "feed_ingredients" not in current_data or "feed_ingredients" not in compare_data:
            return

        # Chuẩn bị dữ liệu cho bảng so sánh
        table_data = []

        # Gộp tất cả các thành phần
        all_ingredients = set(current_data["feed_ingredients"].keys()) | set(compare_data["feed_ingredients"].keys())

        # Tính tổng lượng
        current_total = 0
        compare_total = 0
        current_total_bags = 0
        compare_total_bags = 0

        # Tạo dữ liệu so sánh
        for ingredient in all_ingredients:
            current_val = current_data["feed_ingredients"].get(ingredient, 0)
            compare_val = compare_data["feed_ingredients"].get(ingredient, 0)
            diff = current_val - compare_val

            # Tính số bao
            current_bags = self.inventory_manager.calculate_bags(ingredient, current_val)
            compare_bags = self.inventory_manager.calculate_bags(ingredient, compare_val)
            bags_diff = current_bags - compare_bags

            table_data.append((ingredient, current_val, compare_val, diff, current_bags, compare_bags, bags_diff))

            # Cộng vào tổng
            current_total += current_val
            compare_total += compare_val
            current_total_bags += current_bags
            compare_total_bags += compare_bags

        # Sắp xếp theo lượng sử dụng hiện tại (giảm dần)
        table_data.sort(key=lambda x: x[1], reverse=True)

        # Cập nhật bảng
        self.history_feed_table.setColumnCount(7)  # Thành phần, Hiện tại (kg), So sánh (kg), Chênh lệch (kg), Hiện tại (bao), So sánh (bao), Chênh lệch (bao)
        self.history_feed_table.setHorizontalHeaderLabels([
            "Thành phần",
            f"Hiện tại (kg)",
            f"So sánh (kg)",
            "Chênh lệch (kg)",
            f"Hiện tại (bao)",
            f"So sánh (bao)",
            "Chênh lệch (bao)"
        ])
        self.history_feed_table.setRowCount(len(table_data) + 1)  # +1 cho hàng tổng cộng

        for row, (ingredient, current_val, compare_val, diff, current_bags, compare_bags, bags_diff) in enumerate(table_data):
            self.history_feed_table.setItem(row, 0, QTableWidgetItem(ingredient))
            self.history_feed_table.setItem(row, 1, QTableWidgetItem(format_number(current_val)))
            self.history_feed_table.setItem(row, 2, QTableWidgetItem(format_number(compare_val)))

            # Hiển thị chênh lệch kg với màu sắc
            diff_item = QTableWidgetItem(format_number(diff))
            if diff > 0:
                diff_item.setForeground(QColor(0, 128, 0))  # Màu xanh lá cho tăng
            elif diff < 0:
                diff_item.setForeground(QColor(255, 0, 0))  # Màu đỏ cho giảm

            self.history_feed_table.setItem(row, 3, diff_item)

            # Hiển thị số bao
            self.history_feed_table.setItem(row, 4, QTableWidgetItem(format_number(current_bags)))
            self.history_feed_table.setItem(row, 5, QTableWidgetItem(format_number(compare_bags)))

            # Hiển thị chênh lệch bao với màu sắc
            bags_diff_item = QTableWidgetItem(format_number(bags_diff))
            if bags_diff > 0:
                bags_diff_item.setForeground(QColor(0, 128, 0))  # Màu xanh lá cho tăng
            elif bags_diff < 0:
                bags_diff_item.setForeground(QColor(255, 0, 0))  # Màu đỏ cho giảm

            self.history_feed_table.setItem(row, 6, bags_diff_item)

        # Thêm hàng tổng cộng
        total_row = len(table_data)
        total_item = QTableWidgetItem("Tổng lượng Cám")
        total_item.setFont(QFont("Arial", weight=QFont.Bold))
        self.history_feed_table.setItem(total_row, 0, total_item)

        # Hiển thị tổng lượng hiện tại
        current_total_item = QTableWidgetItem(format_number(current_total))
        current_total_item.setFont(QFont("Arial", weight=QFont.Bold))
        current_total_item.setBackground(QColor(200, 230, 250))  # Light blue background
        self.history_feed_table.setItem(total_row, 1, current_total_item)

        # Hiển thị tổng lượng so sánh
        compare_total_item = QTableWidgetItem(format_number(compare_total))
        compare_total_item.setFont(QFont("Arial", weight=QFont.Bold))
        compare_total_item.setBackground(QColor(200, 230, 250))  # Light blue background
        self.history_feed_table.setItem(total_row, 2, compare_total_item)

        # Hiển thị chênh lệch tổng lượng
        total_diff = current_total - compare_total
        total_diff_item = QTableWidgetItem(format_number(total_diff))
        total_diff_item.setFont(QFont("Arial", weight=QFont.Bold))
        total_diff_item.setBackground(QColor(200, 230, 250))  # Light blue background
        if total_diff > 0:
            total_diff_item.setForeground(QColor(0, 128, 0))  # Màu xanh lá cho tăng
        elif total_diff < 0:
            total_diff_item.setForeground(QColor(255, 0, 0))  # Màu đỏ cho giảm
        self.history_feed_table.setItem(total_row, 3, total_diff_item)

        # Hiển thị tổng số bao hiện tại
        current_total_bags_item = QTableWidgetItem(format_number(current_total_bags))
        current_total_bags_item.setFont(QFont("Arial", weight=QFont.Bold))
        current_total_bags_item.setBackground(QColor(200, 230, 250))  # Light blue background
        self.history_feed_table.setItem(total_row, 4, current_total_bags_item)

        # Hiển thị tổng số bao so sánh
        compare_total_bags_item = QTableWidgetItem(format_number(compare_total_bags))
        compare_total_bags_item.setFont(QFont("Arial", weight=QFont.Bold))
        compare_total_bags_item.setBackground(QColor(200, 230, 250))  # Light blue background
        self.history_feed_table.setItem(total_row, 5, compare_total_bags_item)

        # Hiển thị chênh lệch tổng số bao
        total_bags_diff = current_total_bags - compare_total_bags
        total_bags_diff_item = QTableWidgetItem(format_number(total_bags_diff))
        total_bags_diff_item.setFont(QFont("Arial", weight=QFont.Bold))
        total_bags_diff_item.setBackground(QColor(200, 230, 250))  # Light blue background
        if total_bags_diff > 0:
            total_bags_diff_item.setForeground(QColor(0, 128, 0))  # Màu xanh lá cho tăng
        elif total_bags_diff < 0:
            total_bags_diff_item.setForeground(QColor(255, 0, 0))  # Màu đỏ cho giảm
        self.history_feed_table.setItem(total_row, 6, total_bags_diff_item)

    def update_history_mix_comparison(self, current_data, compare_data):
        """Update the history mix ingredients table with comparison data"""
        if "mix_ingredients" not in current_data or "mix_ingredients" not in compare_data:
            return

        # Get linked mix formula names if available
        current_linked_mix = current_data.get("linked_mix_formula", "")
        compare_linked_mix = compare_data.get("linked_mix_formula", "")

        # Set title with linked formula info
        mix_title = "Thành Phần Mix"
        if current_linked_mix and compare_linked_mix:
            if current_linked_mix == compare_linked_mix:
                mix_title += f" ({current_linked_mix})"
            else:
                mix_title += f" ({current_linked_mix} vs {compare_linked_mix})"
        elif current_linked_mix:
            mix_title += f" ({current_linked_mix} vs Không có)"
        elif compare_linked_mix:
            mix_title += f" (Không có vs {compare_linked_mix})"

        self.history_tabs.setTabText(2, mix_title)

        # Chuẩn bị dữ liệu cho bảng so sánh
        table_data = []

        # Gộp tất cả các thành phần
        all_ingredients = set(current_data["mix_ingredients"].keys()) | set(compare_data["mix_ingredients"].keys())

        # Tính tổng lượng
        current_total = 0
        compare_total = 0
        current_total_bags = 0
        compare_total_bags = 0

        # Tạo dữ liệu so sánh
        for ingredient in all_ingredients:
            current_val = current_data["mix_ingredients"].get(ingredient, 0)
            compare_val = compare_data["mix_ingredients"].get(ingredient, 0)
            diff = current_val - compare_val

            # Tính số bao
            current_bags = self.inventory_manager.calculate_bags(ingredient, current_val)
            compare_bags = self.inventory_manager.calculate_bags(ingredient, compare_val)
            bags_diff = current_bags - compare_bags

            table_data.append((ingredient, current_val, compare_val, diff, current_bags, compare_bags, bags_diff))

            # Cộng vào tổng
            current_total += current_val
            compare_total += compare_val
            current_total_bags += current_bags
            compare_total_bags += compare_bags

        # Sắp xếp theo lượng sử dụng hiện tại (giảm dần)
        table_data.sort(key=lambda x: x[1], reverse=True)

        # Cập nhật bảng
        self.history_mix_table.setColumnCount(7)  # Thành phần, Hiện tại (kg), So sánh (kg), Chênh lệch (kg), Hiện tại (bao), So sánh (bao), Chênh lệch (bao)
        self.history_mix_table.setHorizontalHeaderLabels([
            "Thành phần",
            f"Hiện tại (kg)",
            f"So sánh (kg)",
            "Chênh lệch (kg)",
            f"Hiện tại (bao)",
            f"So sánh (bao)",
            "Chênh lệch (bao)"
        ])
        self.history_mix_table.setRowCount(len(table_data) + 1)  # +1 cho hàng tổng cộng

        for row, (ingredient, current_val, compare_val, diff, current_bags, compare_bags, bags_diff) in enumerate(table_data):
            self.history_mix_table.setItem(row, 0, QTableWidgetItem(ingredient))
            self.history_mix_table.setItem(row, 1, QTableWidgetItem(format_number(current_val)))
            self.history_mix_table.setItem(row, 2, QTableWidgetItem(format_number(compare_val)))

            # Hiển thị chênh lệch kg với màu sắc
            diff_item = QTableWidgetItem(format_number(diff))
            if diff > 0:
                diff_item.setForeground(QColor(0, 128, 0))  # Màu xanh lá cho tăng
            elif diff < 0:
                diff_item.setForeground(QColor(255, 0, 0))  # Màu đỏ cho giảm

            self.history_mix_table.setItem(row, 3, diff_item)

            # Hiển thị số bao
            self.history_mix_table.setItem(row, 4, QTableWidgetItem(format_number(current_bags)))
            self.history_mix_table.setItem(row, 5, QTableWidgetItem(format_number(compare_bags)))

            # Hiển thị chênh lệch bao với màu sắc
            bags_diff_item = QTableWidgetItem(format_number(bags_diff))
            if bags_diff > 0:
                bags_diff_item.setForeground(QColor(0, 128, 0))  # Màu xanh lá cho tăng
            elif bags_diff < 0:
                bags_diff_item.setForeground(QColor(255, 0, 0))  # Màu đỏ cho giảm

            self.history_mix_table.setItem(row, 6, bags_diff_item)

        # Thêm hàng tổng cộng
        total_row = len(table_data)
        total_item = QTableWidgetItem("Tổng lượng Mix")
        total_item.setFont(QFont("Arial", weight=QFont.Bold))
        self.history_mix_table.setItem(total_row, 0, total_item)

        # Hiển thị tổng lượng hiện tại
        current_total_item = QTableWidgetItem(format_number(current_total))
        current_total_item.setFont(QFont("Arial", weight=QFont.Bold))
        current_total_item.setBackground(QColor(230, 250, 200))  # Light green background
        self.history_mix_table.setItem(total_row, 1, current_total_item)

        # Hiển thị tổng lượng so sánh
        compare_total_item = QTableWidgetItem(format_number(compare_total))
        compare_total_item.setFont(QFont("Arial", weight=QFont.Bold))
        compare_total_item.setBackground(QColor(230, 250, 200))  # Light green background
        self.history_mix_table.setItem(total_row, 2, compare_total_item)

        # Hiển thị chênh lệch tổng lượng
        total_diff = current_total - compare_total
        total_diff_item = QTableWidgetItem(format_number(total_diff))
        total_diff_item.setFont(QFont("Arial", weight=QFont.Bold))
        total_diff_item.setBackground(QColor(230, 250, 200))  # Light green background
        if total_diff > 0:
            total_diff_item.setForeground(QColor(0, 128, 0))  # Màu xanh lá cho tăng
        elif total_diff < 0:
            total_diff_item.setForeground(QColor(255, 0, 0))  # Màu đỏ cho giảm
        self.history_mix_table.setItem(total_row, 3, total_diff_item)

        # Hiển thị tổng số bao hiện tại
        current_total_bags_item = QTableWidgetItem(format_number(current_total_bags))
        current_total_bags_item.setFont(QFont("Arial", weight=QFont.Bold))
        current_total_bags_item.setBackground(QColor(230, 250, 200))  # Light green background
        self.history_mix_table.setItem(total_row, 4, current_total_bags_item)

        # Hiển thị tổng số bao so sánh
        compare_total_bags_item = QTableWidgetItem(format_number(compare_total_bags))
        compare_total_bags_item.setFont(QFont("Arial", weight=QFont.Bold))
        compare_total_bags_item.setBackground(QColor(230, 250, 200))  # Light green background
        self.history_mix_table.setItem(total_row, 5, compare_total_bags_item)

        # Hiển thị chênh lệch tổng số bao
        total_bags_diff = current_total_bags - compare_total_bags
        total_bags_diff_item = QTableWidgetItem(format_number(total_bags_diff))
        total_bags_diff_item.setFont(QFont("Arial", weight=QFont.Bold))
        total_bags_diff_item.setBackground(QColor(230, 250, 200))  # Light green background
        if total_bags_diff > 0:
            total_bags_diff_item.setForeground(QColor(0, 128, 0))  # Màu xanh lá cho tăng
        elif total_bags_diff < 0:
            total_bags_diff_item.setForeground(QColor(255, 0, 0))  # Màu đỏ cho giảm
        self.history_mix_table.setItem(total_row, 6, total_bags_diff_item)

    def export_history_to_excel(self):
        """Export historical data for the selected date to Excel"""
        current_index = self.history_date_combo.currentIndex()
        if current_index < 0:
            QMessageBox.warning(self, "Lỗi", "Không có dữ liệu lịch sử để xuất Excel.")
            return

        report_file = self.history_date_combo.itemData(current_index)
        if not report_file:
            QMessageBox.warning(self, "Lỗi", "Không tìm thấy file báo cáo.")
            return

        try:
            # Load report data
            with open(report_file, 'r', encoding='utf-8') as f:
                report_data = json.load(f)

            # Create reports directory if it doesn't exist
            reports_dir = "reports"
            if not os.path.exists(reports_dir):
                os.makedirs(reports_dir)

            # Get base filename without extension and directory
            base_filename = os.path.splitext(os.path.basename(report_file))[0]
            excel_filename = os.path.join(reports_dir, f"{base_filename}_history.xlsx")

            # Create a pandas ExcelWriter object
            writer = pd.ExcelWriter(excel_filename, engine='openpyxl')

            # Create feed usage by khu dataframe
            khu_data = []
            for khu_idx in range(AREAS):
                khu_name = f"Khu {khu_idx + 1}"
                row_data = {"Khu": khu_name}

                # Calculate total for each shift in this khu
                for shift_idx, shift in enumerate(SHIFTS):
                    total = 0
                    farms = FARMS.get(khu_idx, [])

                    # If this khu has farms, sum up their values
                    if farms:
                        col_start = 0 # Bắt đầu từ cột 0 vì đã bỏ cột nhãn
                        for prev_khu_idx in range(khu_idx):
                            col_start += len(FARMS.get(prev_khu_idx, []))

                        for farm_idx in range(len(farms)):
                            col = col_start + farm_idx
                            spin_box = self.feed_table.cellWidget(shift_idx + 2, col)
                            if spin_box:
                                total += spin_box.value()

                    row_data[shift] = total

                khu_data.append(row_data)

            khu_df = pd.DataFrame(khu_data)

            # Create feed usage by farm dataframe
            farm_data = []
            col_index = 0 # Bắt đầu từ cột 0 vì đã bỏ cột nhãn
            for khu_idx, farms in FARMS.items():
                khu_name = f"Khu {khu_idx + 1}"

                for farm in farms:
                    row_data = {"Khu": khu_name, "Trại": farm}

                    for shift_idx, shift in enumerate(SHIFTS):
                        spin_box = self.feed_table.cellWidget(shift_idx + 2, col_index)
                        if spin_box:
                            row_data[shift] = spin_box.value()

                    farm_data.append(row_data)
                    col_index += 1

            farm_df = pd.DataFrame(farm_data)

            # Tính tổng số mẻ
            total_batches = 0
            for row in farm_data:
                total_batches += sum([row[shift] for shift in SHIFTS])

            # Tính toán thành phần cám sử dụng (không bao gồm mix)
            feed_ingredients_data = []
            for ingredient, amount_per_batch in self.feed_formula.items():
                if ingredient != "Nguyên liệu tổ hợp":
                    amount = amount_per_batch * total_batches
                    bags = self.inventory_manager.calculate_bags(ingredient, amount)
                    feed_ingredients_data.append({
                        "Thành phần": ingredient,
                        "Số lượng (kg)": amount,
                        "Số bao": bags
                    })

            feed_ingredients_df = pd.DataFrame(feed_ingredients_data)

            # Tính toán thành phần mix sử dụng
            mix_ingredients_data = []
            for ingredient, amount_per_batch in self.mix_formula.items():
                amount = amount_per_batch * total_batches
                bags = self.inventory_manager.calculate_bags(ingredient, amount)
                mix_ingredients_data.append({
                    "Thành phần": ingredient,
                    "Số lượng (kg)": amount,
                    "Số bao": bags
                })

            mix_ingredients_df = pd.DataFrame(mix_ingredients_data)

            # Write to Excel
            khu_df.to_excel(writer, sheet_name='Sử dụng Cám theo Khu', index=False)
            farm_df.to_excel(writer, sheet_name='Sử dụng Cám theo Trại', index=False)
            feed_ingredients_df.to_excel(writer, sheet_name='Thành phần Kho Cám', index=False)
            mix_ingredients_df.to_excel(writer, sheet_name='Thành phần Kho Mix', index=False)

            # Save the Excel file
            writer.close()

            QMessageBox.information(self, "Thành công", f"Đã xuất dữ liệu lịch sử vào file {excel_filename}!")

        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể xuất dữ liệu lịch sử: {str(e)}")

    def update_mix_link_combo(self):
        """Update the combo box to show available mix formulas."""
        self.mix_link_combo.clear()

        # Add "Không có công thức" option
        self.mix_link_combo.addItem("Không có công thức", "")

        # Get all mix formulas
        all_mix_formulas = self.formula_manager.get_mix_presets()
        for formula_name in all_mix_formulas:
            self.mix_link_combo.addItem(formula_name, formula_name)

        # Set current linked formula if any
        current_preset = self.feed_preset_combo.currentText()
        linked_formula = ""

        if current_preset:
            # Nếu đang xem một preset, lấy liên kết cho preset đó
            linked_formula = self.formula_manager.get_linked_mix_formula_name(current_preset)
        else:
            # Nếu đang xem công thức hiện tại, lấy liên kết hiện tại
            linked_formula = self.formula_manager.get_linked_mix_formula_name()

        if linked_formula:
            index = self.mix_link_combo.findData(linked_formula)
            if index >= 0:
                self.mix_link_combo.setCurrentIndex(index)

    def set_mix_formula_link(self):
        """Set the selected mix formula as the link for the 'Nguyên liệu tổ hợp' in the feed formula."""
        selected_mix_formula_name = self.mix_link_combo.currentData()
        current_preset = self.feed_preset_combo.currentText()

        if current_preset:
            # Nếu đang xem một preset, lưu liên kết cho preset đó
            if not selected_mix_formula_name:
                # Clear link
                self.formula_manager.set_linked_mix_formula("", current_preset)
                QMessageBox.information(self, "Thành công", f"Đã xóa liên kết công thức Mix cho Nguyên liệu tổ hợp trong công thức '{current_preset}'.")
            else:
                # Set the link to the selected mix formula
                self.formula_manager.set_linked_mix_formula(selected_mix_formula_name, current_preset)
                QMessageBox.information(self, "Thành công", f"Đã gắn công thức Mix '{selected_mix_formula_name}' cho Nguyên liệu tổ hợp trong công thức '{current_preset}'.")
        else:
            # Nếu đang xem công thức hiện tại, lưu liên kết hiện tại
            if not selected_mix_formula_name:
                # Clear link
                self.formula_manager.set_linked_mix_formula("")
                QMessageBox.information(self, "Thành công", "Đã xóa liên kết công thức Mix cho Nguyên liệu tổ hợp.")
            else:
                # Set the link to the selected mix formula
                self.formula_manager.set_linked_mix_formula(selected_mix_formula_name)
                QMessageBox.information(self, "Thành công", f"Đã gắn công thức Mix '{selected_mix_formula_name}' cho Nguyên liệu tổ hợp.")

        # Update the feed formula table to show the linked mix formula
        self.update_feed_formula_table()

    def update_feed_preset(self):
        """Cập nhật công thức cám đã lưu"""
        preset_name = self.feed_preset_combo.currentText()
        if not preset_name:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn một công thức để cập nhật")
            return

        try:
            # Lưu công thức hiện tại
            updated_formula = {}

            # Duyệt qua các hàng trong bảng
            for row in range(self.feed_formula_table.rowCount()):
                # Bỏ qua nếu không có item ở cột 0
                if self.feed_formula_table.item(row, 0) is None:
                    continue

                # Lấy tên thành phần
                ingredient = self.feed_formula_table.item(row, 0).text()

                # Kiểm tra xem hàng hiện tại có phải là hàng tổng cộng không
                if ingredient == "Tổng lượng Cám":
                    continue  # Bỏ qua hàng tổng cộng

                # Loại bỏ phần "(Gắn với: ...)" nếu có
                if " (Gắn với: " in ingredient:
                    ingredient = ingredient.split(" (Gắn với: ")[0]

                # Lấy giá trị
                try:
                    # Thử lấy giá trị từ spin box
                    amount_spin = self.feed_formula_table.cellWidget(row, 1)
                    if amount_spin is not None:
                        amount = amount_spin.value()
                    else:
                        # Nếu không có spin box, thử lấy giá trị từ item
                        item = self.feed_formula_table.item(row, 1)
                        if item is not None:
                            amount = float(item.text().replace(',', '.'))
                        else:
                            # Nếu không có item, sử dụng giá trị từ công thức hiện tại
                            amount = self.feed_formula.get(ingredient, 0)

                    # Đối với Nguyên liệu tổ hợp, lưu giá trị gốc nếu có công thức mix được gắn
                    if ingredient == "Nguyên liệu tổ hợp":
                        linked_mix_name = self.formula_manager.get_linked_mix_formula_name(preset_name)
                        if linked_mix_name:
                            # Nếu có công thức mix được gắn, lưu giá trị gốc
                            preset_formula = self.formula_manager.load_feed_preset(preset_name)
                            if "Nguyên liệu tổ hợp" in preset_formula:
                                amount = preset_formula["Nguyên liệu tổ hợp"]

                    updated_formula[ingredient] = amount
                except Exception as e:
                    print(f"Lỗi khi xử lý thành phần {ingredient}: {e}")

            # Cập nhật preset
            if self.formula_manager.save_preset("feed", preset_name, updated_formula):
                # Cập nhật công thức hiện tại
                self.formula_manager.set_feed_formula(updated_formula)
                self.feed_formula = updated_formula

                # Cập nhật lại bảng
                self.update_feed_formula_table()

                QMessageBox.information(self, "Thành công", f"Đã cập nhật công thức cám '{preset_name}'")
            else:
                QMessageBox.warning(self, "Lỗi", f"Không thể cập nhật công thức cám '{preset_name}'")
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể cập nhật công thức cám: {str(e)}")
            # In thông tin lỗi ra console để debug
            import traceback
            traceback.print_exc()

    def update_mix_preset(self):
        """Cập nhật công thức mix đã lưu"""
        preset_name = self.mix_preset_combo.currentText()
        if not preset_name:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn một công thức để cập nhật")
            return

        try:
            # Lưu công thức hiện tại
            updated_formula = {}

            # Duyệt qua các hàng trong bảng
            for row in range(self.mix_formula_table.rowCount()):
                # Bỏ qua nếu không có item ở cột 0
                if self.mix_formula_table.item(row, 0) is None:
                    continue

                # Lấy tên thành phần
                ingredient = self.mix_formula_table.item(row, 0).text()

                # Kiểm tra xem hàng hiện tại có phải là hàng tổng cộng không
                if ingredient == "Tổng lượng Mix":
                    continue  # Bỏ qua hàng tổng cộng

                # Lấy giá trị
                try:
                    # Thử lấy giá trị từ spin box
                    amount_spin = self.mix_formula_table.cellWidget(row, 1)
                    if amount_spin is not None:
                        amount = amount_spin.value()
                    else:
                        # Nếu không có spin box, thử lấy giá trị từ item
                        item = self.mix_formula_table.item(row, 1)
                        if item is not None:
                            amount = float(item.text().replace(',', '.'))
                        else:
                            # Nếu không có item, sử dụng giá trị từ công thức hiện tại
                            amount = self.mix_formula.get(ingredient, 0)

                    updated_formula[ingredient] = amount
                except Exception as e:
                    print(f"Lỗi khi xử lý thành phần {ingredient}: {e}")

            # Cập nhật preset
            if self.formula_manager.save_preset("mix", preset_name, updated_formula):
                # Cập nhật công thức hiện tại
                self.formula_manager.set_mix_formula(updated_formula)
                self.mix_formula = updated_formula

                # Cập nhật lại bảng
                self.update_mix_formula_table()

                QMessageBox.information(self, "Thành công", f"Đã cập nhật công thức mix '{preset_name}'")
            else:
                QMessageBox.warning(self, "Lỗi", f"Không thể cập nhật công thức mix '{preset_name}'")
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể cập nhật công thức mix: {str(e)}")
            # In thông tin lỗi ra console để debug
            import traceback
            traceback.print_exc()

    # Thêm phương thức auto_load_feed_preset để tự động tải công thức cám khi chọn
    def auto_load_feed_preset(self, index):
        """Tự động tải công thức cám khi chọn từ combo box"""
        if index < 0:
            return

        preset_name = self.feed_preset_combo.currentText()
        if not preset_name:
            return

        preset_formula = self.formula_manager.load_feed_preset(preset_name)
        if preset_formula:
            self.formula_manager.set_feed_formula(preset_formula)
            self.feed_formula = preset_formula
            self.update_feed_formula_table()

            # Cập nhật combo box liên kết mix để hiển thị liên kết cho preset này
            self.update_mix_link_combo()

    # Thêm phương thức auto_load_mix_preset để tự động tải công thức mix khi chọn
    def auto_load_mix_preset(self, index):
        """Tự động tải công thức mix khi chọn từ combo box"""
        if index < 0:
            return

        preset_name = self.mix_preset_combo.currentText()
        if not preset_name:
            return

        preset_formula = self.formula_manager.load_mix_preset(preset_name)
        if preset_formula:
            self.formula_manager.set_mix_formula(preset_formula)
            self.mix_formula = preset_formula
            self.update_mix_formula_table()

def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(create_app_icon())
    window = ChickenFarmApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()