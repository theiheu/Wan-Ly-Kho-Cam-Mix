import sys
import os
import json
import subprocess
import pandas as pd
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout,
                            QHBoxLayout, QGridLayout, QLabel, QLineEdit, QPushButton,
                            QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
                            QMessageBox, QFileDialog, QSpinBox, QDoubleSpinBox, QInputDialog,
                            QGroupBox, QDialog, QRadioButton, QDateEdit, QScrollArea, QSizePolicy,
                            QMenu, QAction, QAbstractSpinBox, QAbstractItemView, QCalendarWidget,
                            QCheckBox, QListWidget, QListWidgetItem, QTextEdit)
from PyQt5.QtCore import Qt, QDate, QTimer
from PyQt5.QtGui import QFont, QColor, QCursor, QBrush

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

def format_total(value):
    """Format total numbers (feed/mix) as integers without decimal places"""
    # Nếu giá trị là 0, trả về chuỗi rỗng
    if value == 0:
        return ""

    # Làm tròn thành số nguyên và định dạng với dấu phẩy ngăn cách hàng nghìn
    return f"{int(round(value)):,}"

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

        # Initialize responsive design utilities
        self.init_responsive_design()

        # Setup main window with responsive sizing
        self.setup_responsive_main_window()

        # Set application icon
        self.setWindowIcon(create_app_icon())

        # Initialize managers and data
        self.init_managers_and_data()

        # Initialize UI components
        try:
            print("Initializing UI...")
            self.init_ui()
            print("UI initialization completed successfully")
        except Exception as e:
            print(f"Error during UI initialization: {e}")
            import traceback
            traceback.print_exc()

    def init_responsive_design(self):
        """Initialize responsive design utilities and screen information"""
        # Get screen information
        screen = QApplication.primaryScreen()
        self.screen_geometry = screen.geometry()
        self.screen_width = self.screen_geometry.width()
        self.screen_height = self.screen_geometry.height()
        self.screen_dpi = screen.logicalDotsPerInch()

        # Calculate responsive scaling factors
        width_scale = self.screen_width / 1920
        height_scale = self.screen_height / 1080
        self.scale_factor = min(width_scale, height_scale)

        # Apply optimized scaling for perfect display compatibility
        if self.screen_width < 1366:
            # For small screens, extremely compact scaling with 0.10 target
            self.scale_factor = max(0.08, min(0.12, self.scale_factor))
        elif self.screen_width == 1366:
            # Ultra-compact for 1366x768 - 0.30 scale factor for maximum density
            self.scale_factor = max(0.25, min(0.35, self.scale_factor))
        elif self.screen_width <= 1600:
            # Balanced for medium screens
            self.scale_factor = max(0.75, min(1.0, self.scale_factor))
        else:
            # For large screens, use original range
            self.scale_factor = max(0.8, min(1.5, self.scale_factor))

        # Define responsive breakpoints
        self.is_small_screen = self.screen_width < 1366
        self.is_medium_screen = 1366 <= self.screen_width < 1920
        self.is_large_screen = self.screen_width >= 1920

        # Calculate responsive dimensions for perfect display compatibility
        if self.is_small_screen:
            # Extremely compact ratios for small screens with 0.10 scale factor
            self.responsive_dialog_width_ratio = 0.95
            self.responsive_dialog_height_ratio = 0.92
        elif self.is_medium_screen:
            if self.screen_width == 1366:
                # Optimized ratios for 1366x768 - perfect fit without cutoff
                self.responsive_dialog_width_ratio = 0.88
                self.responsive_dialog_height_ratio = 0.85
            else:
                self.responsive_dialog_width_ratio = 0.85
                self.responsive_dialog_height_ratio = 0.82
        else:  # large screen
            self.responsive_dialog_width_ratio = 0.80
            self.responsive_dialog_height_ratio = 0.80

        # Enhanced debug information for optimized scale factors
        screen_category = "Small" if self.is_small_screen else "Medium" if self.is_medium_screen else "Large"

        if self.screen_width < 1366:
            compact_info = " (EXTREME-COMPACT-0.10)"
        elif self.screen_width == 1366:
            compact_info = " (ULTRA-COMPACT-0.30)"
        else:
            compact_info = ""

        print(f"Screen: {self.screen_width}x{self.screen_height} ({screen_category}{compact_info})")
        print(f"Scale Factor: {self.scale_factor:.3f}")
        print(f"Dialog Ratios: {self.responsive_dialog_width_ratio:.2f}w x {self.responsive_dialog_height_ratio:.2f}h")
        dialog_w, dialog_h = self.get_responsive_dialog_size()
        print(f"Dialog Size: {dialog_w}x{dialog_h}px")
        print(f"Extreme-Compact Font: 12px → {self.get_responsive_font_size(12)}px")
        print(f"Extreme-Compact Row: 30px → {self.get_responsive_row_height(30)}px")
        print(f"Extreme-Compact Table: 500px → {self.get_responsive_table_height(500)}px")
        print("Extreme-Compact Design: 0.10 scale factor for maximum information density")

    def setup_responsive_main_window(self):
        """Setup main window with responsive sizing"""
        # Calculate responsive window size
        if self.is_small_screen:
            window_width = int(self.screen_width * 0.98)
            window_height = int(self.screen_height * 0.95)
        elif self.is_large_screen:
            window_width = int(self.screen_width * 0.90)
            window_height = int(self.screen_height * 0.85)
        else:
            window_width = int(self.screen_width * 0.95)
            window_height = int(self.screen_height * 0.90)

        # Calculate position to center window
        x_position = (self.screen_width - window_width) // 2
        y_position = (self.screen_height - window_height) // 2

        # Set window geometry
        self.setGeometry(x_position, y_position, window_width, window_height)

    def get_responsive_font_size(self, base_size):
        """Get responsive font size optimized for perfect display compatibility"""
        # Balanced scaling for optimal readability and fit
        scaled_size = int(base_size * self.scale_factor * 0.8)  # 20% reduction for balance

        # Apply balanced screen-specific font size constraints
        if self.is_small_screen:
            return max(7, min(9, scaled_size))   # Extremely compact fonts for small screens with 0.10 scale
        elif self.is_medium_screen:
            # Ultra-compact handling for 1366x768 with 0.30 scale factor
            if self.screen_width == 1366:
                return max(8, min(10, scaled_size))  # Ultra-compact for 1366x768 with 0.30 scale
            else:
                return max(10, min(13, scaled_size))  # Compact for other medium screens
        else:
            return max(11, min(15, scaled_size))  # Controlled fonts for large screens

    def get_responsive_dimension(self, base_dimension):
        """Get responsive dimension based on screen scale"""
        return max(20, int(base_dimension * self.scale_factor))

    def get_responsive_dialog_size(self, base_width_ratio=0.80, base_height_ratio=0.80):
        """Get responsive dialog size with perfect screen fit guarantee"""
        width = int(self.screen_width * self.responsive_dialog_width_ratio)
        height = int(self.screen_height * self.responsive_dialog_height_ratio)

        # Apply screen-specific constraints for perfect fit
        if self.screen_width < 1366:
            # Special constraints for small screens with 0.10 scale factor
            min_width = 400
            max_width = 1100  # Extremely compact fit for small screens
            min_height = 300
            max_height = 550   # Extremely compact height for small screens
        elif self.screen_width == 1366:
            # Special constraints for 1366x768 - ensure perfect fit
            min_width = 600
            max_width = 1300  # Leave margin for window decorations
            min_height = 400
            max_height = 650   # Leave margin for taskbar and title bar
        else:
            # Standard constraints for other screens
            min_width = 800
            max_width = 2000
            min_height = 600
            max_height = 1400

        width = max(min_width, min(max_width, width))
        height = max(min_height, min(max_height, height))

        return width, height

    def get_responsive_table_height(self, base_height=500):
        """Get responsive table height optimized for perfect display compatibility"""
        # Balanced heights for optimal fit and usability
        if self.is_small_screen:
            # Extremely compact tables for small screens with 0.10 scale factor
            return max(180, int(base_height * 0.45))
        elif self.is_medium_screen:
            # Ultra-compact handling for 1366x768 with 0.30 scale factor
            if self.screen_width == 1366:
                return max(250, int(base_height * 0.55))  # Ultra-compact for 1366x768 with 0.30 scale
            else:
                return max(320, int(base_height * 0.75))  # Compact for other medium screens
        elif self.is_large_screen:
            # Controlled height for large screens
            return max(400, int(base_height * 0.90))
        else:
            return int(base_height * 0.75)  # Default balanced sizing

    def get_responsive_row_height(self, base_height=70):
        """Get responsive row height optimized for perfect display compatibility"""
        # Balanced scaling for optimal usability and fit
        scaled_height = int(base_height * self.scale_factor * 0.6)  # 40% reduction for balance

        # Apply balanced screen-specific constraints
        if self.is_small_screen:
            return max(15, min(22, scaled_height))  # Extremely compact rows for small screens with 0.10 scale
        elif self.is_medium_screen:
            # Ultra-compact handling for 1366x768 with 0.30 scale factor
            if self.screen_width == 1366:
                return max(18, min(25, scaled_height))  # Ultra-compact for 1366x768 with 0.30 scale
            else:
                return max(35, min(45, scaled_height))  # Compact for other medium screens
        else:
            return max(40, min(50, scaled_height))  # Controlled rows for large screens

    def get_responsive_table_css(self, accent_color="#4CAF50", header_text_color="#2E7D32"):
        """Generate responsive CSS for tables - optimized for perfect display compatibility"""
        responsive_font_size = self.get_responsive_font_size(12)  # Balanced compact base
        responsive_header_font_size = self.get_responsive_font_size(13)  # Balanced compact header
        responsive_row_height = self.get_responsive_row_height(30)  # Balanced compact rows
        responsive_header_height = self.get_responsive_row_height(28)  # Balanced compact header

        # Ultra-compact padding for maximum density with 0.30 scale factor
        if self.screen_width == 1366:
            # Ultra-compact padding for 1366x768 with 0.30 scale factor
            responsive_padding_v = max(4, int(6 * self.scale_factor))
            responsive_padding_h = max(6, int(8 * self.scale_factor))
        else:
            # Standard compact padding for other screens
            responsive_padding_v = max(8, int(10 * self.scale_factor))
            responsive_padding_h = max(10, int(12 * self.scale_factor))

        return f"""
            QTableWidget {{
                gridline-color: #e0e0e0;
                background-color: white;
                alternate-background-color: #f8f9fa;
                border: 1px solid #d0d0d0;
                border-radius: 8px;
                font-size: {responsive_font_size}px;
                font-weight: 500;
                selection-background-color: #e3f2fd;
            }}
            QTableWidget::item {{
                padding: {responsive_padding_v}px {responsive_padding_h}px;
                border-bottom: 1px solid #e8e8e8;
                border-right: 1px solid #f0f0f0;
                color: #2c2c2c;
                font-weight: 500;
                min-height: {responsive_row_height}px;
            }}
            QTableWidget::item:selected {{
                background-color: #e3f2fd;
                color: #1976d2;
                font-weight: 600;
            }}
            QTableWidget::item:hover {{
                background-color: #f5f5f5;
            }}
            QHeaderView::section {{
                background-color: #f8f9fa;
                padding: {responsive_padding_v}px {responsive_padding_h}px;
                border: none;
                border-bottom: 3px solid {accent_color};
                border-right: 1px solid #e0e0e0;
                font-weight: bold;
                font-size: {responsive_header_font_size}px;
                color: {header_text_color};
                min-height: {responsive_header_height}px;
            }}
            QHeaderView::section:hover {{
                background-color: #e8f5e8;
            }}
        """

    def init_managers_and_data(self):
        """Initialize managers and data structures"""
        print("Initializing managers and data...")

        # Các thư mục dữ liệu
        os.makedirs("src/data/reports", exist_ok=True)
        os.makedirs("src/data/imports", exist_ok=True)

        # Initialize managers
        self.formula_manager = FormulaManager()
        self.inventory_manager = InventoryManager()

        # Get formulas and inventory data
        self.feed_formula = self.formula_manager.get_feed_formula()
        self.mix_formula = self.formula_manager.get_mix_formula()
        self.inventory = self.inventory_manager.get_inventory()

        # Tải công thức mix theo cột từ file cấu hình
        self.column_mix_formulas = self.formula_manager.column_mix_formulas

        # Initialize data structures
        self.feed_ingredients = {}
        self.mix_ingredients = {}
        self.formula_ingredients = {}
        self.total_batches_by_area = {}
        self.cell_formula_data = {}

        print("Managers and data initialized successfully")

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
        # Tải lịch sử cám với bộ lọc mặc định
        QTimer.singleShot(1500, lambda: self.load_feed_usage_history(show_message=False,
                                                                     filter_from_date=QDate.currentDate().addDays(-7),
                                                                     filter_to_date=QDate.currentDate()))

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
        self.import_tab = QWidget()  # Tab mới cho nhập hàng
        self.formula_tab = QWidget()
        self.history_tab = QWidget()  # Tab mới cho lịch sử
        self.team_management_tab = QWidget()  # Tab quản lý tổ cám

        # Add tabs to widget
        self.tabs.addTab(self.feed_usage_tab, "Tổng quan")
        self.tabs.addTab(self.inventory_tab, "Tồn Kho")
        self.tabs.addTab(self.import_tab, "Nhập Hàng")  # Tab nhập hàng
        self.tabs.addTab(self.formula_tab, "Công Thức")
        self.tabs.addTab(self.history_tab, "Lịch Sử")  # Thêm tab lịch sử
        self.tabs.addTab(self.team_management_tab, "Quản lý tổ cám")  # Tab quản lý tổ cám

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
        self.setup_import_tab()  # Thiết lập tab nhập hàng
        self.setup_formula_tab()
        self.setup_history_tab()  # Thiết lập tab lịch sử
        self.setup_team_management_tab()  # Thiết lập tab quản lý tổ cám

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

        # Thêm nút Điền Cám Theo Ngày
        fill_by_date_button = QPushButton("Điền Cám Theo Ngày")
        fill_by_date_button.setFont(BUTTON_FONT)
        fill_by_date_button.setMinimumHeight(30)
        fill_by_date_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        fill_by_date_button.clicked.connect(self.fill_table_by_date)
        date_layout.addWidget(fill_by_date_button)

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
                # Tạo font to hơn cho hàng khu và trại
                larger_font = QFont("Arial", DEFAULT_FONT_SIZE + 1, QFont.Bold)  # Tăng size chữ lên +3

                khu_item = QTableWidgetItem(khu_name)
                khu_item.setTextAlignment(Qt.AlignCenter)
                khu_item.setFont(larger_font)
                khu_item.setForeground(QColor(160, 160, 160))  # Màu chữ xám nhạt hơn
                self.feed_table.setItem(0, col_index, khu_item)

                farm_item = QTableWidgetItem(farm)
                farm_item.setTextAlignment(Qt.AlignCenter)
                farm_item.setFont(larger_font)
                farm_item.setForeground(QColor(160, 160, 160))  # Màu chữ xám nhạt hơn
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
                        spin_box.setDecimals(2)  # Cho phép 2 chữ số thập phân để nhập 0.25
                        spin_box.setMinimum(0)
                        spin_box.setMaximum(100)
                        spin_box.setSingleStep(0.25)  # Bước nhảy 0.25 để dễ nhập các giá trị như 0.25, 0.5, 0.75
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
                        formula_label.setFont(QFont("Arial", 14, 8))
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
        # Tạo GroupBox cho bảng nhập liệu cám
        feed_group = QGroupBox("Bảng Điền Cám")
        feed_group.setFont(QFont("Arial", DEFAULT_FONT_SIZE, QFont.Bold))
        feed_layout = QVBoxLayout()
        feed_layout.addWidget(self.feed_table)
        feed_group.setLayout(feed_layout)

        # Tạo GroupBox cho bảng lịch sử cám
        history_group = QGroupBox("Lịch sử cám các ngày trước")
        history_group.setFont(QFont("Arial", DEFAULT_FONT_SIZE, QFont.Bold))
        history_layout = QVBoxLayout()

        # Tạo layout cho Date Range Picker (không dùng GroupBox)
        date_filter_container = QWidget()
        date_filter_main_layout = QHBoxLayout()
        date_filter_main_layout.setContentsMargins(10, 10, 10, 10)

        # Tạo widget con chứa Date Range Picker (chiếm 50% chiều rộng)
        date_filter_widget = QWidget()
        date_filter_widget.setMaximumWidth(600)  # Giới hạn chiều rộng
        date_filter_widget.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 5px;
            }
        """)
        date_filter_layout = QGridLayout()
        date_filter_layout.setSpacing(10)
        date_filter_layout.setContentsMargins(15, 10, 15, 10)

        # Label và DateEdit cho "Từ ngày"
        from_date_label = QLabel("Từ ngày:")
        from_date_label.setFont(QFont("Arial", DEFAULT_FONT_SIZE, QFont.Bold))
        from_date_label.setStyleSheet("color: #495057;")

        self.history_from_date = QDateEdit()
        self.history_from_date.setFont(QFont("Arial", DEFAULT_FONT_SIZE))
        self.history_from_date.setCalendarPopup(True)
        self.history_from_date.setDisplayFormat("dd/MM/yyyy")
        self.history_from_date.setMinimumWidth(120)
        self.history_from_date.setStyleSheet("""
            QDateEdit {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 5px 8px;
                background-color: white;
            }
            QDateEdit:focus {
                border-color: #4CAF50;
                outline: none;
            }
        """)
        # Mặc định: 7 ngày trước
        self.history_from_date.setDate(QDate.currentDate().addDays(-7))

        # Label và DateEdit cho "Đến ngày"
        to_date_label = QLabel("Đến ngày:")
        to_date_label.setFont(QFont("Arial", DEFAULT_FONT_SIZE, QFont.Bold))
        to_date_label.setStyleSheet("color: #495057;")

        self.history_to_date = QDateEdit()
        self.history_to_date.setFont(QFont("Arial", DEFAULT_FONT_SIZE))
        self.history_to_date.setCalendarPopup(True)
        self.history_to_date.setDisplayFormat("dd/MM/yyyy")
        self.history_to_date.setMinimumWidth(120)
        self.history_to_date.setStyleSheet("""
            QDateEdit {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 5px 8px;
                background-color: white;
            }
            QDateEdit:focus {
                border-color: #4CAF50;
                outline: none;
            }
        """)
        # Mặc định: hôm nay
        self.history_to_date.setDate(QDate.currentDate())



        # Sắp xếp Date Range Picker trong grid layout
        date_filter_layout.addWidget(from_date_label, 0, 0)
        date_filter_layout.addWidget(self.history_from_date, 0, 1)
        date_filter_layout.addWidget(to_date_label, 0, 2)
        date_filter_layout.addWidget(self.history_to_date, 0, 3)

        date_filter_widget.setLayout(date_filter_layout)

        # Thêm widget vào layout chính với căn trái
        date_filter_main_layout.addWidget(date_filter_widget)
        date_filter_main_layout.addStretch()  # Đẩy về bên trái

        date_filter_container.setLayout(date_filter_main_layout)
        history_layout.addWidget(date_filter_container)

        # Kết nối sự kiện thay đổi ngày để tự động lọc
        self.history_from_date.dateChanged.connect(self.filter_feed_usage_history)
        self.history_to_date.dateChanged.connect(self.filter_feed_usage_history)

        # Tạo bảng lịch sử cám
        self.feed_usage_history_table = QTableWidget()
        self.feed_usage_history_table.setFont(TABLE_CELL_FONT)
        self.feed_usage_history_table.setColumnCount(4)
        self.feed_usage_history_table.setHorizontalHeaderLabels(["Ngày báo cáo", "Tổng lượng cám (kg)", "Tổng lượng mix (kg)", "Tổng số mẻ cám"])
        self.feed_usage_history_table.horizontalHeader().setFont(TABLE_HEADER_FONT)
        self.feed_usage_history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.feed_usage_history_table.setStyleSheet("""
            /* QTableWidget với hiệu ứng hover và selection cả hàng */
            QTableWidget {
                gridline-color: #aaa;
                selection-background-color: #c8e6c9;
                alternate-background-color: #f0f8f0;
                border: 1px solid #ddd;
                border-radius: 4px;
                outline: none;

                /* Thiết lập chế độ chọn cả hàng */
                selection-behavior: select-rows;
            }

            QHeaderView::section {
                background-color: #2E7D32;
                color: white;
                padding: 8px;
                border: 1px solid #1B5E20;
                font-weight: bold;
            }

            /* Styling cho từng cell */
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
                border-right: none;
                border-left: none;
                border-top: none;
            }


            /* Selection effect cho cả hàng */
            QTableWidget::item:selected {
                background-color: #c8e6c9;
                color: #000;
                font-weight: bold;
            }

            /* Focus effect */
            QTableWidget::item:focus {
                border: 1px solid #4CAF50;
                outline: none;
            }

            /* Đảm bảo hover hoạt động trên toàn bộ hàng */
            QTableWidget QTableWidgetItem:hover {
                background-color: #e8f5e9;
            }

            /* Selection cho inactive state */
            QTableWidget::item:selected:!active {
                background-color: #d4edda;
                color: #155724;
            }

            /* Tăng cường hiệu ứng hover cho các hàng alternate */
            QTableWidget::item:alternate:hover {
                background-color: #e8f5e9;
            }

            QTableWidget::item:alternate:selected {
                background-color: #c8e6c9;
            }
        """)
        self.feed_usage_history_table.setAlternatingRowColors(True)
        self.feed_usage_history_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Chỉ đọc

        # Tăng chiều cao hàng cho bảng lịch sử
        self.feed_usage_history_table.verticalHeader().setDefaultSectionSize(55)

        # Kết nối sự kiện double click vào hàng để tải dữ liệu vào bảng cám
        self.feed_usage_history_table.doubleClicked.connect(self.on_history_row_double_clicked)

        # Kết nối sự kiện click vào hàng để chọn toàn bộ hàng
        self.feed_usage_history_table.clicked.connect(self.on_history_row_clicked)

        history_layout.addWidget(self.feed_usage_history_table)
        history_group.setLayout(history_layout)

        # Thêm bảng cám vào layout chính
        layout.addWidget(feed_group, 40)

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

        # Tạo layout ngang cho các button ở giữa với khoảng cách đẹp
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)  # Khoảng cách giữa các button
        buttons_layout.setContentsMargins(10, 10, 10, 10)  # Margin xung quanh
        buttons_layout.addWidget(mix_formula_button)
        buttons_layout.addWidget(view_report_button)

        # Thêm layout buttons vào giữa bảng cám và lịch sử cám
        layout.addLayout(buttons_layout)

        # Thêm bảng lịch sử cám vào layout chính
        layout.addWidget(history_group, 60)

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
        """Xóa toàn bộ dữ liệu trong bảng điền cám"""
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

    def setup_import_tab(self):
        """Setup the import goods tab"""
        layout = QVBoxLayout()

        # Add a header for the tab
        header = QLabel("Nhập Hàng Vào Kho")
        header.setFont(HEADER_FONT)
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("QLabel { padding: 10px; background-color: #e0f2f1; border-radius: 5px; }")
        layout.addWidget(header)

        # Create tabs for Feed and Mix imports
        import_tabs = QTabWidget()
        import_tabs.setFont(DEFAULT_FONT)
        import_tabs.setStyleSheet("""
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

        # Create tabs for importing feed and mix ingredients
        feed_import_tab = QWidget()
        mix_import_tab = QWidget()
        import_history_tab = QWidget()

        import_tabs.addTab(feed_import_tab, "Nhập kho cám")
        import_tabs.addTab(mix_import_tab, "Nhập kho mix")
        import_tabs.addTab(import_history_tab, "Lịch Sử Nhập Hàng")

        # Setup Feed Import tab
        feed_import_layout = QVBoxLayout()

        # Form layout for feed import
        feed_form_group = QGroupBox("Thông Tin Nhập kho cám")
        feed_form_group.setFont(DEFAULT_FONT)
        feed_form_layout = QGridLayout()

        # Add form fields
        feed_form_layout.addWidget(QLabel("Thành phần:"), 0, 0)
        self.feed_import_combo = QComboBox()
        self.feed_import_combo.setFont(DEFAULT_FONT)

        # Lấy danh sách các thành phần từ công thức cám
        feed_ingredients = self.formula_manager.get_feed_formula().keys()
        for ingredient in feed_ingredients:
            self.feed_import_combo.addItem(ingredient)
        feed_form_layout.addWidget(self.feed_import_combo, 0, 1)

        feed_form_layout.addWidget(QLabel("Số lượng (kg):"), 1, 0)
        self.feed_import_amount = CustomDoubleSpinBox()
        self.feed_import_amount.setRange(0, 1000000)
        self.feed_import_amount.setDecimals(2)
        self.feed_import_amount.setSingleStep(10)
        self.feed_import_amount.setFont(DEFAULT_FONT)
        feed_form_layout.addWidget(self.feed_import_amount, 1, 1)

        feed_form_layout.addWidget(QLabel("Ngày nhập:"), 2, 0)
        self.feed_import_date = QDateEdit()
        self.feed_import_date.setDate(QDate.currentDate())
        self.feed_import_date.setCalendarPopup(True)
        self.feed_import_date.setFont(DEFAULT_FONT)
        feed_form_layout.addWidget(self.feed_import_date, 2, 1)

        feed_form_layout.addWidget(QLabel("Ghi chú:"), 3, 0)
        self.feed_import_note = QLineEdit()
        self.feed_import_note.setFont(DEFAULT_FONT)
        feed_form_layout.addWidget(self.feed_import_note, 3, 1)

        feed_form_group.setLayout(feed_form_layout)
        feed_import_layout.addWidget(feed_form_group)

        # Add submit button
        feed_import_btn = QPushButton("Nhập kho cám")
        feed_import_btn.setFont(BUTTON_FONT)
        feed_import_btn.setMinimumHeight(40)
        feed_import_btn.setStyleSheet("""
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
        feed_import_btn.clicked.connect(lambda: self.import_feed())
        feed_import_layout.addWidget(feed_import_btn)

        # Thêm bảng lịch sử Nhập kho cám
        feed_history_group = QGroupBox("Lịch Sử Nhập kho cám")
        feed_history_group.setFont(DEFAULT_FONT)
        feed_history_layout = QVBoxLayout()

        self.feed_import_history_table = QTableWidget()
        self.feed_import_history_table.setFont(TABLE_CELL_FONT)
        self.feed_import_history_table.setColumnCount(5)
        self.feed_import_history_table.setHorizontalHeaderLabels(["Thời gian", "Thành phần", "Số lượng (kg)", "Số bao", "Ghi chú"])
        self.feed_import_history_table.horizontalHeader().setFont(TABLE_HEADER_FONT)
        self.feed_import_history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.feed_import_history_table.setAlternatingRowColors(True)
        self.feed_import_history_table.setStyleSheet("""
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
        self.feed_import_history_table.setMinimumHeight(200)
        feed_history_layout.addWidget(self.feed_import_history_table)
        feed_history_group.setLayout(feed_history_layout)
        feed_import_layout.addWidget(feed_history_group)

        # Cập nhật lịch sử Nhập kho cám lần đầu
        self.update_feed_import_history()

        feed_import_tab.setLayout(feed_import_layout)

        # Setup Mix Import tab (similar to feed import)
        mix_import_layout = QVBoxLayout()

        # Form layout for mix import
        mix_form_group = QGroupBox("Thông Tin Nhập kho mix")
        mix_form_group.setFont(DEFAULT_FONT)
        mix_form_layout = QGridLayout()

        # Add form fields
        mix_form_layout.addWidget(QLabel("Thành phần:"), 0, 0)
        self.mix_import_combo = QComboBox()
        self.mix_import_combo.setFont(DEFAULT_FONT)

        # Lấy danh sách các thành phần từ công thức mix
        mix_ingredients = self.formula_manager.get_mix_formula().keys()
        for ingredient in mix_ingredients:
            self.mix_import_combo.addItem(ingredient)
        mix_form_layout.addWidget(self.mix_import_combo, 0, 1)

        mix_form_layout.addWidget(QLabel("Số lượng (kg):"), 1, 0)
        self.mix_import_amount = CustomDoubleSpinBox()
        self.mix_import_amount.setRange(0, 1000000)
        self.mix_import_amount.setDecimals(2)
        self.mix_import_amount.setSingleStep(10)
        self.mix_import_amount.setFont(DEFAULT_FONT)
        mix_form_layout.addWidget(self.mix_import_amount, 1, 1)

        mix_form_layout.addWidget(QLabel("Ngày nhập:"), 2, 0)
        self.mix_import_date = QDateEdit()
        self.mix_import_date.setDate(QDate.currentDate())
        self.mix_import_date.setCalendarPopup(True)
        self.mix_import_date.setFont(DEFAULT_FONT)
        mix_form_layout.addWidget(self.mix_import_date, 2, 1)

        mix_form_layout.addWidget(QLabel("Ghi chú:"), 3, 0)
        self.mix_import_note = QLineEdit()
        self.mix_import_note.setFont(DEFAULT_FONT)
        mix_form_layout.addWidget(self.mix_import_note, 3, 1)

        mix_form_group.setLayout(mix_form_layout)
        mix_import_layout.addWidget(mix_form_group)

        # Add submit button
        mix_import_btn = QPushButton("Nhập kho mix")
        mix_import_btn.setFont(BUTTON_FONT)
        mix_import_btn.setMinimumHeight(40)
        mix_import_btn.setStyleSheet("""
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
        mix_import_btn.clicked.connect(lambda: self.import_mix())
        mix_import_layout.addWidget(mix_import_btn)

        # Thêm bảng lịch sử Nhập kho mix
        mix_history_group = QGroupBox("Lịch Sử Nhập kho mix")
        mix_history_group.setFont(DEFAULT_FONT)
        mix_history_layout = QVBoxLayout()

        self.mix_import_history_table = QTableWidget()
        self.mix_import_history_table.setFont(TABLE_CELL_FONT)
        self.mix_import_history_table.setColumnCount(5)
        self.mix_import_history_table.setHorizontalHeaderLabels(["Thời gian", "Thành phần", "Số lượng (kg)", "Số bao", "Ghi chú"])
        self.mix_import_history_table.horizontalHeader().setFont(TABLE_HEADER_FONT)
        self.mix_import_history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.mix_import_history_table.setAlternatingRowColors(True)
        self.mix_import_history_table.setStyleSheet("""
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
        self.mix_import_history_table.setMinimumHeight(200)
        mix_history_layout.addWidget(self.mix_import_history_table)
        mix_history_group.setLayout(mix_history_layout)
        mix_import_layout.addWidget(mix_history_group)

        # Cập nhật lịch sử Nhập kho mix lần đầu
        self.update_mix_import_history()

        mix_import_tab.setLayout(mix_import_layout)

        # Setup Import History tab
        history_layout = QVBoxLayout()

        # Date range selector for import history
        date_range_group = QGroupBox("Lọc lịch sử nhập kho")
        date_range_group.setFont(DEFAULT_FONT)
        date_range_layout = QGridLayout()

        # From date
        date_range_layout.addWidget(QLabel("Từ ngày:"), 0, 0)
        self.import_history_from_date = QDateEdit()
        self.import_history_from_date.setDate(QDate.currentDate().addDays(-30))  # Default 30 ngày trước
        self.import_history_from_date.setCalendarPopup(True)
        self.import_history_from_date.setFont(DEFAULT_FONT)
        date_range_layout.addWidget(self.import_history_from_date, 0, 1)

        # To date
        date_range_layout.addWidget(QLabel("Đến ngày:"), 0, 2)
        self.import_history_to_date = QDateEdit()
        self.import_history_to_date.setDate(QDate.currentDate())  # Default ngày hiện tại
        self.import_history_to_date.setCalendarPopup(True)
        self.import_history_to_date.setFont(DEFAULT_FONT)
        date_range_layout.addWidget(self.import_history_to_date, 0, 3)

        # Filter by type
        date_range_layout.addWidget(QLabel("Loại:"), 1, 0)
        self.history_type_filter = QComboBox()
        self.history_type_filter.setFont(DEFAULT_FONT)
        self.history_type_filter.addItem("Tất cả")
        self.history_type_filter.addItem("Cám")
        self.history_type_filter.addItem("Mix")
        date_range_layout.addWidget(self.history_type_filter, 1, 1)

        # Search button
        search_history_btn = QPushButton("Tìm kiếm")
        search_history_btn.setFont(DEFAULT_FONT)
        search_history_btn.clicked.connect(self.load_import_history)
        date_range_layout.addWidget(search_history_btn, 1, 3)

        date_range_group.setLayout(date_range_layout)
        history_layout.addWidget(date_range_group)

        # Import history table
        self.import_history_table = QTableWidget()
        self.import_history_table.setFont(TABLE_CELL_FONT)
        self.import_history_table.setColumnCount(6)
        self.import_history_table.setHorizontalHeaderLabels(["Ngày", "Thời gian", "Loại", "Thành phần", "Số lượng (kg)", "Số bao"])
        self.import_history_table.horizontalHeader().setFont(TABLE_HEADER_FONT)
        self.import_history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.import_history_table.setAlternatingRowColors(True)
        self.import_history_table.setStyleSheet("""
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
        history_layout.addWidget(self.import_history_table)

        import_history_tab.setLayout(history_layout)

        # Add the tabs to the main layout
        layout.addWidget(import_tabs)

        self.import_tab.setLayout(layout)

    def import_feed(self):
        """Import feed into inventory"""
        try:
            ingredient = self.feed_import_combo.currentText()
            amount = self.feed_import_amount.value()
            # Fix: Use YYYY-MM-DD format for filename compatibility
            date_obj = self.feed_import_date.date()
            date_display = date_obj.toString("dd/MM/yyyy")  # For display
            date_filename = date_obj.toString("yyyy-MM-dd")  # For filename
            note = self.feed_import_note.text()

            if amount <= 0:
                QMessageBox.warning(self, "Lỗi", "Số lượng nhập phải lớn hơn 0!")
                return

            if not ingredient:
                QMessageBox.warning(self, "Lỗi", "Vui lòng chọn thành phần!")
                return

            # Show employee selection dialog
            if self.show_employee_selection_dialog(date_filename, ingredient, amount, "feed"):
                selected_employees = self.get_selected_employees()

                # Update inventory
                inventory = self.inventory_manager.get_inventory()
                current_amount = inventory.get(ingredient, 0)
                inventory[ingredient] = current_amount + amount
                self.inventory_manager.update_inventory(ingredient, current_amount + amount)

                # Save import history
                self.save_import_history("feed", ingredient, amount, date_filename, note)

                # Save employee participation
                self.save_employee_participation("feed", ingredient, amount, date_filename, note, selected_employees)

            else:
                # User cancelled - don't proceed with import
                return

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể nhập kho cám: {str(e)}")
            print(f"Error in import_feed: {str(e)}")
            return

        # Update tables
        self.update_feed_inventory_table()

        # Update import history
        self.update_feed_import_history()

        # Clear form
        self.feed_import_amount.setValue(0)
        self.feed_import_note.clear()

        QMessageBox.information(self, "Thành công", f"Đã nhập {amount} kg {ingredient} vào kho cám!")

    def import_mix(self):
        """Import mix into inventory"""
        try:
            ingredient = self.mix_import_combo.currentText()
            amount = self.mix_import_amount.value()
            # Fix: Use YYYY-MM-DD format for filename compatibility
            date_obj = self.mix_import_date.date()
            date_filename = date_obj.toString("yyyy-MM-dd")  # For filename
            note = self.mix_import_note.text()

            if amount <= 0:
                QMessageBox.warning(self, "Lỗi", "Số lượng nhập phải lớn hơn 0!")
                return

            if not ingredient:
                QMessageBox.warning(self, "Lỗi", "Vui lòng chọn thành phần!")
                return

            # Show employee selection dialog
            if self.show_employee_selection_dialog(date_filename, ingredient, amount, "mix"):
                selected_employees = self.get_selected_employees()

                # Update inventory
                inventory = self.inventory_manager.get_inventory()
                current_amount = inventory.get(ingredient, 0)
                inventory[ingredient] = current_amount + amount
                self.inventory_manager.update_inventory(ingredient, current_amount + amount)

                # Save import history
                self.save_import_history("mix", ingredient, amount, date_filename, note)

                # Save employee participation
                self.save_employee_participation("mix", ingredient, amount, date_filename, note, selected_employees)

            else:
                # User cancelled - don't proceed with import
                return

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể nhập kho mix: {str(e)}")
            print(f"Error in import_mix: {str(e)}")
            return

        # Update tables
        self.update_mix_inventory_table()

        # Update import history
        self.update_mix_import_history()

        # Clear form
        self.mix_import_amount.setValue(0)
        self.mix_import_note.clear()

        QMessageBox.information(self, "Thành công", f"Đã nhập {amount} kg {ingredient} vào kho mix!")

    def save_import_history(self, import_type, ingredient, amount, date, note):
        """Save import history to file"""
        try:
            # Ensure date is in YYYY-MM-DD format
            if "/" in date:
                # Convert dd/MM/yyyy to yyyy-MM-dd
                day, month, year = date.split("/")
                date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"

            # Create filename based on date
            filename = f"src/data/imports/import_{date}.json"

            # Ensure directory exists
            os.makedirs(os.path.dirname(filename), exist_ok=True)

            # Load existing data if file exists
            imports = []
            if os.path.exists(filename):
                try:
                    with open(filename, "r", encoding="utf-8") as f:
                        imports = json.load(f)
                        if not isinstance(imports, list):
                            imports = []
                except (json.JSONDecodeError, UnicodeDecodeError) as e:
                    print(f"Warning: Could not read existing import file {filename}: {e}")
                    imports = []

            # Add new import record
            import_data = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "type": import_type,
                "ingredient": ingredient,
                "amount": float(amount),  # Ensure amount is numeric
                "note": str(note) if note else ""
            }

            imports.append(import_data)

            # Save updated data
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(imports, f, ensure_ascii=False, indent=2)

            # Update history tables
            self.update_feed_import_history()
            self.update_mix_import_history()

            # Show success message
            QMessageBox.information(self, "Thành công", f"Đã nhập {amount} kg {ingredient} vào kho!")

            # Reset form
            if import_type == "feed":
                self.feed_import_amount.setValue(0)
                self.feed_import_note.clear()
            else:
                self.mix_import_amount.setValue(0)
                self.mix_import_note.clear()

        except Exception as e:
            error_msg = f"Không thể lưu lịch sử nhập hàng: {str(e)}"
            QMessageBox.critical(self, "Lỗi", error_msg)
            print(f"Error in save_import_history: {str(e)}")
            raise

    def load_import_history(self):
        """Tìm kiếm lịch sử nhập hàng từ ngày đến ngày"""
        from_date = self.import_history_from_date.date()
        to_date = self.import_history_to_date.date()

        # Đảm bảo from_date <= to_date
        if from_date > to_date:
            QMessageBox.warning(self, "Lỗi", "Ngày bắt đầu phải nhỏ hơn hoặc bằng ngày kết thúc!")
            return

        # Chuyển đổi ngày thành định dạng dd/MM/yyyy để đọc file
        from_date_str = from_date.toString("dd/MM/yyyy")
        to_date_str = to_date.toString("dd/MM/yyyy")

        # Lọc loại nhập kho
        filter_type = self.history_type_filter.currentText()

        # Xóa dữ liệu cũ trong bảng
        self.import_history_table.setRowCount(0)

        # Danh sách lưu tất cả bản ghi nhập kho trong khoảng thời gian
        all_imports = []

        # Tạo danh sách tất cả các ngày từ from_date đến to_date
        current_date = from_date
        while current_date <= to_date:
            date_str = current_date.toString("dd/MM/yyyy")
            filename = f"src/data/imports/import_{date_str}.json"

            # Nếu có file dữ liệu cho ngày này
            if os.path.exists(filename):
                with open(filename, "r", encoding="utf-8") as f:
                    try:
                        imports = json.load(f)
                        for import_data in imports:
                            # Thêm thông tin ngày vào mỗi bản ghi
                            import_data["date"] = current_date.toString("dd/MM/yyyy")
                            all_imports.append(import_data)
                    except json.JSONDecodeError:
                        print(f"Lỗi đọc file {filename}")

            # Chuyển sang ngày tiếp theo
            current_date = current_date.addDays(1)

        # Lọc theo loại nếu cần
        if filter_type == "Cám":
            all_imports = [imp for imp in all_imports if imp["type"] == "feed"]
        elif filter_type == "Mix":
            all_imports = [imp for imp in all_imports if imp["type"] == "mix"]

        # Sắp xếp theo thời gian, mới nhất lên đầu
        all_imports.sort(key=lambda x: (x["date"], x["timestamp"]), reverse=True)

        # Hiển thị kết quả
        self.import_history_table.setRowCount(len(all_imports))

        for row, import_data in enumerate(all_imports):
            # Ngày
            date_item = QTableWidgetItem(import_data["date"])
            self.import_history_table.setItem(row, 0, date_item)

            # Thời gian
            time_item = QTableWidgetItem(import_data["timestamp"].split(" ")[1] if " " in import_data["timestamp"] else import_data["timestamp"])
            self.import_history_table.setItem(row, 1, time_item)

            # Loại
            type_text = "Cám" if import_data["type"] == "feed" else "Mix"
            type_item = QTableWidgetItem(type_text)
            self.import_history_table.setItem(row, 2, type_item)

            # Thành phần
            ingredient_item = QTableWidgetItem(import_data["ingredient"])
            self.import_history_table.setItem(row, 3, ingredient_item)

            # Số lượng
            amount_item = QTableWidgetItem(format_number(import_data["amount"]))
            amount_item.setTextAlignment(Qt.AlignCenter)
            self.import_history_table.setItem(row, 4, amount_item)

            # Số bao
            ingredient_name = import_data["ingredient"]
            amount = import_data["amount"]
            bag_size = self.inventory_manager.get_bag_size(ingredient_name)
            if bag_size > 0:
                bags = amount / bag_size
                bags_item = QTableWidgetItem(format_number(bags))
            else:
                bags_item = QTableWidgetItem("")
            bags_item.setTextAlignment(Qt.AlignCenter)
            self.import_history_table.setItem(row, 5, bags_item)

        # Hiển thị thông báo kết quả
        if len(all_imports) > 0:
            QMessageBox.information(self, "Kết quả tìm kiếm", f"Tìm thấy {len(all_imports)} bản ghi nhập kho.")
        else:
            QMessageBox.information(self, "Kết quả tìm kiếm", "Không tìm thấy dữ liệu nhập kho nào trong khoảng thời gian đã chọn!")

    def update_feed_import_history(self):
        """Cập nhật bảng lịch sử Nhập kho cám"""
        try:
            # Lấy ngày hiện tại với format đúng
            current_date = QDate.currentDate().toString("yyyy-MM-dd")
            filename = f"src/data/imports/import_{current_date}.json"

            # Xóa dữ liệu hiện tại
            self.feed_import_history_table.setRowCount(0)

            # Kiểm tra xem file có tồn tại không
            if not os.path.exists(filename):
                return

            # Đọc dữ liệu
            with open(filename, "r", encoding="utf-8") as f:
                imports = json.load(f)

            if not isinstance(imports, list):
                print(f"Warning: Invalid data format in {filename}")
                return

        except Exception as e:
            print(f"Error updating feed import history: {str(e)}")
            return

                # Lọc chỉ lấy dữ liệu cám
        feed_imports = [import_data for import_data in imports if import_data["type"] == "feed"]

        # Sắp xếp theo thời gian, mới nhất lên đầu
        feed_imports.sort(key=lambda x: x["timestamp"], reverse=True)

        # Điền vào bảng
        self.feed_import_history_table.setRowCount(len(feed_imports))

        for row, import_data in enumerate(feed_imports):
            # Thời gian
            time_item = QTableWidgetItem(import_data["timestamp"])
            self.feed_import_history_table.setItem(row, 0, time_item)

            # Thành phần
            ingredient_item = QTableWidgetItem(import_data["ingredient"])
            self.feed_import_history_table.setItem(row, 1, ingredient_item)

            # Số lượng
            amount_item = QTableWidgetItem(format_number(import_data["amount"]))
            amount_item.setTextAlignment(Qt.AlignCenter)
            self.feed_import_history_table.setItem(row, 2, amount_item)

            # Số bao
            ingredient_name = import_data["ingredient"]
            amount = import_data["amount"]
            # Lấy kích thước bao từ packaging_info
            bag_size = self.inventory_manager.get_bag_size(ingredient_name)
            if bag_size > 0:
                bags = amount / bag_size
                bags_item = QTableWidgetItem(format_number(bags))
            else:
                bags_item = QTableWidgetItem("")
            bags_item.setTextAlignment(Qt.AlignCenter)
            self.feed_import_history_table.setItem(row, 3, bags_item)

            # Ghi chú
            note_item = QTableWidgetItem(import_data["note"])
            self.feed_import_history_table.setItem(row, 4, note_item)

    def update_mix_import_history(self):
        """Cập nhật bảng lịch sử Nhập kho mix"""
        try:
            # Lấy ngày hiện tại với format đúng
            current_date = QDate.currentDate().toString("yyyy-MM-dd")
            filename = f"src/data/imports/import_{current_date}.json"

            # Xóa dữ liệu hiện tại
            self.mix_import_history_table.setRowCount(0)

            # Kiểm tra xem file có tồn tại không
            if not os.path.exists(filename):
                return

            # Đọc dữ liệu
            with open(filename, "r", encoding="utf-8") as f:
                imports = json.load(f)

            if not isinstance(imports, list):
                print(f"Warning: Invalid data format in {filename}")
                return

        except Exception as e:
            print(f"Error updating mix import history: {str(e)}")
            return

                # Lọc chỉ lấy dữ liệu mix
        mix_imports = [import_data for import_data in imports if import_data["type"] == "mix"]

        # Sắp xếp theo thời gian, mới nhất lên đầu
        mix_imports.sort(key=lambda x: x["timestamp"], reverse=True)

        # Điền vào bảng
        self.mix_import_history_table.setRowCount(len(mix_imports))

        for row, import_data in enumerate(mix_imports):
            # Thời gian
            time_item = QTableWidgetItem(import_data["timestamp"])
            self.mix_import_history_table.setItem(row, 0, time_item)

            # Thành phần
            ingredient_item = QTableWidgetItem(import_data["ingredient"])
            self.mix_import_history_table.setItem(row, 1, ingredient_item)

            # Số lượng
            amount_item = QTableWidgetItem(format_number(import_data["amount"]))
            amount_item.setTextAlignment(Qt.AlignCenter)
            self.mix_import_history_table.setItem(row, 2, amount_item)

            # Số bao
            ingredient_name = import_data["ingredient"]
            amount = import_data["amount"]
            # Lấy kích thước bao từ packaging_info
            bag_size = self.inventory_manager.get_bag_size(ingredient_name)
            if bag_size > 0:
                bags = amount / bag_size
                bags_item = QTableWidgetItem(format_number(bags))
            else:
                bags_item = QTableWidgetItem("")
            bags_item.setTextAlignment(Qt.AlignCenter)
            self.mix_import_history_table.setItem(row, 3, bags_item)

            # Ghi chú
            note_item = QTableWidgetItem(import_data["note"])
            self.mix_import_history_table.setItem(row, 4, note_item)

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
        self.mix_formula_table.setColumnCount(4)  # Thêm một cột mới
        self.mix_formula_table.setHorizontalHeaderLabels(["Thành phần", "Tỷ lệ (%)", "1 mẻ (kg)", "10 mẻ (kg)"])
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

        # Đánh dấu đang tải báo cáo để hàm calculate_feed_usage biết
        self.loading_report = True

        # Nếu báo cáo có chứa thông tin về công thức mix cho cột
        if report_data and "column_mix_formulas" in report_data:
            self.column_mix_formulas = report_data["column_mix_formulas"]
        elif report_data and "area_mix_formulas" in report_data:  # Tương thích ngược
            self.area_mix_formulas = report_data["area_mix_formulas"]

        # Tải thông tin công thức mix cho từng ô
        if report_data and "cell_mix_formulas" in report_data:
            self.cell_mix_formulas = report_data["cell_mix_formulas"]

        # Cập nhật các bảng
        self.update_history_usage_table(report_data)
        self.update_history_feed_table(report_data)
        self.update_history_mix_table(report_data)

        # Kết thúc trạng thái tải báo cáo
        self.loading_report = False
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
            if not report_data:
                self.history_mix_table.setRowCount(0)
                return

            # Đặt bảng chỉ đọc - không cho phép sửa đổi
            self.history_mix_table.setEditTriggers(QTableWidget.NoEditTriggers)

            # Lấy dữ liệu thành phần mix từ báo cáo
            mix_ingredients = {}
            if "mix_ingredients" in report_data:
                mix_ingredients = report_data.get("mix_ingredients", {})
            else:
                # Nếu không có dữ liệu mix_ingredients trong báo cáo, thông báo và thoát
                print("Báo cáo không chứa dữ liệu mix_ingredients, không thể hiển thị thành phần mix")
                self.history_mix_table.setRowCount(0)
                return

            # Kiểm tra lại mix_ingredients sau khi tính toán
            if not mix_ingredients:
                self.history_mix_table.setRowCount(0)
                print("Không có dữ liệu thành phần mix để hiển thị")
                return

            # Thiết lập số hàng và cột cho bảng
            self.history_mix_table.setRowCount(len(mix_ingredients))
            self.history_mix_table.setColumnCount(4)  # Thành phần, Tỷ lệ (%), Số lượng (kg), Số bao
            self.history_mix_table.setHorizontalHeaderLabels(["Thành phần", "Tỷ lệ (%)", "Số lượng (kg)", "Số bao"])

            # Tính tổng lượng mix
            total_mix = sum(mix_ingredients.values())
            print(f"Tổng lượng mix: {total_mix:.2f} kg")

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
            import traceback
            traceback.print_exc()

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

            # 1 mẻ (kg) input - read-only
            one_batch_amount = amount / 10  # 1 mẻ bằng 1/10 của giá trị 10 mẻ
            one_batch_item = QTableWidgetItem(format_number(one_batch_amount))
            one_batch_item.setFont(TABLE_CELL_FONT)
            one_batch_item.setTextAlignment(Qt.AlignCenter)  # Căn giữa số
            one_batch_item.setBackground(QColor(240, 248, 255))  # Light blue background
            self.mix_formula_table.setItem(i, 2, one_batch_item)

            # 10 mẻ (kg) input
            amount_spin = CustomDoubleSpinBox()
            amount_spin.setFont(TABLE_CELL_FONT)
            amount_spin.setMinimumHeight(30)
            amount_spin.setRange(0, 2000)
            amount_spin.setDecimals(2)  # Hiển thị tối đa 2 chữ số thập phân
            amount_spin.setValue(amount)

            # Khi thay đổi giá trị cột 10 mẻ, tự động cập nhật cột 1 mẻ
            def update_one_batch(value, row=i):
                one_batch_value = value / 10
                one_batch_item = QTableWidgetItem(format_number(one_batch_value))
                one_batch_item.setFont(TABLE_CELL_FONT)
                one_batch_item.setTextAlignment(Qt.AlignCenter)  # Căn giữa số
                one_batch_item.setBackground(QColor(240, 248, 255))  # Light blue background
                self.mix_formula_table.setItem(row, 2, one_batch_item)

            amount_spin.valueChanged.connect(update_one_batch)
            self.mix_formula_table.setCellWidget(i, 3, amount_spin)

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

        # Tổng lượng cho 1 mẻ
        total_one_batch = mix_total / 10
        total_one_batch_item = QTableWidgetItem(format_number(total_one_batch))
        total_one_batch_item.setFont(QFont("Arial", DEFAULT_FONT_SIZE + 1, QFont.Bold))
        total_one_batch_item.setBackground(QColor(230, 250, 200))  # Light green background
        total_one_batch_item.setTextAlignment(Qt.AlignCenter)  # Căn giữa số
        self.mix_formula_table.setItem(total_row, 2, total_one_batch_item)

        # Tổng lượng cho 10 mẻ
        total_value = QTableWidgetItem(format_number(mix_total))
        total_value.setFont(QFont("Arial", DEFAULT_FONT_SIZE + 1, QFont.Bold))
        total_value.setBackground(QColor(230, 250, 200))  # Light green background
        total_value.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.mix_formula_table.setItem(total_row, 3, total_value)

        # Tăng chiều cao của các hàng để dễ nhìn hơn
        for row in range(self.mix_formula_table.rowCount()):
            self.mix_formula_table.setRowHeight(row, 40)

    def update_feed_inventory_table(self):
        """Update the feed inventory table"""
        # Get relevant ingredients from feed formula
        feed_ingredients = list(self.feed_formula.keys())
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
        # Reset dữ liệu tích lũy từ lần tính toán trước để tránh cộng dồn
        self.cell_formula_data = {}

        # Collect data from table
        formula_batches = {}  # Dictionary to store formula name and total batches
        farm_formula_batches = {}  # Dictionary to store formula name and batches for each farm

        # Dictionary để lưu thông tin công thức mix cho từng cell
        cell_mix_data = {}

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

                # Xác định công thức mix cho cell này
                mix_formula_name = None

                # 1. Kiểm tra xem ô này có công thức mix riêng không
                if hasattr(self, 'cell_mix_formulas') and self.cell_mix_formulas and cell_key in self.cell_mix_formulas:
                    mix_formula_name = self.cell_mix_formulas[cell_key]

                # 2. Nếu không, kiểm tra xem cột này có công thức mix không
                if not mix_formula_name and hasattr(self, 'column_mix_formulas') and self.column_mix_formulas:
                    col_str = f"{col}"
                    if col_str in self.column_mix_formulas:
                        mix_formula_name = self.column_mix_formulas[col_str]

                # 3. Nếu không, kiểm tra xem khu này có công thức mix không
                if not mix_formula_name and hasattr(self, 'area_mix_formulas') and self.area_mix_formulas and khu_name in self.area_mix_formulas:
                    mix_formula_name = self.area_mix_formulas[khu_name]

                self.cell_formula_data[cell_key] = {
                    "feed_formula": formula_name,
                    "batch_value": batch_value,
                    "actual_batches": actual_batches,
                    "khu": khu_name,
                    "farm": farm_name,
                    "shift": shift,
                    "mix_formula": mix_formula_name
                }

                # Lưu thông tin mix formula cho cell này
                if mix_formula_name:
                    cell_mix_data[cell_key] = mix_formula_name

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

        # Không sử dụng nguyên liệu tổ hợp nữa

        # Kiểm tra xem có báo cáo đang được tải lại không
        is_loading_report = hasattr(self, 'loading_report') and self.loading_report

        # Nếu đang tải lại báo cáo và có thông tin về công thức mix
        if is_loading_report and hasattr(self, 'current_report_data') and self.current_report_data:
            print("Đang tải báo cáo, kiểm tra thông tin công thức mix...")
            # Kiểm tra công thức mix theo cột
            if "column_mix_formulas" in self.current_report_data:
                self.column_mix_formulas = self.current_report_data["column_mix_formulas"]
                print(f"Đã tải công thức mix theo cột từ báo cáo: {self.column_mix_formulas}")
            # Tương thích ngược với phiên bản cũ
            elif "area_mix_formulas" in self.current_report_data:
                self.area_mix_formulas = self.current_report_data["area_mix_formulas"]
                print(f"Đã tải công thức mix theo khu từ báo cáo: {self.area_mix_formulas}")

            # Đảm bảo self.cell_mix_formulas được tải lại từ báo cáo
            if "cell_mix_formulas" in self.current_report_data:
                self.cell_mix_formulas = self.current_report_data["cell_mix_formulas"]
                print(f"Đã tải công thức mix theo ô từ báo cáo: {self.cell_mix_formulas}")
        # Nếu không phải đang tải báo cáo, đảm bảo đã tải công thức mix theo cột từ file cấu hình
        elif not hasattr(self, 'column_mix_formulas') or not self.column_mix_formulas:
            self.column_mix_formulas = self.formula_manager.column_mix_formulas
            print(f"Đã tải công thức mix theo cột từ cấu hình: {self.column_mix_formulas}")

        # Không tự động hiển thị dialog chọn công thức mix - để người dùng chọn thủ công

        # Trước tiên, tính toán tổng thành phần cám (không bao gồm mix)
        for formula_name, batch_count in formula_batches.items():
            if not formula_name:
                continue

            # Lấy công thức cám
            feed_formula = self.formula_manager.load_feed_preset(formula_name)
            if not feed_formula:
                continue

            # Tính toán thành phần cám
            for ingredient, amount_per_batch in feed_formula.items():
                    # Áp dụng quy tắc 0.5 = 1 mẻ, 1 = 2 mẻ
                    # batch_count là số hiển thị trên giao diện, cần nhân 2 để tính đúng số mẻ thực tế
                    feed_amount = amount_per_batch * batch_count * 2

                    # Cộng dồn vào tổng thành phần cám
                    if ingredient in feed_ingredients:
                        feed_ingredients[ingredient] += feed_amount
                    else:
                        feed_ingredients[ingredient] = feed_amount

            # Lưu thông tin công thức và thành phần cho hiển thị chi tiết nếu cần
            self.formula_ingredients[formula_name] = {
                "batches": batch_count
            }

        # Tính toán thành phần mix dựa trên số mẻ thực tế
        print(f"Tính toán mix từ các công thức đã chọn cho từng ô")

        # Duyệt qua từng ô đã có dữ liệu
        for cell_key, cell_data in self.cell_formula_data.items():
            batch_value = cell_data["batch_value"]
            actual_batches = cell_data["actual_batches"]
            mix_formula_name = cell_data.get("mix_formula")

            if not mix_formula_name:
                continue

            # Lấy công thức mix
            mix_formula = self.formula_manager.load_mix_preset(mix_formula_name)
            if not mix_formula:
                continue

            # Lưu thông tin công thức mix được sử dụng
            if mix_formula_name not in mix_formulas_used:
                mix_formulas_used[mix_formula_name] = {
                    "formula": mix_formula,
                    "batch_value": 0
                }

            # Cộng dồn số mẻ
            mix_formulas_used[mix_formula_name]["batch_value"] += batch_value

        # Tính toán thành phần mix từ các công thức mix đã sử dụng
        print(f"Tính toán từ {len(mix_formulas_used)} công thức mix")

        for mix_name, mix_data in mix_formulas_used.items():
            mix_formula = mix_data["formula"]
            batch_value = mix_data["batch_value"]

            # Áp dụng quy tắc 0.5 = 1 mẻ, 1 = 2 mẻ
            actual_batches = batch_value * 2

            print(f"Công thức mix '{mix_name}': {batch_value} mẻ (thực tế {actual_batches} mẻ)")

            # Tính lượng từng thành phần mix
            for ingredient, amount_per_batch in mix_formula.items():
                # Lấy giá trị từ cột '1 mẻ (kg)' thay vì cột '10 mẻ (kg)'
                # amount_per_batch là giá trị cho 10 mẻ, chia 10 để có giá trị cho 1 mẻ
                one_batch_amount = amount_per_batch / 10

                # Tính lượng thành phần theo số mẻ thực tế
                mix_amount = one_batch_amount * actual_batches

                print(f"  {ingredient}: {one_batch_amount} × {actual_batches} = {mix_amount:.2f} kg")

                # Cộng dồn vào kết quả
                if ingredient in mix_ingredients:
                    mix_ingredients[ingredient] += mix_amount
                    print(f"    Cộng dồn: {ingredient} = {mix_ingredients[ingredient]:.2f} kg")
                else:
                    mix_ingredients[ingredient] = mix_amount
                    print(f"    Thêm mới: {ingredient} = {mix_amount:.2f} kg")

        # Tính tổng lượng mix trước
        total_mix = sum(mix_ingredients.values()) if mix_ingredients else 0

        # Đảm bảo thành phần "Nguyên liệu tổ hợp" trong cám trùng với tổng mix
        if "Nguyên liệu tổ hợp" in feed_ingredients:
            # Nếu có thành phần "Nguyên liệu tổ hợp" thì cập nhật giá trị bằng tổng mix
            if total_mix > 0:
                feed_ingredients["Nguyên liệu tổ hợp"] = total_mix

        # Tính tổng lượng cám (BAO GỒM cả "Nguyên liệu tổ hợp")
        total_feed = sum(feed_ingredients.values()) if feed_ingredients else 0

        # Validation: total_feed phải bằng (individual feed ingredients) + total_mix
        individual_feed_total = 0
        for ingredient, amount in feed_ingredients.items():
            if ingredient != "Nguyên liệu tổ hợp":  # Chỉ tính các nguyên liệu cám thuần
                individual_feed_total += amount

        expected_total_feed = individual_feed_total + total_mix
        if abs(total_feed - expected_total_feed) > 0.1:  # Tolerance 0.1 kg
            print(f"CẢNH BÁO: Sai lệch tính toán! total_feed={total_feed:.2f}, expected={expected_total_feed:.2f}")

        print(f"Tính toán hoàn tất - Total feed: {format_total(total_feed)} kg (bao gồm {individual_feed_total:.2f} kg cám + {format_total(total_mix)} kg mix)")

        # Lưu kết quả tính toán vào biến thành viên để sử dụng khi lưu báo cáo
        self.feed_ingredients = feed_ingredients
        self.mix_ingredients = mix_ingredients
        self.mix_formulas_used = mix_formulas_used
        self.total_batches = total_batches
        self.total_batches_by_area = total_batches_by_area
        self.total_tong_hop = total_mix  # Lưu tổng mix để sử dụng sau này

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
                    # Thử lấy giá trị từ spin box ở cột 2 (lượng kg) không phải cột 1 (%)
                    amount_spin = self.feed_formula_table.cellWidget(row, 2)
                    if amount_spin is not None:
                        amount = amount_spin.value()
                    else:
                        # Nếu không có spin box, thử lấy giá trị từ item ở cột 2
                        item = self.feed_formula_table.item(row, 2)
                        if item is not None:
                            amount = float(item.text().replace(',', '.'))
                        else:
                            # Nếu không có item, sử dụng giá trị từ công thức hiện tại
                            amount = self.feed_formula.get(ingredient, 0)

                    # Đã bỏ "Nguyên liệu tổ hợp" nên không cần đoạn code xử lý riêng cho nó

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
                    # Thử lấy giá trị từ spin box ở cột 2 (lượng kg) không phải cột 1 (%)
                    amount_spin = self.mix_formula_table.cellWidget(row, 2)
                    if amount_spin is not None:
                        amount = amount_spin.value()
                    else:
                        # Nếu không có spin box, thử lấy giá trị từ item ở cột 2
                        item = self.mix_formula_table.item(row, 2)
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

            # Cập nhật tồn kho dựa trên số lượng đã sử dụng
            all_ingredients_used = {}

            # Gộp tất cả nguyên liệu đã sử dụng
            for ingredient, amount in self.feed_ingredients.items():
                if ingredient in all_ingredients_used:
                    all_ingredients_used[ingredient] += amount
                else:
                    all_ingredients_used[ingredient] = amount

            for ingredient, amount in self.mix_ingredients.items():
                if ingredient in all_ingredients_used:
                    all_ingredients_used[ingredient] += amount
                else:
                    all_ingredients_used[ingredient] = amount

            # Cập nhật tồn kho
            self.update_inventory_after_usage(all_ingredients_used)

            # Tạo thư mục báo cáo nếu chưa tồn tại
            reports_dir = "src/data/reports"
            if not os.path.exists(reports_dir):
                os.makedirs(reports_dir)

            # Luôn lấy ngày từ UI để đảm bảo lưu đúng vào ngày đang hiển thị
            date_text = ""
            for widget in self.findChildren(QLabel):
                if widget.text().startswith("Ngày:"):
                    date_text = widget.text().replace("Ngày:", "").strip()
                    break

            # Nếu không tìm thấy ngày trên UI, sử dụng ngày hiện tại
            if not date_text:
                date_text = QDate.currentDate().toString("dd/MM/yyyy")

            # Chuyển đổi định dạng ngày từ dd/MM/yyyy sang yyyyMMdd để đặt tên file
            try:
                day, month, year = date_text.split('/')
                date_str = f"{year}{month.zfill(2)}{day.zfill(2)}"
            except Exception as e:
                print(f"Lỗi khi chuyển đổi định dạng ngày: {str(e)}")
                # Nếu có lỗi, sử dụng ngày hiện tại
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

            # Tính tổng lượng cám và mix từ thành phần
            total_mix = 0
            batch_count = 0

            # Tính tổng lượng mix từ thành phần
            for ingredient, amount in self.mix_ingredients.items():
                total_mix += amount

            # Tính tổng lượng cám (BAO GỒM cả "Nguyên liệu tổ hợp")
            total_feed = sum(self.feed_ingredients.values()) if self.feed_ingredients else 0

            # Lấy tổng số mẻ
            batch_count = self.total_batches

            # Tạo dữ liệu báo cáo
            report_data = {
                "date": date_str,
                "display_date": display_date,
                "feed_usage": feed_usage,
                "formula_usage": formula_usage,
                "feed_ingredients": self.feed_ingredients,
                "mix_ingredients": self.mix_ingredients,
                "total_batches": self.total_batches,
                "total_batches_by_area": self.total_batches_by_area,
                "default_formula": self.default_formula_combo.currentText(),
                "total_feed": total_feed,
                "total_mix": total_mix,
                "batch_count": batch_count
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

            QMessageBox.information(self, "Thành công", f"Đã lưu báo cáo vào {report_file} và đã cập nhật tồn kho")

            # Cập nhật danh sách báo cáo trong tab lịch sử
            self.update_history_dates()

            # Cập nhật bảng lịch sử cám
            self.load_feed_usage_history(show_message=False)

        except Exception as e:
            print(f"Lỗi khi lưu báo cáo: {str(e)}")
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu báo cáo: {str(e)}")

        return True

    def export_to_excel(self):
        """Export current report to Excel"""
        try:
            # Luôn lấy ngày từ UI để đảm bảo xuất đúng vào ngày đang hiển thị
            date_text = ""
            for widget in self.findChildren(QLabel):
                if widget.text().startswith("Ngày:"):
                    date_text = widget.text().replace("Ngày:", "").strip()
                    break

            # Nếu không tìm thấy ngày trên UI, sử dụng ngày hiện tại
            if not date_text:
                date_text = QDate.currentDate().toString("dd/MM/yyyy")

            # Chuyển đổi định dạng ngày từ dd/MM/yyyy sang yyyyMMdd để đặt tên file
            try:
                day, month, year = date_text.split('/')
                date_str = f"{year}{month.zfill(2)}{day.zfill(2)}"
            except Exception as e:
                print(f"Lỗi khi chuyển đổi định dạng ngày: {str(e)}")
                # Nếu có lỗi, sử dụng ngày hiện tại
                date_str = QDate.currentDate().toString("yyyyMMdd")

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
            self.update_mix_preset_combo()

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
                    # Thử lấy giá trị từ spin box ở cột 2 (lượng kg) không phải cột 1 (%)
                    amount_spin = self.feed_formula_table.cellWidget(row, 2)
                    if amount_spin is not None:
                        amount = amount_spin.value()
                    else:
                        # Nếu không có spin box, thử lấy giá trị từ item ở cột 2
                        item = self.feed_formula_table.item(row, 2)
                        if item is not None:
                            amount = float(item.text().replace(',', '.'))
                        else:
                            # Nếu không có item, sử dụng giá trị từ công thức hiện tại
                            amount = self.feed_formula.get(ingredient, 0)

                    # Đã bỏ "Nguyên liệu tổ hợp" nên không cần đoạn code xử lý riêng cho nó

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
                    # Thử lấy giá trị từ spin box ở cột 2 (lượng kg) không phải cột 1 (%)
                    amount_spin = self.mix_formula_table.cellWidget(row, 2)
                    if amount_spin is not None:
                        amount = amount_spin.value()
                    else:
                        # Nếu không có spin box, thử lấy giá trị từ item ở cột 2
                        item = self.mix_formula_table.item(row, 2)
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
            self.update_mix_preset_combo()

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

    def fill_table_from_report(self, date_text, update_default_formula=True):
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

            # Chỉ cập nhật default formula khi user chọn báo cáo, không phải khi auto-load
            if update_default_formula and "default_formula" in report_data and report_data["default_formula"]:
                default_formula = report_data["default_formula"]
                print(f"[DEBUG] Updating default formula from report: '{default_formula}' (update_default_formula={update_default_formula})")
                # Cập nhật UI và lưu vào cấu hình
                self.default_formula_combo.setCurrentText(default_formula)
                self.formula_manager.save_default_feed_formula(default_formula)
                print(f"[SUCCESS] Default formula updated and saved: '{default_formula}'")
            elif "default_formula" in report_data and report_data["default_formula"]:
                print(f"[DEBUG] Skipping default formula update from report: '{report_data['default_formula']}' (update_default_formula={update_default_formula})")

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
            # Kiểm tra xem đã có báo cáo cho ngày này chưa
            report_exists = False
            for i in range(self.history_date_combo.count()):
                if self.history_date_combo.itemText(i) == date_text:
                    report_exists = True
                    break

            if report_exists:
                reply = QMessageBox.question(
                    self,
                    "Xác nhận",
                    f"Đã tồn tại báo cáo cho ngày {date_text}. Bạn muốn:\n\n"
                    "- Tải dữ liệu từ báo cáo đã lưu (Có)\n"
                    "- Tạo bảng mới để nhập dữ liệu (Không)",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )

                if reply == QMessageBox.Yes:
                    self.fill_table_from_report(date_text)
                    return

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

            # Xóa dữ liệu công thức mix cho từng ô
            if hasattr(self, 'cell_mix_formulas'):
                self.cell_mix_formulas = {}

            QMessageBox.information(self, "Thành công", f"Đã tạo bảng mới cho ngày {date_text}\n\nBạn có thể bắt đầu nhập dữ liệu cám cho ngày này.")

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

                    # Tự động điền vào bảng cám (không cập nhật default formula)
                    self.fill_table_from_report(today, update_default_formula=False)
                    print(f"Đã điền bảng cám với dữ liệu ngày {today} (giữ nguyên default formula)")
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

        # Get responsive dialog size
        dialog_width, dialog_height = self.get_responsive_dialog_size()
        report_dialog.resize(dialog_width, dialog_height)

        # Center dialog on screen
        report_dialog.move((self.screen_width - dialog_width) // 2, (self.screen_height - dialog_height) // 2)

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

                # Tạo các tab (removed tab_batches)
        tab_area_report = QWidget() # Tab báo cáo theo khu - moved to first position
        tab_feed = QWidget()        # Tab thành phần cám
        tab_mix = QWidget()         # Tab thành phần mix

        # Thêm các tab vào TabWidget với thứ tự mới
        report_tabs.addTab(tab_area_report, "🏭 Báo cáo theo Khu")  # Position 1
        report_tabs.addTab(tab_feed, "Thành Phần Cám")              # Position 2
        report_tabs.addTab(tab_mix, "Thành Phần Mix")               # Position 3

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

                # Tạo bảng thành phần cám với compact styling
        feed_table = QTableWidget()
        responsive_font_size = self.get_responsive_font_size(14)  # Compact font
        feed_table.setFont(QFont("Arial", responsive_font_size, QFont.Medium))
        feed_table.setColumnCount(5)  # Ingredient, Amount, Bags, Inventory, Remaining
        feed_table.setHorizontalHeaderLabels(["🌾 Thành phần", "⚖️ Số lượng (kg)", "📦 Số bao", "📊 Tồn kho (kg)", "📈 Tồn kho sau (kg)"])
        responsive_header_font_size = self.get_responsive_font_size(15)  # Compact header font
        feed_table.horizontalHeader().setFont(QFont("Arial", responsive_header_font_size, QFont.Bold))

        # Enhanced column width configuration
        header = feed_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Thành phần
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Số lượng
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Số bao
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Tồn kho
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Tồn kho sau
        header.setMinimumSectionSize(120)

        # Enhanced row height with responsive scaling
        responsive_row_height = self.get_responsive_row_height(70)
        feed_table.verticalHeader().setDefaultSectionSize(responsive_row_height)
        feed_table.verticalHeader().setVisible(False)

        # Đặt bảng ở chế độ chỉ đọc - không cho phép chỉnh sửa
        feed_table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Enhanced table styling matching Area Report
        feed_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #e0e0e0;
                background-color: white;
                alternate-background-color: #f8f9fa;
                border: 1px solid #d0d0d0;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 500;
                selection-background-color: #e3f2fd;
            }
            QTableWidget::item {
                padding: 20px 16px;
                border-bottom: 1px solid #e8e8e8;
                border-right: 1px solid #f0f0f0;
                color: #2c2c2c;
                font-weight: 500;
                min-height: 70px;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
                font-weight: 600;
            }
            QTableWidget::item:hover {
                background-color: #f5f5f5;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 20px 16px;
                border: none;
                border-bottom: 3px solid #4CAF50;
                border-right: 1px solid #e0e0e0;
                font-weight: bold;
                font-size: 17px;
                color: #2E7D32;
                min-height: 65px;
            }
            QHeaderView::section:hover {
                background-color: #e8f5e8;
            }
        """)

        feed_table.setAlternatingRowColors(True)
        feed_table.setSelectionBehavior(QAbstractItemView.SelectRows)

        # Set responsive table height
        responsive_table_height = self.get_responsive_table_height(500)
        feed_table.setMinimumHeight(responsive_table_height)
        feed_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

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
        feed_table.setSpan(row, 0, 1, 5)  # Merge cells for header across 5 columns

        row += 1

        # Thêm thành phần cám với enhanced formatting
        for ingredient, amount in sorted_feed_ingredients.items():
            # Ingredient name with compact styling
            ingredient_item = QTableWidgetItem(ingredient)
            ingredient_item.setFont(QFont("Arial", self.get_responsive_font_size(13), QFont.Medium))
            ingredient_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            feed_table.setItem(row, 0, ingredient_item)

            # Amount with thousand separators and compact font
            amount_item = QTableWidgetItem(f"{amount:,.1f}")
            amount_item.setFont(QFont("Arial", self.get_responsive_font_size(13), QFont.Bold))
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            feed_table.setItem(row, 1, amount_item)

            # Calculate bags with enhanced formatting
            bag_size = self.inventory_manager.get_bag_size(ingredient)
            bags = self.inventory_manager.calculate_bags(ingredient, amount)
            bags_item = QTableWidgetItem(f"{bags:,.1f}")
            bags_item.setFont(QFont("Arial", 16, QFont.Medium))
            bags_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            feed_table.setItem(row, 2, bags_item)

            # Add inventory information with enhanced styling
            inventory_amount = self.inventory_manager.get_inventory().get(ingredient, 0)
            inventory_item = QTableWidgetItem(f"{inventory_amount:,.1f}")
            inventory_item.setFont(QFont("Arial", 16, QFont.Medium))
            inventory_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            inventory_item.setBackground(QColor("#e3f2fd"))  # Light blue background
            feed_table.setItem(row, 3, inventory_item)

            # Add remaining inventory after usage with enhanced styling
            remaining = max(0, inventory_amount - amount)
            remaining_item = QTableWidgetItem(f"{remaining:,.1f}")
            remaining_item.setFont(QFont("Arial", 16, QFont.Medium))
            remaining_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            # Color code remaining inventory
            if remaining < amount * 0.1:  # Less than 10% of usage
                remaining_item.setBackground(QColor("#ffebee"))  # Light red
                remaining_item.setForeground(QBrush(QColor("#d32f2f")))  # Red text
            elif remaining < amount * 0.5:  # Less than 50% of usage
                remaining_item.setBackground(QColor("#fff3e0"))  # Light orange
                remaining_item.setForeground(QBrush(QColor("#f57c00")))  # Orange text
            else:
                remaining_item.setBackground(QColor("#e8f5e9"))  # Light green
                remaining_item.setForeground(QBrush(QColor("#388e3c")))  # Green text

            feed_table.setItem(row, 4, remaining_item)

            row += 1

        # Thêm tổng cộng cho cám với enhanced styling
        total_feed_amount = sum(self.feed_ingredients.values())

        # Enhanced TOTAL row styling
        total_feed_item = QTableWidgetItem("📊 TỔNG CÁM")
        total_feed_item.setFont(QFont("Arial", 16, QFont.Bold))
        total_feed_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        total_feed_item.setBackground(QColor("#2E7D32"))  # Dark green background
        total_feed_item.setForeground(QBrush(QColor("#ffffff")))  # White text
        feed_table.setItem(row, 0, total_feed_item)

        total_feed_amount_item = QTableWidgetItem(f"{total_feed_amount:,.1f}")
        total_feed_amount_item.setFont(QFont("Arial", 16, QFont.Bold))
        total_feed_amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        total_feed_amount_item.setBackground(QColor("#2E7D32"))  # Dark green background
        total_feed_amount_item.setForeground(QBrush(QColor("#ffffff")))  # White text
        feed_table.setItem(row, 1, total_feed_amount_item)

        # Enhanced empty cells for total row
        for col in range(2, 5):
            empty_item = QTableWidgetItem("")
            empty_item.setBackground(QColor("#2E7D32"))  # Dark green background
            feed_table.setItem(row, col, empty_item)

        # Thêm bảng vào layout tab thành phần cám
        feed_layout_scroll.addWidget(feed_table)

        # Hoàn thành scroll area cho tab thành phần cám
        feed_scroll.setWidget(feed_content)
        feed_layout.addWidget(feed_scroll)

        # Tạo bảng thành phần mix với compact styling
        mix_table = QTableWidget()
        responsive_font_size = self.get_responsive_font_size(14)  # Compact font
        mix_table.setFont(QFont("Arial", responsive_font_size, QFont.Medium))
        mix_table.setColumnCount(5)  # Ingredient, Amount, Bags, Inventory, Remaining
        mix_table.setHorizontalHeaderLabels(["🧪 Thành phần", "⚖️ Số lượng (kg)", "📦 Số bao", "📊 Tồn kho (kg)", "📈 Tồn kho sau (kg)"])
        responsive_header_font_size = self.get_responsive_font_size(15)  # Compact header font
        mix_table.horizontalHeader().setFont(QFont("Arial", responsive_header_font_size, QFont.Bold))

        # Enhanced column width configuration
        header = mix_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Thành phần
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Số lượng
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Số bao
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Tồn kho
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Tồn kho sau
        header.setMinimumSectionSize(120)

        # Enhanced row height with responsive scaling
        responsive_row_height = self.get_responsive_row_height(70)
        mix_table.verticalHeader().setDefaultSectionSize(responsive_row_height)
        mix_table.verticalHeader().setVisible(False)

        # Đặt bảng ở chế độ chỉ đọc - không cho phép chỉnh sửa
        mix_table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Enhanced table styling matching Area Report (with orange accent for mix)
        mix_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #e0e0e0;
                background-color: white;
                alternate-background-color: #f8f9fa;
                border: 1px solid #d0d0d0;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 500;
                selection-background-color: #e3f2fd;
            }
            QTableWidget::item {
                padding: 20px 16px;
                border-bottom: 1px solid #e8e8e8;
                border-right: 1px solid #f0f0f0;
                color: #2c2c2c;
                font-weight: 500;
                min-height: 70px;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
                font-weight: 600;
            }
            QTableWidget::item:hover {
                background-color: #f5f5f5;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 20px 16px;
                border: none;
                border-bottom: 3px solid #FF9800;
                border-right: 1px solid #e0e0e0;
                font-weight: bold;
                font-size: 17px;
                color: #E65100;
                min-height: 65px;
            }
            QHeaderView::section:hover {
                background-color: #fff3e0;
            }
        """)

        mix_table.setAlternatingRowColors(True)
        mix_table.setSelectionBehavior(QAbstractItemView.SelectRows)

        # Set responsive table height
        responsive_table_height = self.get_responsive_table_height(500)
        mix_table.setMinimumHeight(responsive_table_height)
        mix_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Tính tổng số hàng cần thiết cho bảng mix
        mix_rows = len(self.mix_ingredients) + 2  # +2 cho tiêu đề và tổng cộng
        mix_table.setRowCount(mix_rows)

        # Thêm tiêu đề kho mix
        row = 0
        mix_header = QTableWidgetItem("THÀNH PHẦN KHO MIX")
        mix_header.setFont(QFont("Arial", DEFAULT_FONT_SIZE + 2, QFont.Bold))  # Tăng kích thước font
        mix_header.setBackground(QColor(240, 220, 220))  # Light red background
        mix_table.setItem(row, 0, mix_header)
        mix_table.setSpan(row, 0, 1, 5)  # Merge cells for header across 5 columns

        row += 1

        # Thêm thành phần mix với enhanced formatting
        for ingredient, amount in self.mix_ingredients.items():
            # Ingredient name with enhanced styling
            ingredient_item = QTableWidgetItem(ingredient)
            ingredient_item.setFont(QFont("Arial", 16, QFont.Medium))
            ingredient_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            mix_table.setItem(row, 0, ingredient_item)

            # Amount with thousand separators
            amount_item = QTableWidgetItem(f"{amount:,.1f}")
            amount_item.setFont(QFont("Arial", 16, QFont.Bold))
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            mix_table.setItem(row, 1, amount_item)

            # Calculate bags with enhanced formatting
            bag_size = self.inventory_manager.get_bag_size(ingredient)
            bags = self.inventory_manager.calculate_bags(ingredient, amount)
            bags_item = QTableWidgetItem(f"{bags:,.1f}")
            bags_item.setFont(QFont("Arial", 16, QFont.Medium))
            bags_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            mix_table.setItem(row, 2, bags_item)

            # Add inventory information with enhanced styling
            inventory_amount = self.inventory_manager.get_inventory().get(ingredient, 0)
            inventory_item = QTableWidgetItem(f"{inventory_amount:,.1f}")
            inventory_item.setFont(QFont("Arial", 16, QFont.Medium))
            inventory_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            inventory_item.setBackground(QColor("#fff3e0"))  # Light orange background
            mix_table.setItem(row, 3, inventory_item)

            # Add remaining inventory after usage with enhanced styling
            remaining = max(0, inventory_amount - amount)
            remaining_item = QTableWidgetItem(f"{remaining:,.1f}")
            remaining_item.setFont(QFont("Arial", 16, QFont.Medium))
            remaining_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            # Color code remaining inventory (orange theme for mix)
            if remaining < amount * 0.1:  # Less than 10% of usage
                remaining_item.setBackground(QColor("#ffebee"))  # Light red
                remaining_item.setForeground(QBrush(QColor("#d32f2f")))  # Red text
            elif remaining < amount * 0.5:  # Less than 50% of usage
                remaining_item.setBackground(QColor("#fff8e1"))  # Light amber
                remaining_item.setForeground(QBrush(QColor("#f57c00")))  # Orange text
            else:
                remaining_item.setBackground(QColor("#f3e5f5"))  # Light purple
                remaining_item.setForeground(QBrush(QColor("#7b1fa2")))  # Purple text

            mix_table.setItem(row, 4, remaining_item)

            row += 1

        # Thêm tổng cộng cho mix
        total_mix_amount = sum(self.mix_ingredients.values())

        # Enhanced TOTAL row styling for mix
        total_mix_item = QTableWidgetItem("🧪 TỔNG MIX")
        total_mix_item.setFont(QFont("Arial", 16, QFont.Bold))
        total_mix_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        total_mix_item.setBackground(QColor("#E65100"))  # Dark orange background
        total_mix_item.setForeground(QBrush(QColor("#ffffff")))  # White text
        mix_table.setItem(row, 0, total_mix_item)

        total_mix_amount_item = QTableWidgetItem(f"{total_mix_amount:,.1f}")
        total_mix_amount_item.setFont(QFont("Arial", 16, QFont.Bold))
        total_mix_amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        total_mix_amount_item.setBackground(QColor("#E65100"))  # Dark orange background
        total_mix_amount_item.setForeground(QBrush(QColor("#ffffff")))  # White text
        mix_table.setItem(row, 1, total_mix_amount_item)

        # Enhanced empty cells for total row
        for col in range(2, 5):
            empty_item = QTableWidgetItem("")
            empty_item.setBackground(QColor("#E65100"))  # Dark orange background
            mix_table.setItem(row, col, empty_item)

        # Thêm bảng vào layout tab thành phần mix
        mix_layout_scroll.addWidget(mix_table)

        # Hoàn thành scroll area cho tab thành phần mix
        mix_scroll.setWidget(mix_content)
        mix_layout.addWidget(mix_scroll)

        # Thiết lập tab báo cáo theo khu (moved to first position)
        self.setup_area_report_tab(tab_area_report)

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

    def setup_area_report_tab(self, tab_area_report):
        """Setup area report tab with detailed breakdown by area"""
        area_layout = QVBoxLayout(tab_area_report)

        # Tạo widget scroll cho nội dung tab báo cáo theo khu
        area_scroll = QScrollArea()
        area_scroll.setWidgetResizable(True)
        area_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        area_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        area_content = QWidget()
        area_layout_scroll = QVBoxLayout(area_content)

        # Header section
        header_label = QLabel("<b>📊 Báo cáo chi tiết theo từng khu vực sản xuất</b>")
        header_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet("""
            QLabel {
                color: #2E7D32;
                background-color: #e8f5e9;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 15px;
            }
        """)
        area_layout_scroll.addWidget(header_label)

        # Calculate area-specific data
        area_data = self.calculate_area_breakdown()

        # Create area report table with improved structure
        area_table = QTableWidget()
        area_table.setFont(QFont("Arial", 16, QFont.Medium))  # Increased font size
        area_table.setColumnCount(5)  # Reduced from 7 to 5 columns
        area_table.setHorizontalHeaderLabels([
            "🏭 Khu vực", "🌾 Cám (kg)", "🧪 Mix (kg)", "🔢 Số mẻ", "📊 Tỷ lệ (%)"
        ])

        # Enhanced table styling with responsive design
        area_table.setStyleSheet(self.get_responsive_table_css("#4CAF50", "#2E7D32"))

        # Set enhanced row height with responsive scaling
        responsive_row_height = self.get_responsive_row_height(70)
        area_table.verticalHeader().setDefaultSectionSize(responsive_row_height)
        area_table.verticalHeader().setVisible(False)

        # Set improved column widths for better readability
        header = area_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Khu vực
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Cám (kg) - more space
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Mix (kg) - more space
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Số mẻ
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Tỷ lệ
        header.setMinimumSectionSize(120)  # Increased minimum width

        area_table.setAlternatingRowColors(True)
        area_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        area_table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Set responsive minimum height for better visibility
        responsive_table_height = self.get_responsive_table_height(500)
        area_table.setMinimumHeight(responsive_table_height)
        area_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Populate table with area data
        self.populate_area_table(area_table, area_data)

        area_layout_scroll.addWidget(area_table)

        # Add summary section
        self.add_area_summary_section(area_layout_scroll, area_data)

        area_layout_scroll.addStretch()

        # Complete scroll area setup
        area_scroll.setWidget(area_content)
        area_layout.addWidget(area_scroll)

    def calculate_area_breakdown(self):
        """Calculate feed and mix breakdown by area"""
        area_data = {}

        try:
            # Get total batches by area
            total_batches_by_area = getattr(self, 'total_batches_by_area', {})
            total_batches = sum(total_batches_by_area.values()) if total_batches_by_area else 0

            # Get total ingredients
            feed_ingredients = getattr(self, 'feed_ingredients', {})
            mix_ingredients = getattr(self, 'mix_ingredients', {})

            total_feed_kg = sum(feed_ingredients.values()) if feed_ingredients else 0
            total_mix_kg = sum(mix_ingredients.values()) if mix_ingredients else 0

            # Calculate breakdown for each area
            for area, area_batches in total_batches_by_area.items():
                if total_batches > 0:
                    # Calculate proportional distribution
                    batch_ratio = area_batches / total_batches

                    # Calculate feed quantities for this area
                    area_feed_kg = total_feed_kg * batch_ratio

                    # Calculate mix quantities for this area
                    area_mix_kg = total_mix_kg * batch_ratio

                    # Calculate percentage
                    percentage = (area_batches / total_batches) * 100 if total_batches > 0 else 0

                    area_data[area] = {
                        'feed_kg': area_feed_kg,
                        'mix_kg': area_mix_kg,
                        'batches': area_batches,
                        'percentage': percentage
                    }

            # Add totals
            area_data['TOTAL'] = {
                'feed_kg': total_feed_kg,
                'mix_kg': total_mix_kg,
                'batches': total_batches,
                'percentage': 100.0
            }

        except Exception as e:
            print(f"Error calculating area breakdown: {str(e)}")

        return area_data

    def populate_area_table(self, table, area_data):
        """Populate area table with calculated data"""
        try:
            # Define area colors for visual distinction
            area_colors = {
                'Khu A': '#e3f2fd',    # Light blue
                'Khu B': '#e8f5e9',    # Light green
                'Khu C': '#fff3e0',    # Light orange
                'Khu D': '#f3e5f5',    # Light purple
                'Khu E': '#fce4ec',    # Light pink
                'TOTAL': '#2E7D32'     # Dark green for prominence
            }

            # Text colors for better contrast
            text_colors = {
                'Khu A': '#2c2c2c',    # Dark text for light backgrounds
                'Khu B': '#2c2c2c',
                'Khu C': '#2c2c2c',
                'Khu D': '#2c2c2c',
                'Khu E': '#2c2c2c',
                'TOTAL': '#ffffff'     # White text for dark background
            }

            # Sort areas (put TOTAL at the end)
            sorted_areas = sorted([area for area in area_data.keys() if area != 'TOTAL'])
            if 'TOTAL' in area_data:
                sorted_areas.append('TOTAL')

            table.setRowCount(len(sorted_areas))

            for row, area in enumerate(sorted_areas):
                data = area_data[area]

                # Area name with icon
                area_icon = "🏭" if area != 'TOTAL' else "📊"
                area_name = f"{area_icon} {area}"
                area_item = QTableWidgetItem(area_name)
                area_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                area_item.setFont(QFont("Arial", 16, QFont.Bold if area == 'TOTAL' else QFont.Medium))

                # Set background and text colors for enhanced TOTAL row
                if area in area_colors:
                    area_item.setBackground(QColor(area_colors[area]))
                if area in text_colors:
                    area_item.setForeground(QBrush(QColor(text_colors[area])))

                table.setItem(row, 0, area_item)

                # Feed kg - Column 1
                feed_kg_item = QTableWidgetItem(f"{data['feed_kg']:,.1f}")
                feed_kg_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                feed_kg_item.setFont(QFont("Arial", 16, QFont.Bold if area == 'TOTAL' else QFont.Medium))
                if area in area_colors:
                    feed_kg_item.setBackground(QColor(area_colors[area]))
                if area in text_colors:
                    feed_kg_item.setForeground(QBrush(QColor(text_colors[area])))
                table.setItem(row, 1, feed_kg_item)

                # Mix kg - Column 2
                mix_kg_item = QTableWidgetItem(f"{data['mix_kg']:,.1f}")
                mix_kg_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                mix_kg_item.setFont(QFont("Arial", 16, QFont.Bold if area == 'TOTAL' else QFont.Medium))
                if area in area_colors:
                    mix_kg_item.setBackground(QColor(area_colors[area]))
                if area in text_colors:
                    mix_kg_item.setForeground(QBrush(QColor(text_colors[area])))
                table.setItem(row, 2, mix_kg_item)

                # Batches - Column 3
                batches_item = QTableWidgetItem(f"{data['batches']:,.0f}")
                batches_item.setTextAlignment(Qt.AlignCenter)
                batches_item.setFont(QFont("Arial", 16, QFont.Bold if area == 'TOTAL' else QFont.Medium))
                if area in area_colors:
                    batches_item.setBackground(QColor(area_colors[area]))
                if area in text_colors:
                    batches_item.setForeground(QBrush(QColor(text_colors[area])))
                table.setItem(row, 3, batches_item)

                # Percentage - Column 4
                percentage_item = QTableWidgetItem(f"{data['percentage']:.1f}%")
                percentage_item.setTextAlignment(Qt.AlignCenter)
                percentage_item.setFont(QFont("Arial", 16, QFont.Bold if area == 'TOTAL' else QFont.Medium))
                if area in area_colors:
                    percentage_item.setBackground(QColor(area_colors[area]))

                # Enhanced color coding for percentage
                if area == 'TOTAL':
                    # White text for TOTAL row
                    percentage_item.setForeground(QBrush(QColor(text_colors[area])))
                else:
                    # Color code percentage for better visual feedback
                    if data['percentage'] >= 30:
                        percentage_item.setForeground(QBrush(QColor("#4CAF50")))  # Green
                    elif data['percentage'] >= 15:
                        percentage_item.setForeground(QBrush(QColor("#FF9800")))  # Orange
                    else:
                        percentage_item.setForeground(QBrush(QColor("#f44336")))  # Red

                table.setItem(row, 4, percentage_item)

        except Exception as e:
            print(f"Error populating area table: {str(e)}")

    def add_area_summary_section(self, layout, area_data):
        """Add summary section with key insights"""
        try:
            # Summary header
            summary_header = QLabel("<b>📈 Tóm tắt và Phân tích</b>")
            summary_header.setFont(QFont("Arial", 16, QFont.Bold))
            summary_header.setStyleSheet("""
                QLabel {
                    color: #1976D2;
                    background-color: #e3f2fd;
                    padding: 12px;
                    border-radius: 8px;
                    margin: 15px 0px 10px 0px;
                }
            """)
            layout.addWidget(summary_header)

            # Calculate insights
            if area_data and len(area_data) > 1:  # More than just TOTAL
                areas = [area for area in area_data.keys() if area != 'TOTAL']

                # Find highest and lowest production areas
                highest_area = max(areas, key=lambda x: area_data[x]['batches'])
                lowest_area = min(areas, key=lambda x: area_data[x]['batches'])

                # Calculate efficiency metrics
                total_data = area_data.get('TOTAL', {})
                avg_batches_per_area = total_data.get('batches', 0) / len(areas) if areas else 0

                # Create insights text
                insights_text = f"""
                <div style="font-size: 14px; line-height: 1.6;">
                    <p><b>🎯 Khu vực sản xuất cao nhất:</b> {highest_area}
                       ({area_data[highest_area]['batches']:.0f} mẻ - {area_data[highest_area]['percentage']:.1f}%)</p>

                    <p><b>📉 Khu vực sản xuất thấp nhất:</b> {lowest_area}
                       ({area_data[lowest_area]['batches']:.0f} mẻ - {area_data[lowest_area]['percentage']:.1f}%)</p>

                    <p><b>📊 Trung bình mẻ/khu:</b> {avg_batches_per_area:.1f} mẻ</p>

                    <p><b>🌾 Tổng lượng cám:</b> {total_data.get('feed_kg', 0):,.1f} kg</p>

                    <p><b>🧪 Tổng lượng mix:</b> {total_data.get('mix_kg', 0):,.1f} kg</p>

                    <p><b>🔢 Tổng số mẻ:</b> {total_data.get('batches', 0):,.0f} mẻ</p>
                </div>
                """

                insights_label = QLabel(insights_text)
                insights_label.setFont(QFont("Arial", 14))
                insights_label.setStyleSheet("""
                    QLabel {
                        background-color: #f8f9fa;
                        padding: 15px;
                        border-radius: 8px;
                        border-left: 4px solid #4CAF50;
                        margin: 5px 0px;
                    }
                """)
                insights_label.setWordWrap(True)
                layout.addWidget(insights_label)

                # Add efficiency recommendations
                self.add_efficiency_recommendations(layout, area_data)

        except Exception as e:
            print(f"Error adding area summary: {str(e)}")

    def add_efficiency_recommendations(self, layout, area_data):
        """Add efficiency recommendations based on area data"""
        try:
            recommendations = []

            if area_data and len(area_data) > 1:
                areas = [area for area in area_data.keys() if area != 'TOTAL']
                total_batches = area_data.get('TOTAL', {}).get('batches', 0)

                # Check for imbalanced production
                for area in areas:
                    percentage = area_data[area]['percentage']
                    if percentage > 40:
                        recommendations.append(f"⚠️ {area} chiếm {percentage:.1f}% sản lượng - cân nhắc phân bổ lại")
                    elif percentage < 10:
                        recommendations.append(f"📈 {area} chỉ chiếm {percentage:.1f}% - có thể tăng công suất")

                # Check feed/mix ratio
                total_feed = area_data.get('TOTAL', {}).get('feed_kg', 0)
                total_mix = area_data.get('TOTAL', {}).get('mix_kg', 0)
                if total_feed > 0:
                    mix_ratio = (total_mix / total_feed) * 100
                    if mix_ratio < 1:
                        recommendations.append(f"🧪 Tỷ lệ mix thấp ({mix_ratio:.1f}%) - xem xét tăng mix")
                    elif mix_ratio > 3:
                        recommendations.append(f"🧪 Tỷ lệ mix cao ({mix_ratio:.1f}%) - kiểm tra công thức")

            if recommendations:
                rec_header = QLabel("<b>💡 Khuyến nghị cải thiện</b>")
                rec_header.setFont(QFont("Arial", 14, QFont.Bold))
                rec_header.setStyleSheet("""
                    QLabel {
                        color: #FF9800;
                        margin: 10px 0px 5px 0px;
                    }
                """)
                layout.addWidget(rec_header)

                rec_text = "<br>".join(recommendations)
                rec_label = QLabel(rec_text)
                rec_label.setFont(QFont("Arial", 13))
                rec_label.setStyleSheet("""
                    QLabel {
                        background-color: #fff3e0;
                        padding: 12px;
                        border-radius: 6px;
                        border-left: 4px solid #FF9800;
                        margin: 5px 0px;
                    }
                """)
                rec_label.setWordWrap(True)
                layout.addWidget(rec_label)

        except Exception as e:
            print(f"Error adding recommendations: {str(e)}")

    def load_default_formula(self):
        """Tải công thức mặc định khi khởi động app"""
        if self.default_formula_loaded:
            print("[DEBUG] Default formula already loaded, skipping...")
            return

        default_formula = self.formula_manager.get_default_feed_formula()
        print(f"[DEBUG] Loading default formula from config: '{default_formula}'")

        # Chỉ thiết lập khi có công thức mặc định
        if default_formula:
            self.default_formula_combo.setCurrentText(default_formula)
            print(f"[SUCCESS] Đã tải và áp dụng công thức mặc định: {default_formula}")
            # KHÔNG áp dụng công thức mặc định cho tất cả các ô khi khởi động
            # Chỉ lưu thông tin công thức mặc định để sử dụng khi người dùng nhập mẻ mới
        else:
            print("[INFO] Không có công thức mặc định được lưu, sử dụng mặc định")

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

    def filter_feed_usage_history(self):
        """Lọc lịch sử cám theo khoảng thời gian đã chọn"""
        from_date = self.history_from_date.date()
        to_date = self.history_to_date.date()

        # Kiểm tra "Từ ngày" <= "Đến ngày"
        if from_date > to_date:
            QMessageBox.warning(self, "Lỗi", "Từ ngày phải nhỏ hơn hoặc bằng đến ngày!")
            return

        # Gọi load_feed_usage_history với tham số lọc
        self.load_feed_usage_history(show_message=False, filter_from_date=from_date, filter_to_date=to_date)



    def load_feed_usage_history(self, show_message=True, filter_from_date=None, filter_to_date=None):
        """Tải lịch sử sử dụng cám từ các báo cáo đã lưu"""

        # Xóa dữ liệu cũ trong bảng
        if hasattr(self, 'feed_usage_history_table'):
            self.feed_usage_history_table.setRowCount(0)
        else:
            print("LOAD: feed_usage_history_table not found")
            return

        # Reports directory
        reports_dir = "src/data/reports"

        # Check if reports directory exists
        if not os.path.exists(reports_dir):
            # Thử đường dẫn cũ
            reports_dir = "reports"
            if not os.path.exists(reports_dir):
                if show_message:
                    QMessageBox.information(self, "Thông báo", "Không tìm thấy thư mục báo cáo!")
                return

        # Find all report files in the reports directory
        report_files = []
        for f in os.listdir(reports_dir):
            if f.startswith('report_') and f.endswith('.json'):
                report_files.append(os.path.join(reports_dir, f))

        # Nếu không có file báo cáo
        if not report_files:
            if show_message:
                QMessageBox.information(self, "Thông báo", "Không tìm thấy báo cáo nào!")
            return

        # Sort by date (newest first)
        report_files.sort(reverse=True)

        # Danh sách lưu thông tin báo cáo
        history_data = []

        files_included = 0
        files_excluded = 0

        # Đọc dữ liệu từ các file báo cáo
        for report_file in report_files:
            try:
                # Extract date from filename (format: reports/report_YYYYMMDD.json)
                file_name = os.path.basename(report_file)
                if file_name.startswith('report_') and file_name.endswith('.json'):
                    date_str = file_name[7:-5]  # Remove 'report_' and '.json'

                    # Format date as DD/MM/YYYY for display
                    # Hỗ trợ cả hai định dạng: YYYYMMDD và YYYY-MM-DD
                    if len(date_str) == 8 and date_str.isdigit():  # YYYYMMDD
                        year = date_str[0:4]
                        month = date_str[4:6]
                        day = date_str[6:8]
                        formatted_date = f"{day}/{month}/{year}"
                    elif len(date_str) == 10 and date_str.count('-') == 2:  # YYYY-MM-DD
                        parts = date_str.split('-')
                        if len(parts) == 3:
                            year, month, day = parts
                            formatted_date = f"{day}/{month}/{year}"
                        else:
                            continue
                    else:
                        continue

                    # Kiểm tra lọc theo khoảng thời gian nếu có
                    if filter_from_date and filter_to_date:
                        # Chuyển đổi ngày từ file thành QDate để so sánh
                        file_date = QDate.fromString(formatted_date, "dd/MM/yyyy")

                        if file_date.isValid():
                            # Kiểm tra xem ngày có nằm trong khoảng lọc không
                            if file_date < filter_from_date or file_date > filter_to_date:
                                files_excluded += 1
                                continue  # Bỏ qua file này nếu không nằm trong khoảng
                            else:
                                files_included += 1
                        else:
                            files_excluded += 1
                            continue
                    else:
                        files_included += 1

                    # Đọc dữ liệu báo cáo
                    with open(report_file, 'r', encoding='utf-8') as f:
                        report_data = json.load(f)

                    # Lấy tổng lượng cám và tổng số mẻ từ báo cáo
                    total_feed = 0
                    total_mix = 0
                    batch_count = 0

                    # Ưu tiên sử dụng dữ liệu đã tính toán sẵn trong báo cáo
                    if "total_feed" in report_data and "total_mix" in report_data and "batch_count" in report_data:
                        total_feed = report_data["total_feed"]
                        total_mix = report_data["total_mix"]
                        batch_count = report_data["batch_count"]
                        print(f"Sử dụng dữ liệu tính sẵn cho {formatted_date}: {format_total(total_feed)} kg cám, {format_total(total_mix)} kg mix, {batch_count} mẻ")
                    else:
                        print(f"Không tìm thấy dữ liệu tính sẵn, tính lại từ dữ liệu gốc cho {formatted_date}")
                        # Nếu không có dữ liệu đã tính toán, tính từ dữ liệu sử dụng
                        if "mix_ingredients" in report_data:
                            mix_ingredients = report_data["mix_ingredients"]
                            # Kiểm tra xem mix_ingredients có phải là dict không
                            if isinstance(mix_ingredients, dict):
                                # Tính tổng lượng mix từ thành phần
                                for ingredient, amount in mix_ingredients.items():
                                    if isinstance(amount, (int, float)):
                                        total_mix += amount
                            else:
                                print(f"Warning: mix_ingredients is not a dict in {report_file}")

                        if "feed_ingredients" in report_data:
                            feed_ingredients = report_data["feed_ingredients"]
                            # Kiểm tra xem feed_ingredients có phải là dict không
                            if isinstance(feed_ingredients, dict):
                                # Tính tổng lượng cám (BAO GỒM cả "Nguyên liệu tổ hợp")
                                for ingredient, amount in feed_ingredients.items():
                                    if isinstance(amount, (int, float)):
                                        total_feed += amount
                            else:
                                print(f"Warning: feed_ingredients is not a dict in {report_file}")

                        # Tính tổng số mẻ từ dữ liệu sử dụng
                        if "feed_usage" in report_data:
                            for khu, farms in report_data["feed_usage"].items():
                                for farm, shifts in farms.items():
                                    for shift, value in shifts.items():
                                        batch_count += value

                    # Thêm vào danh sách
                    history_data.append({
                        "date": formatted_date,
                        "total_feed": total_feed,
                        "total_mix": total_mix,
                        "batch_count": batch_count,
                        "report_file": report_file
                    })

            except Exception as e:
                print(f"Lỗi khi đọc file báo cáo {report_file}: {str(e)}")

                # Hiển thị dữ liệu lịch sử
        self.feed_usage_history_table.setRowCount(len(history_data))

        # Tạo font đậm cho ngày
        bold_font = QFont()
        bold_font.setBold(True)

        for row, data in enumerate(history_data):
            # Ngày báo cáo
            date_item = QTableWidgetItem(data["date"])
            date_item.setTextAlignment(Qt.AlignCenter)
            date_item.setFont(bold_font)

            # Thêm tooltip giải thích
            date_item.setToolTip(f"Nhấp đúp để tải báo cáo ngày {data['date']}")

            self.feed_usage_history_table.setItem(row, 0, date_item)

            # Tổng lượng cám
            total_feed = data["total_feed"]
            total_feed_item = QTableWidgetItem(f"{format_total(total_feed)} kg")
            total_feed_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            # Đặt màu chữ dựa trên giá trị
            if total_feed > 5000:
                total_feed_item.setForeground(QBrush(QColor("#2E7D32")))  # Màu xanh lá đậm

            self.feed_usage_history_table.setItem(row, 1, total_feed_item)

            # Tổng lượng mix
            total_mix = data["total_mix"]
            total_mix_item = QTableWidgetItem(f"{format_total(total_mix)} kg")
            total_mix_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            # Đặt màu chữ dựa trên giá trị
            if total_mix > 100:
                total_mix_item.setForeground(QBrush(QColor("#1565C0")))  # Màu xanh dương đậm

            self.feed_usage_history_table.setItem(row, 2, total_mix_item)

            # Tổng số mẻ
            batch_count = data["batch_count"]
            batch_count_item = QTableWidgetItem(format_number(batch_count))
            batch_count_item.setTextAlignment(Qt.AlignCenter)

            # Đặt màu chữ dựa trên giá trị
            if batch_count > 3:
                batch_count_item.setForeground(QBrush(QColor("#C62828")))  # Màu đỏ đậm

            self.feed_usage_history_table.setItem(row, 3, batch_count_item)

            # Lưu đường dẫn file báo cáo vào data của item
            date_item.setData(Qt.UserRole, data["report_file"])



        # Hiển thị thông báo
        if show_message:
            QMessageBox.information(self, "Thông báo", f"Tìm thấy {len(history_data)} báo cáo!")


    def on_history_row_clicked(self, index):
        """Xử lý sự kiện khi click vào hàng trong bảng lịch sử"""
        # Chọn toàn bộ hàng
        row = index.row()
        self.feed_usage_history_table.selectRow(row)

    def on_history_row_double_clicked(self, index):
        """Xử lý sự kiện khi double click vào hàng trong bảng lịch sử"""
        row = index.row()

        # Lấy đường dẫn file báo cáo từ item đầu tiên của hàng
        report_file = self.feed_usage_history_table.item(row, 0).data(Qt.UserRole)

        # Lấy ngày từ item đầu tiên của hàng
        date_text = self.feed_usage_history_table.item(row, 0).text()

        # Tải dữ liệu vào bảng cám
        self.load_feed_table_from_history(report_file, date_text)

    def load_feed_table_from_history(self, report_file, date_text, show_message=False):
        """Tải dữ liệu từ báo cáo lịch sử vào bảng cám"""
        try:
            # Đọc dữ liệu báo cáo
            with open(report_file, 'r', encoding='utf-8') as f:
                report_data = json.load(f)

            # Reset bảng cám trước khi điền dữ liệu mới
            self.reset_feed_table()

            # Cập nhật nhãn ngày trên giao diện
            for widget in self.findChildren(QLabel):
                if widget.text().startswith("Ngày:"):
                    widget.setText(f"Ngày: {date_text}")
                    break

            # Điền dữ liệu vào bảng cám
            if "feed_usage" in report_data:
                feed_usage = report_data["feed_usage"]

                # Duyệt qua từng khu và trại
                col_index = 0
                for khu_idx, farms in FARMS.items():
                    khu_name = f"Khu {khu_idx + 1}"

                    for farm_idx, farm in enumerate(farms):
                        # Nếu có dữ liệu cho khu và trại này
                        if khu_name in feed_usage and farm in feed_usage[khu_name]:
                            farm_data = feed_usage[khu_name][farm]

                            # Điền dữ liệu cho từng ca
                            for shift_idx, shift in enumerate(SHIFTS):
                                if shift in farm_data:
                                    value = farm_data[shift]

                                    # Lấy cell widget
                                    cell_widget = self.feed_table.cellWidget(shift_idx + 2, col_index)
                                    if cell_widget and hasattr(cell_widget, 'spin_box'):
                                        cell_widget.spin_box.setValue(value)

                                        # Nếu có dữ liệu công thức, cập nhật công thức
                                        if "formula_usage" in report_data and khu_name in report_data["formula_usage"] and farm in report_data["formula_usage"][khu_name] and shift in report_data["formula_usage"][khu_name][farm]:
                                            formula = report_data["formula_usage"][khu_name][farm][shift]
                                            if formula and hasattr(cell_widget, 'formula_combo'):
                                                # Tìm index của công thức trong combo box
                                                index = cell_widget.formula_combo.findText(formula)
                                                if index >= 0:
                                                    cell_widget.formula_combo.setCurrentIndex(index)

                        col_index += 1

            # Nếu có dữ liệu công thức mix cho cột, cập nhật
            if "column_mix_formulas" in report_data:
                self.column_mix_formulas = report_data["column_mix_formulas"]

            # Nếu có dữ liệu công thức mix cho từng ô, cập nhật
            if "cell_mix_formulas" in report_data:
                self.cell_mix_formulas = report_data["cell_mix_formulas"]

            # Tính toán lại kết quả
            self.calculate_feed_usage()

            # Hiển thị thông báo
            if show_message:
                QMessageBox.information(self, "Thông báo", f"Đã điền bảng cám từ báo cáo ngày {date_text}")

        except Exception as e:
            print(f"Lỗi khi tải dữ liệu từ báo cáo: {str(e)}")
            if show_message:
                QMessageBox.warning(self, "Lỗi", f"Không thể tải dữ liệu từ báo cáo: {str(e)}")


    def reset_feed_table_silent(self):
        """Reset bảng cám mà không hiển thị thông báo"""
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

        # Ẩn bảng kết quả nếu đang hiển thị
        self.results_label.setVisible(False)
        self.results_table.setVisible(False)

        # Xóa dữ liệu kết quả
        self.results_data = {}

        # Cập nhật hiển thị bảng
        self.update_feed_table_display()

    def setup_team_management_tab(self):
        """Setup the team management tab for feed team management and bonus calculation"""
        layout = QVBoxLayout()

        # Header
        header = QLabel("Quản lý tổ cám và tính toán tiền thưởng")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("""
            QLabel {
                background-color: #4CAF50;
                color: white;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(header)

        # Create tabs for different management functions
        team_tabs = QTabWidget()
        team_tabs.setFont(DEFAULT_FONT)
        team_tabs.setStyleSheet("""
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
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom-color: white;
            }
            QTabBar::tab:hover {
                background: #e0e0e0;
            }
        """)

        # Create sub-tabs
        employee_tab = QWidget()  # Quản lý nhân viên
        attendance_tab = QWidget()  # Quản lý nghỉ phép/ốm
        import_tracking_tab = QWidget()  # Theo dõi nhập kho
        salary_calculation_tab = QWidget()  # Tính lương tháng
        bonus_calculation_tab = QWidget()  # Tính toán tiền thưởng

        team_tabs.addTab(employee_tab, "Nhân viên")
        team_tabs.addTab(attendance_tab, "Nghỉ phép/ốm")
        team_tabs.addTab(import_tracking_tab, "Theo dõi nhập kho")
        team_tabs.addTab(salary_calculation_tab, "Tính lương")
        team_tabs.addTab(bonus_calculation_tab, "Tính tiền thưởng")

        # Setup each sub-tab
        self.setup_employee_management_tab(employee_tab)
        self.setup_attendance_management_tab(attendance_tab)
        self.setup_import_tracking_tab(import_tracking_tab)
        self.setup_salary_calculation_tab(salary_calculation_tab)
        self.setup_bonus_calculation_tab(bonus_calculation_tab)

        layout.addWidget(team_tabs)
        self.team_management_tab.setLayout(layout)

    def setup_employee_management_tab(self, tab_widget):
        """Setup employee management sub-tab"""
        layout = QVBoxLayout()
        layout.setSpacing(20)  # Increased spacing between sections
        layout.setContentsMargins(20, 20, 20, 20)  # Add margins around the tab

        # Header section with improved styling
        header_widget = QWidget()
        header_widget.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-radius: 10px;
                margin-bottom: 15px;
            }
        """)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(20, 15, 20, 15)

        title = QLabel("👥 Danh sách nhân viên tổ cám")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("""
            QLabel {
                color: #2E7D32;
                background: transparent;
                padding: 5px 0px;
            }
        """)

        # Enhanced add employee button
        add_employee_btn = QPushButton("➕ Thêm nhân viên")
        add_employee_btn.setFont(QFont("Arial", DEFAULT_FONT_SIZE, QFont.Bold))
        add_employee_btn.setMinimumHeight(40)
        add_employee_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
                border: 2px solid #4CAF50;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
                border: 2px solid #2E7D32;
            }
        """)
        add_employee_btn.clicked.connect(self.add_employee)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(add_employee_btn)
        header_widget.setLayout(header_layout)

        layout.addWidget(header_widget)

        # Employee table with enhanced font sizes
        self.employee_table = QTableWidget()
        self.employee_table.setFont(QFont("Arial", 15, QFont.Medium))  # Increased to 15px
        self.employee_table.setColumnCount(4)
        self.employee_table.setHorizontalHeaderLabels(["ID", "Họ tên", "Vị trí", "Thao tác"])

        # Set row height for better readability
        self.employee_table.verticalHeader().setDefaultSectionSize(50)  # Increased height
        self.employee_table.verticalHeader().setVisible(False)

        # Set column widths
        header = self.employee_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Họ tên
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Vị trí
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Thao tác
        header.setMinimumSectionSize(90)

        # Enhanced table styling with larger fonts
        self.employee_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #e0e0e0;
                background-color: white;
                alternate-background-color: #f8f9fa;
                border: 1px solid #d0d0d0;
                border-radius: 8px;
                font-size: 15px;
                font-weight: 500;
                selection-background-color: #e3f2fd;
            }
            QTableWidget::item {
                padding: 14px 16px;
                border-bottom: 1px solid #e8e8e8;
                border-right: 1px solid #f0f0f0;
                color: #2c2c2c;
                font-weight: 500;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
                font-weight: 600;
            }
            QTableWidget::item:hover {
                background-color: #f5f5f5;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 16px 14px;
                border: none;
                border-bottom: 2px solid #4CAF50;
                border-right: 1px solid #e0e0e0;
                font-weight: bold;
                font-size: 16px;
                color: #2e7d32;
            }
            QHeaderView::section:hover {
                background-color: #e8f5e8;
            }
        """)

        self.employee_table.setAlternatingRowColors(True)
        self.employee_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.employee_table.setShowGrid(True)

        layout.addWidget(self.employee_table)

        # Load existing employees
        self.load_employees()

        tab_widget.setLayout(layout)

    def setup_attendance_management_tab(self, tab_widget):
        """Setup enhanced attendance management sub-tab"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Enhanced header section
        header_widget = QWidget()
        header_widget.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-radius: 10px;
                margin-bottom: 15px;
            }
        """)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(20, 15, 20, 15)

        title = QLabel("📅 Quản lý chấm công và nghỉ phép")
        title.setFont(QFont("Arial", 18, QFont.Bold))  # Increased font size
        title.setStyleSheet("""
            QLabel {
                color: #2E7D32;
                background: transparent;
                padding: 5px 0px;
            }
        """)

        # Add attendance statistics button
        stats_btn = QPushButton("📊 Thống kê chấm công")
        stats_btn.setFont(QFont("Arial", 14, QFont.Bold))
        stats_btn.setMinimumHeight(40)
        stats_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
                border: 2px solid #2196F3;
            }
            QPushButton:pressed {
                background-color: #1565C0;
                border: 2px solid #1976D2;
            }
        """)
        stats_btn.clicked.connect(self.show_attendance_statistics)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(stats_btn)
        header_widget.setLayout(header_layout)

        layout.addWidget(header_widget)

        # Main content layout
        main_layout = QHBoxLayout()

        # Left side - Employee selection and calendar
        left_widget = QWidget()
        left_layout = QVBoxLayout()

        # Leave request section
        leave_request_group = QGroupBox("📝 Đăng ký nghỉ phép")
        leave_request_group.setFont(QFont("Arial", 16, QFont.Bold))
        leave_request_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                color: #2E7D32;
                background-color: white;
            }
        """)
        leave_request_layout = QVBoxLayout()
        leave_request_layout.setContentsMargins(15, 20, 15, 15)

        # Employee selection for leave
        employee_select_layout = QHBoxLayout()
        employee_select_layout.addWidget(QLabel("Nhân viên:"))
        self.leave_employee_combo = QComboBox()
        self.leave_employee_combo.setFont(QFont("Arial", 14))
        self.leave_employee_combo.setMinimumHeight(35)
        self.leave_employee_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 5px 10px;
                background-color: white;
            }
            QComboBox:hover {
                border-color: #4CAF50;
            }
        """)
        employee_select_layout.addWidget(self.leave_employee_combo)
        leave_request_layout.addLayout(employee_select_layout)

        # Leave type selection
        leave_type_layout = QHBoxLayout()
        leave_type_layout.addWidget(QLabel("Loại nghỉ:"))
        self.leave_type_combo = QComboBox()
        self.leave_type_combo.setFont(QFont("Arial", 14))
        self.leave_type_combo.setMinimumHeight(35)
        self.leave_type_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 5px 10px;
                background-color: white;
            }
            QComboBox:hover {
                border-color: #4CAF50;
            }
        """)
        leave_type_layout.addWidget(self.leave_type_combo)
        leave_request_layout.addLayout(leave_type_layout)

        # Date selection
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Ngày nghỉ:"))
        self.leave_date_edit = QDateEdit()
        self.leave_date_edit.setFont(QFont("Arial", 14))
        self.leave_date_edit.setMinimumHeight(35)
        self.leave_date_edit.setDate(QDate.currentDate())
        self.leave_date_edit.setCalendarPopup(True)
        self.leave_date_edit.setStyleSheet("""
            QDateEdit {
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 5px 10px;
                background-color: white;
            }
            QDateEdit:hover {
                border-color: #4CAF50;
            }
        """)
        date_layout.addWidget(self.leave_date_edit)
        leave_request_layout.addLayout(date_layout)

        # Reason field
        leave_request_layout.addWidget(QLabel("Lý do:"))
        self.leave_reason_edit = QTextEdit()
        self.leave_reason_edit.setFont(QFont("Arial", 14))
        self.leave_reason_edit.setMaximumHeight(80)
        self.leave_reason_edit.setPlaceholderText("Nhập lý do nghỉ phép...")
        self.leave_reason_edit.setStyleSheet("""
            QTextEdit {
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 8px;
                background-color: white;
            }
            QTextEdit:hover {
                border-color: #4CAF50;
            }
            QTextEdit:focus {
                border-color: #4CAF50;
                border-width: 2px;
            }
        """)
        leave_request_layout.addWidget(self.leave_reason_edit)

        # Submit button
        submit_leave_btn = QPushButton("📝 Đăng ký nghỉ phép")
        submit_leave_btn.setFont(QFont("Arial", 14, QFont.Bold))
        submit_leave_btn.setMinimumHeight(45)
        submit_leave_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
                border: 2px solid #4CAF50;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
                border: 2px solid #2E7D32;
            }
        """)
        submit_leave_btn.clicked.connect(self.submit_leave_request)
        leave_request_layout.addWidget(submit_leave_btn)

        leave_request_group.setLayout(leave_request_layout)
        left_layout.addWidget(leave_request_group)

        # Initialize combo boxes
        self.populate_leave_employee_combo()
        self.populate_leave_type_combo()

        # Enhanced calendar
        calendar_group = QGroupBox("📅 Lịch nghỉ phép/ốm")
        calendar_group.setFont(QFont("Arial", DEFAULT_FONT_SIZE + 1, QFont.Bold))
        calendar_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                color: #2E7D32;
                background-color: white;
            }
        """)
        calendar_layout = QVBoxLayout()
        calendar_layout.setContentsMargins(15, 20, 15, 15)

        self.attendance_calendar = QCalendarWidget()
        self.attendance_calendar.setFont(QFont("Arial", DEFAULT_FONT_SIZE))
        self.attendance_calendar.setStyleSheet("""
            QCalendarWidget {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                background-color: white;
                font-size: 13px;
            }
            QCalendarWidget QToolButton {
                height: 35px;
                width: 70px;
                color: #2E7D32;
                font-size: 13px;
                font-weight: bold;
                icon-size: 20px;
                background-color: #f8f9fa;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                margin: 2px;
            }
            QCalendarWidget QToolButton:hover {
                background-color: #e8f5e8;
                border-color: #4CAF50;
            }
            QCalendarWidget QMenu {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
            }
            QCalendarWidget QSpinBox {
                font-size: 13px;
                color: #2E7D32;
                background-color: white;
                selection-background-color: #4CAF50;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 3px;
            }
            QCalendarWidget QAbstractItemView:enabled {
                font-size: 12px;
                color: #333;
                background-color: white;
                selection-background-color: #4CAF50;
                gridline-color: #f0f0f0;
            }
            QCalendarWidget QAbstractItemView::item {
                padding: 8px;
            }
            QCalendarWidget QAbstractItemView::item:hover {
                background-color: #e8f5e8;
            }
        """)

        # Connect calendar click event
        self.attendance_calendar.clicked.connect(self.on_calendar_date_clicked)

        calendar_layout.addWidget(self.attendance_calendar)
        calendar_group.setLayout(calendar_layout)
        left_layout.addWidget(calendar_group)

        left_widget.setLayout(left_layout)
        main_layout.addWidget(left_widget, 1)

        # Right side - Absence type and management
        right_widget = QWidget()
        right_layout = QVBoxLayout()

        # Absence type selection
        type_group = QGroupBox("Loại nghỉ")
        type_group.setFont(DEFAULT_FONT)
        type_layout = QVBoxLayout()

        self.absence_type_combo = QComboBox()
        self.absence_type_combo.setFont(DEFAULT_FONT)
        self.absence_type_combo.addItems([
            "Nghỉ phép",
            "Nghỉ ốm",
            "Nghỉ việc riêng",
            "Nghỉ không phép"
        ])
        self.absence_type_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
            }
            QComboBox:focus {
                border-color: #4CAF50;
            }
        """)

        type_layout.addWidget(self.absence_type_combo)
        type_group.setLayout(type_layout)
        right_layout.addWidget(type_group)

        # Action buttons
        button_layout = QVBoxLayout()

        mark_absent_btn = QPushButton("📝 Đánh dấu nghỉ")
        mark_absent_btn.setFont(QFont("Arial", DEFAULT_FONT_SIZE, QFont.Bold))
        mark_absent_btn.setMinimumHeight(45)
        mark_absent_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #F57C00;
                border: 2px solid #FF9800;
            }
            QPushButton:pressed {
                background-color: #EF6C00;
                border: 2px solid #E65100;
            }
        """)
        mark_absent_btn.clicked.connect(self.mark_employee_absent)

        remove_absent_btn = QPushButton("❌ Xóa đánh dấu")
        remove_absent_btn.setFont(QFont("Arial", DEFAULT_FONT_SIZE, QFont.Bold))
        remove_absent_btn.setMinimumHeight(45)
        remove_absent_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
                border: 2px solid #f44336;
            }
            QPushButton:pressed {
                background-color: #c62828;
                border: 2px solid #b71c1c;
            }
        """)
        remove_absent_btn.clicked.connect(self.remove_employee_absent)

        button_layout.addWidget(mark_absent_btn)
        button_layout.addWidget(remove_absent_btn)
        button_layout.addStretch()

        right_layout.addLayout(button_layout)

        # Absence history
        history_group = QGroupBox("Lịch sử nghỉ")
        history_group.setFont(DEFAULT_FONT)
        history_layout = QVBoxLayout()

        self.absence_history_list = QListWidget()
        self.absence_history_list.setFont(DEFAULT_FONT)
        self.absence_history_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                background-color: white;
            }
            QListWidget::item {
                padding: 6px;
                border-bottom: 1px solid #e0e0e0;
            }
        """)

        history_layout.addWidget(self.absence_history_list)
        history_group.setLayout(history_layout)
        right_layout.addWidget(history_group)

        right_widget.setLayout(right_layout)
        main_layout.addWidget(right_widget, 1)

        layout.addLayout(main_layout)

        # Connect signals
        self.attendance_calendar.clicked.connect(self.on_calendar_date_clicked)

        # Load data
        self.load_attendance_employees()
        self.load_attendance_data()

        tab_widget.setLayout(layout)

    def setup_import_tracking_tab(self, tab_widget):
        """Setup import tracking sub-tab"""
        layout = QVBoxLayout()

        # Header section
        header_layout = QHBoxLayout()

        title = QLabel("Theo dõi hoạt động nhập kho")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setStyleSheet("color: #2E7D32; margin-bottom: 10px;")

        # Refresh button
        refresh_btn = QPushButton("Làm mới dữ liệu")
        refresh_btn.setFont(DEFAULT_FONT)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_import_tracking_data)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(refresh_btn)

        layout.addLayout(header_layout)

        # Filter section
        filter_group = QGroupBox("Bộ lọc")
        filter_group.setFont(DEFAULT_FONT)
        filter_layout = QHBoxLayout()

        # Date range filter
        filter_layout.addWidget(QLabel("Từ ngày:"))
        self.import_tracking_from_date = QDateEdit()
        self.import_tracking_from_date.setFont(DEFAULT_FONT)
        self.import_tracking_from_date.setCalendarPopup(True)
        self.import_tracking_from_date.setDisplayFormat("dd/MM/yyyy")
        self.import_tracking_from_date.setDate(QDate.currentDate().addDays(-30))
        filter_layout.addWidget(self.import_tracking_from_date)

        filter_layout.addWidget(QLabel("Đến ngày:"))
        self.import_tracking_to_date = QDateEdit()
        self.import_tracking_to_date.setFont(DEFAULT_FONT)
        self.import_tracking_to_date.setCalendarPopup(True)
        self.import_tracking_to_date.setDisplayFormat("dd/MM/yyyy")
        self.import_tracking_to_date.setDate(QDate.currentDate())
        filter_layout.addWidget(self.import_tracking_to_date)

        # Material type filter
        filter_layout.addWidget(QLabel("Loại nguyên liệu:"))
        self.import_material_filter = QComboBox()
        self.import_material_filter.setFont(DEFAULT_FONT)
        self.import_material_filter.addItems([
            "Tất cả",
            "Bắp",
            "Nành",
            "Đá hạt",
            "Cám gạo",
            "Khác"
        ])
        filter_layout.addWidget(self.import_material_filter)

        # Filter button
        filter_btn = QPushButton("Lọc")
        filter_btn.setFont(DEFAULT_FONT)
        filter_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        filter_btn.clicked.connect(self.filter_import_tracking_data)
        filter_layout.addWidget(filter_btn)

        filter_layout.addStretch()
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)

        # Enhanced import tracking table with larger fonts
        self.import_tracking_table = QTableWidget()
        self.import_tracking_table.setFont(QFont("Arial", 15, QFont.Medium))
        self.import_tracking_table.setColumnCount(6)
        self.import_tracking_table.setHorizontalHeaderLabels([
            "📅 Ngày", "🏷️ Loại nguyên liệu", "⚖️ Số lượng (kg)",
            "👥 Nhân viên tham gia", "📝 Ghi chú", "⚙️ Thao tác"
        ])

        # Enhanced row height and styling
        self.import_tracking_table.verticalHeader().setDefaultSectionSize(55)  # Increased height
        self.import_tracking_table.verticalHeader().setVisible(False)

        # Set column widths with optimized date column width
        header = self.import_tracking_table.horizontalHeader()

        # Set minimum width for date column to accommodate full timestamp "YYYY-MM-DD HH:MM:SS"
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # Ngày - Fixed width for timestamp
        header.resizeSection(0, 180)  # Set fixed width of 180px for full timestamp visibility

        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Loại nguyên liệu
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Số lượng
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # Nhân viên tham gia
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Ghi chú
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Thao tác
        header.setMinimumSectionSize(110)

        # Enhanced table styling with larger fonts
        self.import_tracking_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #e0e0e0;
                background-color: white;
                alternate-background-color: #f8f9fa;
                border: 1px solid #d0d0d0;
                border-radius: 8px;
                font-size: 15px;
                font-weight: 500;
                selection-background-color: #e3f2fd;
            }
            QTableWidget::item {
                padding: 16px 14px;
                border-bottom: 1px solid #e8e8e8;
                border-right: 1px solid #f0f0f0;
                color: #2c2c2c;
                font-weight: 500;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
                font-weight: 600;
            }
            QTableWidget::item:hover {
                background-color: #f5f5f5;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 16px 14px;
                border: none;
                border-bottom: 2px solid #FF9800;
                border-right: 1px solid #e0e0e0;
                font-weight: bold;
                font-size: 17px;
                color: #e65100;
            }
            QHeaderView::section:hover {
                background-color: #fff3e0;
            }
        """)

        self.import_tracking_table.setAlternatingRowColors(True)
        self.import_tracking_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.import_tracking_table.setShowGrid(True)

        layout.addWidget(self.import_tracking_table)

        # Load initial data
        self.load_import_tracking_data()

        tab_widget.setLayout(layout)

    def setup_salary_calculation_tab(self, tab_widget):
        """Setup salary calculation sub-tab"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Enhanced header section
        header_widget = QWidget()
        header_widget.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-radius: 10px;
                margin-bottom: 15px;
            }
        """)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(20, 15, 20, 15)

        title = QLabel("💰 Tính lương tháng")
        title.setFont(QFont("Arial", 18, QFont.Bold))  # Increased font size
        title.setStyleSheet("""
            QLabel {
                color: #2E7D32;
                background: transparent;
                padding: 5px 0px;
            }
        """)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_widget.setLayout(header_layout)

        layout.addWidget(header_widget)

        # Salary rates section
        rates_group = QGroupBox("💼 Lương cơ bản theo vị trí (VNĐ/tháng)")
        rates_group.setFont(QFont("Arial", 16, QFont.Bold))  # Increased font size
        rates_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                color: #2E7D32;
                background-color: white;
            }
        """)
        rates_layout = QVBoxLayout()
        rates_layout.setContentsMargins(15, 20, 15, 15)

        # Current rates display
        current_rates_layout = QGridLayout()

        # Load current salary rates
        salary_config = self.load_salary_rates()
        position_salaries = salary_config.get("position_salaries", {})

        positions = ["Tổ trưởng", "Phó tổ trưởng", "Kỹ thuật viên", "Thủ kho", "Công nhân"]
        self.salary_rate_labels = {}

        for i, position in enumerate(positions):
            row = i // 2
            col = (i % 2) * 2

            current_rates_layout.addWidget(QLabel(f"{position}:"), row, col)

            salary_label = QLabel(f"{position_salaries.get(position, 5500000):,} VNĐ")
            salary_label.setFont(QFont("Arial", 15, QFont.Bold))  # Increased font size
            salary_label.setStyleSheet("color: #1976d2; font-weight: bold;")
            self.salary_rate_labels[position] = salary_label
            current_rates_layout.addWidget(salary_label, row, col + 1)

        rates_layout.addLayout(current_rates_layout)

        # Settings button
        settings_btn_layout = QHBoxLayout()
        settings_btn_layout.addStretch()

        salary_settings_btn = QPushButton("⚙️ Cài đặt lương cơ bản")
        salary_settings_btn.setFont(QFont("Arial", 14, QFont.Bold))  # Increased font size
        salary_settings_btn.setMinimumHeight(45)
        salary_settings_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F57C00;
                border: 2px solid #FF9800;
            }
            QPushButton:pressed {
                background-color: #EF6C00;
                border: 2px solid #E65100;
            }
        """)
        salary_settings_btn.clicked.connect(self.show_salary_settings_dialog)
        settings_btn_layout.addWidget(salary_settings_btn)

        rates_layout.addLayout(settings_btn_layout)
        rates_group.setLayout(rates_layout)
        layout.addWidget(rates_group)

        # Month/Year selection section
        selection_group = QGroupBox("📅 Chọn tháng tính lương")
        selection_group.setFont(QFont("Arial", 16, QFont.Bold))  # Increased font size
        selection_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                color: #2E7D32;
                background-color: white;
            }
        """)
        selection_layout = QHBoxLayout()
        selection_layout.setContentsMargins(15, 20, 15, 15)

        selection_layout.addWidget(QLabel("Tháng:"))
        self.salary_month_combo = QComboBox()
        self.salary_month_combo.setFont(QFont("Arial", 14))  # Increased font size
        self.salary_month_combo.setMinimumHeight(35)
        for i in range(1, 13):
            self.salary_month_combo.addItem(f"Tháng {i:02d}", i)
        self.salary_month_combo.setCurrentIndex(QDate.currentDate().month() - 1)
        selection_layout.addWidget(self.salary_month_combo)

        selection_layout.addWidget(QLabel("Năm:"))
        self.salary_year_combo = QComboBox()
        self.salary_year_combo.setFont(QFont("Arial", 14))  # Increased font size
        self.salary_year_combo.setMinimumHeight(35)
        current_year = QDate.currentDate().year()
        for year in range(current_year - 2, current_year + 1):
            self.salary_year_combo.addItem(str(year), year)
        self.salary_year_combo.setCurrentText(str(current_year))
        selection_layout.addWidget(self.salary_year_combo)

        # Calculate button
        calculate_salary_btn = QPushButton("💰 Tính lương tháng")
        calculate_salary_btn.setFont(QFont("Arial", 14, QFont.Bold))  # Increased font size
        calculate_salary_btn.setMinimumHeight(45)
        calculate_salary_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
                border: 2px solid #4CAF50;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
                border: 2px solid #2E7D32;
            }
        """)
        calculate_salary_btn.clicked.connect(self.calculate_monthly_salary)
        selection_layout.addWidget(calculate_salary_btn)

        selection_layout.addStretch()
        selection_group.setLayout(selection_layout)
        layout.addWidget(selection_group)

        # Results table
        results_group = QGroupBox("📊 Kết quả tính lương")
        results_group.setFont(QFont("Arial", 16, QFont.Bold))  # Increased font size
        results_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                color: #2E7D32;
                background-color: white;
            }
        """)
        results_layout = QVBoxLayout()
        results_layout.setContentsMargins(15, 20, 15, 15)

        self.salary_results_table = QTableWidget()
        self.salary_results_table.setFont(QFont("Arial", 15, QFont.Medium))  # Increased font size
        self.salary_results_table.setColumnCount(7)
        self.salary_results_table.setHorizontalHeaderLabels([
            "👤 Nhân viên", "💼 Vị trí", "💵 Lương cơ bản", "📅 Ngày làm việc",
            "🏠 Ngày nghỉ", "🎁 Tiền thưởng", "💰 Tổng lương"
        ])

        # Enhanced row height and styling
        self.salary_results_table.verticalHeader().setDefaultSectionSize(55)
        self.salary_results_table.verticalHeader().setVisible(False)

        # Set column widths
        header = self.salary_results_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Nhân viên
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Vị trí
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Lương cơ bản
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Ngày làm việc
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Ngày nghỉ
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Tiền thưởng
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Tổng lương
        header.setMinimumSectionSize(120)

        # Enhanced table styling
        self.salary_results_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #e0e0e0;
                background-color: white;
                alternate-background-color: #f8f9fa;
                border: 1px solid #d0d0d0;
                border-radius: 8px;
                font-size: 15px;
                font-weight: 500;
                selection-background-color: #e8f5e8;
            }
            QTableWidget::item {
                padding: 16px 14px;
                border-bottom: 1px solid #e8e8e8;
                border-right: 1px solid #f0f0f0;
                color: #2c2c2c;
                font-weight: 500;
            }
            QTableWidget::item:selected {
                background-color: #e8f5e8;
                color: #2E7D32;
                font-weight: 600;
            }
            QTableWidget::item:hover {
                background-color: #f5f5f5;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 16px 14px;
                border: none;
                border-bottom: 2px solid #4CAF50;
                border-right: 1px solid #e0e0e0;
                font-weight: bold;
                font-size: 17px;
                color: #2E7D32;
            }
            QHeaderView::section:hover {
                background-color: #e8f5e8;
            }
        """)

        self.salary_results_table.setAlternatingRowColors(True)
        self.salary_results_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.salary_results_table.setShowGrid(True)

        results_layout.addWidget(self.salary_results_table)
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)

        tab_widget.setLayout(layout)

    def setup_bonus_calculation_tab(self, tab_widget):
        """Setup bonus calculation sub-tab"""
        layout = QVBoxLayout()

        # Header section
        header_layout = QHBoxLayout()

        title = QLabel("Tính toán tiền thưởng cuối tháng")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setStyleSheet("color: #2E7D32; margin-bottom: 10px;")

        header_layout.addWidget(title)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Bonus rates section
        rates_group = QGroupBox("Mức thưởng cố định (VNĐ/tháng)")
        rates_group.setFont(DEFAULT_FONT)
        rates_layout = QVBoxLayout()

        # Current rates display
        current_rates_layout = QGridLayout()

        # Load current rates
        bonus_config = self.load_bonus_rates()
        default_rates = bonus_config.get("default_rates", {})

        current_rates_layout.addWidget(QLabel("Bắp:"), 0, 0)
        self.bap_rate_label = QLabel(f"{default_rates.get('Bắp', 400000):,} VNĐ")
        current_rates_layout.addWidget(self.bap_rate_label, 0, 1)

        current_rates_layout.addWidget(QLabel("Nành:"), 0, 2)
        self.nanh_rate_label = QLabel(f"{default_rates.get('Nành', 400000):,} VNĐ")
        current_rates_layout.addWidget(self.nanh_rate_label, 0, 3)

        current_rates_layout.addWidget(QLabel("Cám gạo:"), 1, 0)
        self.cam_gao_rate_label = QLabel(f"{default_rates.get('Cám gạo', 270000):,} VNĐ")
        current_rates_layout.addWidget(self.cam_gao_rate_label, 1, 1)

        current_rates_layout.addWidget(QLabel("Khác:"), 1, 2)
        self.khac_rate_label = QLabel(f"{default_rates.get('Khác', 350000):,} VNĐ")
        current_rates_layout.addWidget(self.khac_rate_label, 1, 3)

        rates_layout.addLayout(current_rates_layout)

        # Settings button
        settings_btn_layout = QHBoxLayout()
        settings_btn_layout.addStretch()

        settings_btn = QPushButton("Cài đặt mức thưởng")
        settings_btn.setFont(DEFAULT_FONT)
        settings_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        settings_btn.clicked.connect(self.show_bonus_settings_dialog)
        settings_btn_layout.addWidget(settings_btn)

        rates_layout.addLayout(settings_btn_layout)
        rates_group.setLayout(rates_layout)
        layout.addWidget(rates_group)

        # Month/Year selection section
        selection_group = QGroupBox("Chọn tháng tính thưởng")
        selection_group.setFont(DEFAULT_FONT)
        selection_layout = QHBoxLayout()

        selection_layout.addWidget(QLabel("Tháng:"))
        self.bonus_month_combo = QComboBox()
        self.bonus_month_combo.setFont(DEFAULT_FONT)
        for i in range(1, 13):
            self.bonus_month_combo.addItem(f"Tháng {i:02d}", i)
        self.bonus_month_combo.setCurrentIndex(QDate.currentDate().month() - 1)
        selection_layout.addWidget(self.bonus_month_combo)

        selection_layout.addWidget(QLabel("Năm:"))
        self.bonus_year_combo = QComboBox()
        self.bonus_year_combo.setFont(DEFAULT_FONT)
        current_year = QDate.currentDate().year()
        for year in range(current_year - 2, current_year + 1):
            self.bonus_year_combo.addItem(str(year), year)
        self.bonus_year_combo.setCurrentText(str(current_year))
        selection_layout.addWidget(self.bonus_year_combo)

        # Calculate button
        calculate_btn = QPushButton("Tính toán tiền thưởng")
        calculate_btn.setFont(DEFAULT_FONT)
        calculate_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        calculate_btn.clicked.connect(self.calculate_monthly_bonus)
        selection_layout.addWidget(calculate_btn)

        selection_layout.addStretch()
        selection_group.setLayout(selection_layout)
        layout.addWidget(selection_group)

        # Results table
        results_group = QGroupBox("Kết quả tính thưởng")
        results_group.setFont(DEFAULT_FONT)
        results_layout = QVBoxLayout()

        self.bonus_results_table = QTableWidget()
        self.bonus_results_table.setFont(QFont("Arial", 15, QFont.Medium))
        self.bonus_results_table.setColumnCount(7)
        self.bonus_results_table.setHorizontalHeaderLabels([
            "👤 Nhân viên", "💼 Vị trí", "🌽 Bắp", "🫘 Nành", "🌾 Cám gạo", "🔧 Khác", "💰 Tổng thưởng"
        ])

        # Enhanced row height and styling
        self.bonus_results_table.verticalHeader().setDefaultSectionSize(55)  # Increased height
        self.bonus_results_table.verticalHeader().setVisible(False)

        # Set column widths
        header = self.bonus_results_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Nhân viên
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Vị trí
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Bắp
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Nành
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Cám gạo
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Khác
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Tổng thưởng
        header.setMinimumSectionSize(110)

        # Enhanced table styling with larger fonts
        self.bonus_results_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #e0e0e0;
                background-color: white;
                alternate-background-color: #f8f9fa;
                border: 1px solid #d0d0d0;
                border-radius: 8px;
                font-size: 15px;
                font-weight: 500;
                selection-background-color: #e8f5e8;
            }
            QTableWidget::item {
                padding: 16px 14px;
                border-bottom: 1px solid #e8e8e8;
                border-right: 1px solid #f0f0f0;
                color: #2c2c2c;
                font-weight: 500;
            }
            QTableWidget::item:selected {
                background-color: #e8f5e8;
                color: #2E7D32;
                font-weight: 600;
            }
            QTableWidget::item:hover {
                background-color: #f5f5f5;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 16px 14px;
                border: none;
                border-bottom: 2px solid #4CAF50;
                border-right: 1px solid #e0e0e0;
                font-weight: bold;
                font-size: 17px;
                color: #2E7D32;
            }
            QHeaderView::section:hover {
                background-color: #e8f5e8;
            }
        """)

        self.bonus_results_table.setAlternatingRowColors(True)
        self.bonus_results_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.bonus_results_table.setShowGrid(True)

        results_layout.addWidget(self.bonus_results_table)

        # Export button
        export_layout = QHBoxLayout()
        export_layout.addStretch()

        export_btn = QPushButton("Xuất báo cáo Excel")
        export_btn.setFont(DEFAULT_FONT)
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        export_btn.clicked.connect(self.export_bonus_report)
        export_layout.addWidget(export_btn)

        results_layout.addLayout(export_layout)
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)

        tab_widget.setLayout(layout)

    def load_employees(self):
        """Load employees from JSON file"""
        try:
            employees_file = "src/data/employees.json"
            if os.path.exists(employees_file):
                with open(employees_file, 'r', encoding='utf-8') as f:
                    employees_data = json.load(f)
            else:
                employees_data = []

            # Clear table
            self.employee_table.setRowCount(0)

            # Populate table
            for employee in employees_data:
                self.add_employee_to_table(employee)

        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể tải danh sách nhân viên: {str(e)}")

    def add_employee_to_table(self, employee):
        """Add an employee to the table"""
        row = self.employee_table.rowCount()
        self.employee_table.insertRow(row)

        # ID
        id_item = QTableWidgetItem(str(employee.get('id', '')))
        id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)  # Read-only
        self.employee_table.setItem(row, 0, id_item)

        # Name
        name_item = QTableWidgetItem(employee.get('name', ''))
        self.employee_table.setItem(row, 1, name_item)

        # Position
        position_item = QTableWidgetItem(employee.get('position', ''))
        self.employee_table.setItem(row, 2, position_item)

        # Action buttons
        action_widget = QWidget()
        action_layout = QHBoxLayout()
        action_layout.setContentsMargins(5, 2, 5, 2)

        edit_btn = QPushButton("✏️ Sửa")
        edit_btn.setMinimumHeight(32)
        edit_btn.setFont(QFont("Arial", DEFAULT_FONT_SIZE - 1, QFont.Bold))
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
                border: 2px solid #2196F3;
            }
            QPushButton:pressed {
                background-color: #1565C0;
                border: 2px solid #1976D2;
            }
        """)
        edit_btn.clicked.connect(lambda: self.edit_employee(row))

        delete_btn = QPushButton("🗑️ Xóa")
        delete_btn.setMinimumHeight(32)
        delete_btn.setFont(QFont("Arial", DEFAULT_FONT_SIZE - 1, QFont.Bold))
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
                border: 2px solid #f44336;
            }
            QPushButton:pressed {
                background-color: #c62828;
                border: 2px solid #b71c1c;
            }
        """)
        delete_btn.clicked.connect(lambda: self.delete_employee(row))

        action_layout.addWidget(edit_btn)
        action_layout.addWidget(delete_btn)
        action_widget.setLayout(action_layout)

        self.employee_table.setCellWidget(row, 3, action_widget)

    def add_employee(self):
        """Add new employee dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Thêm nhân viên mới")
        dialog.setModal(True)
        dialog.resize(400, 200)

        layout = QVBoxLayout()

        # Form fields
        form_layout = QGridLayout()

        # Name field
        form_layout.addWidget(QLabel("Họ tên:"), 0, 0)
        name_edit = QLineEdit()
        name_edit.setFont(DEFAULT_FONT)
        form_layout.addWidget(name_edit, 0, 1)

        # Position field
        form_layout.addWidget(QLabel("Vị trí:"), 1, 0)
        position_combo = QComboBox()
        position_combo.setFont(DEFAULT_FONT)
        position_combo.addItems([
            "Công nhân",
            "Tổ trưởng",
            "Phó tổ trưởng",
            "Kỹ thuật viên",
            "Thủ kho"
        ])
        form_layout.addWidget(position_combo, 1, 1)

        layout.addLayout(form_layout)

        # Buttons
        button_layout = QHBoxLayout()

        save_btn = QPushButton("Lưu")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        cancel_btn = QPushButton("Hủy")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #9E9E9E;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #757575;
            }
        """)

        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)
        dialog.setLayout(layout)

        # Connect buttons
        cancel_btn.clicked.connect(dialog.reject)
        save_btn.clicked.connect(lambda: self.save_new_employee(dialog, name_edit.text(), position_combo.currentText()))

        dialog.exec_()

    def save_new_employee(self, dialog, name, position):
        """Save new employee to file and table"""
        if not name.strip():
            QMessageBox.warning(dialog, "Lỗi", "Vui lòng nhập họ tên nhân viên!")
            return

        try:
            # Load existing employees
            employees_file = "src/data/employees.json"
            if os.path.exists(employees_file):
                with open(employees_file, 'r', encoding='utf-8') as f:
                    employees_data = json.load(f)
            else:
                employees_data = []

            # Generate new ID
            if employees_data:
                new_id = max(emp.get('id', 0) for emp in employees_data) + 1
            else:
                new_id = 1

            # Create new employee
            new_employee = {
                'id': new_id,
                'name': name.strip(),
                'position': position,
                'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            # Add to list
            employees_data.append(new_employee)

            # Save to file
            os.makedirs(os.path.dirname(employees_file), exist_ok=True)
            with open(employees_file, 'w', encoding='utf-8') as f:
                json.dump(employees_data, f, ensure_ascii=False, indent=2)

            # Add to table
            self.add_employee_to_table(new_employee)

            dialog.accept()
            QMessageBox.information(self, "Thành công", f"Đã thêm nhân viên: {name}")

        except Exception as e:
            QMessageBox.critical(dialog, "Lỗi", f"Không thể lưu nhân viên: {str(e)}")

    def edit_employee(self, row):
        """Edit employee information"""
        # Get current data
        id_item = self.employee_table.item(row, 0)
        name_item = self.employee_table.item(row, 1)
        position_item = self.employee_table.item(row, 2)

        if not all([id_item, name_item, position_item]):
            return

        employee_id = int(id_item.text())
        current_name = name_item.text()
        current_position = position_item.text()

        # Create edit dialog
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Sửa thông tin nhân viên - ID: {employee_id}")
        dialog.setModal(True)
        dialog.resize(400, 200)

        layout = QVBoxLayout()

        # Form fields
        form_layout = QGridLayout()

        # Name field
        form_layout.addWidget(QLabel("Họ tên:"), 0, 0)
        name_edit = QLineEdit(current_name)
        name_edit.setFont(DEFAULT_FONT)
        form_layout.addWidget(name_edit, 0, 1)

        # Position field
        form_layout.addWidget(QLabel("Vị trí:"), 1, 0)
        position_combo = QComboBox()
        position_combo.setFont(DEFAULT_FONT)
        positions = ["Công nhân", "Tổ trưởng", "Phó tổ trưởng", "Kỹ thuật viên", "Thủ kho"]
        position_combo.addItems(positions)

        # Set current position
        if current_position in positions:
            position_combo.setCurrentText(current_position)

        form_layout.addWidget(position_combo, 1, 1)

        layout.addLayout(form_layout)

        # Buttons
        button_layout = QHBoxLayout()

        save_btn = QPushButton("Lưu")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        cancel_btn = QPushButton("Hủy")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #9E9E9E;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #757575;
            }
        """)

        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)
        dialog.setLayout(layout)

        # Connect buttons
        cancel_btn.clicked.connect(dialog.reject)
        save_btn.clicked.connect(lambda: self.save_edited_employee(dialog, employee_id, name_edit.text(), position_combo.currentText(), row))

        dialog.exec_()

    def save_edited_employee(self, dialog, employee_id, name, position, row):
        """Save edited employee information"""
        if not name.strip():
            QMessageBox.warning(dialog, "Lỗi", "Vui lòng nhập họ tên nhân viên!")
            return

        try:
            # Load existing employees
            employees_file = "src/data/employees.json"
            with open(employees_file, 'r', encoding='utf-8') as f:
                employees_data = json.load(f)

            # Find and update employee
            for employee in employees_data:
                if employee.get('id') == employee_id:
                    employee['name'] = name.strip()
                    employee['position'] = position
                    employee['updated_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    break

            # Save to file
            with open(employees_file, 'w', encoding='utf-8') as f:
                json.dump(employees_data, f, ensure_ascii=False, indent=2)

            # Update table
            self.employee_table.item(row, 1).setText(name.strip())
            self.employee_table.item(row, 2).setText(position)

            dialog.accept()
            QMessageBox.information(self, "Thành công", f"Đã cập nhật thông tin nhân viên: {name}")

        except Exception as e:
            QMessageBox.critical(dialog, "Lỗi", f"Không thể cập nhật nhân viên: {str(e)}")

    def delete_employee(self, row):
        """Delete employee"""
        # Get employee info
        id_item = self.employee_table.item(row, 0)
        name_item = self.employee_table.item(row, 1)

        if not all([id_item, name_item]):
            return

        employee_id = int(id_item.text())
        employee_name = name_item.text()

        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Xác nhận xóa",
            f"Bạn có chắc chắn muốn xóa nhân viên:\n{employee_name} (ID: {employee_id})?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                # Load existing employees
                employees_file = "src/data/employees.json"
                with open(employees_file, 'r', encoding='utf-8') as f:
                    employees_data = json.load(f)

                # Remove employee
                employees_data = [emp for emp in employees_data if emp.get('id') != employee_id]

                # Save to file
                with open(employees_file, 'w', encoding='utf-8') as f:
                    json.dump(employees_data, f, ensure_ascii=False, indent=2)

                # Remove from table
                self.employee_table.removeRow(row)

                QMessageBox.information(self, "Thành công", f"Đã xóa nhân viên: {employee_name}")

            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể xóa nhân viên: {str(e)}")

    def load_attendance_employees(self):
        """Load employees for attendance management"""
        try:
            # This method is now handled by populate_leave_employee_combo()
            # Keep for backward compatibility but redirect to new method
            pass
        except Exception as e:
            print(f"Lỗi khi tải danh sách nhân viên: {str(e)}")

    def load_attendance_data(self):
        """Load attendance data and update calendar"""
        try:
            attendance_file = "src/data/attendance.json"
            if os.path.exists(attendance_file):
                with open(attendance_file, 'r', encoding='utf-8') as f:
                    self.attendance_data = json.load(f)
            else:
                self.attendance_data = {}

            self.update_calendar_display()

        except Exception as e:
            print(f"Lỗi khi tải dữ liệu nghỉ phép: {str(e)}")
            self.attendance_data = {}

    def update_calendar_display(self):
        """Update calendar to show absence days"""
        # Reset calendar format
        self.attendance_calendar.setDateTextFormat(QDate(), self.attendance_calendar.dateTextFormat(QDate()))

        # Get selected employee from combo
        employee_text = self.leave_employee_combo.currentText()
        if not employee_text:
            return

        employee_id = employee_text.split(" - ")[0] if " - " in employee_text else "1"

        # Get employee's absence data
        employee_absences = self.attendance_data.get(str(employee_id), {})

        # Format absence days on calendar
        for date_str, absence_info in employee_absences.items():
            try:
                date_parts = date_str.split('-')
                if len(date_parts) == 3:
                    year, month, day = map(int, date_parts)
                    qdate = QDate(year, month, day)

                    # Set color based on absence type
                    format = self.attendance_calendar.dateTextFormat(qdate)
                    absence_type = absence_info.get('type', '')

                    if absence_type == 'Nghỉ ốm':
                        format.setBackground(QBrush(QColor(255, 152, 0)))  # Orange
                    elif absence_type == 'Nghỉ phép':
                        format.setBackground(QBrush(QColor(76, 175, 80)))  # Green
                    elif absence_type == 'Nghỉ việc riêng':
                        format.setBackground(QBrush(QColor(33, 150, 243)))  # Blue
                    else:  # Nghỉ không phép
                        format.setBackground(QBrush(QColor(244, 67, 54)))  # Red

                    format.setForeground(QBrush(QColor(255, 255, 255)))  # White text
                    self.attendance_calendar.setDateTextFormat(qdate, format)

            except Exception as e:
                print(f"Lỗi khi format ngày {date_str}: {str(e)}")

    def on_employee_selection_changed(self, current, previous):
        """Handle employee selection change"""
        if current:
            self.update_calendar_display()
            # Update absence history for currently selected date
            selected_date = self.attendance_calendar.selectedDate()
            self.update_absence_history(selected_date)

    def on_calendar_date_clicked(self, date):
        """Handle calendar date click"""
        # Update absence history for selected date
        self.update_absence_history(date)

    def update_absence_history(self, date):
        """Update absence history list for selected date"""
        self.absence_history_list.clear()

        date_str = date.toString('yyyy-MM-dd')

        # Show all employees' absence status for this date
        try:
            employees_file = "src/data/employees.json"
            if os.path.exists(employees_file):
                with open(employees_file, 'r', encoding='utf-8') as f:
                    employees_data = json.load(f)

                for employee in employees_data:
                    employee_id = str(employee.get('id', ''))
                    employee_name = employee.get('name', '')

                    # Check if employee was absent on this date
                    if employee_id in self.attendance_data:
                        if date_str in self.attendance_data[employee_id]:
                            absence_info = self.attendance_data[employee_id][date_str]
                            absence_type = absence_info.get('type', '')
                            note = absence_info.get('note', '')

                            item_text = f"{employee_name}: {absence_type}"
                            if note:
                                item_text += f" - {note}"

                            item = QListWidgetItem(item_text)

                            # Set color based on absence type
                            if absence_type == 'Nghỉ ốm':
                                item.setBackground(QColor(255, 152, 0, 50))
                            elif absence_type == 'Nghỉ phép':
                                item.setBackground(QColor(76, 175, 80, 50))
                            elif absence_type == 'Nghỉ việc riêng':
                                item.setBackground(QColor(33, 150, 243, 50))
                            else:  # Nghỉ không phép
                                item.setBackground(QColor(244, 67, 54, 50))

                            self.absence_history_list.addItem(item)
                        else:
                            # Employee was present
                            item = QListWidgetItem(f"{employee_name}: Có mặt")
                            item.setBackground(QColor(200, 255, 200, 50))
                            self.absence_history_list.addItem(item)
                    else:
                        # No data for this employee
                        item = QListWidgetItem(f"{employee_name}: Có mặt")
                        item.setBackground(QColor(200, 255, 200, 50))
                        self.absence_history_list.addItem(item)

        except Exception as e:
            print(f"Lỗi khi cập nhật lịch sử nghỉ: {str(e)}")

    def mark_employee_absent(self):
        """Mark selected employee as absent on selected date"""
        # Get selected employee from combo
        employee_text = self.leave_employee_combo.currentText()
        if not employee_text:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn nhân viên!")
            return

        employee_id = employee_text.split(" - ")[0] if " - " in employee_text else "1"
        employee_name = employee_text.split(' - ')[1] if " - " in employee_text else "Unknown"

        # Get selected date
        selected_date = self.attendance_calendar.selectedDate()
        date_str = selected_date.toString('yyyy-MM-dd')

        # Get absence type
        absence_type = self.absence_type_combo.currentText()

        # Ask for note (optional)
        note, ok = QInputDialog.getText(
            self,
            "Ghi chú",
            f"Ghi chú cho {employee_name} nghỉ {absence_type} ngày {selected_date.toString('dd/MM/yyyy')}:",
            text=""
        )

        if ok:
            try:
                # Update attendance data
                if employee_id not in self.attendance_data:
                    self.attendance_data[employee_id] = {}

                self.attendance_data[employee_id][date_str] = {
                    'type': absence_type,
                    'note': note.strip(),
                    'marked_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }

                # Save to file
                attendance_file = "src/data/attendance.json"
                os.makedirs(os.path.dirname(attendance_file), exist_ok=True)
                with open(attendance_file, 'w', encoding='utf-8') as f:
                    json.dump(self.attendance_data, f, ensure_ascii=False, indent=2)

                # Update display
                self.update_calendar_display()
                self.update_absence_history(selected_date)

                QMessageBox.information(
                    self,
                    "Thành công",
                    f"Đã đánh dấu {employee_name} {absence_type} ngày {selected_date.toString('dd/MM/yyyy')}"
                )

            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể lưu dữ liệu nghỉ phép: {str(e)}")

    def remove_employee_absent(self):
        """Remove absence mark for selected employee on selected date"""
        # Get selected employee from combo
        employee_text = self.leave_employee_combo.currentText()
        if not employee_text:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn nhân viên!")
            return

        employee_id = employee_text.split(" - ")[0] if " - " in employee_text else "1"
        employee_name = employee_text.split(' - ')[1] if " - " in employee_text else "Unknown"

        # Get selected date
        selected_date = self.attendance_calendar.selectedDate()
        date_str = selected_date.toString('yyyy-MM-dd')

        # Check if employee has absence record for this date
        if employee_id not in self.attendance_data or date_str not in self.attendance_data[employee_id]:
            QMessageBox.information(self, "Thông báo", f"{employee_name} không có đánh dấu nghỉ ngày {selected_date.toString('dd/MM/yyyy')}")
            return

        # Confirm removal
        reply = QMessageBox.question(
            self,
            "Xác nhận",
            f"Bạn có chắc chắn muốn xóa đánh dấu nghỉ của {employee_name} ngày {selected_date.toString('dd/MM/yyyy')}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                # Remove absence record
                del self.attendance_data[employee_id][date_str]

                # Clean up empty employee records
                if not self.attendance_data[employee_id]:
                    del self.attendance_data[employee_id]

                # Save to file
                attendance_file = "src/data/attendance.json"
                with open(attendance_file, 'w', encoding='utf-8') as f:
                    json.dump(self.attendance_data, f, ensure_ascii=False, indent=2)

                # Update display
                self.update_calendar_display()
                self.update_absence_history(selected_date)

                QMessageBox.information(
                    self,
                    "Thành công",
                    f"Đã xóa đánh dấu nghỉ của {employee_name} ngày {selected_date.toString('dd/MM/yyyy')}"
                )

            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể xóa dữ liệu nghỉ phép: {str(e)}")

    def load_import_tracking_data(self):
        """Load import tracking data from existing import files"""
        try:
            self.import_tracking_table.setRowCount(0)

            # Load participation data
            participation_file = "src/data/import_participation.json"
            if os.path.exists(participation_file):
                with open(participation_file, 'r', encoding='utf-8') as f:
                    participation_data = json.load(f)
            else:
                participation_data = {}

            all_imports = []

            # Process import files from imports directory
            imports_dir = "src/data/imports"
            if os.path.exists(imports_dir):
                for filename in os.listdir(imports_dir):
                    if filename.startswith('import_') and filename.endswith('.json'):
                        file_path = os.path.join(imports_dir, filename)

                        # Extract date from filename (import_YYYY-MM-DD.json)
                        try:
                            date_part = filename.replace('import_', '').replace('.json', '')
                            import_date = date_part  # Keep as YYYY-MM-DD format
                        except:
                            continue

                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                import_entries = json.load(f)

                            for entry in import_entries:
                                ingredient = entry.get('ingredient', '')
                                amount = entry.get('amount', 0)
                                import_type = entry.get('type', '')
                                timestamp = entry.get('timestamp', '')
                                note = entry.get('note', '')

                                if amount > 0 and ingredient:
                                    # Determine material type
                                    material_type = self.categorize_material(ingredient)

                                    # Create unique import key
                                    import_key = f"{import_date}_{timestamp}_{ingredient}_{amount}"

                                    # Get participation info
                                    participants = participation_data.get(import_key, {}).get('participants', [])
                                    participant_names = [p.get('name', '') for p in participants]

                                    all_imports.append({
                                        'date': import_date,
                                        'timestamp': timestamp,
                                        'material_type': material_type,
                                        'ingredient': ingredient,
                                        'amount': amount,
                                        'type': import_type,
                                        'participants': participant_names,
                                        'import_key': import_key,
                                        'note': note
                                    })
                        except Exception as e:
                            print(f"Lỗi khi đọc file {filename}: {str(e)}")
                            continue

            # Sort by timestamp (newest first) - timestamp already contains full date and time
            all_imports.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

            # Populate table
            for import_data in all_imports:
                self.add_import_tracking_row(import_data)

            print(f"Đã tải {len(all_imports)} bản ghi nhập kho")

        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể tải dữ liệu nhập kho: {str(e)}")
            print(f"Chi tiết lỗi: {str(e)}")

    def categorize_material(self, ingredient_name):
        """Categorize ingredient into material types"""
        ingredient_lower = ingredient_name.lower()

        # Bắp (Corn)
        if 'bắp' in ingredient_lower or 'corn' in ingredient_lower:
            return 'Bắp'

        # Nành (Soybean)
        elif 'nành' in ingredient_lower or 'soybean' in ingredient_lower or 'đậu nành' in ingredient_lower:
            return 'Nành'

        # Đá hạt (Stone/Gravel)
        elif 'đá hạt' in ingredient_lower or 'stone' in ingredient_lower or 'gravel' in ingredient_lower:
            return 'Đá hạt'

        # Cám gạo (Rice bran)
        elif 'cám gạo' in ingredient_lower or 'rice bran' in ingredient_lower or 'cám' in ingredient_lower:
            return 'Cám gạo'

        # Các nguyên liệu khác (amino acids, vitamins, etc.)
        else:
            return 'Khác'

    def add_import_tracking_row(self, import_data):
        """Add a row to import tracking table"""
        row = self.import_tracking_table.rowCount()
        self.import_tracking_table.insertRow(row)

        # Date with timestamp - create styled display with faded time part
        date_display = ""
        if 'timestamp' in import_data and import_data['timestamp']:
            timestamp = import_data['timestamp']
            if ' ' in timestamp:
                # Split date and time parts
                date_part, time_part = timestamp.split(' ', 1)
                # Create HTML formatted text with faded time
                date_display = f'<span style="color: #2c2c2c; font-weight: 600;">{date_part}</span> <span style="color: #888888; font-weight: 400;">{time_part}</span>'
            else:
                date_display = timestamp
        else:
            # Fallback to date if timestamp is not available
            date_display = import_data.get('date', '')

        date_item = QTableWidgetItem()
        date_item.setFlags(date_item.flags() & ~Qt.ItemIsEditable)

        # Create a custom widget for rich text display with optimized font size
        date_widget = QLabel()
        date_widget.setFont(QFont("Arial", 14, QFont.Medium))  # Increased to 14px for better readability
        date_widget.setText(date_display)
        date_widget.setAlignment(Qt.AlignCenter)
        date_widget.setStyleSheet("""
            QLabel {
                background: transparent;
                padding: 4px 6px;
                border: none;
                font-size: 14px;
            }
        """)

        # Set the widget in the table
        self.import_tracking_table.setItem(row, 0, date_item)
        self.import_tracking_table.setCellWidget(row, 0, date_widget)

        # Material type with ingredient name
        material_display = f"{import_data['material_type']}"
        if import_data['ingredient'] != import_data['material_type']:
            material_display += f" ({import_data['ingredient']})"

        material_item = QTableWidgetItem(material_display)
        material_item.setFlags(material_item.flags() & ~Qt.ItemIsEditable)

        # Color code by material type
        if import_data['material_type'] == 'Bắp':
            material_item.setBackground(QColor(255, 235, 59, 50))  # Yellow
        elif import_data['material_type'] == 'Nành':
            material_item.setBackground(QColor(139, 195, 74, 50))  # Light Green
        elif import_data['material_type'] == 'Cám gạo':
            material_item.setBackground(QColor(255, 152, 0, 50))   # Orange
        elif import_data['material_type'] == 'Đá hạt':
            material_item.setBackground(QColor(158, 158, 158, 50))  # Gray
        else:  # Khác
            material_item.setBackground(QColor(156, 39, 176, 50))   # Purple

        self.import_tracking_table.setItem(row, 1, material_item)

        # Amount
        amount_item = QTableWidgetItem(f"{import_data['amount']:,.1f} kg")
        amount_item.setFlags(amount_item.flags() & ~Qt.ItemIsEditable)
        self.import_tracking_table.setItem(row, 2, amount_item)

        # Participants
        participants_text = ", ".join(import_data['participants']) if import_data['participants'] else "Chưa ghi nhận"
        participants_item = QTableWidgetItem(participants_text)
        participants_item.setFlags(participants_item.flags() & ~Qt.ItemIsEditable)

        # Color code participants
        if import_data['participants']:
            participants_item.setBackground(QColor(200, 255, 200, 100))  # Light green
        else:
            participants_item.setBackground(QColor(255, 200, 200, 100))  # Light red

        self.import_tracking_table.setItem(row, 3, participants_item)

        # Note
        note_text = import_data.get('note', '')
        if import_data.get('type'):
            note_text = f"[{import_data['type'].upper()}] {note_text}".strip()

        note_item = QTableWidgetItem(note_text)
        note_item.setFlags(note_item.flags() & ~Qt.ItemIsEditable)
        self.import_tracking_table.setItem(row, 4, note_item)

        # Action button
        action_widget = QWidget()
        action_layout = QHBoxLayout()
        action_layout.setContentsMargins(5, 2, 5, 2)

        manage_btn = QPushButton("Quản lý NV")
        manage_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 3px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        manage_btn.clicked.connect(lambda: self.manage_import_participants(import_data))

        action_layout.addWidget(manage_btn)
        action_widget.setLayout(action_layout)

        self.import_tracking_table.setCellWidget(row, 5, action_widget)

    def refresh_import_tracking_data(self):
        """Refresh import tracking data"""
        self.load_import_tracking_data()
        QMessageBox.information(self, "Thành công", "Đã làm mới dữ liệu nhập kho!")

    def filter_import_tracking_data(self):
        """Filter import tracking data based on date range and material type"""
        from_date = self.import_tracking_from_date.date()
        to_date = self.import_tracking_to_date.date()
        material_filter = self.import_material_filter.currentText()

        # Hide/show rows based on filter
        for row in range(self.import_tracking_table.rowCount()):
            show_row = True

            # Check date range
            date_widget = self.import_tracking_table.cellWidget(row, 0)
            if date_widget:
                try:
                    # Extract date from the widget's text (which may contain HTML)
                    timestamp_text = date_widget.text()
                    # Remove HTML tags if present
                    import re
                    clean_text = re.sub(r'<[^>]+>', '', timestamp_text)

                    if ' ' in clean_text:
                        date_part = clean_text.split(' ')[0]  # Get date part only
                    else:
                        date_part = clean_text

                    row_date = QDate.fromString(date_part, "yyyy-MM-dd")
                    if row_date.isValid():
                        if row_date < from_date or row_date > to_date:
                            show_row = False
                except:
                    pass

            # Check material type
            if material_filter != "Tất cả":
                material_item = self.import_tracking_table.item(row, 1)
                if material_item and material_filter not in material_item.text():
                    show_row = False

            self.import_tracking_table.setRowHidden(row, not show_row)

    def manage_import_participants(self, import_data):
        """Manage employees participating in import activity"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Quản lý nhân viên tham gia nhập kho")
        dialog.setModal(True)
        dialog.resize(600, 500)

        layout = QVBoxLayout()

        # Info section
        info_layout = QGridLayout()
        info_layout.addWidget(QLabel("Ngày:"), 0, 0)
        info_layout.addWidget(QLabel(import_data['date']), 0, 1)
        info_layout.addWidget(QLabel("Nguyên liệu:"), 1, 0)
        info_layout.addWidget(QLabel(f"{import_data['material_type']} ({import_data['ingredient']})"), 1, 1)
        info_layout.addWidget(QLabel("Số lượng:"), 2, 0)
        info_layout.addWidget(QLabel(f"{import_data['amount']:,.0f} kg"), 2, 1)

        info_group = QGroupBox("Thông tin nhập kho")
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Employee selection section
        employee_group = QGroupBox("Chọn nhân viên tham gia")
        employee_layout = QVBoxLayout()

        # Get available employees (exclude those on leave)
        available_employees = self.get_available_employees(import_data['date'])

        # Create checkboxes for each employee
        self.participant_checkboxes = {}

        if available_employees:
            for employee in available_employees:
                checkbox = QCheckBox(f"{employee['name']} - {employee['position']} (ID: {employee['id']})")
                checkbox.setFont(DEFAULT_FONT)

                # Check if employee was already selected
                if employee['name'] in import_data['participants']:
                    checkbox.setChecked(True)

                self.participant_checkboxes[employee['id']] = {
                    'checkbox': checkbox,
                    'employee': employee
                }
                employee_layout.addWidget(checkbox)
        else:
            no_employees_label = QLabel("Không có nhân viên nào có mặt trong ngày này")
            no_employees_label.setStyleSheet("color: #666666; font-style: italic;")
            employee_layout.addWidget(no_employees_label)

        employee_group.setLayout(employee_layout)

        # Scroll area for employee list
        scroll_area = QScrollArea()
        scroll_area.setWidget(employee_group)
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(300)
        layout.addWidget(scroll_area)

        # Buttons
        button_layout = QHBoxLayout()

        save_btn = QPushButton("Lưu")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        cancel_btn = QPushButton("Hủy")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #9E9E9E;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #757575;
            }
        """)

        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)
        dialog.setLayout(layout)

        # Connect buttons
        cancel_btn.clicked.connect(dialog.reject)
        save_btn.clicked.connect(lambda: self.save_import_participants(dialog, import_data))

        dialog.exec_()

    def get_available_employees(self, date_str):
        """Get employees available on a specific date (not on leave)"""
        try:
            # Load all employees
            employees_file = "src/data/employees.json"
            if not os.path.exists(employees_file):
                return []

            with open(employees_file, 'r', encoding='utf-8') as f:
                all_employees = json.load(f)

            # Load attendance data
            attendance_file = "src/data/attendance.json"
            if os.path.exists(attendance_file):
                with open(attendance_file, 'r', encoding='utf-8') as f:
                    attendance_data = json.load(f)
            else:
                attendance_data = {}

            # Filter available employees
            available_employees = []

            for employee in all_employees:
                employee_id = str(employee.get('id', ''))

                # Check if employee was absent on this date
                is_absent = False
                if employee_id in attendance_data:
                    if date_str in attendance_data[employee_id]:
                        absence_type = attendance_data[employee_id][date_str].get('type', '')
                        # Exclude sick leave, but allow other types to participate
                        if absence_type == 'Nghỉ ốm':
                            is_absent = True

                if not is_absent:
                    available_employees.append(employee)

            return available_employees

        except Exception as e:
            print(f"Lỗi khi lấy danh sách nhân viên có mặt: {str(e)}")
            return []

    def save_import_participants(self, dialog, import_data):
        """Save selected participants for import activity"""
        try:
            # Get selected participants
            selected_participants = []

            for employee_id, data in self.participant_checkboxes.items():
                if data['checkbox'].isChecked():
                    selected_participants.append({
                        'id': employee_id,
                        'name': data['employee']['name'],
                        'position': data['employee']['position']
                    })

            # Load existing participation data
            participation_file = "src/data/import_participation.json"
            if os.path.exists(participation_file):
                with open(participation_file, 'r', encoding='utf-8') as f:
                    participation_data = json.load(f)
            else:
                participation_data = {}

            # Save participation data
            import_key = import_data['import_key']
            participation_data[import_key] = {
                'date': import_data['date'],
                'material_type': import_data['material_type'],
                'ingredient': import_data['ingredient'],
                'amount': import_data['amount'],
                'participants': selected_participants,
                'updated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            # Save to file
            os.makedirs(os.path.dirname(participation_file), exist_ok=True)
            with open(participation_file, 'w', encoding='utf-8') as f:
                json.dump(participation_data, f, ensure_ascii=False, indent=2)

            # Refresh table
            self.load_import_tracking_data()

            dialog.accept()
            QMessageBox.information(
                self,
                "Thành công",
                f"Đã lưu danh sách {len(selected_participants)} nhân viên tham gia nhập kho!"
            )

        except Exception as e:
            QMessageBox.critical(dialog, "Lỗi", f"Không thể lưu dữ liệu tham gia: {str(e)}")

    def calculate_monthly_bonus(self):
        """Calculate monthly bonus for all employees"""
        try:
            selected_month = self.bonus_month_combo.currentData()
            selected_year = self.bonus_year_combo.currentData()

            print(f"Tính thưởng cho tháng {selected_month}/{selected_year}")

            # Load bonus rates from config
            bonus_config = self.load_bonus_rates()
            bonus_rates = bonus_config.get("default_rates", {
                'Bắp': 400000,
                'Nành': 400000,
                'Cám gạo': 270000,
                'Khác': 350000
            })

            # Load participation data
            participation_file = "src/data/import_participation.json"
            if not os.path.exists(participation_file):
                QMessageBox.warning(self, "Cảnh báo", "Chưa có dữ liệu tham gia nhập kho!")
                return

            with open(participation_file, 'r', encoding='utf-8') as f:
                participation_data = json.load(f)

            # Load employees data
            employees_file = "src/data/employees.json"
            if not os.path.exists(employees_file):
                QMessageBox.warning(self, "Cảnh báo", "Chưa có dữ liệu nhân viên!")
                return

            with open(employees_file, 'r', encoding='utf-8') as f:
                employees_data = json.load(f)

            # Load attendance data to exclude sick leave
            attendance_file = "src/data/attendance.json"
            if os.path.exists(attendance_file):
                with open(attendance_file, 'r', encoding='utf-8') as f:
                    attendance_data = json.load(f)
            else:
                attendance_data = {}

            # Calculate participation counts for each material type
            material_participation = {}  # {material_type: {employee_id: count}}

            for import_key, import_info in participation_data.items():
                import_date = import_info.get('date', '')
                material_type = import_info.get('material_type', '')
                participants = import_info.get('participants', [])

                # Check if import is in selected month/year
                try:
                    date_parts = import_date.split('-')
                    if len(date_parts) == 3:
                        year, month, day = map(int, date_parts)
                        if year == selected_year and month == selected_month:
                            # Count participation for each employee
                            if material_type not in material_participation:
                                material_participation[material_type] = {}

                            for participant in participants:
                                employee_id = str(participant.get('id', ''))

                                # Check if employee was sick on this date
                                is_sick = False
                                if employee_id in attendance_data:
                                    if import_date in attendance_data[employee_id]:
                                        absence_type = attendance_data[employee_id][import_date].get('type', '')
                                        if absence_type == 'Nghỉ ốm':
                                            is_sick = True

                                # Only count if not sick
                                if not is_sick:
                                    if employee_id not in material_participation[material_type]:
                                        material_participation[material_type][employee_id] = 0
                                    material_participation[material_type][employee_id] += 1
                except:
                    continue

            # Calculate bonus for each employee
            employee_bonuses = {}  # {employee_id: {material_type: bonus_amount}}

            for material_type, participants in material_participation.items():
                if participants:  # If there are participants for this material
                    total_bonus = bonus_rates.get(material_type, 0)
                    bonus_per_person = total_bonus / len(participants)

                    for employee_id in participants:
                        if employee_id not in employee_bonuses:
                            employee_bonuses[employee_id] = {}
                        employee_bonuses[employee_id][material_type] = bonus_per_person

            # Display results
            self.display_bonus_results(employees_data, employee_bonuses, selected_month, selected_year)

            # Save results
            self.save_bonus_calculation(employee_bonuses, selected_month, selected_year)

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tính toán tiền thưởng: {str(e)}")

    def display_bonus_results(self, employees_data, employee_bonuses, month, year):
        """Display bonus calculation results in table"""
        self.bonus_results_table.setRowCount(0)

        # Create employee lookup
        employee_lookup = {str(emp.get('id', '')): emp for emp in employees_data}

        # Get all employees who have bonuses
        bonus_employee_ids = set(employee_bonuses.keys())

        # Add all employees to table (even those with 0 bonus)
        all_employee_ids = set(str(emp.get('id', '')) for emp in employees_data)

        for employee_id in all_employee_ids:
            employee = employee_lookup.get(employee_id, {})
            bonuses = employee_bonuses.get(employee_id, {})

            row = self.bonus_results_table.rowCount()
            self.bonus_results_table.insertRow(row)

            # Employee name
            name_item = QTableWidgetItem(employee.get('name', ''))
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.bonus_results_table.setItem(row, 0, name_item)

            # Position
            position_item = QTableWidgetItem(employee.get('position', ''))
            position_item.setFlags(position_item.flags() & ~Qt.ItemIsEditable)
            self.bonus_results_table.setItem(row, 1, position_item)

            # Material bonuses
            material_types = ['Bắp', 'Nành', 'Cám gạo', 'Khác']
            total_bonus = 0

            for i, material_type in enumerate(material_types):
                bonus_amount = bonuses.get(material_type, 0)
                total_bonus += bonus_amount

                bonus_item = QTableWidgetItem(f"{bonus_amount:,.0f}")
                bonus_item.setFlags(bonus_item.flags() & ~Qt.ItemIsEditable)

                # Color code based on amount
                if bonus_amount > 0:
                    bonus_item.setBackground(QColor(200, 255, 200))  # Light green

                self.bonus_results_table.setItem(row, 2 + i, bonus_item)

            # Total bonus
            total_item = QTableWidgetItem(f"{total_bonus:,.0f}")
            total_item.setFlags(total_item.flags() & ~Qt.ItemIsEditable)
            total_item.setBackground(QColor(255, 255, 200))  # Light yellow
            total_item.setFont(QFont("Arial", DEFAULT_FONT_SIZE, QFont.Bold))
            self.bonus_results_table.setItem(row, 6, total_item)

        QMessageBox.information(
            self,
            "Thành công",
            f"Đã tính toán tiền thưởng cho tháng {month:02d}/{year}!\n"
            f"Tổng số nhân viên: {len(all_employee_ids)}\n"
            f"Nhân viên có thưởng: {len(bonus_employee_ids)}"
        )

    def save_bonus_calculation(self, employee_bonuses, month, year):
        """Save bonus calculation results to file"""
        try:
            bonus_file = "src/data/bonus_calculation.json"

            # Load existing data
            if os.path.exists(bonus_file):
                with open(bonus_file, 'r', encoding='utf-8') as f:
                    bonus_data = json.load(f)
            else:
                bonus_data = {}

            # Save calculation for this month/year
            period_key = f"{year}-{month:02d}"
            bonus_data[period_key] = {
                'year': year,
                'month': month,
                'employee_bonuses': employee_bonuses,
                'calculated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            # Save to file
            os.makedirs(os.path.dirname(bonus_file), exist_ok=True)
            with open(bonus_file, 'w', encoding='utf-8') as f:
                json.dump(bonus_data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"Lỗi khi lưu kết quả tính thưởng: {str(e)}")

    def export_bonus_report(self):
        """Export bonus report to Excel"""
        try:
            # Check if there's data to export
            if self.bonus_results_table.rowCount() == 0:
                QMessageBox.warning(self, "Cảnh báo", "Chưa có dữ liệu để xuất báo cáo!")
                return

            # Get file path
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Lưu báo cáo Excel",
                f"BaoCaoTienThuong_{QDate.currentDate().toString('yyyyMMdd')}.xlsx",
                "Excel Files (*.xlsx)"
            )

            if file_path:
                self.create_excel_report(file_path)
                QMessageBox.information(self, "Thành công", f"Đã xuất báo cáo Excel: {file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể xuất báo cáo Excel: {str(e)}")

    def create_excel_report(self, file_path):
        """Create comprehensive Excel report with multiple sheets"""
        try:
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # Sheet 1: Employee List
                self.create_employee_sheet(writer)

                # Sheet 2: Attendance Data
                self.create_attendance_sheet(writer)

                # Sheet 3: Import Tracking
                self.create_import_tracking_sheet(writer)

                # Sheet 4: Bonus Calculation
                self.create_bonus_sheet(writer)

        except Exception as e:
            raise Exception(f"Lỗi khi tạo file Excel: {str(e)}")

    def create_employee_sheet(self, writer):
        """Create employee list sheet"""
        try:
            employees_file = "src/data/employees.json"
            if os.path.exists(employees_file):
                with open(employees_file, 'r', encoding='utf-8') as f:
                    employees_data = json.load(f)

                # Convert to DataFrame
                df_employees = pd.DataFrame(employees_data)
                if not df_employees.empty:
                    # Reorder columns
                    columns_order = ['id', 'name', 'position', 'created_date']
                    df_employees = df_employees.reindex(columns=[col for col in columns_order if col in df_employees.columns])

                    # Rename columns to Vietnamese
                    df_employees.columns = ['ID', 'Họ tên', 'Vị trí', 'Ngày tạo']

                    df_employees.to_excel(writer, sheet_name='Nhân viên', index=False)

        except Exception as e:
            print(f"Lỗi khi tạo sheet nhân viên: {str(e)}")

    def create_attendance_sheet(self, writer):
        """Create attendance data sheet"""
        try:
            attendance_file = "src/data/attendance.json"
            employees_file = "src/data/employees.json"

            if os.path.exists(attendance_file) and os.path.exists(employees_file):
                with open(attendance_file, 'r', encoding='utf-8') as f:
                    attendance_data = json.load(f)

                with open(employees_file, 'r', encoding='utf-8') as f:
                    employees_data = json.load(f)

                # Create employee lookup
                employee_lookup = {str(emp.get('id', '')): emp.get('name', '') for emp in employees_data}

                # Convert attendance data to list
                attendance_list = []
                for employee_id, dates in attendance_data.items():
                    employee_name = employee_lookup.get(employee_id, f"ID: {employee_id}")
                    for date_str, absence_info in dates.items():
                        attendance_list.append({
                            'Nhân viên': employee_name,
                            'Ngày': date_str,
                            'Loại nghỉ': absence_info.get('type', ''),
                            'Ghi chú': absence_info.get('note', ''),
                            'Ngày đánh dấu': absence_info.get('marked_date', '')
                        })

                if attendance_list:
                    df_attendance = pd.DataFrame(attendance_list)
                    df_attendance = df_attendance.sort_values(['Nhân viên', 'Ngày'])
                    df_attendance.to_excel(writer, sheet_name='Nghỉ phép', index=False)

        except Exception as e:
            print(f"Lỗi khi tạo sheet nghỉ phép: {str(e)}")

    def create_import_tracking_sheet(self, writer):
        """Create import tracking sheet"""
        try:
            participation_file = "src/data/import_participation.json"

            if os.path.exists(participation_file):
                with open(participation_file, 'r', encoding='utf-8') as f:
                    participation_data = json.load(f)

                # Convert to list
                import_list = []
                for import_key, import_info in participation_data.items():
                    participants = import_info.get('participants', [])
                    participant_names = [p.get('name', '') for p in participants]

                    import_list.append({
                        'Ngày': import_info.get('date', ''),
                        'Loại nguyên liệu': import_info.get('material_type', ''),
                        'Tên nguyên liệu': import_info.get('ingredient', ''),
                        'Số lượng (kg)': import_info.get('amount', 0),
                        'Nhân viên tham gia': ', '.join(participant_names),
                        'Số lượng NV': len(participants),
                        'Cập nhật lần cuối': import_info.get('updated_date', '')
                    })

                if import_list:
                    df_import = pd.DataFrame(import_list)
                    df_import = df_import.sort_values(['Ngày', 'Loại nguyên liệu'])
                    df_import.to_excel(writer, sheet_name='Nhập kho', index=False)

        except Exception as e:
            print(f"Lỗi khi tạo sheet nhập kho: {str(e)}")

    def create_bonus_sheet(self, writer):
        """Create bonus calculation sheet"""
        try:
            # Get data from current table
            bonus_list = []

            for row in range(self.bonus_results_table.rowCount()):
                employee_name = self.bonus_results_table.item(row, 0).text() if self.bonus_results_table.item(row, 0) else ""
                position = self.bonus_results_table.item(row, 1).text() if self.bonus_results_table.item(row, 1) else ""
                bap_bonus = self.bonus_results_table.item(row, 2).text() if self.bonus_results_table.item(row, 2) else "0"
                nanh_bonus = self.bonus_results_table.item(row, 3).text() if self.bonus_results_table.item(row, 3) else "0"
                cam_gao_bonus = self.bonus_results_table.item(row, 4).text() if self.bonus_results_table.item(row, 4) else "0"
                khac_bonus = self.bonus_results_table.item(row, 5).text() if self.bonus_results_table.item(row, 5) else "0"
                total_bonus = self.bonus_results_table.item(row, 6).text() if self.bonus_results_table.item(row, 6) else "0"

                # Convert comma-separated numbers to integers
                try:
                    bap_bonus = int(bap_bonus.replace(',', ''))
                    nanh_bonus = int(nanh_bonus.replace(',', ''))
                    cam_gao_bonus = int(cam_gao_bonus.replace(',', ''))
                    khac_bonus = int(khac_bonus.replace(',', ''))
                    total_bonus = int(total_bonus.replace(',', ''))
                except:
                    bap_bonus = nanh_bonus = cam_gao_bonus = khac_bonus = total_bonus = 0

                bonus_list.append({
                    'Nhân viên': employee_name,
                    'Vị trí': position,
                    'Thưởng Bắp (VNĐ)': bap_bonus,
                    'Thưởng Nành (VNĐ)': nanh_bonus,
                    'Thưởng Cám gạo (VNĐ)': cam_gao_bonus,
                    'Thưởng Khác (VNĐ)': khac_bonus,
                    'Tổng thưởng (VNĐ)': total_bonus
                })

            if bonus_list:
                df_bonus = pd.DataFrame(bonus_list)

                # Add summary row
                summary_row = {
                    'Nhân viên': 'TỔNG CỘNG',
                    'Vị trí': '',
                    'Thưởng Bắp (VNĐ)': df_bonus['Thưởng Bắp (VNĐ)'].sum(),
                    'Thưởng Nành (VNĐ)': df_bonus['Thưởng Nành (VNĐ)'].sum(),
                    'Thưởng Cám gạo (VNĐ)': df_bonus['Thưởng Cám gạo (VNĐ)'].sum(),
                    'Thưởng Khác (VNĐ)': df_bonus['Thưởng Khác (VNĐ)'].sum(),
                    'Tổng thưởng (VNĐ)': df_bonus['Tổng thưởng (VNĐ)'].sum()
                }

                df_bonus = pd.concat([df_bonus, pd.DataFrame([summary_row])], ignore_index=True)
                df_bonus.to_excel(writer, sheet_name='Tiền thưởng', index=False)

                # Add bonus rates info
                rates_info = pd.DataFrame([
                    {'Loại nguyên liệu': 'Bắp', 'Mức thưởng (VNĐ/tháng)': 400000},
                    {'Loại nguyên liệu': 'Nành', 'Mức thưởng (VNĐ/tháng)': 400000},
                    {'Loại nguyên liệu': 'Cám gạo', 'Mức thưởng (VNĐ/tháng)': 270000},
                    {'Loại nguyên liệu': 'Khác', 'Mức thưởng (VNĐ/tháng)': 350000}
                ])

                # Write to a separate area in the same sheet
                startrow = len(df_bonus) + 3
                rates_info.to_excel(writer, sheet_name='Tiền thưởng', startrow=startrow, index=False)

        except Exception as e:
            print(f"Lỗi khi tạo sheet tiền thưởng: {str(e)}")

    def load_bonus_rates(self):
        """Load bonus rates from config file"""
        try:
            bonus_rates_file = "src/data/config/bonus_rates.json"
            if os.path.exists(bonus_rates_file):
                with open(bonus_rates_file, 'r', encoding='utf-8') as f:
                    bonus_config = json.load(f)
                return bonus_config
            else:
                # Create default config if not exists
                default_config = {
                    "default_rates": {
                        "Bắp": 400000,
                        "Nành": 400000,
                        "Cám gạo": 270000,
                        "Khác": 350000
                    },
                    "specific_rates": {},
                    "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "updated_by": "System"
                }
                self.save_bonus_rates(default_config)
                return default_config
        except Exception as e:
            print(f"Error loading bonus rates: {str(e)}")
            return {
                "default_rates": {"Bắp": 400000, "Nành": 400000, "Cám gạo": 270000, "Khác": 350000},
                "specific_rates": {}
            }

    def save_bonus_rates(self, bonus_config):
        """Save bonus rates to config file"""
        try:
            bonus_rates_file = "src/data/config/bonus_rates.json"
            os.makedirs(os.path.dirname(bonus_rates_file), exist_ok=True)

            bonus_config["last_updated"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            with open(bonus_rates_file, 'w', encoding='utf-8') as f:
                json.dump(bonus_config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving bonus rates: {str(e)}")
            return False

    def get_bonus_rate_for_ingredient(self, ingredient):
        """Get bonus rate for specific ingredient"""
        bonus_config = self.load_bonus_rates()

        # First check specific rates
        specific_rates = bonus_config.get("specific_rates", {})
        if ingredient in specific_rates:
            return specific_rates[ingredient]

        # Then check default rates by material type
        material_type = self.categorize_material(ingredient)
        default_rates = bonus_config.get("default_rates", {})
        return default_rates.get(material_type, 350000)  # Default to "Khác" rate

    def show_employee_selection_dialog(self, import_date, ingredient, amount, import_type):
        """Show dialog to select employees for import participation"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Chọn nhân viên tham gia xuống hàng")
        dialog.setModal(True)
        dialog.resize(500, 400)

        layout = QVBoxLayout()

        # Info section
        info_group = QGroupBox("Thông tin nhập kho")
        info_layout = QGridLayout()
        info_layout.addWidget(QLabel("Ngày:"), 0, 0)
        info_layout.addWidget(QLabel(import_date), 0, 1)
        info_layout.addWidget(QLabel("Nguyên liệu:"), 1, 0)
        info_layout.addWidget(QLabel(ingredient), 1, 1)
        info_layout.addWidget(QLabel("Số lượng:"), 2, 0)
        info_layout.addWidget(QLabel(f"{amount:,.1f} kg"), 2, 1)
        info_layout.addWidget(QLabel("Loại:"), 3, 0)
        info_layout.addWidget(QLabel("Cám" if import_type == "feed" else "Mix"), 3, 1)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Employee selection
        employee_group = QGroupBox("Chọn nhân viên tham gia")
        employee_layout = QVBoxLayout()

        # Get available employees (exclude those on sick leave)
        available_employees = self.get_available_employees(import_date)

        self.import_employee_checkboxes = {}

        if available_employees:
            for employee in available_employees:
                checkbox = QCheckBox(f"{employee['name']} - {employee['position']} (ID: {employee['id']})")
                checkbox.setFont(DEFAULT_FONT)
                checkbox.setChecked(True)  # Default to all selected

                self.import_employee_checkboxes[employee['id']] = {
                    'checkbox': checkbox,
                    'employee': employee
                }
                employee_layout.addWidget(checkbox)
        else:
            no_employees_label = QLabel("Không có nhân viên nào có mặt trong ngày này")
            no_employees_label.setStyleSheet("color: #666666; font-style: italic;")
            employee_layout.addWidget(no_employees_label)

        employee_group.setLayout(employee_layout)

        # Scroll area for employee list
        scroll_area = QScrollArea()
        scroll_area.setWidget(employee_group)
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(200)
        layout.addWidget(scroll_area)

        # Buttons
        button_layout = QHBoxLayout()

        select_all_btn = QPushButton("Chọn tất cả")
        select_all_btn.clicked.connect(lambda: self.toggle_all_employees(True))

        deselect_all_btn = QPushButton("Bỏ chọn tất cả")
        deselect_all_btn.clicked.connect(lambda: self.toggle_all_employees(False))

        save_btn = QPushButton("Lưu")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        cancel_btn = QPushButton("Hủy")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #9E9E9E;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #757575;
            }
        """)

        button_layout.addWidget(select_all_btn)
        button_layout.addWidget(deselect_all_btn)
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)
        dialog.setLayout(layout)

        # Connect buttons
        cancel_btn.clicked.connect(dialog.reject)
        save_btn.clicked.connect(dialog.accept)

        return dialog.exec_() == QDialog.Accepted

    def toggle_all_employees(self, select_all):
        """Toggle all employee checkboxes"""
        for data in self.import_employee_checkboxes.values():
            data['checkbox'].setChecked(select_all)

    def get_selected_employees(self):
        """Get list of selected employees from dialog"""
        selected_employees = []

        for employee_id, data in self.import_employee_checkboxes.items():
            if data['checkbox'].isChecked():
                selected_employees.append({
                    'id': employee_id,
                    'name': data['employee']['name'],
                    'position': data['employee']['position']
                })

        return selected_employees

    def save_employee_participation(self, import_type, ingredient, amount, date, note, selected_employees):
        """Save employee participation data for import activity"""
        try:
            # Create unique import key
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            import_key = f"{date}_{timestamp}_{ingredient}_{amount}"

            # Load existing participation data
            participation_file = "src/data/import_participation.json"
            if os.path.exists(participation_file):
                with open(participation_file, 'r', encoding='utf-8') as f:
                    participation_data = json.load(f)
            else:
                participation_data = {}

            # Determine material type
            material_type = self.categorize_material(ingredient)

            # Save participation data
            participation_data[import_key] = {
                'date': date,
                'timestamp': timestamp,
                'material_type': material_type,
                'ingredient': ingredient,
                'amount': float(amount),
                'import_type': import_type,
                'note': note,
                'participants': selected_employees,
                'updated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            # Save to file
            os.makedirs(os.path.dirname(participation_file), exist_ok=True)
            with open(participation_file, 'w', encoding='utf-8') as f:
                json.dump(participation_data, f, ensure_ascii=False, indent=2)

            print(f"Saved participation for {len(selected_employees)} employees")

        except Exception as e:
            print(f"Error saving employee participation: {str(e)}")
            QMessageBox.warning(self, "Cảnh báo", f"Không thể lưu thông tin nhân viên tham gia: {str(e)}")

    def show_bonus_settings_dialog(self):
        """Show dialog to configure bonus rates"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Cài đặt mức thưởng")
        dialog.setModal(True)
        dialog.resize(600, 500)

        layout = QVBoxLayout()

        # Header
        header = QLabel("Cài đặt mức thưởng cho từng loại nguyên liệu")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("color: #2E7D32; margin-bottom: 15px;")
        layout.addWidget(header)

        # Default rates section
        default_group = QGroupBox("Mức thưởng mặc định (VNĐ/tháng)")
        default_layout = QGridLayout()

        # Load current rates
        bonus_config = self.load_bonus_rates()
        default_rates = bonus_config.get("default_rates", {})

        # Create input fields for default rates
        self.bonus_inputs = {}

        material_types = ["Bắp", "Nành", "Cám gạo", "Khác"]
        for i, material_type in enumerate(material_types):
            row = i // 2
            col = (i % 2) * 2

            default_layout.addWidget(QLabel(f"{material_type}:"), row, col)

            input_field = QSpinBox()
            input_field.setFont(DEFAULT_FONT)
            input_field.setRange(0, 10000000)
            input_field.setSingleStep(10000)
            input_field.setValue(default_rates.get(material_type, 350000))
            input_field.setSuffix(" VNĐ")

            self.bonus_inputs[material_type] = input_field
            default_layout.addWidget(input_field, row, col + 1)

        default_group.setLayout(default_layout)
        layout.addWidget(default_group)

        # Specific rates section
        specific_group = QGroupBox("Mức thưởng riêng cho nguyên liệu cụ thể")
        specific_layout = QVBoxLayout()

        # Table for specific rates
        self.specific_rates_table = QTableWidget()
        self.specific_rates_table.setColumnCount(3)
        self.specific_rates_table.setHorizontalHeaderLabels(["Nguyên liệu", "Mức thưởng (VNĐ)", "Thao tác"])

        # Set column widths
        header = self.specific_rates_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

        # Load specific rates
        specific_rates = bonus_config.get("specific_rates", {})
        self.populate_specific_rates_table(specific_rates)

        specific_layout.addWidget(self.specific_rates_table)

        # Add specific rate button
        add_specific_btn = QPushButton("Thêm mức thưởng riêng")
        add_specific_btn.clicked.connect(self.add_specific_rate)
        specific_layout.addWidget(add_specific_btn)

        specific_group.setLayout(specific_layout)
        layout.addWidget(specific_group)

        # Buttons
        button_layout = QHBoxLayout()

        save_btn = QPushButton("Lưu")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        cancel_btn = QPushButton("Hủy")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #9E9E9E;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #757575;
            }
        """)

        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)
        dialog.setLayout(layout)

        # Connect buttons
        cancel_btn.clicked.connect(dialog.reject)
        save_btn.clicked.connect(lambda: self.save_bonus_settings(dialog))

        dialog.exec_()

    def populate_specific_rates_table(self, specific_rates):
        """Populate the specific rates table"""
        self.specific_rates_table.setRowCount(len(specific_rates))

        for row, (ingredient, rate) in enumerate(specific_rates.items()):
            # Ingredient name
            ingredient_item = QTableWidgetItem(ingredient)
            self.specific_rates_table.setItem(row, 0, ingredient_item)

            # Rate
            rate_item = QTableWidgetItem(f"{rate:,}")
            self.specific_rates_table.setItem(row, 1, rate_item)

            # Delete button
            delete_btn = QPushButton("Xóa")
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    border: none;
                    padding: 4px 8px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #d32f2f;
                }
            """)
            delete_btn.clicked.connect(lambda checked, r=row: self.delete_specific_rate(r))
            self.specific_rates_table.setCellWidget(row, 2, delete_btn)

    def add_specific_rate(self):
        """Add a new specific rate"""
        ingredient, ok = QInputDialog.getText(self, "Thêm mức thưởng riêng", "Tên nguyên liệu:")
        if ok and ingredient:
            rate, ok = QInputDialog.getInt(self, "Thêm mức thưởng riêng", "Mức thưởng (VNĐ):", 350000, 0, 10000000)
            if ok:
                row = self.specific_rates_table.rowCount()
                self.specific_rates_table.insertRow(row)

                # Ingredient name
                ingredient_item = QTableWidgetItem(ingredient)
                self.specific_rates_table.setItem(row, 0, ingredient_item)

                # Rate
                rate_item = QTableWidgetItem(f"{rate:,}")
                self.specific_rates_table.setItem(row, 1, rate_item)

                # Delete button
                delete_btn = QPushButton("Xóa")
                delete_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #f44336;
                        color: white;
                        border: none;
                        padding: 4px 8px;
                        border-radius: 3px;
                    }
                    QPushButton:hover {
                        background-color: #d32f2f;
                    }
                """)
                delete_btn.clicked.connect(lambda checked, r=row: self.delete_specific_rate(r))
                self.specific_rates_table.setCellWidget(row, 2, delete_btn)

    def delete_specific_rate(self, row):
        """Delete a specific rate"""
        self.specific_rates_table.removeRow(row)
        # Reconnect delete buttons for remaining rows
        for r in range(self.specific_rates_table.rowCount()):
            delete_btn = self.specific_rates_table.cellWidget(r, 2)
            if delete_btn:
                delete_btn.clicked.disconnect()
                delete_btn.clicked.connect(lambda checked, row_num=r: self.delete_specific_rate(row_num))

    def save_bonus_settings(self, dialog):
        """Save bonus settings"""
        try:
            # Get default rates
            default_rates = {}
            for material_type, input_field in self.bonus_inputs.items():
                default_rates[material_type] = input_field.value()

            # Get specific rates
            specific_rates = {}
            for row in range(self.specific_rates_table.rowCount()):
                ingredient_item = self.specific_rates_table.item(row, 0)
                rate_item = self.specific_rates_table.item(row, 1)

                if ingredient_item and rate_item:
                    ingredient = ingredient_item.text()
                    rate_text = rate_item.text().replace(',', '')
                    try:
                        rate = int(rate_text)
                        specific_rates[ingredient] = rate
                    except ValueError:
                        continue

            # Create config
            bonus_config = {
                "default_rates": default_rates,
                "specific_rates": specific_rates,
                "updated_by": "User"
            }

            # Save config
            if self.save_bonus_rates(bonus_config):
                # Update display labels
                self.update_bonus_rate_labels()
                dialog.accept()
                QMessageBox.information(self, "Thành công", "Đã lưu cài đặt mức thưởng!")
            else:
                QMessageBox.critical(self, "Lỗi", "Không thể lưu cài đặt!")

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu cài đặt: {str(e)}")

    def update_bonus_rate_labels(self):
        """Update bonus rate labels in the main interface"""
        try:
            bonus_config = self.load_bonus_rates()
            default_rates = bonus_config.get("default_rates", {})

            self.bap_rate_label.setText(f"{default_rates.get('Bắp', 400000):,} VNĐ")
            self.nanh_rate_label.setText(f"{default_rates.get('Nành', 400000):,} VNĐ")
            self.cam_gao_rate_label.setText(f"{default_rates.get('Cám gạo', 270000):,} VNĐ")
            self.khac_rate_label.setText(f"{default_rates.get('Khác', 350000):,} VNĐ")
        except Exception as e:
            print(f"Error updating bonus rate labels: {str(e)}")

    def load_salary_rates(self):
        """Load salary rates from config file"""
        try:
            salary_rates_file = "src/data/config/salary_rates.json"
            if os.path.exists(salary_rates_file):
                with open(salary_rates_file, 'r', encoding='utf-8') as f:
                    salary_config = json.load(f)
                return salary_config
            else:
                # Create default config if not exists
                default_config = {
                    "position_salaries": {
                        "Tổ trưởng": 8000000,
                        "Phó tổ trưởng": 7000000,
                        "Kỹ thuật viên": 6500000,
                        "Thủ kho": 6000000,
                        "Công nhân": 5500000
                    },
                    "working_days_per_month": 30,
                    "allowances": {},
                    "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "updated_by": "System"
                }
                self.save_salary_rates(default_config)
                return default_config
        except Exception as e:
            print(f"Error loading salary rates: {str(e)}")
            return {
                "position_salaries": {
                    "Tổ trưởng": 8000000,
                    "Phó tổ trưởng": 7000000,
                    "Kỹ thuật viên": 6500000,
                    "Thủ kho": 6000000,
                    "Công nhân": 5500000
                },
                "working_days_per_month": 30
            }

    def save_salary_rates(self, salary_config):
        """Save salary rates to config file"""
        try:
            salary_rates_file = "src/data/config/salary_rates.json"
            os.makedirs(os.path.dirname(salary_rates_file), exist_ok=True)

            salary_config["last_updated"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            with open(salary_rates_file, 'w', encoding='utf-8') as f:
                json.dump(salary_config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving salary rates: {str(e)}")
            return False

    def show_salary_settings_dialog(self):
        """Show dialog to configure salary rates"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Cài đặt lương cơ bản")
        dialog.setModal(True)
        dialog.resize(500, 400)

        layout = QVBoxLayout()

        # Header
        header = QLabel("Cài đặt lương cơ bản theo vị trí")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("color: #2E7D32; margin-bottom: 15px;")
        layout.addWidget(header)

        # Salary rates section
        rates_group = QGroupBox("Lương cơ bản (VNĐ/tháng)")
        rates_layout = QGridLayout()

        # Load current rates
        salary_config = self.load_salary_rates()
        position_salaries = salary_config.get("position_salaries", {})

        # Create input fields for salary rates
        self.salary_inputs = {}

        positions = ["Tổ trưởng", "Phó tổ trưởng", "Kỹ thuật viên", "Thủ kho", "Công nhân"]
        for i, position in enumerate(positions):
            rates_layout.addWidget(QLabel(f"{position}:"), i, 0)

            input_field = QSpinBox()
            input_field.setFont(QFont("Arial", 14))
            input_field.setRange(1000000, 50000000)
            input_field.setSingleStep(100000)
            input_field.setValue(position_salaries.get(position, 5500000))
            input_field.setSuffix(" VNĐ")
            input_field.setMinimumHeight(35)

            self.salary_inputs[position] = input_field
            rates_layout.addWidget(input_field, i, 1)

        rates_group.setLayout(rates_layout)
        layout.addWidget(rates_group)

        # Buttons
        button_layout = QHBoxLayout()

        save_btn = QPushButton("Lưu")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        cancel_btn = QPushButton("Hủy")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #9E9E9E;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #757575;
            }
        """)

        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)
        dialog.setLayout(layout)

        # Connect buttons
        cancel_btn.clicked.connect(dialog.reject)
        save_btn.clicked.connect(lambda: self.save_salary_settings(dialog))

        dialog.exec_()

    def save_salary_settings(self, dialog):
        """Save salary settings"""
        try:
            # Get salary rates
            position_salaries = {}
            for position, input_field in self.salary_inputs.items():
                position_salaries[position] = input_field.value()

            # Create config
            salary_config = self.load_salary_rates()
            salary_config["position_salaries"] = position_salaries
            salary_config["updated_by"] = "User"

            # Save config
            if self.save_salary_rates(salary_config):
                # Update display labels
                self.update_salary_rate_labels()
                dialog.accept()
                QMessageBox.information(self, "Thành công", "Đã lưu cài đặt lương cơ bản!")
            else:
                QMessageBox.critical(self, "Lỗi", "Không thể lưu cài đặt!")

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu cài đặt: {str(e)}")

    def update_salary_rate_labels(self):
        """Update salary rate labels in the main interface"""
        try:
            salary_config = self.load_salary_rates()
            position_salaries = salary_config.get("position_salaries", {})

            for position, label in self.salary_rate_labels.items():
                salary = position_salaries.get(position, 5500000)
                label.setText(f"{salary:,} VNĐ")
        except Exception as e:
            print(f"Error updating salary rate labels: {str(e)}")

    def calculate_monthly_salary(self):
        """Calculate monthly salary for all employees"""
        try:
            # Get selected month and year
            month = self.salary_month_combo.currentData()
            year = self.salary_year_combo.currentData()

            # Load employees
            employees = self.load_employees()
            if not employees:
                QMessageBox.warning(self, "Cảnh báo", "Không có dữ liệu nhân viên!")
                return

            # Load salary rates
            salary_config = self.load_salary_rates()
            position_salaries = salary_config.get("position_salaries", {})
            working_days_per_month = salary_config.get("working_days_per_month", 30)

            # Calculate days in month
            days_in_month = QDate(year, month, 1).daysInMonth()

            # Load attendance data for the month
            attendance_data = self.load_attendance_data_for_salary(month, year)

            # Load bonus data for the month
            bonus_data = self.get_bonus_data_for_month(month, year)

            # Calculate salary for each employee
            salary_results = []

            for employee in employees:
                employee_id = str(employee.get('id', ''))
                employee_name = employee.get('name', '')
                position = employee.get('position', 'Công nhân')

                # Get base salary for position
                base_salary = position_salaries.get(position, 5500000)

                # Calculate working days
                absent_days = self.count_absent_days(employee_id, month, year, attendance_data)
                working_days = days_in_month - absent_days

                # Calculate base salary for working days
                daily_salary = base_salary / working_days_per_month
                working_salary = daily_salary * working_days

                # Get bonus for this employee
                employee_bonus = bonus_data.get(employee_id, 0)

                # Calculate total salary
                total_salary = working_salary + employee_bonus

                salary_results.append({
                    'employee_name': employee_name,
                    'position': position,
                    'base_salary': base_salary,
                    'working_days': working_days,
                    'absent_days': absent_days,
                    'bonus': employee_bonus,
                    'total_salary': total_salary
                })

            # Display results in table
            self.display_salary_results(salary_results)

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tính lương: {str(e)}")
            print(f"Error calculating salary: {str(e)}")

    def count_absent_days(self, employee_id, month, year, attendance_data):
        """Count absent days for an employee in a specific month"""
        try:
            absent_days = 0

            # Check attendance data for the month
            for date_str, absent_employees in attendance_data.items():
                try:
                    # Parse date
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    if date_obj.month == month and date_obj.year == year:
                        if employee_id in absent_employees:
                            absent_days += 1
                except:
                    continue

            return absent_days
        except Exception as e:
            print(f"Error counting absent days: {str(e)}")
            return 0

    def load_attendance_data_for_salary(self, month, year):
        """Load attendance data for salary calculation"""
        try:
            attendance_file = "src/data/attendance.json"
            if os.path.exists(attendance_file):
                with open(attendance_file, 'r', encoding='utf-8') as f:
                    attendance_data = json.load(f)
                return attendance_data
            return {}
        except Exception as e:
            print(f"Error loading attendance data: {str(e)}")
            return {}

    def get_bonus_data_for_month(self, month, year):
        """Get bonus data for employees for a specific month"""
        try:
            # This would integrate with the bonus calculation system
            # For now, return empty dict - will be enhanced later
            bonus_data = {}

            # Try to get bonus data from recent calculations
            # This is a placeholder - actual implementation would depend on
            # how bonus data is stored and retrieved

            return bonus_data
        except Exception as e:
            print(f"Error getting bonus data: {str(e)}")
            return {}

    def display_salary_results(self, salary_results):
        """Display salary calculation results in the table"""
        try:
            self.salary_results_table.setRowCount(len(salary_results))

            for row, result in enumerate(salary_results):
                # Employee name
                name_item = QTableWidgetItem(result['employee_name'])
                name_item.setFont(QFont("Arial", 15, QFont.Medium))
                self.salary_results_table.setItem(row, 0, name_item)

                # Position
                position_item = QTableWidgetItem(result['position'])
                position_item.setFont(QFont("Arial", 15, QFont.Medium))
                position_item.setTextAlignment(Qt.AlignCenter)
                self.salary_results_table.setItem(row, 1, position_item)

                # Base salary
                base_salary_item = QTableWidgetItem(f"{result['base_salary']:,}")
                base_salary_item.setFont(QFont("Arial", 15, QFont.Bold))
                base_salary_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                base_salary_item.setForeground(QColor("#1976d2"))
                self.salary_results_table.setItem(row, 2, base_salary_item)

                # Working days
                working_days_item = QTableWidgetItem(str(result['working_days']))
                working_days_item.setFont(QFont("Arial", 15, QFont.Medium))
                working_days_item.setTextAlignment(Qt.AlignCenter)
                self.salary_results_table.setItem(row, 3, working_days_item)

                # Absent days
                absent_days_item = QTableWidgetItem(str(result['absent_days']))
                absent_days_item.setFont(QFont("Arial", 15, QFont.Medium))
                absent_days_item.setTextAlignment(Qt.AlignCenter)
                if result['absent_days'] > 0:
                    absent_days_item.setForeground(QColor("#f44336"))
                self.salary_results_table.setItem(row, 4, absent_days_item)

                # Bonus
                bonus_item = QTableWidgetItem(f"{result['bonus']:,}")
                bonus_item.setFont(QFont("Arial", 15, QFont.Bold))
                bonus_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                bonus_item.setForeground(QColor("#4CAF50"))
                self.salary_results_table.setItem(row, 5, bonus_item)

                # Total salary
                total_salary_item = QTableWidgetItem(f"{result['total_salary']:,.0f}")
                total_salary_item.setFont(QFont("Arial", 15, QFont.Bold))
                total_salary_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                total_salary_item.setForeground(QColor("#2E7D32"))
                total_salary_item.setBackground(QColor("#e8f5e8"))
                self.salary_results_table.setItem(row, 6, total_salary_item)

            # Auto-resize columns to content
            self.salary_results_table.resizeColumnsToContents()

        except Exception as e:
            print(f"Error displaying salary results: {str(e)}")

    def load_leave_types(self):
        """Load leave types configuration"""
        try:
            leave_types_file = "src/data/config/leave_types.json"
            if os.path.exists(leave_types_file):
                with open(leave_types_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                return config
            return {}
        except Exception as e:
            print(f"Error loading leave types: {str(e)}")
            return {}

    def show_attendance_statistics(self):
        """Show attendance statistics dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Thống kê chấm công")
        dialog.setModal(True)
        dialog.resize(800, 600)

        layout = QVBoxLayout()

        # Header
        header = QLabel("📊 Thống kê chấm công nhân viên")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("color: #2E7D32; margin-bottom: 15px;")
        layout.addWidget(header)

        # Placeholder content
        content = QLabel("Chức năng thống kê đang được phát triển...")
        content.setFont(QFont("Arial", 14))
        content.setAlignment(Qt.AlignCenter)
        content.setStyleSheet("color: #666; padding: 50px;")
        layout.addWidget(content)

        # Close button
        close_btn = QPushButton("Đóng")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #9E9E9E;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #757575;
            }
        """)
        close_btn.clicked.connect(dialog.accept)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)

        dialog.setLayout(layout)
        dialog.exec_()

    def submit_leave_request(self):
        """Submit leave request"""
        try:
            # Get form data
            employee_text = self.leave_employee_combo.currentText()
            if not employee_text:
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn nhân viên!")
                return

            leave_type = self.leave_type_combo.currentData()
            if not leave_type:
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn loại nghỉ!")
                return

            leave_date = self.leave_date_edit.date().toString("yyyy-MM-dd")
            reason = self.leave_reason_edit.toPlainText().strip()

            if not reason:
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập lý do nghỉ!")
                return

            # Extract employee ID from combo text
            employee_id = employee_text.split(" - ")[0] if " - " in employee_text else "1"

            # Create leave request data
            leave_data = {
                "employee_id": employee_id,
                "leave_type": leave_type,
                "leave_date": leave_date,
                "reason": reason,
                "half_day": self.half_day_checkbox.isChecked(),
                "status": "pending",
                "submitted_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            # Save leave request (placeholder)
            QMessageBox.information(self, "Thành công", "Đã gửi yêu cầu nghỉ phép!")

            # Clear form
            self.leave_reason_edit.clear()
            self.half_day_checkbox.setChecked(False)

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể gửi yêu cầu: {str(e)}")

    def populate_leave_employee_combo(self):
        """Populate employee combo for leave requests"""
        try:
            self.leave_employee_combo.clear()
            employees = self.load_employees()

            if employees:  # Check if employees is not None
                for employee in employees:
                    employee_id = employee.get('id', '')
                    employee_name = employee.get('name', '')
                    display_text = f"{employee_id} - {employee_name}"
                    self.leave_employee_combo.addItem(display_text, employee_id)
            else:
                # Add a default item if no employees found
                self.leave_employee_combo.addItem("Không có nhân viên", "")

        except Exception as e:
            print(f"Error populating employee combo: {str(e)}")

    def populate_leave_type_combo(self):
        """Populate leave type combo"""
        try:
            self.leave_type_combo.clear()
            leave_config = self.load_leave_types()
            leave_types = leave_config.get("leave_types", {})

            for leave_key, leave_info in leave_types.items():
                icon = leave_info.get("icon", "")
                name = leave_info.get("name", "")
                display_text = f"{icon} {name}"
                self.leave_type_combo.addItem(display_text, leave_key)

        except Exception as e:
            print(f"Error populating leave type combo: {str(e)}")


def main():
    import sys
    from PyQt5.QtWidgets import QApplication

    print("Starting Chicken Farm Application...")
    app = QApplication(sys.argv)
    app.setWindowIcon(create_app_icon())

    # Thiết lập font mặc định cho toàn bộ ứng dụng
    app.setFont(DEFAULT_FONT)

    print("Creating main window...")
    window = ChickenFarmApp()
    print("Showing main window...")
    window.show()
    print("Entering application event loop...")
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()


