import sys
import os
import json
import subprocess
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout,
                            QHBoxLayout, QGridLayout, QLabel, QLineEdit, QPushButton,
                            QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
                            QMessageBox, QFileDialog, QSpinBox, QDoubleSpinBox, QInputDialog,
                            QGroupBox, QDialog, QRadioButton, QDateEdit, QScrollArea, QSizePolicy,
                            QMenu, QAction, QAbstractSpinBox)
from PyQt5.QtCore import Qt, QDate, QTimer
from PyQt5.QtGui import QFont, QColor, QCursor

# Kiểm tra xem đang chạy từ thư mục gốc hay từ thư mục src
try:
    from src.core.formula_manager import FormulaManager
    from src.core.inventory_manager import InventoryManager
    from src.utils.default_formulas import PACKAGING_INFO
    from src.utils.app_icon import create_app_icon
except ImportError:
    # Nếu không import được từ src, thử import trực tiếp
    from core.formula_manager import FormulaManager
    from core.inventory_manager import InventoryManager
    from utils.default_formulas import PACKAGING_INFO
    from utils.app_icon import create_app_icon

# Constants
AREAS = 5  # Number of areas
SHIFTS = ["Sáng", "Chiều"]  # Morning and afternoon shifts

# Định nghĩa các trại cho từng khu
FARMS = {
    0: ["T1", "T2", "T4", "T6"],          # Khu 1
    1: ["T1", "T2", "T4", "T6"],          # Khu 2
    2: ["1D", "2D", "4D", "2N"],          # Khu 3
    3: ["T2", "T4", "T6", "T8", "Trại 1 khu 4"],  # Khu 4
    4: [""]                           # Khu 5
}

# Thiết lập font mặc định cho toàn bộ ứng dụng
DEFAULT_FONT_SIZE = 14  # Tăng kích thước font mặc định
DEFAULT_FONT = QFont("Arial", DEFAULT_FONT_SIZE)
HEADER_FONT = QFont("Arial", DEFAULT_FONT_SIZE + 2, QFont.Bold)
BUTTON_FONT = QFont("Arial", DEFAULT_FONT_SIZE, QFont.Bold)
TABLE_HEADER_FONT = QFont("Arial", DEFAULT_FONT_SIZE + 1, QFont.Bold)  # Tăng kích thước font header trong bảng
TABLE_CELL_FONT = QFont("Arial", DEFAULT_FONT_SIZE)

# Helper function to format numbers (display with thousands separator, max 2 decimal places, and remove trailing zeros)
def format_number(value):
    """Format a number with thousands separator, max 2 decimal places, and remove trailing zeros"""
    # Nếu giá trị là 0, trả về chuỗi rỗng
    if value == 0:
        return ""

    if value == int(value):
        # Nếu là số nguyên, hiển thị không có phần thập phân và thêm dấu phẩy ngăn cách hàng nghìn
        return f"{int(value):,}"
    else:
        # Làm tròn đến 2 chữ số thập phân
        rounded_value = round(value, 2)

        # Định dạng với dấu phẩy ngăn cách hàng nghìn
        formatted = f"{rounded_value:,.2f}"

        # Tách phần nguyên và phần thập phân
        parts = formatted.split('.')
        if len(parts) == 2:
            # Loại bỏ số 0 thừa ở cuối phần thập phân
            decimal_part = parts[1].rstrip('0')
            if decimal_part:
                return f"{parts[0]}.{decimal_part}"
            else:
                return parts[0]
        return formatted

# Custom QDoubleSpinBox để định dạng số theo yêu cầu
class CustomDoubleSpinBox(QDoubleSpinBox):
    def textFromValue(self, value):
        """Định dạng số với dấu phẩy ngăn cách hàng nghìn, tối đa 2 chữ số thập phân và loại bỏ số 0 thừa ở cuối"""
        # Nếu giá trị là 0, trả về chuỗi rỗng thay vì số 0
        if value == 0:
            return ""
        return format_number(value)

    def valueFromText(self, text):
        """Chuyển đổi từ chuỗi có định dạng về số"""
        # Loại bỏ dấu phẩy ngăn cách hàng nghìn
        text = text.replace(',', '')
        return float(text)

class ChickenFarmApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Phần mềm Quản lý Cám - Trại Gà")

        # Biến cờ để kiểm soát việc tải báo cáo
        self.report_loaded = False
        self.default_formula_loaded = False



        # Lấy kích thước màn hình
        desktop = QApplication.desktop()
        screen_rect = desktop.availableGeometry()
        screen_width = screen_rect.width()
        screen_height = screen_rect.height()

        # Tính toán kích thước cửa sổ (95% kích thước màn hình)
        window_width = int(screen_width * 0.95)
        window_height = int(screen_height * 0.95)

        # Tính toán vị trí để cửa sổ xuất hiện ở giữa màn hình
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2

        # Thiết lập kích thước và vị trí cửa sổ
        self.setGeometry(x_position, y_position, window_width, window_height)

        # Set application icon
        self.setWindowIcon(create_app_icon())

        # Thiết lập style cho toàn bộ ứng dụng
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background: white;
                border-radius: 5px;
            }
            QTabBar::tab {
                background: #f0f0f0;
                border: 1px solid #cccccc;
                border-bottom-color: #cccccc;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 10px 15px;
                margin-right: 2px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: #4CAF50;
                color: white;
            }
            QTabBar::tab:!selected {
                margin-top: 2px;
            }
            QLabel {
                color: #333333;
            }
            QMessageBox {
                background-color: #ffffff;
            }
            QMessageBox QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 4px;
                padding: 5px 15px;
                min-width: 80px;
                min-height: 25px;
            }
            QMessageBox QPushButton:hover {
                background-color: #45a000;
            }
        """)

        # Initialize managers
        self.formula_manager = FormulaManager()
        self.inventory_manager = InventoryManager()

        # Get formulas and inventory data
        self.feed_formula = self.formula_manager.get_feed_formula()
        self.mix_formula = self.formula_manager.get_mix_formula()
        self.inventory = self.inventory_manager.get_inventory()

        # Tải công thức mix theo cột từ file cấu hình
        self.column_mix_formulas = self.formula_manager.column_mix_formulas

        # Thiết lập stylesheet chung cho spinbox
        self.setStyleSheet(self.styleSheet() + """
            QDoubleSpinBox {
                border: none;  /* Bỏ viền */
                background-color: white;
            }
        """)

        # Áp dụng font mặc định cho toàn bộ ứng dụng
        self.setFont(DEFAULT_FONT)

        # Initialize UI
        self.init_ui()

        # Tự động tải báo cáo mới nhất khi khởi động
        QTimer.singleShot(100, self.load_latest_report)

    def init_ui(self):
        """Initialize the main UI components"""
        # Create main tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background: white;
                border-radius: 5px;
            }
            QTabWidget::tab-bar {
                left: 5px;
            }
            QTabBar::tab {
                background: #f0f0f0;
                border: 1px solid #cccccc;
                border-bottom-color: #cccccc;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 10px 20px;
                margin-right: 5px;
                font-weight: bold;
                min-width: 120px;
                font-size: 12pt;
            }
            QTabBar::tab:selected {
                background: #4CAF50;
                color: white;
            }
            QTabBar::tab:!selected {
                margin-top: 2px;
            }
        """)

        # Create tabs
        self.feed_usage_tab = QWidget()
        self.inventory_tab = QWidget()
        self.formula_tab = QWidget()
        self.history_tab = QWidget()  # Tab mới cho lịch sử

        # Add tabs to widget
        self.tabs.addTab(self.feed_usage_tab, "Tổng quan")
        self.tabs.addTab(self.inventory_tab, "Tồn Kho")
        self.tabs.addTab(self.formula_tab, "Công Thức")
        self.tabs.addTab(self.history_tab, "Lịch Sử")  # Thêm tab lịch sử

        # Khởi tạo các combobox trước khi sử dụng
        self.feed_preset_combo = QComboBox()
        self.feed_preset_combo.setFont(DEFAULT_FONT)
        self.mix_preset_combo = QComboBox()
        self.mix_preset_combo.setFont(DEFAULT_FONT)

        # Create menu bar
        self.create_menu_bar()

        # Setup each tab
        self.setup_feed_usage_tab()
        self.setup_inventory_tab()
        self.setup_formula_tab()
        self.setup_history_tab()  # Thiết lập tab lịch sử

        # Tải công thức mặc định và tải báo cáo mới nhất khi khởi động
        QTimer.singleShot(200, self.load_default_formula)
        QTimer.singleShot(500, self.load_latest_report)

    def create_menu_bar(self):
        """Create the menu bar"""
        menu_bar = self.menuBar()
        menu_bar.setStyleSheet("""
            QMenuBar {
                background-color: #4CAF50;
                color: white;
                padding: 5px;
                font-weight: bold;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 5px 10px;
                margin: 0px 2px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background-color: #45a049;
            }
            QMenu {
                background-color: white;
                border: 1px solid #cccccc;
            }
            QMenu::item {
                padding: 5px 25px 5px 20px;
                border: 1px solid transparent;
            }
            QMenu::item:selected {
                background-color: #e0f2f1;
                color: #333333;
            }
        """)

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
            """<h1 style="color: #4CAF50;">Phần mềm Quản lý Cám - Trại Gà</h1>
            <p style="font-size: 14px;">Phiên bản 1.0</p>
            <p style="font-size: 14px;">Phần mềm quản lý cám cho trại gà, giúp theo dõi lượng cám sử dụng hàng ngày và quản lý tồn kho.</p>
            <p style="font-size: 14px;">© 2025 Minh-Tan_Phat</p>"""
        )

    def setup_feed_usage_tab(self):
        """Setup the feed usage tab"""
        layout = QVBoxLayout()

        # Thêm tiêu đề
        header = QLabel("Báo cáo Cám")
        header.setFont(HEADER_FONT)
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("QLabel { padding: 10px; background-color: #e0f2f1; border-radius: 5px; }")
        layout.addWidget(header)

        # Thêm nhãn ngày
        date_layout = QHBoxLayout()
        date_label = QLabel(f"Ngày: {QDate.currentDate().toString('dd/MM/yyyy')}")
        date_label.setFont(QFont("Arial", DEFAULT_FONT_SIZE, QFont.Bold))
        date_layout.addWidget(date_label)
        date_layout.addStretch()

        # Thêm nút Reset
        reset_button = QPushButton("Reset Bảng")
        reset_button.setFont(BUTTON_FONT)
        reset_button.setMinimumHeight(30)
        reset_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        reset_button.clicked.connect(self.reset_feed_table)
        date_layout.addWidget(reset_button)

        layout.addLayout(date_layout)

        # Thêm combo box chọn công thức mặc định
        default_formula_layout = QHBoxLayout()
        default_formula_label = QLabel("Công thức cám mặc định:")
        default_formula_label.setFont(QFont("Arial", DEFAULT_FONT_SIZE))
        default_formula_layout.addWidget(default_formula_label)

        self.default_formula_combo = QComboBox()
        self.default_formula_combo.setFont(QFont("Arial", DEFAULT_FONT_SIZE))
        self.default_formula_combo.setMinimumWidth(200)
        self.default_formula_combo.currentIndexChanged.connect(self.apply_default_formula)

        # Thêm các công thức cám vào combo box
        feed_presets = self.formula_manager.get_feed_presets()
        for preset in feed_presets:
            self.default_formula_combo.addItem(preset)

        default_formula_layout.addWidget(self.default_formula_combo)
        default_formula_layout.addStretch()
        layout.addLayout(default_formula_layout)

        # Tạo bảng nhập liệu
        self.feed_table = QTableWidget()
        self.feed_table.setFont(TABLE_CELL_FONT)

        # Tính tổng số cột dựa trên số trại trong mỗi khu
        total_columns = sum(len(farms) for farms in FARMS.values())

        self.feed_table.setColumnCount(total_columns)
        self.feed_table.setRowCount(2 + len(SHIFTS))  # 2 hàng đầu cho khu và trại, các hàng còn lại cho các ca

        # Thiết lập header ngang
        self.feed_table.setHorizontalHeaderLabels([""] * total_columns)
        self.feed_table.horizontalHeader().setVisible(False)

        # Thiết lập header dọc
        vertical_headers = ["Khu", "Trại"] + SHIFTS
        self.feed_table.setVerticalHeaderLabels(vertical_headers)

        # Tạo các ô cho khu và trại
        col_index = 0
        for khu_idx, farms in FARMS.items():
            khu_name = f"Khu {khu_idx + 1}"

            # Tạo các ô cho khu
            for farm_idx, farm in enumerate(farms):
                khu_item = QTableWidgetItem(khu_name)
                khu_item.setTextAlignment(Qt.AlignCenter)
                khu_item.setFont(TABLE_HEADER_FONT)
                self.feed_table.setItem(0, col_index, khu_item)

                farm_item = QTableWidgetItem(farm)
                farm_item.setTextAlignment(Qt.AlignCenter)
                farm_item.setFont(TABLE_HEADER_FONT)
                self.feed_table.setItem(1, col_index, farm_item)

                col_index += 1

        # Thiết lập màu nền cho các khu
        col_index = 0
        for khu_idx, farms in FARMS.items():
            khu_colors = [
                QColor(240, 248, 255),  # Khu 1: Alice Blue
                QColor(245, 245, 220),  # Khu 2: Beige
                QColor(240, 255, 240),  # Khu 3: Honeydew
                QColor(255, 240, 245),  # Khu 4: Lavender Blush
                QColor(255, 250, 240),  # Khu 5: Floral White
            ]

            color = khu_colors[khu_idx % len(khu_colors)]

            for farm_idx in range(len(farms)):
                for row in range(self.feed_table.rowCount()):
                    if row < 2:  # Chỉ thiết lập màu nền cho hàng khu và trại
                        item = self.feed_table.item(row, col_index + farm_idx)
                        if item:
                            item.setBackground(color)
                    else:
                        # Tạo cell widget cho các ô nhập liệu
                        container = QWidget()
                        container.setStyleSheet(f"background-color: {color.name()};")

                        # Tạo spin box cho nhập số mẻ
                        spin_box = CustomDoubleSpinBox()
                        spin_box.setFont(QFont("Arial", 14))
                        spin_box.setDecimals(1)
                        spin_box.setMinimum(0)
                        spin_box.setMaximum(100)
                        spin_box.setSingleStep(0.5)
                        spin_box.setAlignment(Qt.AlignTop | Qt.AlignHCenter)  # Canh lề trên và canh giữa ngang
                        spin_box.setButtonSymbols(QAbstractSpinBox.NoButtons)  # Ẩn nút tăng/giảm
                        spin_box.setStyleSheet("""
                            QDoubleSpinBox {
                                border: none;
                                border-radius: 3px;
                                padding-top: 1px;
                                padding-bottom: 1px;
                                padding-left: 5px;
                                padding-right: 5px;
                                background-color: transparent;
                                font-weight: bold;
                            }
                        """)

                        # Tạo label hiển thị tên công thức
                        formula_label = QLabel("")
                        formula_label.setFont(QFont("Arial", 14))
                        formula_label.setAlignment(Qt.AlignCenter)
                        formula_label.setStyleSheet("color: #0277bd;")
                        formula_label.setVisible(False)  # Ban đầu ẩn label

                        # Tạo combo box chọn công thức (ẩn)
                        formula_combo = QComboBox()
                        formula_combo.setFont(QFont("Arial", 10))
                        formula_combo.setVisible(False)  # Ẩn combo box

                        # Thêm các công thức cám vào combo box
                        for preset in feed_presets:
                            formula_combo.addItem(preset)

                        # Tạo layout cho container
                        container_layout = QVBoxLayout()
                        container_layout.setContentsMargins(1, 1, 1, 1)
                        container_layout.setSpacing(0)  # Giảm khoảng cách giữa các widget

                        container.setLayout(container_layout)

                        container_layout.addWidget(spin_box)
                        container_layout.addWidget(formula_label)
                        container_layout.addWidget(formula_combo)  # Combobox ẩn

                        # Thiết lập tỷ lệ không gian
                        container_layout.setStretch(0, 60)  # 60% cho spin_box (trên)
                        container_layout.setStretch(1, 40)  # 40% cho formula_label (dưới)
                        container_layout.setStretch(2, 0)   # 0% cho formula_combo (ẩn)

                        # Lưu reference đến các widget con để truy cập sau này
                        container.spin_box = spin_box
                        container.formula_combo = formula_combo
                        container.formula_label = formula_label

                        # Khi giá trị thay đổi, cập nhật hiển thị để ẩn số 0 và tự động chọn công thức mặc định
                        def on_value_changed(value, spin=spin_box, combo=formula_combo, label=formula_label):
                            # Tự động chọn công thức mặc định
                            self.auto_select_default_formula(value, combo)

                            # Nếu giá trị là 0, hiển thị chuỗi rỗng thay vì số 0
                            if value == 0:
                                # Tạm ngắt kết nối sự kiện để tránh đệ quy
                                spin.valueChanged.disconnect()
                                # Thiết lập lại prefix để hiển thị trống thay vì "0"
                                spin.setPrefix(" " if value == 0 else "")
                                # Kết nối lại sự kiện
                                spin.valueChanged.connect(lambda v: on_value_changed(v, spin, combo, label))

                                # Ẩn label công thức
                                label.setVisible(False)
                                # Giữ số mẻ ở phía trên, để khoảng trống phía dưới
                                container.layout().setStretch(0, 60)
                                container.layout().setStretch(1, 40)
                            else:
                                # Đảm bảo prefix là trống khi có giá trị
                                if spin.prefix() != "":
                                    # Tạm ngắt kết nối sự kiện để tránh đệ quy
                                    spin.valueChanged.disconnect()
                                    # Thiết lập lại prefix để hiển thị trống
                                    spin.setPrefix("")
                                    # Kết nối lại sự kiện
                                    spin.valueChanged.connect(lambda v: on_value_changed(v, spin, combo, label))

                                # Hiển thị tên công thức
                                formula_text = combo.currentText()
                                default_formula = self.default_formula_combo.currentText()

                                # Kiểm tra xem có phải công thức mặc định không
                                if formula_text and formula_text != default_formula:
                                    # Nếu không phải công thức mặc định, hiển thị tên
                                    label.setText(formula_text)
                                    label.setVisible(True)
                                    # Giữ tỷ lệ ban đầu với số luôn ở trên
                                    container.layout().setStretch(0, 60)
                                    container.layout().setStretch(1, 40)
                                else:
                                    # Nếu là công thức mặc định hoặc không có công thức, ẩn label
                                    label.setText("")
                                    label.setVisible(False)
                                    # Giữ số mẻ ở phía trên, để khoảng trống phía dưới
                                    container.layout().setStretch(0, 60)
                                    container.layout().setStretch(1, 40)

                        # Thiết lập prefix ban đầu để ẩn số 0 nếu cần
                        if spin_box.value() == 0:
                            spin_box.setPrefix(" ")

                        # Kết nối sự kiện
                        spin_box.valueChanged.connect(lambda value, spin=spin_box, combo=formula_combo, label=formula_label: on_value_changed(value, spin, combo, label))

                        # Thêm container vào cell
                        self.feed_table.setCellWidget(row, col_index + farm_idx, container)

            col_index += len(farms)

        # Stretch columns to fill available space
        self.feed_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Tăng chiều cao của các hàng để dễ nhìn hơn
        self.feed_table.setRowHeight(0, 50)  # Tăng chiều cao hàng khu
        self.feed_table.setRowHeight(1, 50)  # Tăng chiều cao hàng trại
        for row in range(2, self.feed_table.rowCount()):
            self.feed_table.setRowHeight(row, 60)  # Tăng chiều cao hàng nhập liệu

                # Xem báo cáo button (sẽ tự động tính toán)
        view_report_button = QPushButton("Xem Báo Cáo Trong Ngày")
        view_report_button.setFont(BUTTON_FONT)
        view_report_button.setMinimumHeight(40)
        view_report_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        view_report_button.clicked.connect(self.show_daily_report)

        # Kết nối sự kiện click vào cell
        self.feed_table.cellClicked.connect(self.on_feed_table_cell_clicked)

        # Thêm bảng vào layout
        layout.addWidget(self.feed_table)

        # Thêm button chọn công thức mix theo khu
        mix_formula_button = QPushButton("Chọn Công Thức Mix Theo Khu")
        mix_formula_button.setFont(BUTTON_FONT)
        mix_formula_button.setMinimumHeight(40)
        mix_formula_button.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        mix_formula_button.clicked.connect(self.assign_mix_formulas_to_areas)

        # Tạo layout ngang cho các button
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(mix_formula_button)
        buttons_layout.addWidget(view_report_button)

        # Thêm layout buttons vào layout chính
        layout.addLayout(buttons_layout)

        # Thêm label hiển thị kết quả
        self.results_label = QLabel("Kết quả tính toán:")
        self.results_label.setFont(QFont("Arial", DEFAULT_FONT_SIZE, QFont.Bold))
        self.results_label.setVisible(False)  # Ban đầu ẩn label

        # Tạo bảng kết quả
        self.results_table = QTableWidget()
        self.results_table.setFont(TABLE_CELL_FONT)
        self.results_table.setColumnCount(3)
        self.results_table.setHorizontalHeaderLabels(["Thành phần", "Số lượng (kg)", "Số bao"])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.results_table.setVisible(False)  # Ban đầu ẩn bảng

        # Lưu dữ liệu kết quả để sử dụng khi lưu báo cáo
        self.results_data = {}

        layout.addWidget(self.results_label)
        layout.addWidget(self.results_table)

        # Không cần nút lưu báo cáo và xuất Excel ở đây nữa, đã chuyển vào popup

        self.feed_usage_tab.setLayout(layout)

    def reset_feed_table(self):
        """Xóa toàn bộ dữ liệu trong bảng điền mẻ cám"""
        # Hiển thị hộp thoại xác nhận
        reply = QMessageBox.question(
            self,
            "Xác nhận reset",
            "Bạn có chắc chắn muốn xóa toàn bộ dữ liệu đã nhập trong bảng không?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Xóa dữ liệu trong bảng
            for col in range(self.feed_table.columnCount()):
                for row in range(2, self.feed_table.rowCount()):
                    cell_widget = self.feed_table.cellWidget(row, col)
                    if cell_widget and hasattr(cell_widget, 'spin_box'):
                        cell_widget.spin_box.setValue(0)
                    if cell_widget and hasattr(cell_widget, 'formula_combo'):
                        cell_widget.formula_combo.setCurrentText("")

            # Xóa dữ liệu công thức mix cho từng ô
            if hasattr(self, 'cell_mix_formulas'):
                self.cell_mix_formulas = {}

            # Ẩn bảng kết quả nếu đang hiển thị
            self.results_label.setVisible(False)
            self.results_table.setVisible(False)

            # Xóa dữ liệu kết quả
            self.results_data = {}

            # Thông báo đã reset thành công
            QMessageBox.information(self, "Thành công", "Đã xóa toàn bộ dữ liệu trong bảng!")

            # Cập nhật hiển thị bảng
            self.update_feed_table_display()

    def setup_inventory_tab(self):
        """Setup the inventory management tab"""
        layout = QVBoxLayout()

        # Create tabs for Feed and Mix inventory
        inventory_tabs = QTabWidget()
        inventory_tabs.setFont(DEFAULT_FONT)
        inventory_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background: white;
            }
            QTabWidget::tab-bar {
                left: 5px;
            }
            QTabBar::tab {
                background: #f0f0f0;
                border: 1px solid #cccccc;
                border-bottom-color: #cccccc;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 12px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #4CAF50;
                color: white;
            }
            QTabBar::tab:!selected {
                margin-top: 2px;
            }
        """)

        feed_inventory_tab = QWidget()
        mix_inventory_tab = QWidget()

        inventory_tabs.addTab(feed_inventory_tab, "Kho Cám")
        inventory_tabs.addTab(mix_inventory_tab, "Kho Mix")

        # Setup Feed Inventory tab
        feed_layout = QVBoxLayout()

        # Thêm tiêu đề
        feed_header = QLabel("Quản Lý Kho Cám")
        feed_header.setFont(HEADER_FONT)
        feed_header.setAlignment(Qt.AlignCenter)
        feed_header.setStyleSheet("QLabel { padding: 10px; background-color: #e0f2f1; border-radius: 5px; }")
        feed_layout.addWidget(feed_header)

        self.feed_inventory_table = QTableWidget()
        self.feed_inventory_table.setFont(TABLE_CELL_FONT)
        self.feed_inventory_table.setColumnCount(4)
        self.feed_inventory_table.setHorizontalHeaderLabels(["Thành phần", "Tồn kho (kg)", "Kích thước bao (kg)", "Số bao"])
        self.feed_inventory_table.horizontalHeader().setFont(TABLE_HEADER_FONT)
        self.feed_inventory_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.feed_inventory_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #aaa;
                selection-background-color: #e0e0ff;
                alternate-background-color: #f9f9f9;
            }
            QHeaderView::section {
                background-color: #4CAF50;
                color: white;
                padding: 6px;
                border: 1px solid #ddd;
            }
            QTableWidget::item {
                padding: 4px;
            }
        """)
        self.feed_inventory_table.setAlternatingRowColors(True)

        # Populate feed inventory table
        self.update_feed_inventory_table()

        feed_layout.addWidget(self.feed_inventory_table)

        # Add update button for feed inventory
        update_feed_button = QPushButton("Cập Nhật Kho Cám")
        update_feed_button.setFont(BUTTON_FONT)
        update_feed_button.setMinimumHeight(40)
        update_feed_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        update_feed_button.clicked.connect(lambda: self.update_inventory("feed"))
        feed_layout.addWidget(update_feed_button)

        feed_inventory_tab.setLayout(feed_layout)

        # Setup Mix Inventory tab
        mix_layout = QVBoxLayout()

        # Thêm tiêu đề
        mix_header = QLabel("Quản Lý Kho Mix")
        mix_header.setFont(HEADER_FONT)
        mix_header.setAlignment(Qt.AlignCenter)
        mix_header.setStyleSheet("QLabel { padding: 10px; background-color: #e8f5e9; border-radius: 5px; }")
        mix_layout.addWidget(mix_header)

        self.mix_inventory_table = QTableWidget()
        self.mix_inventory_table.setFont(TABLE_CELL_FONT)
        self.mix_inventory_table.setColumnCount(4)
        self.mix_inventory_table.setHorizontalHeaderLabels(["Thành phần", "Tồn kho (kg)", "Kích thước bao (kg)", "Số bao"])
        self.mix_inventory_table.horizontalHeader().setFont(TABLE_HEADER_FONT)
        self.mix_inventory_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.mix_inventory_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #aaa;
                selection-background-color: #e0e0ff;
                alternate-background-color: #f9f9f9;
            }
            QHeaderView::section {
                background-color: #8BC34A;
                color: white;
                padding: 6px;
                border: 1px solid #ddd;
            }
            QTableWidget::item {
                padding: 4px;
            }
        """)
        self.mix_inventory_table.setAlternatingRowColors(True)

        # Populate mix inventory table
        self.update_mix_inventory_table()

        mix_layout.addWidget(self.mix_inventory_table)

        # Add update button for mix inventory
        update_mix_button = QPushButton("Cập Nhật Kho Mix")
        update_mix_button.setFont(BUTTON_FONT)
        update_mix_button.setMinimumHeight(40)
        update_mix_button.setStyleSheet("""
            QPushButton {
                background-color: #8BC34A;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #7CB342;
            }
        """)
        update_mix_button.clicked.connect(lambda: self.update_inventory("mix"))
        mix_layout.addWidget(update_mix_button)

        mix_inventory_tab.setLayout(mix_layout)

        # Add tabs to layout
        layout.addWidget(inventory_tabs)

        self.inventory_tab.setLayout(layout)

    def setup_formula_tab(self):
        """Setup the formula management tab"""
        layout = QVBoxLayout()

        # Create tabs for Feed and Mix formulas
        formula_tabs = QTabWidget()
        formula_tabs.setFont(DEFAULT_FONT)
        formula_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background: white;
            }
            QTabWidget::tab-bar {
                left: 5px;
            }
            QTabBar::tab {
                background: #f0f0f0;
                border: 1px solid #cccccc;
                border-bottom-color: #cccccc;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 12px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #2196F3;
                color: white;
            }
            QTabBar::tab:!selected {
                margin-top: 2px;
            }
        """)

        feed_formula_tab = QWidget()
        mix_formula_tab = QWidget()

        formula_tabs.addTab(feed_formula_tab, "Công Thức Cám")
        formula_tabs.addTab(mix_formula_tab, "Công Thức Mix")

        # Setup Feed Formula tab
        feed_layout = QVBoxLayout()

        # Thêm tiêu đề
        feed_header = QLabel("Quản Lý Công Thức Cám")
        feed_header.setFont(HEADER_FONT)
        feed_header.setAlignment(Qt.AlignCenter)
        feed_header.setStyleSheet("QLabel { padding: 10px; background-color: #e3f2fd; border-radius: 5px; }")
        feed_layout.addWidget(feed_header)

        # Feed formula table
        self.feed_formula_table = QTableWidget()
        self.feed_formula_table.setFont(TABLE_CELL_FONT)
        self.feed_formula_table.setColumnCount(3)
        self.feed_formula_table.setHorizontalHeaderLabels(["Thành phần", "Tỷ lệ (%)", "Lượng (kg)"])
        self.feed_formula_table.horizontalHeader().setFont(TABLE_HEADER_FONT)
        self.feed_formula_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.feed_formula_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #aaa;
                selection-background-color: #e0e0ff;
                alternate-background-color: #f5f5f5;
            }
            QHeaderView::section {
                background-color: #2196F3;
                color: white;
                padding: 6px;
                border: 1px solid #ddd;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QDoubleSpinBox {
                border: 1px solid #bbb;
                border-radius: 4px;
                padding: 2px;
                background-color: white;
            }
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                width: 20px;
            }
        """)
        self.feed_formula_table.setAlternatingRowColors(True)

        # Populate feed formula table
        self.update_feed_formula_table()

        feed_layout.addWidget(self.feed_formula_table)

        # Feed formula presets section
        preset_section = QGroupBox("Công Thức Có Sẵn")
        preset_section.setFont(DEFAULT_FONT)
        preset_section.setStyleSheet("""
            QGroupBox {
                border: 1px solid #bbbbbb;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                background-color: white;
            }
        """)

        preset_layout = QVBoxLayout()

        # Feed formula presets
        preset_combo_layout = QHBoxLayout()

        preset_label = QLabel("Chọn công thức:")
        preset_label.setFont(DEFAULT_FONT)
        preset_combo_layout.addWidget(preset_label)

        # Sử dụng feed_preset_combo đã được khởi tạo trước đó
        self.feed_preset_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #bbb;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
                min-width: 200px;
            }
            QComboBox::drop-down {
                width: 20px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #bbb;
                selection-background-color: #e0e0ff;
            }
        """)
        self.feed_preset_combo.setMinimumHeight(35)
        self.update_feed_preset_combo()
        self.feed_preset_combo.currentIndexChanged.connect(self.auto_load_feed_preset)
        preset_combo_layout.addWidget(self.feed_preset_combo)
        preset_combo_layout.addStretch()

        preset_layout.addLayout(preset_combo_layout)

        # Bỏ phần liên kết công thức Mix vì không còn sử dụng
        preset_section.setLayout(preset_layout)
        feed_layout.addWidget(preset_section)

        # Buttons for feed formula
        button_layout = QHBoxLayout()

        save_button = QPushButton("Lưu Công Thức")
        save_button.setFont(BUTTON_FONT)
        save_button.setMinimumHeight(40)
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        save_button.clicked.connect(self.save_feed_formula)

        save_as_button = QPushButton("Lưu Công Thức Mới")
        save_as_button.setFont(BUTTON_FONT)
        save_as_button.setMinimumHeight(40)
        save_as_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        save_as_button.clicked.connect(self.save_as_feed_preset)

        delete_button = QPushButton("Xóa Công Thức")
        delete_button.setFont(BUTTON_FONT)
        delete_button.setMinimumHeight(40)
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        delete_button.clicked.connect(self.delete_feed_preset)

        button_layout.addWidget(save_button)
        button_layout.addWidget(save_as_button)
        button_layout.addWidget(delete_button)

        feed_layout.addLayout(button_layout)
        feed_formula_tab.setLayout(feed_layout)

        # Setup Mix Formula tab
        mix_layout = QVBoxLayout()

        # Thêm tiêu đề
        mix_header = QLabel("Quản Lý Công Thức Mix")
        mix_header.setFont(HEADER_FONT)
        mix_header.setAlignment(Qt.AlignCenter)
        mix_header.setStyleSheet("QLabel { padding: 10px; background-color: #fff8e1; border-radius: 5px; }")
        mix_layout.addWidget(mix_header)

        # Mix formula table
        self.mix_formula_table = QTableWidget()
        self.mix_formula_table.setFont(TABLE_CELL_FONT)
        self.mix_formula_table.setColumnCount(3)
        self.mix_formula_table.setHorizontalHeaderLabels(["Thành phần", "Tỷ lệ (%)", "Lượng (kg)"])
        self.mix_formula_table.horizontalHeader().setFont(TABLE_HEADER_FONT)
        self.mix_formula_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.mix_formula_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #aaa;
                selection-background-color: #e0e0ff;
                alternate-background-color: #f5f5f5;
            }
            QHeaderView::section {
                background-color: #FF9800;
                color: white;
                padding: 6px;
                border: 1px solid #ddd;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QDoubleSpinBox {
                border: 1px solid #bbb;
                border-radius: 4px;
                padding: 2px;
                background-color: white;
            }
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                width: 20px;
            }
        """)
        self.mix_formula_table.setAlternatingRowColors(True)

        # Populate mix formula table
        self.update_mix_formula_table()

        mix_layout.addWidget(self.mix_formula_table)

        # Mix formula presets section
        mix_preset_section = QGroupBox("Công Thức Có Sẵn")
        mix_preset_section.setFont(DEFAULT_FONT)
        mix_preset_section.setStyleSheet("""
            QGroupBox {
                border: 1px solid #bbbbbb;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                background-color: white;
            }
        """)

        mix_preset_layout = QVBoxLayout()

        # Mix formula presets
        mix_preset_combo_layout = QHBoxLayout()

        mix_preset_label = QLabel("Chọn công thức:")
        mix_preset_label.setFont(DEFAULT_FONT)
        mix_preset_combo_layout.addWidget(mix_preset_label)

        # Sử dụng mix_preset_combo đã được khởi tạo trước đó
        self.mix_preset_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #bbb;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
                min-width: 200px;
            }
            QComboBox::drop-down {
                width: 20px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #bbb;
                selection-background-color: #e0e0ff;
            }
        """)
        self.mix_preset_combo.setMinimumHeight(35)
        self.update_mix_preset_combo()
        self.mix_preset_combo.currentIndexChanged.connect(self.auto_load_mix_preset)
        mix_preset_combo_layout.addWidget(self.mix_preset_combo)

        mix_preset_combo_layout.addStretch()
        mix_preset_layout.addLayout(mix_preset_combo_layout)
        mix_preset_section.setLayout(mix_preset_layout)
        mix_layout.addWidget(mix_preset_section)

        # Buttons for mix formula
        mix_button_layout = QHBoxLayout()

        mix_save_button = QPushButton("Lưu Công Thức")
        mix_save_button.setFont(BUTTON_FONT)
        mix_save_button.setMinimumHeight(40)
        mix_save_button.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        mix_save_button.clicked.connect(self.save_mix_formula)

        mix_save_as_button = QPushButton("Lưu Công Thức Mới")
        mix_save_as_button.setFont(BUTTON_FONT)
        mix_save_as_button.setMinimumHeight(40)
        mix_save_as_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        mix_save_as_button.clicked.connect(self.save_as_mix_preset)

        mix_delete_button = QPushButton("Xóa Công Thức")
        mix_delete_button.setFont(BUTTON_FONT)
        mix_delete_button.setMinimumHeight(40)
        mix_delete_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        mix_delete_button.clicked.connect(self.delete_mix_preset)

        mix_button_layout.addWidget(mix_save_button)
        mix_button_layout.addWidget(mix_save_as_button)
        mix_button_layout.addWidget(mix_delete_button)

        mix_layout.addLayout(mix_button_layout)
        mix_formula_tab.setLayout(mix_layout)

        # Add tabs to layout
        layout.addWidget(formula_tabs)

        self.formula_tab.setLayout(layout)

    def setup_history_tab(self):
        """Setup the history tab"""
        layout = QVBoxLayout()

        # Thêm tiêu đề
        history_header = QLabel("Lịch Sử Cám (Chỉ Xem)")
        history_header.setFont(HEADER_FONT)
        history_header.setAlignment(Qt.AlignCenter)
        history_header.setStyleSheet("QLabel { padding: 10px; background-color: #e8eaf6; border-radius: 5px; margin-bottom: 10px; }")
        layout.addWidget(history_header)

        # Add history date selection
        date_selection = QGroupBox("Chọn Ngày Báo Cáo")
        date_selection.setFont(DEFAULT_FONT)
        date_selection.setStyleSheet("""
            QGroupBox {
                border: 1px solid #bbbbbb;
                border-radius: 6px;
                margin-top: 12px;
                padding: 10px;
                background-color: #f5f5f5;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                background-color: #f5f5f5;
            }
        """)

        date_layout = QHBoxLayout()

        date_label = QLabel("Chọn ngày:")
        date_label.setFont(DEFAULT_FONT)
        date_layout.addWidget(date_label)

        # Khởi tạo history_date_combo nếu chưa có
        if not hasattr(self, 'history_date_combo'):
            self.history_date_combo = QComboBox()
            self.history_date_combo.setFont(DEFAULT_FONT)

        self.history_date_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #bbb;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
                min-width: 200px;
            }
            QComboBox::drop-down {
                width: 20px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #bbb;
                selection-background-color: #e0e0ff;
            }
        """)
        self.history_date_combo.setMinimumHeight(35)
        self.update_history_dates()
        self.history_date_combo.currentIndexChanged.connect(self.load_history_data)
        date_layout.addWidget(self.history_date_combo)

        # Add compare button
        compare_button = QPushButton("So Sánh")
        compare_button.setFont(BUTTON_FONT)
        compare_button.setMinimumHeight(35)
        compare_button.setStyleSheet("""
            QPushButton {
                background-color: #3F51B5;
                color: white;
                border-radius: 5px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #303F9F;
            }
        """)
        compare_button.clicked.connect(self.compare_history_data)
        date_layout.addWidget(compare_button)

        # Add visualize button
        visualize_button = QPushButton("Biểu Đồ")
        visualize_button.setFont(BUTTON_FONT)
        visualize_button.setMinimumHeight(35)
        visualize_button.setStyleSheet("""
            QPushButton {
                background-color: #009688;
                color: white;
                border-radius: 5px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #00796B;
            }
        """)
        visualize_button.clicked.connect(self.visualize_history_data)
        date_layout.addWidget(visualize_button)

        # Add export button
        export_button = QPushButton("Xuất Excel")
        export_button.setFont(BUTTON_FONT)
        export_button.setMinimumHeight(35)
        export_button.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border-radius: 5px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        export_button.clicked.connect(self.export_history_to_excel)
        date_layout.addWidget(export_button)

        date_layout.addStretch()
        date_selection.setLayout(date_layout)
        layout.addWidget(date_selection)

        # Create tabs for different history views
        self.history_tabs = QTabWidget()
        self.history_tabs.setFont(DEFAULT_FONT)
        self.history_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background: white;
            }
            QTabWidget::tab-bar {
                left: 5px;
            }
            QTabBar::tab {
                background: #f0f0f0;
                border: 1px solid #cccccc;
                border-bottom-color: #cccccc;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 12px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #3F51B5;
                color: white;
            }
            QTabBar::tab:!selected {
                margin-top: 2px;
            }
        """)

        self.history_usage_tab = QWidget()
        self.history_feed_tab = QWidget()
        self.history_mix_tab = QWidget()

        self.history_tabs.addTab(self.history_usage_tab, "Lượng Cám")
        self.history_tabs.addTab(self.history_feed_tab, "Thành Phần Cám")
        self.history_tabs.addTab(self.history_mix_tab, "Thành Phần Mix")

        # Setup each history tab
        self.setup_history_usage_tab()
        self.setup_history_feed_tab()
        self.setup_history_mix_tab()

        # Add to main layout
        layout.addWidget(self.history_tabs)

        self.history_tab.setLayout(layout)

    def setup_history_usage_tab(self):
        """Setup the history usage tab"""
        layout = QVBoxLayout()

        # Create table for history usage data
        self.history_usage_table = QTableWidget()
        self.history_usage_table.setFont(TABLE_CELL_FONT)

        # Đặt bảng chỉ đọc - không cho phép sửa đổi
        self.history_usage_table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Calculate total number of farms
        total_farms = sum(len(farms) for farms in FARMS.values())

        # Tạo bảng với cấu trúc giống với feed_table:
        # - Hàng đầu tiên: Khu (label)
        # - Hàng thứ hai: Trại
        # - Các hàng tiếp theo: Buổi (Sáng/Chiều)
        self.history_usage_table.setRowCount(len(SHIFTS) + 2)  # +2 cho hàng Khu và hàng Trại
        self.history_usage_table.setColumnCount(total_farms)  # Chỉ hiển thị các trại, bỏ cột nhãn

        # Ẩn header row (dãy số trên cùng)
        self.history_usage_table.horizontalHeader().setVisible(False)

        # Set row headers
        khu_header = QTableWidgetItem("Khu")
        khu_header.setFont(TABLE_HEADER_FONT)
        self.history_usage_table.setVerticalHeaderItem(0, khu_header)

        trai_header = QTableWidgetItem("Trại")
        trai_header.setFont(TABLE_HEADER_FONT)
        self.history_usage_table.setVerticalHeaderItem(1, trai_header)

        for i, shift in enumerate(SHIFTS):
            shift_header = QTableWidgetItem(shift)
            shift_header.setFont(TABLE_HEADER_FONT)
            self.history_usage_table.setVerticalHeaderItem(i + 2, shift_header)

        # Thiết lập style cho bảng
        self.history_usage_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #aaa;
                selection-background-color: #e0e0ff;
                alternate-background-color: #f5f5f5;
            }
            QHeaderView::section {
                background-color: #3F51B5;
                color: white;
                padding: 6px;
                border: 1px solid #ddd;
            }
            QTableWidget::item {
                padding: 4px;
            }
        """)

        # Tăng chiều cao của các hàng để dễ nhìn hơn
        self.history_usage_table.setRowHeight(0, 45)  # Hàng khu
        self.history_usage_table.setRowHeight(1, 45)  # Hàng trại
        for row in range(2, self.history_usage_table.rowCount()):
            self.history_usage_table.setRowHeight(row, 50)  # Hàng nhập liệu

        # Stretch columns to fill available space
        self.history_usage_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.history_usage_table)
        self.history_usage_tab.setLayout(layout)

    def setup_history_feed_tab(self):
        """Setup the history feed tab"""
        layout = QVBoxLayout()

        # Create table for history feed data
        self.history_feed_table = QTableWidget()
        self.history_feed_table.setFont(TABLE_CELL_FONT)
        self.history_feed_table.horizontalHeader().setFont(TABLE_HEADER_FONT)
        self.history_feed_table.verticalHeader().setFont(TABLE_HEADER_FONT)

        # Đặt bảng chỉ đọc - không cho phép sửa đổi
        self.history_feed_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.history_feed_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #aaa;
                selection-background-color: #e0e0ff;
                alternate-background-color: #f5f5f5;
            }
            QHeaderView::section {
                background-color: #2196F3;
                color: white;
                padding: 6px;
                border: 1px solid #ddd;
            }
            QTableWidget::item {
                padding: 4px;
            }
        """)
        self.history_feed_table.setAlternatingRowColors(True)

        layout.addWidget(self.history_feed_table)
        self.history_feed_tab.setLayout(layout)

    def setup_history_mix_tab(self):
        """Setup the history mix tab"""
        layout = QVBoxLayout()

        # Create table for history mix data
        self.history_mix_table = QTableWidget()
        self.history_mix_table.setFont(TABLE_CELL_FONT)
        self.history_mix_table.horizontalHeader().setFont(TABLE_HEADER_FONT)
        self.history_mix_table.verticalHeader().setFont(TABLE_HEADER_FONT)

        # Đặt bảng chỉ đọc - không cho phép sửa đổi
        self.history_mix_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.history_mix_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #aaa;
                selection-background-color: #e0e0ff;
                alternate-background-color: #f5f5f5;
            }
            QHeaderView::section {
                background-color: #FF9800;
                color: white;
                padding: 6px;
                border: 1px solid #ddd;
            }
            QTableWidget::item {
                padding: 4px;
            }
        """)
        self.history_mix_table.setAlternatingRowColors(True)

        layout.addWidget(self.history_mix_table)
        self.history_mix_tab.setLayout(layout)

    def update_history_dates(self, combo_box=None):
        """Update the list of available report dates"""
        # Xác định combo box cần cập nhật
        combo_boxes = []
        if combo_box is None:
            combo_boxes.append(self.history_date_combo)
        else:
            combo_boxes.append(combo_box)

        # Xóa dữ liệu cũ
        for cb in combo_boxes:
            cb.clear()

        # Reports directory
        reports_dir = "src/data/reports"

        # Check if reports directory exists
        if not os.path.exists(reports_dir):
            # Thử đường dẫn cũ
            reports_dir = "reports"
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
        if combo_box is not None:
            combo_box.addItem("Không so sánh")

        # Add to combo box
        for report_file in report_files:
            try:
                # Extract date from filename (format: reports/report_YYYYMMDD.json)
                date_str = os.path.basename(report_file)[7:-5]  # Remove 'report_' and '.json'

                # Format date as DD/MM/YYYY for display
                if len(date_str) == 8:  # Đảm bảo đúng định dạng YYYYMMDD
                    year = date_str[0:4]
                    month = date_str[4:6]
                    day = date_str[6:8]
                    formatted_date = f"{day}/{month}/{year}"

                    for cb in combo_boxes:
                        cb.addItem(formatted_date)
                else:
                    # Nếu không đúng định dạng, hiển thị tên file
                    print(f"Định dạng ngày không hợp lệ trong file: {report_file}")
                    for cb in combo_boxes:
                        cb.addItem(os.path.basename(report_file))
            except Exception as e:
                # If date parsing fails, just add the filename
                print(f"Lỗi khi xử lý file báo cáo {report_file}: {str(e)}")
                for cb in combo_boxes:
                    cb.addItem(os.path.basename(report_file))

    def load_history_data(self, show_warnings=True):
        """Load history data based on selected date"""
        selected_date = self.history_date_combo.currentText()

        if selected_date == "Không có dữ liệu":
            # Xóa dữ liệu hiện tại
            self.history_usage_table.setRowCount(0)
            self.history_feed_table.setRowCount(0)
            self.history_mix_table.setRowCount(0)
            self.current_report_data = None
            return

        # Tải dữ liệu báo cáo
        report_data = self.load_report_data(selected_date)

        # Lưu dữ liệu báo cáo hiện tại
        self.current_report_data = report_data

        # Cập nhật các bảng
        self.update_history_usage_table(report_data)
        self.update_history_feed_table(report_data)
        self.update_history_mix_table(report_data)

    def update_history_usage_table(self, report_data):
        """Update the history usage table with data from a report"""
        try:
            # Kiểm tra dữ liệu báo cáo
            if not report_data or "feed_usage" not in report_data:
                return

            # Lấy dữ liệu lượng cám
            feed_usage = report_data.get("feed_usage", {})
            formula_usage = report_data.get("formula_usage", {})

            # Tìm công thức mặc định từ báo cáo
            default_formula = ""
            if "default_formula" in report_data:
                default_formula = report_data.get("default_formula", "")

            # Đặt bảng chỉ đọc - không cho phép sửa đổi
            self.history_usage_table.setEditTriggers(QTableWidget.NoEditTriggers)

            # Thêm thông tin về công thức mặc định
            if default_formula:
                # Tạo một layout để hiển thị thông tin công thức mặc định
                default_formula_label = QLabel(f"Công thức mặc định: {default_formula}")
                default_formula_label.setFont(QFont("Arial", DEFAULT_FONT_SIZE, QFont.Bold))
                default_formula_label.setStyleSheet("color: #2196F3; margin-bottom: 10px;")

                # Thêm label vào phía trên bảng
                history_usage_layout = self.history_usage_tab.layout()
                # Kiểm tra xem đã có label này chưa
                for i in range(history_usage_layout.count()):
                    item = history_usage_layout.itemAt(i)
                    if isinstance(item.widget(), QLabel) and item.widget().text().startswith("Công thức mặc định:"):
                        history_usage_layout.removeItem(item)
                        item.widget().deleteLater()
                        break

                # Thêm label mới vào đầu layout
                history_usage_layout.insertWidget(0, default_formula_label)

            # Màu nền cho các khu khác nhau
            khu_colors = [
                QColor(240, 248, 255),  # Khu 1: Alice Blue
                QColor(245, 245, 220),  # Khu 2: Beige
                QColor(240, 255, 240),  # Khu 3: Honeydew
                QColor(255, 240, 245),  # Khu 4: Lavender Blush
                QColor(255, 250, 240),  # Khu 5: Floral White
            ]

            # Populate table with farms and khu information
            col_index = 0  # Bắt đầu từ cột 0 vì đã bỏ cột nhãn
            for khu_idx, farms in FARMS.items():
                khu_name = f"Khu {khu_idx + 1}"
                khu_color = khu_colors[khu_idx]

                for farm in farms:
                    # Set khu label in first row
                    khu_item = QTableWidgetItem(khu_name)
                    khu_item.setFont(TABLE_CELL_FONT)
                    khu_item.setBackground(khu_color)
                    khu_item.setTextAlignment(Qt.AlignCenter)
                    self.history_usage_table.setItem(0, col_index, khu_item)

                    # Set farm name in second row
                    farm_item = QTableWidgetItem(farm)
                    farm_item.setFont(TABLE_CELL_FONT)
                    farm_item.setBackground(khu_color.lighter(105))
                    farm_item.setTextAlignment(Qt.AlignCenter)
                    self.history_usage_table.setItem(1, col_index, farm_item)

                    # Set values for each shift
                    if khu_name in feed_usage and farm in feed_usage[khu_name]:
                        farm_data = feed_usage[khu_name][farm]

                        # Kiểm tra xem có dữ liệu công thức không
                        has_formula_data = (formula_usage and
                                          khu_name in formula_usage and
                                          farm in formula_usage[khu_name])

                        for shift_idx, shift in enumerate(SHIFTS):
                            if shift in farm_data:
                                value = farm_data[shift]
                                formula = ""

                                # Nếu có dữ liệu công thức, lấy tên công thức
                                if has_formula_data and shift in formula_usage[khu_name][farm]:
                                    formula = formula_usage[khu_name][farm][shift]

                                # Tạo cell hiển thị số mẻ và công thức (không có dấu ngoặc)
                                # Không hiển thị gì nếu giá trị là 0
                                if value > 0:
                                    # Chỉ hiển thị tên công thức nếu khác với công thức mặc định
                                    if formula and formula != default_formula:
                                        cell_text = f"{format_number(value)} {formula}"
                                    else:
                                        cell_text = f"{format_number(value)}"

                                    cell_item = QTableWidgetItem(cell_text)
                                    cell_item.setFont(TABLE_CELL_FONT)
                                    cell_item.setTextAlignment(Qt.AlignCenter)
                                    cell_item.setBackground(khu_color)
                                    self.history_usage_table.setItem(shift_idx + 2, col_index, cell_item)
                                else:
                                    # Tạo ô trống nếu giá trị là 0
                                    cell_item = QTableWidgetItem("")
                                    cell_item.setBackground(khu_color)
                                    self.history_usage_table.setItem(shift_idx + 2, col_index, cell_item)

                    col_index += 1

        except Exception as e:
            print(f"Lỗi khi cập nhật bảng lịch sử lượng cám: {str(e)}")
            QMessageBox.warning(self, "Lỗi", f"Không thể hiển thị dữ liệu lịch sử lượng cám: {str(e)}")

    def update_history_feed_table(self, report_data):
        """Update the history feed table with data from a report"""
        try:
            # Kiểm tra dữ liệu báo cáo
            if not report_data or "feed_ingredients" not in report_data:
                self.history_feed_table.setRowCount(0)
                return

            # Lấy dữ liệu thành phần cám
            feed_ingredients = report_data.get("feed_ingredients", {})

            # Thiết lập số hàng và cột cho bảng
            self.history_feed_table.setRowCount(len(feed_ingredients))
            self.history_feed_table.setColumnCount(4)  # Thành phần, Tỷ lệ (%), Số lượng (kg), Số bao
            self.history_feed_table.setHorizontalHeaderLabels(["Thành phần", "Tỷ lệ (%)", "Số lượng (kg)", "Số bao"])

            # Đặt bảng chỉ đọc - không cho phép sửa đổi
            self.history_feed_table.setEditTriggers(QTableWidget.NoEditTriggers)

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

            # Tính tổng lượng cám
            total_feed = sum(sorted_feed_ingredients.values())

            # Đổ dữ liệu vào bảng
            for row, (ingredient, amount) in enumerate(sorted_feed_ingredients.items()):
                # Thành phần
                ingredient_item = QTableWidgetItem(ingredient)
                ingredient_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                if ingredient in priority_ingredients:
                    ingredient_item.setBackground(QColor(255, 255, 200))  # Light yellow background for priority
                self.history_feed_table.setItem(row, 0, ingredient_item)

                # Tỷ lệ phần trăm
                percentage = 0
                if total_feed > 0:
                    percentage = (amount / total_feed) * 100
                percentage_item = QTableWidgetItem(format_number(percentage) + " %")
                percentage_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self.history_feed_table.setItem(row, 1, percentage_item)

                # Số lượng
                amount_item = QTableWidgetItem(format_number(amount))
                amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.history_feed_table.setItem(row, 2, amount_item)

                # Số bao (nếu có thông tin)
                bags = self.inventory_manager.calculate_bags(ingredient, amount)
                bags_item = QTableWidgetItem(format_number(bags))
                bags_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.history_feed_table.setItem(row, 3, bags_item)

            # Điều chỉnh kích thước cột
            self.history_feed_table.resizeColumnsToContents()

        except Exception as e:
            print(f"Lỗi khi cập nhật bảng lịch sử thành phần cám: {str(e)}")
            QMessageBox.warning(self, "Lỗi", f"Không thể hiển thị dữ liệu lịch sử thành phần cám: {str(e)}")

    def update_history_mix_table(self, report_data):
        """Update the history mix table with data from a report"""
        try:
            # Kiểm tra dữ liệu báo cáo
            if not report_data or "mix_ingredients" not in report_data:
                self.history_mix_table.setRowCount(0)
                return

            # Lấy dữ liệu thành phần mix
            mix_ingredients = report_data.get("mix_ingredients", {})

            # Thiết lập số hàng và cột cho bảng
            self.history_mix_table.setRowCount(len(mix_ingredients))
            self.history_mix_table.setColumnCount(4)  # Thành phần, Tỷ lệ (%), Số lượng (kg), Số bao
            self.history_mix_table.setHorizontalHeaderLabels(["Thành phần", "Tỷ lệ (%)", "Số lượng (kg)", "Số bao"])

            # Đặt bảng chỉ đọc - không cho phép sửa đổi
            self.history_mix_table.setEditTriggers(QTableWidget.NoEditTriggers)

            # Tính tổng lượng mix
            total_mix = sum(mix_ingredients.values())

            # Đổ dữ liệu vào bảng
            for row, (ingredient, amount) in enumerate(mix_ingredients.items()):
                # Thành phần
                ingredient_item = QTableWidgetItem(ingredient)
                ingredient_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.history_mix_table.setItem(row, 0, ingredient_item)

                # Tỷ lệ phần trăm
                percentage = 0
                if total_mix > 0:
                    percentage = (amount / total_mix) * 100
                percentage_item = QTableWidgetItem(format_number(percentage) + " %")
                percentage_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self.history_mix_table.setItem(row, 1, percentage_item)

                # Số lượng
                amount_item = QTableWidgetItem(format_number(amount))
                amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.history_mix_table.setItem(row, 2, amount_item)

                # Số bao (nếu có thông tin)
                bags = self.inventory_manager.calculate_bags(ingredient, amount)
                bags_item = QTableWidgetItem(format_number(bags))
                bags_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.history_mix_table.setItem(row, 3, bags_item)

            # Điều chỉnh kích thước cột
            self.history_mix_table.resizeColumnsToContents()

        except Exception as e:
            print(f"Lỗi khi cập nhật bảng lịch sử thành phần mix: {str(e)}")
            QMessageBox.warning(self, "Lỗi", f"Không thể hiển thị dữ liệu lịch sử thành phần mix: {str(e)}")

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

        # Thêm hàng tổng cộng cho cám (không thêm hàng tổng mix)
        total_rows = len(self.feed_formula) + 1  # +1 cho hàng tổng cám
        self.feed_formula_table.setRowCount(total_rows)

        row = 0
        for ingredient, amount in self.feed_formula.items():
            # Ingredient name
            ingredient_name = ingredient
            ingredient_item = QTableWidgetItem(ingredient_name)
            ingredient_item.setFont(TABLE_CELL_FONT)
            self.feed_formula_table.setItem(row, 0, ingredient_item)

            # Tính tỷ lệ phần trăm
            percentage = 0
            if total_feed > 0:
                percentage = (amount / total_feed) * 100

            # Hiển thị tỷ lệ phần trăm
            percentage_item = QTableWidgetItem(format_number(percentage) + " %")
            percentage_item.setFont(TABLE_CELL_FONT)
            percentage_item.setTextAlignment(Qt.AlignCenter)
            self.feed_formula_table.setItem(row, 1, percentage_item)

            # Amount input
            amount_spin = CustomDoubleSpinBox()
            amount_spin.setFont(TABLE_CELL_FONT)
            amount_spin.setMinimumHeight(30)
            amount_spin.setRange(0, 2000)
            amount_spin.setDecimals(2)  # Hiển thị tối đa 2 chữ số thập phân
            amount_spin.setValue(amount)
            self.feed_formula_table.setCellWidget(row, 2, amount_spin)

            row += 1

        # Thêm hàng tổng lượng cám
        total_item = QTableWidgetItem("Tổng lượng Cám")
        total_item.setFont(QFont("Arial", DEFAULT_FONT_SIZE + 1, QFont.Bold))
        self.feed_formula_table.setItem(row, 0, total_item)

        # Tổng tỷ lệ phần trăm (luôn là 100%)
        total_percentage = QTableWidgetItem("100 %")
        total_percentage.setFont(QFont("Arial", DEFAULT_FONT_SIZE + 1, QFont.Bold))
        total_percentage.setBackground(QColor(200, 230, 250))  # Light blue background
        total_percentage.setTextAlignment(Qt.AlignCenter)
        self.feed_formula_table.setItem(row, 1, total_percentage)

        total_value = QTableWidgetItem(format_number(total_feed))
        total_value.setFont(QFont("Arial", DEFAULT_FONT_SIZE + 1, QFont.Bold))
        total_value.setBackground(QColor(200, 230, 250))  # Light blue background
        self.feed_formula_table.setItem(row, 2, total_value)

        # Tăng chiều cao của các hàng để dễ nhìn hơn
        for row in range(self.feed_formula_table.rowCount()):
            self.feed_formula_table.setRowHeight(row, 40)

    def update_mix_formula_table(self):
        """Update the mix formula table with current formula"""
        self.mix_formula = self.formula_manager.get_mix_formula()

        # Tính tổng lượng mix
        mix_total = self.formula_manager.calculate_mix_total(self.mix_formula)

        # Thêm hàng tổng cộng
        self.mix_formula_table.setRowCount(len(self.mix_formula) + 1)

        for i, (ingredient, amount) in enumerate(self.mix_formula.items()):
            # Ingredient name
            ingredient_item = QTableWidgetItem(ingredient)
            ingredient_item.setFont(TABLE_CELL_FONT)
            self.mix_formula_table.setItem(i, 0, ingredient_item)

            # Tính tỷ lệ phần trăm
            percentage = 0
            if mix_total > 0:
                percentage = (amount / mix_total) * 100

            # Hiển thị tỷ lệ phần trăm
            percentage_item = QTableWidgetItem(format_number(percentage) + " %")
            percentage_item.setFont(TABLE_CELL_FONT)
            percentage_item.setTextAlignment(Qt.AlignCenter)
            self.mix_formula_table.setItem(i, 1, percentage_item)

            # Amount input
            amount_spin = CustomDoubleSpinBox()
            amount_spin.setFont(TABLE_CELL_FONT)
            amount_spin.setMinimumHeight(30)
            amount_spin.setRange(0, 2000)
            amount_spin.setDecimals(2)  # Hiển thị tối đa 2 chữ số thập phân
            amount_spin.setValue(amount)
            self.mix_formula_table.setCellWidget(i, 2, amount_spin)

        # Thêm hàng tổng lượng
        total_row = len(self.mix_formula)
        total_item = QTableWidgetItem("Tổng lượng Mix")
        total_item.setFont(QFont("Arial", DEFAULT_FONT_SIZE + 1, QFont.Bold))
        self.mix_formula_table.setItem(total_row, 0, total_item)

        # Tổng tỷ lệ phần trăm (luôn là 100%)
        total_percentage = QTableWidgetItem("100 %")
        total_percentage.setFont(QFont("Arial", DEFAULT_FONT_SIZE + 1, QFont.Bold))
        total_percentage.setBackground(QColor(230, 250, 200))  # Light green background
        total_percentage.setTextAlignment(Qt.AlignCenter)
        self.mix_formula_table.setItem(total_row, 1, total_percentage)

        total_value = QTableWidgetItem(format_number(mix_total))
        total_value.setFont(QFont("Arial", DEFAULT_FONT_SIZE + 1, QFont.Bold))
        total_value.setBackground(QColor(230, 250, 200))  # Light green background
        self.mix_formula_table.setItem(total_row, 2, total_value)

        # Tăng chiều cao của các hàng để dễ nhìn hơn
        for row in range(self.mix_formula_table.rowCount()):
            self.mix_formula_table.setRowHeight(row, 40)

    def update_feed_inventory_table(self):
        """Update the feed inventory table"""
        # Get relevant ingredients from feed formula
        feed_ingredients = [k for k in self.feed_formula.keys() if k != "Nguyên liệu tổ hợp"]
        self.feed_inventory_table.setRowCount(len(feed_ingredients))

        # Update inventory from manager
        self.inventory = self.inventory_manager.get_inventory()

        for i, ingredient in enumerate(feed_ingredients):
            # Ingredient name
            ingredient_item = QTableWidgetItem(ingredient)
            ingredient_item.setFont(TABLE_CELL_FONT)
            self.feed_inventory_table.setItem(i, 0, ingredient_item)

            # Current inventory
            inventory_amount = self.inventory.get(ingredient, 0)
            inventory_item = QTableWidgetItem(format_number(inventory_amount))
            inventory_item.setFont(TABLE_CELL_FONT)
            self.feed_inventory_table.setItem(i, 1, inventory_item)

            # Bag size
            bag_size = self.inventory_manager.get_bag_size(ingredient)
            bag_size_item = QTableWidgetItem(format_number(bag_size))
            bag_size_item.setFont(TABLE_CELL_FONT)
            self.feed_inventory_table.setItem(i, 2, bag_size_item)

            # Number of bags
            bags = self.inventory_manager.calculate_bags(ingredient, inventory_amount)
            bags_item = QTableWidgetItem(format_number(bags))
            bags_item.setFont(TABLE_CELL_FONT)
            self.feed_inventory_table.setItem(i, 3, bags_item)

        # Tăng chiều cao của các hàng để dễ nhìn hơn
        for row in range(self.feed_inventory_table.rowCount()):
            self.feed_inventory_table.setRowHeight(row, 40)

    def update_mix_inventory_table(self):
        """Update the mix inventory table"""
        mix_ingredients = list(self.mix_formula.keys())
        self.mix_inventory_table.setRowCount(len(mix_ingredients))

        # Update inventory from manager
        self.inventory = self.inventory_manager.get_inventory()

        for i, ingredient in enumerate(mix_ingredients):
            # Ingredient name
            ingredient_item = QTableWidgetItem(ingredient)
            ingredient_item.setFont(TABLE_CELL_FONT)
            self.mix_inventory_table.setItem(i, 0, ingredient_item)

            # Current inventory
            inventory_amount = self.inventory.get(ingredient, 0)
            inventory_item = QTableWidgetItem(format_number(inventory_amount))
            inventory_item.setFont(TABLE_CELL_FONT)
            self.mix_inventory_table.setItem(i, 1, inventory_item)

            # Bag size
            bag_size = self.inventory_manager.get_bag_size(ingredient)
            bag_size_item = QTableWidgetItem(format_number(bag_size))
            bag_size_item.setFont(TABLE_CELL_FONT)
            self.mix_inventory_table.setItem(i, 2, bag_size_item)

            # Number of bags
            bags = self.inventory_manager.calculate_bags(ingredient, inventory_amount)
            bags_item = QTableWidgetItem(format_number(bags))
            bags_item.setFont(TABLE_CELL_FONT)
            self.mix_inventory_table.setItem(i, 3, bags_item)

        # Tăng chiều cao của các hàng để dễ nhìn hơn
        for row in range(self.mix_inventory_table.rowCount()):
            self.mix_inventory_table.setRowHeight(row, 40)

    def calculate_feed_usage(self):
        """Calculate feed usage based on input values"""
        # Collect data from table
        formula_batches = {}  # Dictionary to store formula name and total batches
        farm_formula_batches = {}  # Dictionary to store formula name and batches for each farm

        # Dictionary để lưu tổng số mẻ theo khu
        total_batches_by_area = {}  # Khu -> số mẻ
        total_batches = 0  # Tổng số mẻ

        # Dictionary để lưu thông tin công thức và thành phần
        self.formula_ingredients = {}

        # Duyệt qua từng cột (farm)
        for col in range(self.feed_table.columnCount()):
            # Lấy tên khu và trại
            khu_item = self.feed_table.item(0, col)
            farm_item = self.feed_table.item(1, col)

            if not khu_item or not farm_item:
                continue

            khu_name = khu_item.text()
            farm_name = farm_item.text()
            farm_key = f"{khu_name} - {farm_name}"

            # Duyệt qua các ca (sáng/chiều)
            for shift_idx, shift in enumerate(SHIFTS):
                # Lấy container từ cell
                container = self.feed_table.cellWidget(shift_idx + 2, col)

                if not container:
                    continue

                # Lấy giá trị từ spin_box và formula_combo
                spin_box = container.spin_box
                formula_combo = container.formula_combo

                if not spin_box or not formula_combo:
                    continue

                batch_value = spin_box.value()
                formula_name = formula_combo.currentText()

                # Nếu không có giá trị hoặc không chọn công thức, bỏ qua
                if batch_value <= 0 or not formula_name:
                    continue

                # Chuyển đổi batch_value: 0.5 = 1 mẻ, 1 = 2 mẻ, 1.5 = 3 mẻ, v.v.
                actual_batches = batch_value
                formula_batch_value = batch_value  # Giữ giá trị gốc để tính toán công thức

                # Chuyển đổi số mẻ theo quy tắc: 0.5 = 1 mẻ, 1 = 2 mẻ
                if batch_value > 0:
                    actual_batches = batch_value * 2  # Số mẻ thực tế = giá trị hiển thị * 2

                # Cập nhật tổng số mẻ theo khu
                if khu_name not in total_batches_by_area:
                    total_batches_by_area[khu_name] = 0
                total_batches_by_area[khu_name] += actual_batches
                total_batches += actual_batches

                # Cộng dồn số mẻ cho công thức này
                if formula_name in formula_batches:
                    formula_batches[formula_name] += formula_batch_value
                else:
                    formula_batches[formula_name] = formula_batch_value

                # Lưu thông tin cho từng farm
                if farm_key not in farm_formula_batches:
                    farm_formula_batches[farm_key] = {}

                if formula_name in farm_formula_batches[farm_key]:
                    farm_formula_batches[farm_key][formula_name] += formula_batch_value
                else:
                    farm_formula_batches[farm_key][formula_name] = formula_batch_value

                # Lưu thông tin chi tiết về mỗi ô để có thể áp dụng công thức mix riêng
                cell_key = f"{khu_name}_{farm_name}_{shift}"
                if not hasattr(self, 'cell_formula_data'):
                    self.cell_formula_data = {}

                self.cell_formula_data[cell_key] = {
                    "feed_formula": formula_name,
                    "batch_value": batch_value,
                    "actual_batches": actual_batches,
                    "khu": khu_name,
                    "farm": farm_name,
                    "shift": shift
                }

        # Nếu không có dữ liệu, hiển thị thông báo và thoát
        if not formula_batches:
            QMessageBox.warning(self, "Cảnh báo", "Không có dữ liệu để báo cáo!")
            return

        # Dictionary để lưu tổng thành phần cám
        feed_ingredients = {}

        # Dictionary để lưu tổng thành phần mix
        mix_ingredients = {}

        # Dictionary để lưu thông tin về công thức mix được sử dụng
        mix_formulas_used = {}

        # Lưu thông tin tổng lượng nguyên liệu tổ hợp
        total_tong_hop = 0

        # Kiểm tra xem có báo cáo đang được tải lại không
        is_loading_report = hasattr(self, 'loading_report') and self.loading_report

        # Nếu đang tải lại báo cáo và có thông tin về công thức mix
        if is_loading_report and hasattr(self, 'current_report_data') and self.current_report_data:
            # Kiểm tra công thức mix theo cột
            if "column_mix_formulas" in self.current_report_data:
                self.column_mix_formulas = self.current_report_data["column_mix_formulas"]
            # Tương thích ngược với phiên bản cũ
            elif "area_mix_formulas" in self.current_report_data:
                self.area_mix_formulas = self.current_report_data["area_mix_formulas"]

            # Đảm bảo self.cell_mix_formulas được tải lại từ báo cáo
            if "cell_mix_formulas" in self.current_report_data:
                self.cell_mix_formulas = self.current_report_data["cell_mix_formulas"]
        # Nếu không phải đang tải báo cáo, đảm bảo đã tải công thức mix theo cột từ file cấu hình
        elif not hasattr(self, 'column_mix_formulas') or not self.column_mix_formulas:
            self.column_mix_formulas = self.formula_manager.column_mix_formulas

        # Không tự động hiển thị dialog chọn công thức mix - để người dùng chọn thủ công

        # Trước tiên, tính toán tổng thành phần cám (không bao gồm mix)
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
                    # Áp dụng quy tắc 0.5 = 1 mẻ, 1 = 2 mẻ
                    # batch_count là số hiển thị trên giao diện, cần nhân 2 để tính đúng số mẻ thực tế
                    feed_amount = amount_per_batch * batch_count * 2

                    # Cộng dồn vào tổng thành phần cám
                    if ingredient in feed_ingredients:
                        feed_ingredients[ingredient] += feed_amount
                    else:
                        feed_ingredients[ingredient] = feed_amount
                else:
                    # Tính tổng lượng nguyên liệu tổ hợp
                    # Áp dụng quy tắc 0.5 = 1 mẻ, 1 = 2 mẻ
                    tong_hop_amount = amount_per_batch * batch_count * 2
                    total_tong_hop += tong_hop_amount

            # Lưu thông tin công thức và thành phần cho hiển thị chi tiết nếu cần
            self.formula_ingredients[formula_name] = {
                "batches": batch_count,
                "tong_hop_amount": feed_formula.get("Nguyên liệu tổ hợp", 0) * batch_count * 2  # Áp dụng quy tắc 0.5 = 1 mẻ
            }

        # Tính toán thành phần mix cho từng ô, cột và khu
        # Đánh dấu các ô đã xử lý
        processed_cells = {}

        # 1. Đầu tiên xử lý các ô có công thức mix riêng
        if hasattr(self, 'cell_mix_formulas') and self.cell_mix_formulas:
            for cell_key, mix_formula_name in self.cell_mix_formulas.items():
                if not mix_formula_name:
                    continue

                # Phân tích cell_key để lấy thông tin khu, trại và ca
                parts = cell_key.split('_')
                if len(parts) < 3:
                    continue

                khu_name, farm_name, shift = parts[0], parts[1], parts[2]

                # Kiểm tra xem ô này có dữ liệu không
                cell_data = None
                for key, data in self.cell_formula_data.items():
                    if key == cell_key:
                        cell_data = data
                        break

                if not cell_data:
                    continue

                # Lấy công thức cám và tính lượng nguyên liệu tổ hợp
                feed_formula = self.formula_manager.load_feed_preset(cell_data["feed_formula"])
                if not feed_formula or "Nguyên liệu tổ hợp" not in feed_formula:
                    continue

                tong_hop_amount = feed_formula["Nguyên liệu tổ hợp"] * cell_data["batch_value"] * 2

                # Lấy công thức mix
                mix_formula = self.formula_manager.load_mix_preset(mix_formula_name)
                if not mix_formula:
                    continue

                # Lưu thông tin công thức mix được sử dụng
                if mix_formula_name not in mix_formulas_used:
                    mix_formulas_used[mix_formula_name] = {
                        "formula": mix_formula,
                        "tong_hop_amount": 0
                    }

                # Cộng dồn lượng nguyên liệu tổ hợp cho công thức mix này
                mix_formulas_used[mix_formula_name]["tong_hop_amount"] += tong_hop_amount

                # Đánh dấu ô này đã được xử lý
                processed_cells[cell_key] = True

        # 2. Sau đó xử lý các cột theo công thức mix của cột
        if hasattr(self, 'column_mix_formulas') and self.column_mix_formulas:
            # Duyệt qua từng ô đã nhập
            for cell_key, cell_data in self.cell_formula_data.items():
                # Bỏ qua các ô đã được xử lý riêng
                if cell_key in processed_cells:
                    continue

                # Phân tích cell_key để lấy thông tin và tìm chỉ số cột
                parts = cell_key.split('_')
                if len(parts) < 3:
                    continue

                khu_name, farm_name, shift = parts[0], parts[1], parts[2]

                # Tìm chỉ số cột từ thông tin khu và farm
                col_index = -1
                current_col = 0
                for k_idx, farms in FARMS.items():
                    k_name = f"Khu {k_idx + 1}"
                    for farm in farms:
                        if k_name == khu_name and farm == farm_name:
                            col_index = current_col
                            break
                        current_col += 1
                    if col_index >= 0:
                        break

                if col_index < 0:
                    continue

                # Kiểm tra xem cột này có công thức mix không
                col_key = f"{col_index}"
                if col_key not in self.column_mix_formulas:
                    continue

                mix_formula_name = self.column_mix_formulas[col_key]
                if not mix_formula_name:
                    continue

                # Lấy công thức mix và kiểm tra
                mix_formula = self.formula_manager.load_mix_preset(mix_formula_name)
                if not mix_formula:
                    continue

                # Lấy công thức cám và tính lượng nguyên liệu tổ hợp
                feed_formula = self.formula_manager.load_feed_preset(cell_data["feed_formula"])
                if not feed_formula or "Nguyên liệu tổ hợp" not in feed_formula:
                    continue

                tong_hop_amount = feed_formula["Nguyên liệu tổ hợp"] * cell_data["batch_value"] * 2

                # Lưu thông tin công thức mix được sử dụng
                if mix_formula_name not in mix_formulas_used:
                    mix_formulas_used[mix_formula_name] = {
                        "formula": mix_formula,
                        "tong_hop_amount": 0
                    }

                # Cộng dồn lượng nguyên liệu tổ hợp cho công thức mix này
                mix_formulas_used[mix_formula_name]["tong_hop_amount"] += tong_hop_amount

                # Đánh dấu ô này đã được xử lý
                processed_cells[cell_key] = True

        # 3. Cuối cùng xử lý các khu theo công thức mix của khu (tương thích ngược)
        if hasattr(self, 'area_mix_formulas') and self.area_mix_formulas:
            for khu_name, mix_formula_name in self.area_mix_formulas.items():
                if not mix_formula_name or khu_name not in total_batches_by_area:
                    continue

                # Lấy công thức mix
                mix_formula = self.formula_manager.load_mix_preset(mix_formula_name)
                if not mix_formula:
                    continue

                # Tính tổng lượng nguyên liệu tổ hợp cho khu này (chỉ tính các ô chưa được xử lý)
                khu_tong_hop_amount = 0

                # Tính tổng lượng nguyên liệu tổ hợp cho khu này
                for cell_key, cell_data in self.cell_formula_data.items():
                    # Bỏ qua các ô đã được xử lý riêng
                    if cell_key in processed_cells:
                        continue

                    if cell_data["khu"] == khu_name:
                        feed_formula = self.formula_manager.load_feed_preset(cell_data["feed_formula"])
                        if feed_formula and "Nguyên liệu tổ hợp" in feed_formula:
                            khu_tong_hop_amount += feed_formula["Nguyên liệu tổ hợp"] * cell_data["batch_value"] * 2

                # Lưu thông tin công thức mix được sử dụng
                if mix_formula_name not in mix_formulas_used:
                    mix_formulas_used[mix_formula_name] = {
                        "formula": mix_formula,
                        "tong_hop_amount": 0
                    }

                # Cộng dồn lượng nguyên liệu tổ hợp cho công thức mix này
                mix_formulas_used[mix_formula_name]["tong_hop_amount"] += khu_tong_hop_amount

        # Tính toán thành phần mix từ tất cả các công thức mix được sử dụng
        for mix_name, mix_data in mix_formulas_used.items():
            mix_formula = mix_data["formula"]
            tong_hop_amount = mix_data["tong_hop_amount"]

            # Tính tổng lượng mix
            mix_total = self.formula_manager.calculate_mix_total(mix_formula)

            if mix_total > 0:
                # Tính tỷ lệ từng thành phần trong mix
                for ingredient, amount in mix_formula.items():
                    # Tính lượng thành phần theo tỷ lệ với tổng lượng nguyên liệu tổ hợp
                    ratio = amount / mix_total
                    mix_amount = ratio * tong_hop_amount

                    # Cộng dồn vào tổng thành phần mix
                    if ingredient in mix_ingredients:
                        mix_ingredients[ingredient] += mix_amount
                    else:
                        mix_ingredients[ingredient] = mix_amount

        # Tính tổng lượng cám và mix
        total_feed_amount = sum(feed_ingredients.values()) if feed_ingredients else 0
        total_mix_amount = sum(mix_ingredients.values()) if mix_ingredients else 0

        # Lưu kết quả tính toán vào biến thành viên để sử dụng khi lưu báo cáo
        self.feed_ingredients = feed_ingredients
        self.mix_ingredients = mix_ingredients
        self.mix_formulas_used = mix_formulas_used
        self.total_tong_hop = total_tong_hop
        self.total_batches = total_batches
        self.total_batches_by_area = total_batches_by_area

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

    def assign_mix_formulas_to_areas(self):
        """Hiển thị dialog cho người dùng chọn công thức mix cho từng cột"""
        # Tạo dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Chọn công thức Mix mặc định theo cột")
        dialog.setMinimumWidth(700)
        dialog.setMinimumHeight(600)

        # Tạo layout
        main_layout = QVBoxLayout()

        # Thêm label hướng dẫn
        header_label = QLabel("Chọn công thức Mix mặc định cho từng cột:")
        header_label.setFont(QFont("Arial", DEFAULT_FONT_SIZE, QFont.Bold))
        main_layout.addWidget(header_label)

        # Tạo scroll area để có thể cuộn khi có nhiều cột
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # Tạo dictionary để lưu các combo box
        combo_boxes = {}

        # Lấy danh sách các công thức mix
        mix_presets = self.formula_manager.get_mix_presets()

        # Tạo các phần chọn công thức theo khu
        khu_sections = {}

        # Duyệt qua tất cả các cột trong bảng
        col_index = 0
        for khu_idx, farms in FARMS.items():
            khu_name = f"Khu {khu_idx + 1}"

            # Tạo section cho khu
            khu_group = QGroupBox(khu_name)
            khu_group.setFont(QFont("Arial", DEFAULT_FONT_SIZE, QFont.Bold))
            khu_layout = QVBoxLayout(khu_group)

            for farm_idx, farm_name in enumerate(farms):
                # Tạo layout ngang cho mỗi cột (farm)
                farm_layout = QHBoxLayout()

                # Tạo label cho farm
                farm_label = QLabel(f"{farm_name}:")
                farm_label.setFont(QFont("Arial", DEFAULT_FONT_SIZE - 1))
                farm_label.setMinimumWidth(150)
                farm_layout.addWidget(farm_label)

                # Tạo combo box cho farm
                combo = QComboBox()
                combo.setFont(QFont("Arial", DEFAULT_FONT_SIZE - 1))

                # Thêm tùy chọn "Không có công thức"
                combo.addItem("Không có công thức", "")

                # Thêm các công thức mix
                for preset in mix_presets:
                    combo.addItem(preset, preset)

                # Thêm vào layout
                farm_layout.addWidget(combo)

                # Không cần nút áp dụng cho tất cả các cột nữa

                # Lưu combo box
                col_key = f"{col_index}"
                combo_boxes[col_key] = combo

                # Cài đặt giá trị mặc định nếu đã có
                if hasattr(self, 'column_mix_formulas') and col_key in self.column_mix_formulas:
                    preset = self.column_mix_formulas[col_key]
                    index = combo.findText(preset)
                    if index >= 0:
                        combo.setCurrentIndex(index)

                # Thêm layout farm vào layout khu
                khu_layout.addLayout(farm_layout)

                col_index += 1

            # Thêm section khu vào scroll area
            scroll_layout.addWidget(khu_group)

        scroll_content.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        # Thêm các nút
        button_layout = QHBoxLayout()



        # Các nút xác nhận và hủy
        ok_button = QPushButton("Lưu & Đóng")
        ok_button.setFont(QFont("Arial", DEFAULT_FONT_SIZE))
        ok_button.setMinimumHeight(40)
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        cancel_button = QPushButton("Hủy")
        cancel_button.setFont(QFont("Arial", DEFAULT_FONT_SIZE))
        cancel_button.setMinimumHeight(40)
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)

        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        main_layout.addLayout(button_layout)

        # Thiết lập layout cho dialog
        dialog.setLayout(main_layout)

        # Kết nối sự kiện
        ok_button.clicked.connect(lambda: self.save_mix_formula_selections(combo_boxes, dialog))
        cancel_button.clicked.connect(dialog.reject)

        # Hiển thị dialog
        dialog.exec_()

    def save_mix_formula_selections(self, combo_boxes, dialog):
        """Lưu các lựa chọn công thức mix cho từng cột"""
        if not hasattr(self, 'column_mix_formulas'):
            self.column_mix_formulas = {}

        # Lưu công thức mix cho từng cột
        for col_key, combo in combo_boxes.items():
            mix_formula_name = combo.currentData()
            if mix_formula_name:
                self.column_mix_formulas[col_key] = mix_formula_name
            elif col_key in self.column_mix_formulas:
                # Nếu chọn "Không có công thức", xóa cài đặt cũ
                del self.column_mix_formulas[col_key]

        # Giữ tương thích ngược với code cũ
        self.area_mix_formulas = {}

        # Lưu cài đặt công thức mix theo cột vào file cấu hình
        self.formula_manager.save_column_mix_formulas(self.column_mix_formulas)

        dialog.accept()

        # Hiển thị thông tin về công thức mix đã chọn
        if hasattr(self, 'column_mix_formulas') and self.column_mix_formulas:
            mix_info = "Đã lưu công thức Mix cho các cột:\n"
            count = 0
            for col, formula in self.column_mix_formulas.items():
                col_index = int(col)
                # Lấy thông tin khu và farm
                khu_item = self.feed_table.item(0, col_index)
                farm_item = self.feed_table.item(1, col_index)
                if khu_item and farm_item:
                    khu_name = khu_item.text()
                    farm_name = farm_item.text()
                    mix_info += f"- {khu_name}, {farm_name}: {formula}\n"
                    count += 1
                    if count >= 10:
                        mix_info += f"... và {len(self.column_mix_formulas) - 10} cột khác\n"
                        break
            QMessageBox.information(self, "Thông tin công thức Mix", mix_info)

    def apply_mix_formula_to_all(self, mix_formula):
        """Áp dụng một công thức mix cho tất cả các cột"""
        if not mix_formula or mix_formula == "Chọn công thức...":
            return

        # Kiểm tra xác nhận
        dialog = QMessageBox()
        dialog.setWindowTitle("Xác nhận")
        dialog.setText(f"Bạn có chắc chắn muốn áp dụng công thức mix '{mix_formula}' cho TẤT CẢ các cột không?")
        dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        dialog.setDefaultButton(QMessageBox.No)

        if dialog.exec_() == QMessageBox.Yes:
            # Xóa tất cả cài đặt cũ và tạo mới
            if not hasattr(self, 'column_mix_formulas'):
                self.column_mix_formulas = {}

            # Lưu công thức cho mỗi cột
            col_count = self.feed_table.columnCount()
            for col in range(col_count):
                col_key = f"{col}"
                self.column_mix_formulas[col_key] = mix_formula

            # Lưu cài đặt công thức mix theo cột vào file cấu hình
            self.formula_manager.save_column_mix_formulas(self.column_mix_formulas)

            # Thông báo
            QMessageBox.information(self, "Thông tin", f"Đã áp dụng công thức mix '{mix_formula}' cho tất cả các cột!")

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
        """Save current feed usage data as a report"""
        try:
            # Kiểm tra xem đã tính toán chưa
            if not hasattr(self, 'feed_ingredients') or not self.feed_ingredients:
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng tính toán trước khi lưu báo cáo!")
                return

            # Tạo thư mục báo cáo nếu chưa tồn tại
            reports_dir = "src/data/reports"
            if not os.path.exists(reports_dir):
                os.makedirs(reports_dir)

            # Kiểm tra xem có đang sử dụng ngày tùy chỉnh không
            custom_date = None
            for widget in self.findChildren(QLabel):
                if widget.text().startswith("Ngày:"):
                    date_text = widget.text().replace("Ngày:", "").strip()
                    if date_text != QDate.currentDate().toString("dd/MM/yyyy"):
                        try:
                            # Chuyển đổi định dạng ngày từ dd/MM/yyyy sang yyyyMMdd
                            day, month, year = date_text.split('/')
                            custom_date = f"{year}{month.zfill(2)}{day.zfill(2)}"
                        except:
                            pass
                    break

            # Sử dụng ngày tùy chỉnh nếu có, nếu không thì sử dụng ngày hiện tại
            if custom_date:
                date_str = custom_date
            else:
                date_str = QDate.currentDate().toString("yyyyMMdd")

            report_file = os.path.join(reports_dir, f"report_{date_str}.json")

            # Thu thập dữ liệu lượng cám
            feed_usage = {}
            formula_usage = {}

            col_index = 0  # Bắt đầu từ cột 0 vì đã bỏ cột nhãn
            for khu_idx, farms in FARMS.items():
                khu_name = f"Khu {khu_idx + 1}"
                feed_usage[khu_name] = {}
                formula_usage[khu_name] = {}

                for farm in farms:
                    feed_usage[khu_name][farm] = {}
                    formula_usage[khu_name][farm] = {}

                    for shift_idx, shift in enumerate(SHIFTS):
                        cell_widget = self.feed_table.cellWidget(shift_idx + 2, col_index)
                        if cell_widget:
                            spin_box = cell_widget.spin_box
                            formula_combo = cell_widget.formula_combo

                            # Lưu giá trị và công thức
                            feed_usage[khu_name][farm][shift] = spin_box.value()
                            formula_usage[khu_name][farm][shift] = formula_combo.currentText()

                    col_index += 1

            # Lấy ngày hiển thị từ UI để lưu vào báo cáo
            display_date = ""
            for widget in self.findChildren(QLabel):
                if widget.text().startswith("Ngày:"):
                    display_date = widget.text().replace("Ngày:", "").strip()
                    break

            # Tạo dữ liệu báo cáo
            report_data = {
                "date": date_str,
                "display_date": display_date,
                "feed_usage": feed_usage,
                "formula_usage": formula_usage,
                "results": self.results_data,
                "feed_ingredients": self.feed_ingredients,
                "mix_ingredients": self.mix_ingredients,
                "total_batches": self.total_batches,
                "total_batches_by_area": self.total_batches_by_area,
                "linked_mix_formula": self.formula_manager.get_linked_mix_formula_name(),
                "tong_hop_amount": self.total_tong_hop,
                "default_formula": self.default_formula_combo.currentText()
            }

            # Lưu thông tin về công thức mix cho từng cột
            if hasattr(self, 'column_mix_formulas') and self.column_mix_formulas:
                report_data["column_mix_formulas"] = self.column_mix_formulas

            # Lưu thông tin về công thức mix cho từng khu (tương thích ngược)
            if hasattr(self, 'area_mix_formulas') and self.area_mix_formulas:
                report_data["area_mix_formulas"] = self.area_mix_formulas

            # Lưu thông tin về công thức mix cho từng ô
            if hasattr(self, 'cell_mix_formulas') and self.cell_mix_formulas:
                report_data["cell_mix_formulas"] = self.cell_mix_formulas

            # Lưu báo cáo
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=4)

            QMessageBox.information(self, "Thành công", f"Đã lưu báo cáo vào {report_file}")

            # Cập nhật danh sách báo cáo trong tab lịch sử
            self.update_history_dates()

        except Exception as e:
            print(f"Lỗi khi lưu báo cáo: {str(e)}")
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu báo cáo: {str(e)}")

        return True

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
            khu_df.to_excel(writer, sheet_name='Lượng Cám theo Khu', index=False)
            farm_df.to_excel(writer, sheet_name='Lượng Cám theo Trại', index=False)
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
        """Compare current history data with another date"""
        # Nếu không có dữ liệu hiện tại, không thể so sánh
        if not hasattr(self, 'current_report_data') or not self.current_report_data:
            QMessageBox.warning(self, "Cảnh báo", "Không có dữ liệu hiện tại để so sánh!")
            return

        # Tạo dialog để chọn ngày so sánh
        dialog = QDialog(self)
        dialog.setWindowTitle("Chọn Ngày So Sánh")
        dialog.setMinimumWidth(300)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QLabel {
                font-size: 12pt;
            }
            QComboBox {
                border: 1px solid #bbb;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
                min-height: 30px;
                font-size: 11pt;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 4px;
                padding: 8px 15px;
                font-weight: bold;
                min-height: 30px;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        layout = QVBoxLayout()

        # Thêm label
        label = QLabel("Chọn ngày để so sánh:")
        label.setFont(DEFAULT_FONT)
        layout.addWidget(label)

        # Thêm combobox để chọn ngày
        compare_date_combo = QComboBox()
        compare_date_combo.setFont(DEFAULT_FONT)

        # Cập nhật danh sách ngày (loại bỏ ngày hiện tại)
        self.update_history_dates(compare_date_combo)

        # Nếu chỉ có một lựa chọn (Không có dữ liệu), không thể so sánh
        if compare_date_combo.count() <= 1:
            QMessageBox.warning(self, "Cảnh báo", "Không có dữ liệu khác để so sánh!")
            return

        layout.addWidget(compare_date_combo)

        # Thêm nút OK và Cancel
        button_layout = QHBoxLayout()
        ok_button = QPushButton("So Sánh")
        cancel_button = QPushButton("Hủy")

        ok_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)

        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        dialog.setLayout(layout)

        # Hiển thị dialog
        if dialog.exec_() == QDialog.Accepted:
            # Lấy ngày đã chọn
            compare_date_index = compare_date_combo.currentIndex()
            compare_date_text = compare_date_combo.currentText()

            # Nếu chọn "Không so sánh", thoát
            if compare_date_text == "Không so sánh":
                return

            # Lấy dữ liệu báo cáo để so sánh
            compare_data = self.load_report_data(compare_date_text)

            if not compare_data:
                QMessageBox.warning(self, "Cảnh báo", f"Không thể tải dữ liệu cho ngày {compare_date_text}!")
                return

            # Cập nhật bảng so sánh
            self.update_history_usage_comparison(self.current_report_data, compare_data)
            self.update_history_feed_comparison(self.current_report_data, compare_data)
            self.update_history_mix_comparison(self.current_report_data, compare_data)

    def update_history_usage_comparison(self, current_data, compare_data):
        """Update the history usage table with comparison data"""
        if "feed_usage" not in current_data or "feed_usage" not in compare_data:
            return

        # Đặt bảng chỉ đọc - không cho phép sửa đổi
        self.history_usage_table.setEditTriggers(QTableWidget.NoEditTriggers)

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

        # Đặt bảng chỉ đọc - không cho phép sửa đổi
        self.history_feed_table.setEditTriggers(QTableWidget.NoEditTriggers)

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

        # Đặt bảng chỉ đọc - không cho phép sửa đổi
        self.history_mix_table.setEditTriggers(QTableWidget.NoEditTriggers)

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
            khu_df.to_excel(writer, sheet_name='Lượng Cám theo Khu', index=False)
            farm_df.to_excel(writer, sheet_name='Lượng Cám theo Trại', index=False)
            feed_ingredients_df.to_excel(writer, sheet_name='Thành phần Kho Cám', index=False)
            mix_ingredients_df.to_excel(writer, sheet_name='Thành phần Kho Mix', index=False)

            # Save the Excel file
            writer.close()

            QMessageBox.information(self, "Thành công", f"Đã xuất dữ liệu lịch sử vào file {excel_filename}!")

        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể xuất dữ liệu lịch sử: {str(e)}")

    # Bỏ hàm update_mix_link_combo và set_mix_formula_link vì không còn sử dụng liên kết

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

    def fill_table_from_report(self, date_text):
        """Điền bảng cám từ báo cáo theo ngày đã chọn"""
        try:
            # Tải dữ liệu báo cáo
            report_data = self.load_report_data(date_text)

            if not report_data or "feed_usage" not in report_data:
                QMessageBox.warning(self, "Cảnh báo", f"Không tìm thấy dữ liệu cho ngày {date_text}")
                return

            # Lấy dữ liệu lượng cám và công thức
            feed_usage = report_data.get("feed_usage", {})
            formula_usage = report_data.get("formula_usage", {})

            # Nếu báo cáo có chứa thông tin về công thức mặc định, cập nhật combo box
            if "default_formula" in report_data and report_data["default_formula"]:
                default_formula = report_data["default_formula"]
                # Cập nhật UI và lưu vào cấu hình
                self.default_formula_combo.setCurrentText(default_formula)
                self.formula_manager.save_default_feed_formula(default_formula)

            # Xóa dữ liệu hiện tại trong bảng
            for col in range(self.feed_table.columnCount()):
                for row in range(2, 2 + len(SHIFTS)):
                    cell_widget = self.feed_table.cellWidget(row, col)
                    if cell_widget and hasattr(cell_widget, 'spin_box'):
                        cell_widget.spin_box.setValue(0)
                    if cell_widget and hasattr(cell_widget, 'formula_combo'):
                        cell_widget.formula_combo.setCurrentText("")

            # Xóa dữ liệu công thức mix cho từng ô
            if hasattr(self, 'cell_mix_formulas'):
                self.cell_mix_formulas = {}

            # Tải thông tin công thức mix cho từng ô từ báo cáo
            if "cell_mix_formulas" in report_data:
                self.cell_mix_formulas = report_data["cell_mix_formulas"]

            # Điền dữ liệu từ báo cáo vào bảng
            col_index = 0
            for khu_idx, farms in FARMS.items():
                khu_name = f"Khu {khu_idx + 1}"

                for farm in farms:
                    # Kiểm tra xem có dữ liệu cho khu và trại này không
                    if khu_name in feed_usage and farm in feed_usage[khu_name]:
                        farm_data = feed_usage[khu_name][farm]

                        # Kiểm tra xem có dữ liệu công thức không
                        has_formula_data = (formula_usage and
                                          khu_name in formula_usage and
                                          farm in formula_usage[khu_name])

                        for shift_idx, shift in enumerate(SHIFTS):
                            if shift in farm_data:
                                # Lấy giá trị và công thức
                                value = farm_data[shift]
                                formula = ""

                                if has_formula_data and shift in formula_usage[khu_name][farm]:
                                    formula = formula_usage[khu_name][farm][shift]
                                    print(f"Đã tìm thấy công thức {formula} cho {khu_name}, {farm}, {shift}")

                                # Cập nhật giá trị vào bảng
                                cell_widget = self.feed_table.cellWidget(shift_idx + 2, col_index)
                                if cell_widget:
                                    if hasattr(cell_widget, 'spin_box'):
                                        cell_widget.spin_box.setValue(value)
                                    if hasattr(cell_widget, 'formula_combo') and formula:
                                        cell_widget.formula_combo.setCurrentText(formula)
                                        # Cập nhật hiển thị công thức
                                        if hasattr(cell_widget, 'formula_label'):
                                            default_formula = self.default_formula_combo.currentText()
                                            if formula and formula != default_formula:
                                                cell_widget.formula_label.setText(formula)
                                                cell_widget.formula_label.setVisible(True)
                                                cell_widget.layout().setStretch(0, 60)
                                                cell_widget.layout().setStretch(1, 40)
                                            else:
                                                cell_widget.formula_label.setVisible(False)
                                                cell_widget.layout().setStretch(0, 100)
                                                cell_widget.layout().setStretch(1, 0)

                    col_index += 1

            # Cập nhật hiển thị toàn bộ bảng sau khi điền dữ liệu
            self.update_feed_table_display()

            QMessageBox.information(self, "Thành công", f"Đã điền bảng cám theo dữ liệu ngày {date_text}")

        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể điền bảng cám: {str(e)}")
            import traceback
            traceback.print_exc()

    def fill_table_from_custom_date(self, date_text):
        """Điền bảng cám với ngày tự chọn"""
        try:
            # Xóa dữ liệu hiện tại trong bảng
            for col in range(self.feed_table.columnCount()):
                for row in range(2, 2 + len(SHIFTS)):
                    cell_widget = self.feed_table.cellWidget(row, col)
                    if cell_widget and hasattr(cell_widget, 'spin_box'):
                        cell_widget.spin_box.setValue(0)
                    if cell_widget and hasattr(cell_widget, 'formula_combo'):
                        cell_widget.formula_combo.setCurrentText("")

            # Thử tìm báo cáo gần nhất để lấy công thức mặc định
            default_formula = ""
            try:
                # Lấy báo cáo mới nhất nếu có
                if self.history_date_combo.count() > 0 and self.history_date_combo.currentText() != "Không có dữ liệu":
                    latest_date = self.history_date_combo.itemText(0)
                    latest_report = self.load_report_data(latest_date)

                    if latest_report and "formula_usage" in latest_report:
                        # Tìm công thức được sử dụng nhiều nhất
                        formula_counts = {}
                        for khu_data in latest_report["formula_usage"].values():
                            for farm_data in khu_data.values():
                                for formula in farm_data.values():
                                    if formula:
                                        if formula in formula_counts:
                                            formula_counts[formula] += 1
                                        else:
                                            formula_counts[formula] = 1

                        # Lấy công thức được sử dụng nhiều nhất
                        if formula_counts:
                            default_formula = max(formula_counts.items(), key=lambda x: x[1])[0]
            except Exception as e:
                print(f"Không thể lấy công thức mặc định: {str(e)}")

            # Áp dụng công thức mặc định nếu có
            if default_formula:
                self.default_formula_combo.setCurrentText(default_formula)

            # Cập nhật nhãn ngày trên giao diện
            for widget in self.findChildren(QLabel):
                if widget.text().startswith("Ngày:"):
                    widget.setText(f"Ngày: {date_text}")
                    break

            QMessageBox.information(self, "Thành công", f"Đã tạo bảng mới cho ngày {date_text}")

        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể tạo bảng mới: {str(e)}")
            import traceback
            traceback.print_exc()

    def load_latest_report(self):
        """Tự động tải báo cáo của ngày hiện tại nếu có"""
        # Nếu đã tải báo cáo rồi thì không tải lại nữa
        if self.report_loaded:
            return

        try:
            # Đánh dấu đã tải báo cáo
            self.report_loaded = True

            # Lấy ngày hiện tại
            today = QDate.currentDate().toString("dd/MM/yyyy")
            print(f"Đang tìm báo cáo cho ngày hiện tại: {today}")

            # Cập nhật danh sách các ngày có báo cáo
            self.update_history_dates()

            # Tìm xem có báo cáo cho ngày hiện tại không
            today_report_exists = False
            today_index = -1

            for i in range(self.history_date_combo.count()):
                if self.history_date_combo.itemText(i) == today:
                    today_report_exists = True
                    today_index = i
                    break

            if today_report_exists:
                # Nếu có báo cáo cho ngày hiện tại, tải nó
                self.history_date_combo.setCurrentIndex(today_index)

                try:
                    # Tải dữ liệu báo cáo cho tab lịch sử
                    self.load_history_data(show_warnings=False)
                    print(f"Đã tìm thấy và tải báo cáo cho ngày hiện tại: {today}")

                    # Tự động điền vào bảng cám
                    self.fill_table_from_report(today)
                    print(f"Đã điền bảng cám với dữ liệu ngày {today}")
                except Exception as e:
                    print(f"Lỗi khi tải dữ liệu báo cáo ngày hiện tại: {str(e)}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"Không tìm thấy báo cáo cho ngày hiện tại: {today}")
        except Exception as e:
            print(f"Lỗi khi tự động tải báo cáo: {str(e)}")
            import traceback
            traceback.print_exc()

    def load_report_data(self, date_text):
        """Load report data for a specific date"""
        try:
            # Đánh dấu đang tải báo cáo
            self.loading_report = True

            # Trích xuất ngày từ văn bản (format: DD/MM/YYYY)
            date_parts = date_text.split('/')
            if len(date_parts) != 3:
                print(f"Định dạng ngày không hợp lệ: {date_text}")
                self.loading_report = False
                return None

            day, month, year = date_parts
            date_str = f"{year}{month.zfill(2)}{day.zfill(2)}"
            print(f"Đang tìm báo cáo cho ngày: {date_str}")

            # Tạo đường dẫn file báo cáo
            report_file = f"src/data/reports/report_{date_str}.json"
            print(f"Thử đường dẫn 1: {report_file}")

            # Kiểm tra file tồn tại
            if not os.path.exists(report_file):
                print(f"Không tìm thấy file tại: {report_file}")
                # Thử đường dẫn cũ
                report_file = f"reports/report_{date_str}.json"
                print(f"Thử đường dẫn 2: {report_file}")
                if not os.path.exists(report_file):
                    print(f"Không tìm thấy file tại: {report_file}")

                    # Kiểm tra tất cả các file báo cáo hiện có
                    reports_dir1 = "src/data/reports"
                    reports_dir2 = "reports"

                    if os.path.exists(reports_dir1):
                        print(f"Các file trong {reports_dir1}:")
                        for f in os.listdir(reports_dir1):
                            print(f"  - {f}")

                    if os.path.exists(reports_dir2):
                        print(f"Các file trong {reports_dir2}:")
                        for f in os.listdir(reports_dir2):
                            print(f"  - {f}")

                    self.loading_report = False
                    return None

            # Đọc dữ liệu báo cáo
            print(f"Đọc file báo cáo: {report_file}")
            with open(report_file, 'r', encoding='utf-8') as f:
                report_data = json.load(f)

            print(f"Đã đọc thành công file báo cáo: {report_file}")

            # Lưu báo cáo hiện tại
            self.current_report_data = report_data

            return report_data

        except Exception as e:
            print(f"Lỗi khi tải dữ liệu báo cáo: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            # Đánh dấu đã tải xong báo cáo
            self.loading_report = False

    def fill_table_by_date(self):
        """Điền bảng cám theo ngày đã chọn"""
        # Hiển thị hộp thoại chọn ngày
        date_dialog = QDialog(self)
        date_dialog.setWindowTitle("Chọn Ngày")
        date_dialog.setMinimumWidth(500)

        dialog_layout = QVBoxLayout()

        # Thêm lựa chọn giữa ngày bất kỳ và ngày từ database
        date_source_group = QGroupBox("Nguồn dữ liệu")
        date_source_layout = QVBoxLayout()

        # Radio buttons để chọn nguồn
        custom_date_radio = QRadioButton("Chọn ngày bất kỳ")
        custom_date_radio.setFont(DEFAULT_FONT)
        custom_date_radio.setChecked(True)

        database_date_radio = QRadioButton("Chọn từ báo cáo đã lưu")
        database_date_radio.setFont(DEFAULT_FONT)

        date_source_layout.addWidget(custom_date_radio)
        date_source_layout.addWidget(database_date_radio)
        date_source_group.setLayout(date_source_layout)
        dialog_layout.addWidget(date_source_group)

        # Widget chọn ngày bất kỳ
        custom_date_widget = QWidget()
        custom_date_layout = QVBoxLayout()

        date_label = QLabel("Chọn ngày:")
        date_label.setFont(DEFAULT_FONT)
        custom_date_layout.addWidget(date_label)

        # Sử dụng QDateEdit để chọn ngày
        date_edit = QDateEdit(QDate.currentDate())
        date_edit.setFont(DEFAULT_FONT)
        date_edit.setCalendarPopup(True)
        date_edit.setDisplayFormat("dd/MM/yyyy")
        date_edit.setMinimumHeight(35)
        date_edit.setStyleSheet("""
            QDateEdit {
                border: 1px solid #bbb;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
            }
        """)
        custom_date_layout.addWidget(date_edit)

        custom_date_widget.setLayout(custom_date_layout)
        dialog_layout.addWidget(custom_date_widget)

        # Widget chọn từ database
        database_date_widget = QWidget()
        database_date_layout = QVBoxLayout()

        database_label = QLabel("Chọn báo cáo:")
        database_label.setFont(DEFAULT_FONT)
        database_date_layout.addWidget(database_label)

        # Tạo combo box chọn ngày từ các báo cáo đã lưu
        date_combo = QComboBox()
        date_combo.setFont(DEFAULT_FONT)
        date_combo.setMinimumHeight(35)
        date_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #bbb;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
            }
        """)

        # Cập nhật danh sách ngày từ các báo cáo đã lưu
        self.update_history_dates(date_combo)
        database_date_layout.addWidget(date_combo)

        database_date_widget.setLayout(database_date_layout)
        dialog_layout.addWidget(database_date_widget)

        # Ban đầu ẩn widget chọn từ database
        database_date_widget.setVisible(False)

        # Kết nối sự kiện thay đổi radio button
        def toggle_date_source():
            custom_date_widget.setVisible(custom_date_radio.isChecked())
            database_date_widget.setVisible(database_date_radio.isChecked())

        custom_date_radio.toggled.connect(toggle_date_source)
        database_date_radio.toggled.connect(toggle_date_source)

        # Thêm nút xác nhận và hủy
        button_layout = QHBoxLayout()

        ok_button = QPushButton("Xác nhận")
        ok_button.setFont(BUTTON_FONT)
        ok_button.setMinimumHeight(35)
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                padding: 5px 15px;
            }
        """)

        cancel_button = QPushButton("Hủy")
        cancel_button.setFont(BUTTON_FONT)
        cancel_button.setMinimumHeight(35)
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border-radius: 5px;
                padding: 5px 15px;
            }
        """)

        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        dialog_layout.addLayout(button_layout)

        date_dialog.setLayout(dialog_layout)

        # Kết nối sự kiện cho các nút
        ok_button.clicked.connect(date_dialog.accept)
        cancel_button.clicked.connect(date_dialog.reject)

        # Hiển thị hộp thoại và xử lý kết quả
        if date_dialog.exec_() == QDialog.Accepted:
            if custom_date_radio.isChecked():
                # Lấy ngày từ QDateEdit
                selected_date = date_edit.date().toString("dd/MM/yyyy")
                self.fill_table_from_custom_date(selected_date)
            else:
                # Lấy ngày từ combo box
                selected_date = date_combo.currentText()
                if selected_date and selected_date != "Không có dữ liệu":
                    self.fill_table_from_report(selected_date)

    def show_daily_report(self):
        """Hiển thị popup báo cáo kết quả trong ngày"""
        # Tự động tính toán trước khi hiển thị báo cáo
        self.calculate_feed_usage()

        # Kiểm tra xem đã tính toán thành công chưa
        if not hasattr(self, 'feed_ingredients') or not self.feed_ingredients:
            return  # Đã có thông báo lỗi từ hàm calculate_feed_usage

        # Lấy ngày từ nhãn trong tab tổng quan
        report_date = QDate.currentDate().toString('dd/MM/yyyy')
        for widget in self.findChildren(QLabel):
            if widget.text().startswith("Ngày:"):
                report_date = widget.text().replace("Ngày:", "").strip()
                break

        # Tạo dialog
        report_dialog = QDialog(self)
        report_dialog.setWindowTitle(f"Báo Cáo Ngày {report_date}")

        # Lấy kích thước màn hình desktop
        desktop = QApplication.desktop()
        screen_rect = desktop.screenGeometry()
        screen_width = screen_rect.width()
        screen_height = screen_rect.height()

        # Đặt kích thước dialog bằng 75% màn hình
        dialog_width = int(screen_width * 0.75)
        dialog_height = int(screen_height * 0.75)
        report_dialog.resize(dialog_width, dialog_height)

        # Đặt vị trí giữa màn hình
        report_dialog.move((screen_width - dialog_width) // 2, (screen_height - dialog_height) // 2)

        report_dialog.setWindowModality(Qt.WindowModal)

        # Tạo layout chính
        main_layout = QVBoxLayout(report_dialog)

        # Tiêu đề
        title_label = QLabel(f"BÁO CÁO LƯỢNG CÁM NGÀY {report_date}")
        title_label.setFont(QFont("Arial", DEFAULT_FONT_SIZE + 4, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("QLabel { color: #2196F3; margin: 10px; }")
        main_layout.addWidget(title_label)

        # Tạo TabWidget để hiển thị các tab báo cáo
        report_tabs = QTabWidget()
        report_tabs.setFont(DEFAULT_FONT)
        report_tabs.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        report_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background: white;
                border-radius: 5px;
            }
            QTabWidget::tab-bar {
                left: 5px;
            }
            QTabBar::tab {
                background: #f0f0f0;
                border: 1px solid #cccccc;
                border-bottom-color: #cccccc;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 12px;
                margin-right: 2px;
                min-width: 150px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: #4CAF50;
                color: white;
            }
            QTabBar::tab:!selected {
                margin-top: 2px;
            }
        """)

                # Tạo các tab
        tab_feed = QWidget()        # Tab thành phần cám
        tab_mix = QWidget()         # Tab thành phần mix
        tab_batches = QWidget()     # Tab số mẻ theo khu và công thức

        # Thêm các tab vào TabWidget
        report_tabs.addTab(tab_feed, "Thành Phần Cám")
        report_tabs.addTab(tab_mix, "Thành Phần Mix")
        report_tabs.addTab(tab_batches, "Số Mẻ")

                # Thiết lập tab thành phần cám
        feed_layout = QVBoxLayout(tab_feed)

        # Tạo widget scroll cho nội dung tab thành phần cám
        feed_scroll = QScrollArea()
        feed_scroll.setWidgetResizable(True)
        feed_content = QWidget()
        feed_layout_scroll = QVBoxLayout(feed_content)

        # Thiết lập tab thành phần mix
        mix_layout = QVBoxLayout(tab_mix)

        # Tạo widget scroll cho nội dung tab thành phần mix
        mix_scroll = QScrollArea()
        mix_scroll.setWidgetResizable(True)
        mix_content = QWidget()
        mix_layout_scroll = QVBoxLayout(mix_content)

                # Tạo bảng thành phần cám
        feed_table = QTableWidget()
        feed_table.setFont(TABLE_CELL_FONT)
        feed_table.setColumnCount(4)  # Ingredient, Amount, Bags, Inventory
        feed_table.setHorizontalHeaderLabels(["Thành phần", "Số lượng (kg)", "Số bao", "Tồn kho (kg)"])
        feed_table.horizontalHeader().setFont(TABLE_HEADER_FONT)
        feed_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Đặt bảng ở chế độ chỉ đọc - không cho phép chỉnh sửa
        feed_table.setEditTriggers(QTableWidget.NoEditTriggers)
        feed_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #aaa;
                selection-background-color: #e0e0ff;
            }
            QHeaderView::section {
                background-color: #4CAF50;
                color: white;
                padding: 6px;
                border: 1px solid #ddd;
            }
        """)

        # Sắp xếp các thành phần để đưa bắp và nành lên đầu
        priority_ingredients = ["Bắp", "Nành"]
        sorted_feed_ingredients = {}

        # Thêm các thành phần ưu tiên trước
        for ingredient in priority_ingredients:
            if ingredient in self.feed_ingredients:
                sorted_feed_ingredients[ingredient] = self.feed_ingredients[ingredient]

        # Thêm các thành phần còn lại
        for ingredient, amount in self.feed_ingredients.items():
            if ingredient not in priority_ingredients:
                sorted_feed_ingredients[ingredient] = amount

        # Tính tổng số hàng cần thiết cho bảng cám
        feed_rows = len(sorted_feed_ingredients) + 2  # +2 cho tiêu đề và tổng cộng
        feed_table.setRowCount(feed_rows)

        # Thêm tiêu đề kho cám
        row = 0
        feed_header = QTableWidgetItem("THÀNH PHẦN KHO CÁM")
        feed_header.setFont(QFont("Arial", DEFAULT_FONT_SIZE + 2, QFont.Bold))  # Tăng kích thước font
        feed_header.setBackground(QColor(220, 240, 220))  # Light green background
        feed_table.setItem(row, 0, feed_header)
        feed_table.setSpan(row, 0, 1, 4)  # Merge cells for header across 4 columns

        row += 1

        # Thêm thành phần cám
        for ingredient, amount in sorted_feed_ingredients.items():
                        # Ingredient name
            ingredient_item = QTableWidgetItem(ingredient)
            ingredient_item.setFont(QFont("Arial", DEFAULT_FONT_SIZE + 1))  # Tăng kích thước font
            feed_table.setItem(row, 0, ingredient_item)

            # Amount
            amount_item = QTableWidgetItem(format_number(amount))
            amount_item.setFont(QFont("Arial", DEFAULT_FONT_SIZE + 1, QFont.Bold))  # Tăng kích thước và làm đậm số
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            feed_table.setItem(row, 1, amount_item)

            # Calculate bags
            bag_size = self.inventory_manager.get_bag_size(ingredient)
            bags = self.inventory_manager.calculate_bags(ingredient, amount)
            bags_item = QTableWidgetItem(format_number(bags))
            bags_item.setFont(QFont("Arial", DEFAULT_FONT_SIZE + 1))  # Tăng kích thước font
            bags_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            feed_table.setItem(row, 2, bags_item)

            # Add inventory information
            inventory_amount = self.inventory_manager.get_inventory().get(ingredient, 0)
            inventory_item = QTableWidgetItem(format_number(inventory_amount))
            inventory_item.setFont(QFont("Arial", DEFAULT_FONT_SIZE + 1))  # Tăng kích thước font
            inventory_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            inventory_item.setBackground(QColor(240, 248, 255))  # Light blue background
            feed_table.setItem(row, 3, inventory_item)

            row += 1

        # Thêm tổng cộng cho cám
        total_feed_amount = sum(self.feed_ingredients.values())

        total_feed_item = QTableWidgetItem("Tổng Cám")
        total_feed_item.setFont(QFont("Arial", DEFAULT_FONT_SIZE + 1, QFont.Bold))
        feed_table.setItem(row, 0, total_feed_item)

        total_feed_amount_item = QTableWidgetItem(format_number(total_feed_amount))
        total_feed_amount_item.setFont(QFont("Arial", DEFAULT_FONT_SIZE + 1, QFont.Bold))
        total_feed_amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        total_feed_amount_item.setBackground(QColor(220, 240, 220))  # Light green background
        feed_table.setItem(row, 1, total_feed_amount_item)

        # Tổng số bao cám (để trống vì không có ý nghĩa)
        feed_table.setItem(row, 2, QTableWidgetItem(""))

        # Tổng tồn kho cám (để trống vì không có ý nghĩa cho tổng)
        feed_table.setItem(row, 3, QTableWidgetItem(""))

        # Tăng chiều cao của các hàng để dễ nhìn hơn
        for row in range(feed_table.rowCount()):
            feed_table.setRowHeight(row, 50)  # Tăng chiều cao các hàng

                # Thiết lập bảng cám để kéo dài đến cuối tab
        feed_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        feed_table.setMinimumHeight(int(dialog_height * 0.7))  # Chiều cao tối thiểu 70% của dialog

        # Thêm bảng vào layout tab thành phần cám
        feed_layout_scroll.addWidget(feed_table)

        # Hoàn thành scroll area cho tab thành phần cám
        feed_scroll.setWidget(feed_content)
        feed_layout.addWidget(feed_scroll)

        # Tạo bảng thành phần mix
        mix_table = QTableWidget()
        mix_table.setFont(TABLE_CELL_FONT)
        mix_table.setColumnCount(4)  # Ingredient, Amount, Bags, Inventory
        mix_table.setHorizontalHeaderLabels(["Thành phần", "Số lượng (kg)", "Số bao", "Tồn kho (kg)"])
        mix_table.horizontalHeader().setFont(TABLE_HEADER_FONT)
        mix_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Đặt bảng ở chế độ chỉ đọc - không cho phép chỉnh sửa
        mix_table.setEditTriggers(QTableWidget.NoEditTriggers)
        mix_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #aaa;
                selection-background-color: #e0e0ff;
            }
            QHeaderView::section {
                background-color: #FF9800;
                color: white;
                padding: 6px;
                border: 1px solid #ddd;
            }
        """)

        # Tính tổng số hàng cần thiết cho bảng mix
        mix_rows = len(self.mix_ingredients) + 2  # +2 cho tiêu đề và tổng cộng
        mix_table.setRowCount(mix_rows)

        # Thêm tiêu đề kho mix
        row = 0
        mix_header = QTableWidgetItem("THÀNH PHẦN KHO MIX")
        mix_header.setFont(QFont("Arial", DEFAULT_FONT_SIZE + 2, QFont.Bold))  # Tăng kích thước font
        mix_header.setBackground(QColor(240, 220, 220))  # Light red background
        mix_table.setItem(row, 0, mix_header)
        mix_table.setSpan(row, 0, 1, 4)  # Merge cells for header across 4 columns

        row += 1

        # Thêm thành phần mix
        for ingredient, amount in self.mix_ingredients.items():
                        # Ingredient name
            ingredient_item = QTableWidgetItem(ingredient)
            ingredient_item.setFont(QFont("Arial", DEFAULT_FONT_SIZE + 1))  # Tăng kích thước font
            mix_table.setItem(row, 0, ingredient_item)

            # Amount
            amount_item = QTableWidgetItem(format_number(amount))
            amount_item.setFont(QFont("Arial", DEFAULT_FONT_SIZE + 1, QFont.Bold))  # Tăng kích thước và làm đậm số
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            mix_table.setItem(row, 1, amount_item)

            # Calculate bags
            bag_size = self.inventory_manager.get_bag_size(ingredient)
            bags = self.inventory_manager.calculate_bags(ingredient, amount)
            bags_item = QTableWidgetItem(format_number(bags))
            bags_item.setFont(QFont("Arial", DEFAULT_FONT_SIZE + 1))  # Tăng kích thước font
            bags_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            mix_table.setItem(row, 2, bags_item)

            # Add inventory information
            inventory_amount = self.inventory_manager.get_inventory().get(ingredient, 0)
            inventory_item = QTableWidgetItem(format_number(inventory_amount))
            inventory_item.setFont(QFont("Arial", DEFAULT_FONT_SIZE + 1))  # Tăng kích thước font
            inventory_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            inventory_item.setBackground(QColor(255, 245, 230))  # Light orange background
            mix_table.setItem(row, 3, inventory_item)

            row += 1

        # Thêm tổng cộng cho mix
        total_mix_amount = sum(self.mix_ingredients.values())

        total_mix_item = QTableWidgetItem("Tổng Mix")
        total_mix_item.setFont(QFont("Arial", DEFAULT_FONT_SIZE + 1, QFont.Bold))
        mix_table.setItem(row, 0, total_mix_item)

        total_mix_amount_item = QTableWidgetItem(format_number(total_mix_amount))
        total_mix_amount_item.setFont(QFont("Arial", DEFAULT_FONT_SIZE + 1, QFont.Bold))
        total_mix_amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        total_mix_amount_item.setBackground(QColor(240, 220, 220))  # Light red background
        mix_table.setItem(row, 1, total_mix_amount_item)

        # Tổng số bao mix (để trống vì không có ý nghĩa)
        mix_table.setItem(row, 2, QTableWidgetItem(""))

        # Tổng tồn kho mix (để trống vì không có ý nghĩa cho tổng)
        mix_table.setItem(row, 3, QTableWidgetItem(""))

        # Tăng chiều cao của các hàng để dễ nhìn hơn
        for row in range(mix_table.rowCount()):
            mix_table.setRowHeight(row, 50)  # Tăng chiều cao các hàng

                # Thiết lập bảng mix để kéo dài đến cuối tab
        mix_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        mix_table.setMinimumHeight(int(dialog_height * 0.7))  # Chiều cao tối thiểu 70% của dialog

        # Thêm bảng vào layout tab thành phần mix
        mix_layout_scroll.addWidget(mix_table)

        # Hoàn thành scroll area cho tab thành phần mix
        mix_scroll.setWidget(mix_content)
        mix_layout.addWidget(mix_scroll)

        # Thiết lập tab số mẻ
        batches_layout = QVBoxLayout(tab_batches)

        # Tạo widget scroll cho nội dung tab số mẻ
        batches_scroll = QScrollArea()
        batches_scroll.setWidgetResizable(True)
        batches_content = QWidget()
        batches_layout_scroll = QVBoxLayout(batches_content)

        # Thêm bảng tổng số mẻ
        batches_summary_label = QLabel("<b>Tổng số mẻ:</b>")
        batches_summary_label.setFont(QFont("Arial", DEFAULT_FONT_SIZE + 1, QFont.Bold))
        batches_layout_scroll.addWidget(batches_summary_label)

        # Tạo bảng tổng số mẻ trong ngày
        total_batches_table = QTableWidget()
        total_batches_table.setFont(TABLE_CELL_FONT)
        total_batches_table.setColumnCount(2)
        total_batches_table.setHorizontalHeaderLabels(["Mô tả", "Số mẻ"])
        total_batches_table.horizontalHeader().setFont(TABLE_HEADER_FONT)
        total_batches_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Đặt bảng ở chế độ chỉ đọc - không cho phép chỉnh sửa
        total_batches_table.setEditTriggers(QTableWidget.NoEditTriggers)
        total_batches_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #aaa;
                selection-background-color: #e0e0ff;
            }
            QHeaderView::section {
                background-color: #3F51B5;
                color: white;
                padding: 6px;
                border: 1px solid #ddd;
            }
        """)

        # Tính tổng số mẻ trong ngày
        total_day_batches = 0
        for khu, batches in self.total_batches_by_area.items():
            total_day_batches += batches

        # Thêm hàng tổng số mẻ trong ngày
        total_batches_table.setRowCount(1)
        total_batches_table.setItem(0, 0, QTableWidgetItem("Tổng số mẻ trong ngày"))
        total_batches_item = QTableWidgetItem(format_number(total_day_batches))
        total_batches_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        total_batches_item.setFont(QFont("Arial", DEFAULT_FONT_SIZE, QFont.Bold))
        total_batches_item.setBackground(QColor(230, 240, 250))
        total_batches_table.setItem(0, 1, total_batches_item)

        # Đặt chiều cao hàng
        total_batches_table.setRowHeight(0, 50)  # Tăng chiều cao hàng

        # Thêm bảng vào layout tab số mẻ
        batches_layout_scroll.addWidget(total_batches_table)

        # Tạo bảng tổng số mẻ theo khu
        khu_batches_label = QLabel("<b>Tổng số mẻ theo khu:</b>")
        khu_batches_label.setFont(QFont("Arial", DEFAULT_FONT_SIZE + 1, QFont.Bold))
        batches_layout_scroll.addWidget(khu_batches_label)

        khu_batches_table = QTableWidget()
        khu_batches_table.setFont(TABLE_CELL_FONT)
        khu_batches_table.setColumnCount(2)
        khu_batches_table.setHorizontalHeaderLabels(["Khu", "Số mẻ"])
        khu_batches_table.horizontalHeader().setFont(TABLE_HEADER_FONT)
        khu_batches_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Đặt bảng ở chế độ chỉ đọc - không cho phép chỉnh sửa
        khu_batches_table.setEditTriggers(QTableWidget.NoEditTriggers)
        khu_batches_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #aaa;
                selection-background-color: #e0e0ff;
            }
            QHeaderView::section {
                background-color: #3F51B5;
                color: white;
                padding: 6px;
                border: 1px solid #ddd;
            }
        """)

        # Thêm dữ liệu tổng số mẻ theo khu
        khu_batches_table.setRowCount(len(self.total_batches_by_area))
        row = 0
        for khu, batches in sorted(self.total_batches_by_area.items()):
            khu_batches_table.setItem(row, 0, QTableWidgetItem(khu))
            batches_item = QTableWidgetItem(format_number(batches))
            batches_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            khu_batches_table.setItem(row, 1, batches_item)
            khu_batches_table.setRowHeight(row, 50)  # Tăng chiều cao hàng
            row += 1

        # Thêm bảng vào layout tab số mẻ
        batches_layout_scroll.addWidget(khu_batches_table)

        # Tạo bảng tổng số mẻ theo công thức
        formula_batches_label = QLabel("<b>Tổng số mẻ theo công thức:</b>")
        formula_batches_label.setFont(QFont("Arial", DEFAULT_FONT_SIZE + 1, QFont.Bold))
        batches_layout_scroll.addWidget(formula_batches_label)

        formula_batches_table = QTableWidget()
        formula_batches_table.setFont(TABLE_CELL_FONT)
        formula_batches_table.setColumnCount(3)
        formula_batches_table.setHorizontalHeaderLabels(["Công thức", "Số lượng", "Số mẻ"])
        formula_batches_table.horizontalHeader().setFont(TABLE_HEADER_FONT)
        formula_batches_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Đặt bảng ở chế độ chỉ đọc - không cho phép chỉnh sửa
        formula_batches_table.setEditTriggers(QTableWidget.NoEditTriggers)
        formula_batches_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #aaa;
                selection-background-color: #e0e0ff;
            }
            QHeaderView::section {
                background-color: #3F51B5;
                color: white;
                padding: 6px;
                border: 1px solid #ddd;
            }
        """)

        # Thêm dữ liệu tổng số mẻ theo công thức
        formula_batches_table.setRowCount(len(self.formula_ingredients))
        row = 0
        for formula_name, data in sorted(self.formula_ingredients.items(), key=lambda x: x[0]):
            batches = data["batches"]
            actual_batches = batches * 2  # Số mẻ thực tế = giá trị hiển thị * 2

            formula_item = QTableWidgetItem(formula_name)
            formula_batches_table.setItem(row, 0, formula_item)

            batches_value_item = QTableWidgetItem(format_number(batches))
            batches_value_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            formula_batches_table.setItem(row, 1, batches_value_item)

            actual_batches_item = QTableWidgetItem(format_number(actual_batches))
            actual_batches_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            formula_batches_table.setItem(row, 2, actual_batches_item)

            formula_batches_table.setRowHeight(row, 50)  # Tăng chiều cao hàng
            row += 1

        # Thêm bảng vào layout tab số mẻ
        batches_layout_scroll.addWidget(formula_batches_table)
        batches_layout_scroll.addStretch()

        # Hoàn thành scroll area cho tab số mẻ
        batches_scroll.setWidget(batches_content)
        batches_layout.addWidget(batches_scroll)

        # Thêm tiêu đề "Chỉ xem" cho TabWidget
        readonly_label = QLabel("(Chỉ xem - Không thể chỉnh sửa)")
        italic_font = QFont("Arial", DEFAULT_FONT_SIZE)
        italic_font.setItalic(True)
        readonly_label.setFont(italic_font)
        readonly_label.setAlignment(Qt.AlignCenter)
        readonly_label.setStyleSheet("QLabel { color: #777; margin-bottom: 5px; }")
        main_layout.addWidget(readonly_label)

        # Thêm TabWidget vào layout chính
        main_layout.addWidget(report_tabs)

        # Thêm các nút lưu và xuất Excel
        button_layout = QHBoxLayout()

        save_button = QPushButton("Lưu Báo Cáo")
        save_button.setFont(BUTTON_FONT)
        save_button.setMinimumHeight(40)
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        save_button.clicked.connect(self.save_report)

        export_button = QPushButton("Xuất Excel")
        export_button.setFont(BUTTON_FONT)
        export_button.setMinimumHeight(40)
        export_button.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #e68a00;
            }
        """)
        export_button.clicked.connect(self.export_to_excel)

        close_button = QPushButton("Đóng")
        close_button.setFont(BUTTON_FONT)
        close_button.setMinimumHeight(40)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        close_button.clicked.connect(report_dialog.close)

        button_layout.addWidget(save_button)
        button_layout.addWidget(export_button)
        button_layout.addWidget(close_button)

        main_layout.addLayout(button_layout)

        # Hiển thị dialog
        report_dialog.exec_()

    def load_default_formula(self):
        """Tải công thức mặc định khi khởi động app"""
        if self.default_formula_loaded:
            return

        default_formula = self.formula_manager.get_default_feed_formula()
        print(f"Tải công thức mặc định: {default_formula}")

        # Chỉ thiết lập khi có công thức mặc định
        if default_formula:
            self.default_formula_combo.setCurrentText(default_formula)
            # KHÔNG áp dụng công thức mặc định cho tất cả các ô khi khởi động
            # Chỉ lưu thông tin công thức mặc định để sử dụng khi người dùng nhập mẻ mới

        self.default_formula_loaded = True

    def on_feed_table_cell_clicked(self, row, column):
        """Xử lý sự kiện khi người dùng click vào một ô trong bảng"""
        # Chỉ xử lý các ô chứa dữ liệu cám (bỏ qua hàng khu và trại)
        if row < 2:
            return

        # Lấy widget container trong ô
        cell_widget = self.feed_table.cellWidget(row, column)
        if not cell_widget:
            return

        # Lưu lại ô đang được chọn
        self.selected_cell = (row, column)

        # Đổi màu nền để hiển thị ô đang được chọn
        for r in range(2, self.feed_table.rowCount()):
            for c in range(self.feed_table.columnCount()):
                widget = self.feed_table.cellWidget(r, c)
                if widget:
                    # Lấy màu nền gốc từ khu tương ứng
                    original_c = c  # Lưu lại giá trị c ban đầu
                    khu_idx = -1
                    for idx, farms in FARMS.items():
                        if original_c < len(farms):
                            khu_idx = idx
                            break
                        original_c -= len(farms)

                    khu_colors = [
                        QColor(240, 248, 255),  # Khu 1: Alice Blue
                        QColor(245, 245, 220),  # Khu 2: Beige
                        QColor(240, 255, 240),  # Khu 3: Honeydew
                        QColor(255, 240, 245),  # Khu 4: Lavender Blush
                        QColor(255, 250, 240),  # Khu 5: Floral White
                    ]

                    if r == row and c == column:
                        # Đổi màu nền cho ô được chọn - xanh nhạt đậm hơn
                        widget.setStyleSheet(f"background-color: #b3e5fc;")
                    else:
                        # Khôi phục màu nền gốc cho các ô khác dựa trên khu
                        if 0 <= khu_idx < len(khu_colors):
                            widget.setStyleSheet(f"background-color: {khu_colors[khu_idx].name()};")
                        else:
                            widget.setStyleSheet("")

        # Hiển thị menu ngữ cảnh khi click vào ô
        self.show_cell_context_menu(row, column)

    def show_cell_context_menu(self, row, column):
        """Hiển thị menu ngữ cảnh khi click vào ô trong bảng cám"""
        # Lấy widget container trong ô
        cell_widget = self.feed_table.cellWidget(row, column)
        if not cell_widget or not hasattr(cell_widget, 'spin_box') or not hasattr(cell_widget, 'formula_combo'):
            return

        # Chỉ hiển thị menu nếu đã nhập số lượng mẻ > 0
        if cell_widget.spin_box.value() <= 0:
            return

        # Lấy thông tin khu và trại
        khu_item = self.feed_table.item(0, column)
        farm_item = self.feed_table.item(1, column)

        if not khu_item or not farm_item:
            return

        khu_name = khu_item.text()
        farm_name = farm_item.text()
        shift = SHIFTS[row - 2]  # Trừ 2 vì 2 hàng đầu là khu và trại

        # Tạo menu ngữ cảnh
        context_menu = QMenu(self)

        # Thêm tiêu đề cho menu
        title_action = QAction(f"{khu_name} - {farm_name} - {shift}", self)
        title_action.setEnabled(False)
        title_font = title_action.font()
        title_font.setBold(True)
        title_action.setFont(title_font)
        context_menu.addAction(title_action)
        context_menu.addSeparator()

        # Thêm submenu cho công thức cám
        feed_menu = QMenu("Chọn công thức cám", self)

        # Lấy danh sách công thức cám
        feed_presets = self.formula_manager.get_feed_presets()
        current_feed_formula = cell_widget.formula_combo.currentText()

        # Thêm các công thức cám vào menu
        for preset in sorted(feed_presets):
            action = QAction(preset, self)
            action.setCheckable(True)
            action.setChecked(preset == current_feed_formula)
            action.triggered.connect(lambda checked, formula=preset: self.apply_formula_to_selected_cell(formula))
            feed_menu.addAction(action)

        context_menu.addMenu(feed_menu)

        # Thêm submenu cho công thức mix
        mix_menu = QMenu("Chọn công thức mix", self)

        # Lấy danh sách công thức mix
        mix_presets = self.formula_manager.get_mix_presets()

        # Lấy cell key để kiểm tra công thức mix hiện tại
        cell_key = f"{khu_name}_{farm_name}_{shift}"
        current_mix_formula = ""

        # Kiểm tra xem ô này đã có công thức mix được chọn chưa
        if hasattr(self, 'cell_mix_formulas') and cell_key in self.cell_mix_formulas:
            current_mix_formula = self.cell_mix_formulas[cell_key]

        # Tìm công thức mix theo cột
        column_mix_formula = ""
        col_key = f"{column}"
        if hasattr(self, 'column_mix_formulas') and col_key in self.column_mix_formulas:
            column_mix_formula = self.column_mix_formulas[col_key]

        # Thêm tùy chọn "Không chọn" (sử dụng công thức mix của cột)
        no_mix_action = QAction("Không chọn (sử dụng công thức mix của cột)", self)
        no_mix_action.setCheckable(True)
        no_mix_action.setChecked(current_mix_formula == "")
        no_mix_action.triggered.connect(lambda checked: self.apply_mix_formula_to_cell(cell_key, ""))
        mix_menu.addAction(no_mix_action)

        # Hiển thị công thức mix của cột nếu có
        if column_mix_formula:
            column_mix_info = QAction(f"Công thức mix của cột: {column_mix_formula}", self)
            column_mix_info.setEnabled(False)
            mix_menu.addAction(column_mix_info)

        mix_menu.addSeparator()

        # Thêm các công thức mix vào menu
        for preset in sorted(mix_presets):
            action = QAction(preset, self)
            action.setCheckable(True)
            action.setChecked(preset == current_mix_formula)
            action.triggered.connect(lambda checked, formula=preset: self.apply_mix_formula_to_cell(cell_key, formula))
            mix_menu.addAction(action)

        context_menu.addMenu(mix_menu)

        # Hiển thị menu tại vị trí chuột
        context_menu.exec_(QCursor.pos())

    def apply_mix_formula_to_cell(self, cell_key, mix_formula):
        """Áp dụng công thức mix cho ô đã chọn"""
        if not hasattr(self, 'cell_mix_formulas'):
            self.cell_mix_formulas = {}

        if mix_formula:
            # Lưu công thức mix cho ô này
            self.cell_mix_formulas[cell_key] = mix_formula

            # Hiển thị thông báo
            parts = cell_key.split('_')
            if len(parts) >= 3:
                khu, farm, shift = parts[0], parts[1], parts[2]
                QMessageBox.information(self, "Thông tin", f"Đã áp dụng công thức Mix '{mix_formula}' cho {khu} - {farm} - {shift}")
        else:
            # Xóa công thức mix cho ô này (sử dụng công thức mix của khu)
            if cell_key in self.cell_mix_formulas:
                del self.cell_mix_formulas[cell_key]

            # Hiển thị thông báo
            parts = cell_key.split('_')
            if len(parts) >= 3:
                khu, farm, shift = parts[0], parts[1], parts[2]
                QMessageBox.information(self, "Thông tin", f"Đã xóa công thức Mix riêng cho {khu} - {farm} - {shift} (sẽ sử dụng công thức Mix của cột)")

        # Lưu cài đặt công thức mix cho từng ô vào báo cáo hiện tại
        if hasattr(self, 'current_report_data') and self.current_report_data:
            self.current_report_data["cell_mix_formulas"] = self.cell_mix_formulas

            # Lưu báo cáo hiện tại
            if "date" in self.current_report_data:
                date_str = self.current_report_data["date"]
                report_file = f"src/data/reports/report_{date_str}.json"
                try:
                    with open(report_file, 'w', encoding='utf-8') as f:
                        json.dump(self.current_report_data, f, ensure_ascii=False, indent=4)
                except Exception as e:
                    print(f"Lỗi khi lưu công thức mix cho từng ô: {e}")

        # Cập nhật hiển thị bảng để hiện dấu hiệu có công thức mix riêng
        self.update_feed_table_display()

    def update_feed_table_display(self):
        """Cập nhật hiển thị bảng cám dựa trên giá trị và công thức đã chọn"""
        for col in range(self.feed_table.columnCount()):
            for row in range(2, 2 + len(SHIFTS)):
                cell_widget = self.feed_table.cellWidget(row, col)
                if not cell_widget or not hasattr(cell_widget, 'spin_box') or not hasattr(cell_widget, 'formula_combo'):
                    continue

                # Lấy giá trị và công thức
                value = cell_widget.spin_box.value()
                formula_text = cell_widget.formula_combo.currentText()
                default_formula = self.default_formula_combo.currentText()

                # Cập nhật hiển thị
                if value == 0:
                    # Ẩn label công thức
                    cell_widget.formula_label.setVisible(False)
                    # Mở rộng spinbox để chiếm toàn bộ không gian
                    cell_widget.layout().setStretch(0, 100)
                    cell_widget.layout().setStretch(1, 0)
                else:
                    # Lấy thông tin khu và trại
                    khu_item = self.feed_table.item(0, col)
                    farm_item = self.feed_table.item(1, col)

                    if khu_item and farm_item:
                        khu_name = khu_item.text()
                        farm_name = farm_item.text()
                        shift = SHIFTS[row - 2]  # Trừ 2 vì 2 hàng đầu là khu và trại

                        cell_key = f"{khu_name}_{farm_name}_{shift}"
                        has_custom_mix = hasattr(self, 'cell_mix_formulas') and cell_key in self.cell_mix_formulas

                        # Kiểm tra xem có phải công thức mặc định không
                        if formula_text and formula_text != default_formula:
                            # Nếu không phải công thức mặc định, hiển thị tên
                            display_text = formula_text
                            cell_widget.formula_label.setText(display_text)
                            cell_widget.formula_label.setVisible(True)
                            # Khôi phục tỷ lệ ban đầu
                            cell_widget.layout().setStretch(0, 60)
                            cell_widget.layout().setStretch(1, 40)
                        else:
                            # Nếu là công thức mặc định hoặc không có công thức, ẩn label
                            cell_widget.formula_label.setVisible(False)
                            # Mở rộng spinbox để chiếm toàn bộ không gian
                            cell_widget.layout().setStretch(0, 100)
                            cell_widget.layout().setStretch(1, 0)

    def apply_formula_to_selected_cell(self, formula):
        """Áp dụng công thức cám cho ô đang được chọn"""
        if not self.selected_cell:
            return

        row, column = self.selected_cell
        cell_widget = self.feed_table.cellWidget(row, column)

        if not cell_widget or not hasattr(cell_widget, 'spin_box') or not hasattr(cell_widget, 'formula_combo'):
            return

        # Chỉ áp dụng công thức nếu đã nhập số lượng mẻ > 0
        if cell_widget.spin_box.value() > 0:
            try:
                # Thiết lập công thức
                cell_widget.formula_combo.setCurrentText(formula)

                # Cập nhật hiển thị toàn bộ bảng
                self.update_feed_table_display()
            except Exception as e:
                print(f"Lỗi khi áp dụng công thức: {str(e)}")

    def auto_select_default_formula(self, value, combo):
        """Tự động chọn công thức mặc định khi người dùng nhập số lượng mẻ"""
        # Nếu đã chọn công thức rồi thì không thay đổi
        if combo.currentText():
            return

        # Nếu người dùng nhập giá trị > 0 và chưa chọn công thức, tự động chọn công thức mặc định
        if value > 0:
            default_formula = self.default_formula_combo.currentText()
            if default_formula:
                # Tạm ngắt kết nối sự kiện để tránh gọi lại nhiều lần
                old_handlers = []
                if combo.receivers(combo.currentTextChanged) > 0:
                    old_handlers = [combo.currentTextChanged.disconnect() for _ in range(combo.receivers(combo.currentTextChanged))]

                # Thiết lập công thức
                combo.setCurrentText(default_formula)

                # Kết nối lại các sự kiện nếu có
                for handler in old_handlers:
                    if handler:
                        combo.currentTextChanged.connect(handler)

    def apply_default_formula(self):
        """Áp dụng công thức cám mặc định cho tất cả các ô trong bảng khi thay đổi công thức mặc định"""
        default_formula = self.default_formula_combo.currentText()

        # Lưu công thức mặc định để khi khởi động lại app không bị mất
        self.formula_manager.save_default_feed_formula(default_formula)

        # Nếu không có công thức mặc định, chỉ lưu và không áp dụng
        if not default_formula:
            return

        # Kiểm tra xem feed_table đã được tạo chưa
        if not hasattr(self, 'feed_table'):
            return

        # Áp dụng cho tất cả các ô trong bảng
        for col in range(self.feed_table.columnCount()):
            for row in range(2, 2 + len(SHIFTS)):
                cell_widget = self.feed_table.cellWidget(row, col)
                if cell_widget and hasattr(cell_widget, 'formula_combo'):
                    cell_widget.formula_combo.setCurrentText(default_formula)

        # Kiểm tra xem phương thức update_feed_table_display đã tồn tại chưa
        if hasattr(self, 'update_feed_table_display'):
            # Cập nhật hiển thị bảng
            self.update_feed_table_display()
        if not default_formula:
            return

        # Áp dụng cho tất cả các ô trong bảng
        for col in range(self.feed_table.columnCount()):
            for row in range(2, 2 + len(SHIFTS)):
                cell_widget = self.feed_table.cellWidget(row, col)
                if cell_widget and hasattr(cell_widget, 'formula_combo'):
                    cell_widget.formula_combo.setCurrentText(default_formula)

        # Cập nhật hiển thị bảng
        self.update_feed_table_display()

    def setup_inventory_tab(self):
        """Setup the inventory management tab"""
        layout = QVBoxLayout()

        # Create tabs for Feed and Mix inventory
        inventory_tabs = QTabWidget()
        inventory_tabs.setFont(DEFAULT_FONT)
        inventory_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background: white;
            }
            QTabWidget::tab-bar {
                left: 5px;
            }
            QTabBar::tab {
                background: #f0f0f0;
                border: 1px solid #cccccc;
                border-bottom-color: #cccccc;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 12px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #4CAF50;
                color: white;
            }
            QTabBar::tab:!selected {
                margin-top: 2px;
            }
        """)

        feed_inventory_tab = QWidget()
        mix_inventory_tab = QWidget()

        inventory_tabs.addTab(feed_inventory_tab, "Kho Cám")
        inventory_tabs.addTab(mix_inventory_tab, "Kho Mix")

        # Setup Feed Inventory tab
        feed_layout = QVBoxLayout()

        # Thêm tiêu đề
        feed_header = QLabel("Quản Lý Kho Cám")
        feed_header.setFont(HEADER_FONT)
        feed_header.setAlignment(Qt.AlignCenter)
        feed_header.setStyleSheet("QLabel { padding: 10px; background-color: #e0f2f1; border-radius: 5px; }")
        feed_layout.addWidget(feed_header)

        self.feed_inventory_table = QTableWidget()
        self.feed_inventory_table.setFont(TABLE_CELL_FONT)
        self.feed_inventory_table.setColumnCount(4)
        self.feed_inventory_table.setHorizontalHeaderLabels(["Thành phần", "Tồn kho (kg)", "Kích thước bao (kg)", "Số bao"])
        self.feed_inventory_table.horizontalHeader().setFont(TABLE_HEADER_FONT)
        self.feed_inventory_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.feed_inventory_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #aaa;
                selection-background-color: #e0e0ff;
                alternate-background-color: #f9f9f9;
            }
            QHeaderView::section {
                background-color: #4CAF50;
                color: white;
                padding: 6px;
                border: 1px solid #ddd;
            }
            QTableWidget::item {
                padding: 4px;
            }
        """)
        self.feed_inventory_table.setAlternatingRowColors(True)

        # Populate feed inventory table
        self.update_feed_inventory_table()

        feed_layout.addWidget(self.feed_inventory_table)

        # Add update button for feed inventory
        update_feed_button = QPushButton("Cập Nhật Kho Cám")
        update_feed_button.setFont(BUTTON_FONT)
        update_feed_button.setMinimumHeight(40)
        update_feed_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        update_feed_button.clicked.connect(lambda: self.update_inventory("feed"))
        feed_layout.addWidget(update_feed_button)

        feed_inventory_tab.setLayout(feed_layout)

        # Setup Mix Inventory tab
        mix_layout = QVBoxLayout()

        # Thêm tiêu đề
        mix_header = QLabel("Quản Lý Kho Mix")
        mix_header.setFont(HEADER_FONT)
        mix_header.setAlignment(Qt.AlignCenter)
        mix_header.setStyleSheet("QLabel { padding: 10px; background-color: #e8f5e9; border-radius: 5px; }")
        mix_layout.addWidget(mix_header)

        self.mix_inventory_table = QTableWidget()
        self.mix_inventory_table.setFont(TABLE_CELL_FONT)
        self.mix_inventory_table.setColumnCount(4)
        self.mix_inventory_table.setHorizontalHeaderLabels(["Thành phần", "Tồn kho (kg)", "Kích thước bao (kg)", "Số bao"])
        self.mix_inventory_table.horizontalHeader().setFont(TABLE_HEADER_FONT)
        self.mix_inventory_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.mix_inventory_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #aaa;
                selection-background-color: #e0e0ff;
                alternate-background-color: #f9f9f9;
            }
            QHeaderView::section {
                background-color: #8BC34A;
                color: white;
                padding: 6px;
                border: 1px solid #ddd;
            }
            QTableWidget::item {
                padding: 4px;
            }
        """)
        self.mix_inventory_table.setAlternatingRowColors(True)

        # Populate mix inventory table
        self.update_mix_inventory_table()

        mix_layout.addWidget(self.mix_inventory_table)

        # Add update button for mix inventory
        update_mix_button = QPushButton("Cập Nhật Kho Mix")
        update_mix_button.setFont(BUTTON_FONT)
        update_mix_button.setMinimumHeight(40)
        update_mix_button.setStyleSheet("""
            QPushButton {
                background-color: #8BC34A;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #7CB342;
            }
        """)
        update_mix_button.clicked.connect(lambda: self.update_inventory("mix"))
        mix_layout.addWidget(update_mix_button)

        mix_inventory_tab.setLayout(mix_layout)

        # Add tabs to layout
        layout.addWidget(inventory_tabs)

        self.inventory_tab.setLayout(layout)

def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(create_app_icon())

    # Thiết lập font mặc định cho toàn bộ ứng dụng
    app.setFont(DEFAULT_FONT)

    window = ChickenFarmApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
