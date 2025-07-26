"""
Main Window for the Chicken Farm App
"""

import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout, QMessageBox,
                           QFileDialog, QAction, QMenu, QToolBar, QStatusBar, QLabel, QTableWidgetItem,
                           QScrollArea, QGroupBox, QHBoxLayout, QComboBox, QPushButton, QDialog)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon, QCursor, QColor

from src.core.formula_manager import FormulaManager
from src.core.inventory_manager import InventoryManager
from src.core.report_manager import ReportManager
from src.services.import_service import ImportService
from src.services.export_service import ExportService
from src.services.history_service import HistoryService
from src.utils.constants import AREAS, SHIFTS, FARMS, DEFAULT_FONT_SIZE, HEADER_FONT_SIZE, BUTTON_FONT_SIZE, TABLE_HEADER_FONT_SIZE
from src.utils.formatting import format_number
from src.utils.app_icon import create_app_icon
from src.ui.logo import create_app_logo
from src.ui.tabs.feed_usage_tab import FeedUsageTab
from src.ui.tabs.inventory_tab import InventoryTab
from src.ui.tabs.import_tab import ImportTab
from src.ui.tabs.formula_tab import FormulaTab
from src.ui.tabs.history_tab import HistoryTab

class ChickenFarmApp(QMainWindow):
    """Main window for the Chicken Farm App"""

    def __init__(self):
        """Initialize the main window"""
        super().__init__()
        self.setWindowTitle("Phần mềm Quản lý Cám - Trại Gà")

        # Biến cờ để kiểm soát việc tải báo cáo
        self.report_loaded = False
        self.default_formula_loaded = False

        # Set up managers and services
        self.formula_manager = FormulaManager()
        self.inventory_manager = InventoryManager()
        self.report_manager = ReportManager()
        self.import_service = ImportService(self.inventory_manager)
        self.export_service = ExportService()
        self.history_service = HistoryService()

        # UI elements
        self.tabs = None
        self.feed_usage_tab = None
        self.inventory_tab = None
        self.import_tab = None
        self.formula_tab = None
        self.history_tab = None
        self.status_bar = None
        self.status_label = None
        self.toolbar = None

        # Set up fonts
        self.setup_fonts()

        # Initialize UI
        self.init_ui()

        # Set up menu bar
        self.create_menu_bar()

        # Set up toolbar
        self.create_toolbar()

        # Set up status bar
        self.create_status_bar()

        # Set app icon
        self.setWindowIcon(create_app_logo())

        # Load initial data
        self.load_default_formula()
        self.update_feed_formula_table()
        self.update_mix_formula_table()
        self.update_feed_inventory_table()
        self.update_mix_inventory_table()
        self.update_feed_preset_combo()
        self.update_mix_preset_combo()
        self.load_import_history()
        self.update_history_dates()

        # Update status bar
        self.update_status("Ứng dụng đã sẵn sàng")

    def setup_fonts(self):
        """Set up fonts for the application"""
        self.default_font = QFont("Arial", DEFAULT_FONT_SIZE)
        self.header_font = QFont("Arial", HEADER_FONT_SIZE, QFont.Bold)
        self.button_font = QFont("Arial", BUTTON_FONT_SIZE, QFont.Bold)
        self.table_header_font = QFont("Arial", TABLE_HEADER_FONT_SIZE, QFont.Bold)
        self.table_cell_font = QFont("Arial", DEFAULT_FONT_SIZE)

        # Set default font for the application
        self.setFont(self.default_font)

    def init_ui(self):
        """Initialize the UI components"""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Create tab widget
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setMovable(True)

        # Create tabs
        self.feed_usage_tab = FeedUsageTab(self)
        self.inventory_tab = InventoryTab(self)
        self.import_tab = ImportTab(self)
        self.formula_tab = FormulaTab(self)
        self.history_tab = HistoryTab(self)

        # Add tabs to tab widget
        self.tabs.addTab(self.feed_usage_tab, QIcon.fromTheme("document-edit"), "Sử dụng cám")
        self.tabs.addTab(self.inventory_tab, QIcon.fromTheme("folder"), "Tồn kho")
        self.tabs.addTab(self.import_tab, QIcon.fromTheme("document-import"), "Nhập kho")
        self.tabs.addTab(self.formula_tab, QIcon.fromTheme("document-properties"), "Công thức")
        self.tabs.addTab(self.history_tab, QIcon.fromTheme("document-open-recent"), "Lịch sử")

        # Connect tab changed signal
        self.tabs.currentChanged.connect(self.on_tab_changed)

        # Add tab widget to main layout
        main_layout.addWidget(self.tabs)

        # Set window size
        self.resize(1200, 800)

    def create_menu_bar(self):
        """Create the menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        # Save report action
        save_report_action = QAction(QIcon.fromTheme("document-save"), "&Lưu báo cáo", self)
        save_report_action.setShortcut("Ctrl+S")
        save_report_action.setStatusTip("Lưu báo cáo hiện tại")
        save_report_action.triggered.connect(self.save_report)
        file_menu.addAction(save_report_action)

        # Export to Excel action
        export_action = QAction(QIcon.fromTheme("document-export"), "&Xuất Excel", self)
        export_action.setShortcut("Ctrl+E")
        export_action.setStatusTip("Xuất dữ liệu ra file Excel")
        export_action.triggered.connect(self.export_to_excel)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        # Exit action
        exit_action = QAction(QIcon.fromTheme("application-exit"), "Th&oát", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Thoát ứng dụng")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = menubar.addMenu("&Hiển thị")

        # Toggle toolbar action
        toggle_toolbar_action = QAction("&Thanh công cụ", self)
        toggle_toolbar_action.setCheckable(True)
        toggle_toolbar_action.setChecked(True)
        toggle_toolbar_action.triggered.connect(self.toggle_toolbar)
        view_menu.addAction(toggle_toolbar_action)

        # Toggle status bar action
        toggle_statusbar_action = QAction("Thanh &trạng thái", self)
        toggle_statusbar_action.setCheckable(True)
        toggle_statusbar_action.setChecked(True)
        toggle_statusbar_action.triggered.connect(self.toggle_statusbar)
        view_menu.addAction(toggle_statusbar_action)

        # Help menu
        help_menu = menubar.addMenu("&Trợ giúp")

        # About action
        about_action = QAction(QIcon.fromTheme("help-about"), "&Thông tin", self)
        about_action.setStatusTip("Hiển thị thông tin về ứng dụng")
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def create_toolbar(self):
        """Create the toolbar"""
        self.toolbar = QToolBar("Thanh công cụ chính")
        self.toolbar.setIconSize(QSize(24, 24))
        self.toolbar.setMovable(False)
        self.addToolBar(self.toolbar)

        # Save report action
        save_action = QAction(QIcon.fromTheme("document-save"), "Lưu báo cáo", self)
        save_action.triggered.connect(self.save_report)
        self.toolbar.addAction(save_action)

        # Export to Excel action
        export_action = QAction(QIcon.fromTheme("document-export"), "Xuất Excel", self)
        export_action.triggered.connect(self.export_to_excel)
        self.toolbar.addAction(export_action)

        self.toolbar.addSeparator()

        # Add tab shortcuts
        for i in range(self.tabs.count()):
            tab_action = QAction(self.tabs.tabIcon(i), self.tabs.tabText(i), self)
            tab_action.triggered.connect(lambda checked, index=i: self.tabs.setCurrentIndex(index))
            self.toolbar.addAction(tab_action)

    def create_status_bar(self):
        """Create the status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Add status label
        self.status_label = QLabel("Sẵn sàng")
        self.status_bar.addPermanentWidget(self.status_label)

        # Add date label
        date_label = QLabel(datetime.now().strftime("%d/%m/%Y"))
        self.status_bar.addPermanentWidget(date_label)

    def update_status(self, message):
        """Update status bar message

        Args:
            message: Message to display
        """
        self.status_label.setText(message)

    def toggle_toolbar(self, checked):
        """Toggle toolbar visibility

        Args:
            checked: Whether the toolbar should be visible
        """
        self.toolbar.setVisible(checked)

    def toggle_statusbar(self, checked):
        """Toggle status bar visibility

        Args:
            checked: Whether the status bar should be visible
        """
        self.status_bar.setVisible(checked)

    def on_tab_changed(self, index):
        """Handle tab changed event

        Args:
            index: Index of the selected tab
        """
        tab_name = self.tabs.tabText(index)
        self.update_status(f"Tab hiện tại: {tab_name}")

    def show_about_dialog(self):
        """Show the about dialog"""
        QMessageBox.about(
            self,
            "Thông tin",
            "<h3>Phần mềm Quản lý Cám - Trại Gà</h3>"
            "<p>Phiên bản: 2.0</p>"
            "<p>© 2023 Minh-Tan_Phat</p>"
            "<p>Ứng dụng quản lý cám và thức ăn cho trại gà</p>"
        )

    # Methods delegated from tabs

    def calculate_feed_usage(self):
        """Calculate feed usage based on input values"""
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

        # Lấy dữ liệu từ các ô trong bảng feed_usage_tab
        for shift_idx, shift in enumerate(SHIFTS):
            for area_idx in range(AREAS):
                # Lấy cell key
                cell_key = f"{shift_idx}_{area_idx}"

                # Lấy giá trị từ spin_box và formula_combo
                spin_box = self.feed_usage_tab.feed_spinboxes.get(cell_key)
                formula_combo = self.feed_usage_tab.formula_combos.get(cell_key)

                if not spin_box or not formula_combo:
                    continue

                batch_value = spin_box.value()
                formula_name = formula_combo.currentText()

                # Nếu không có giá trị hoặc không chọn công thức, bỏ qua
                if batch_value <= 0 or not formula_name:
                    continue

                # Chuyển đổi batch_value: 0.5 = 1 mẻ, 1 = 2 mẻ, 1.5 = 3 mẻ, v.v.
                actual_batches = batch_value * 2  # Số mẻ thực tế = giá trị hiển thị * 2

                # Cập nhật tổng số mẻ theo khu
                khu_name = f"Khu {area_idx + 1}"
                if khu_name not in total_batches_by_area:
                    total_batches_by_area[khu_name] = 0
                total_batches_by_area[khu_name] += actual_batches
                total_batches += actual_batches

                # Cộng dồn số mẻ cho công thức này
                if formula_name in formula_batches:
                    formula_batches[formula_name] += batch_value
                else:
                    formula_batches[formula_name] = batch_value

                # Lưu thông tin cho từng farm
                farm_name = ""
                if area_idx in FARMS and len(FARMS[area_idx]) > 0:
                    farm_name = FARMS[area_idx][0]  # Lấy farm đầu tiên

                farm_key = f"{khu_name} - {farm_name}"
                if farm_key not in farm_formula_batches:
                    farm_formula_batches[farm_key] = {}

                if formula_name in farm_formula_batches[farm_key]:
                    farm_formula_batches[farm_key][formula_name] += batch_value
                else:
                    farm_formula_batches[farm_key][formula_name] = batch_value

                # Lưu thông tin chi tiết về mỗi ô để có thể áp dụng công thức mix riêng
                detail_cell_key = f"{khu_name}_{farm_name}_{shift}"
                if not hasattr(self, 'cell_formula_data'):
                    self.cell_formula_data = {}

                # Xác định công thức mix cho cell này
                mix_formula_name = None

                # 1. Kiểm tra xem ô này có công thức mix riêng không
                if hasattr(self, 'cell_mix_formulas') and self.cell_mix_formulas and detail_cell_key in self.cell_mix_formulas:
                    mix_formula_name = self.cell_mix_formulas[detail_cell_key]

                # 2. Nếu không, kiểm tra xem cột này có công thức mix không
                if not mix_formula_name and hasattr(self, 'column_mix_formulas') and self.column_mix_formulas:
                    col_str = f"{area_idx}"
                    if col_str in self.column_mix_formulas:
                        mix_formula_name = self.column_mix_formulas[col_str]

                # 3. Nếu không, kiểm tra xem khu này có công thức mix không
                if not mix_formula_name and hasattr(self, 'area_mix_formulas') and self.area_mix_formulas and khu_name in self.area_mix_formulas:
                    mix_formula_name = self.area_mix_formulas[khu_name]

                self.cell_formula_data[detail_cell_key] = {
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
                    cell_mix_data[detail_cell_key] = mix_formula_name

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
            self.column_mix_formulas = self.formula_manager.load_column_mix_formulas()

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
        for mix_name, mix_data in mix_formulas_used.items():
            mix_formula = mix_data["formula"]
            batch_value = mix_data["batch_value"]

            # Áp dụng quy tắc 0.5 = 1 mẻ, 1 = 2 mẻ
            actual_batches = batch_value * 2

            # Tính lượng từng thành phần mix
            for ingredient, amount_per_batch in mix_formula.items():
                # Lấy giá trị từ cột '1 mẻ (kg)' thay vì cột '10 mẻ (kg)'
                # amount_per_batch là giá trị cho 10 mẻ, chia 10 để có giá trị cho 1 mẻ
                one_batch_amount = amount_per_batch / 10

                # Tính lượng thành phần theo số mẻ thực tế
                mix_amount = one_batch_amount * actual_batches

                # Cộng dồn vào kết quả
                if ingredient in mix_ingredients:
                    mix_ingredients[ingredient] += mix_amount
                else:
                    mix_ingredients[ingredient] = mix_amount

        # Tính tổng lượng cám và mix
        total_feed = sum(feed_ingredients.values()) if feed_ingredients else 0
        total_mix = sum(mix_ingredients.values()) if mix_ingredients else 0

        # Đảm bảo thành phần "Nguyên liệu tổ hợp" trong cám trùng với tổng mix
        if "Nguyên liệu tổ hợp" in feed_ingredients:
            # Nếu có thành phần "Nguyên liệu tổ hợp" thì cập nhật giá trị bằng tổng mix
            if total_mix > 0:
                feed_ingredients["Nguyên liệu tổ hợp"] = total_mix

        # Lưu kết quả tính toán vào biến thành viên để sử dụng khi lưu báo cáo
        self.feed_ingredients = feed_ingredients
        self.mix_ingredients = mix_ingredients
        self.mix_formulas_used = mix_formulas_used
        self.total_batches = total_batches
        self.total_batches_by_area = total_batches_by_area
        self.total_tong_hop = total_mix  # Lưu tổng mix để sử dụng sau này

        # Cập nhật bảng kết quả trong feed_usage_tab
        self.update_feed_usage_results(feed_ingredients, mix_ingredients)

        # Cập nhật trạng thái
        self.update_status("Đã tính toán lượng cám sử dụng")

        # Hỏi người dùng có muốn cập nhật tồn kho không
        # Kết hợp feed_ingredients và mix_ingredients
        all_ingredients = {}
        all_ingredients.update(feed_ingredients)
        all_ingredients.update(mix_ingredients)

        # Cập nhật tồn kho
        self.update_inventory_after_usage(all_ingredients)

    def update_feed_usage_results(self, feed_ingredients, mix_ingredients):
        """Update the feed usage results table"""
        # Xóa dữ liệu cũ
        self.feed_usage_tab.feed_usage_table.setRowCount(0)

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

        # Thêm các thành phần cám
        for ingredient, amount in sorted_feed_ingredients.items():
            row = self.feed_usage_tab.feed_usage_table.rowCount()
            self.feed_usage_tab.feed_usage_table.insertRow(row)

            # Thêm tên thành phần
            name_item = QTableWidgetItem(ingredient)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
            self.feed_usage_tab.feed_usage_table.setItem(row, 0, name_item)

            # Thêm số lượng
            amount_item = QTableWidgetItem(format_number(amount))
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            amount_item.setFlags(amount_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
            self.feed_usage_tab.feed_usage_table.setItem(row, 1, amount_item)

            # Thêm đơn vị
            unit_item = QTableWidgetItem("kg")
            unit_item.setFlags(unit_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
            self.feed_usage_tab.feed_usage_table.setItem(row, 2, unit_item)

        # Thêm các thành phần mix nếu có
        if mix_ingredients:
            # Thêm dòng trống
            row = self.feed_usage_tab.feed_usage_table.rowCount()
            self.feed_usage_tab.feed_usage_table.insertRow(row)

            # Thêm tiêu đề mix
            row = self.feed_usage_tab.feed_usage_table.rowCount()
            self.feed_usage_tab.feed_usage_table.insertRow(row)

            mix_header = QTableWidgetItem("THÀNH PHẦN MIX")
            mix_header.setFlags(mix_header.flags() & ~Qt.ItemIsEditable)  # Make read-only
            mix_header.setBackground(QColor(230, 230, 250))  # Light lavender color
            mix_header.setFont(QFont("Arial", 10, QFont.Bold))
            self.feed_usage_tab.feed_usage_table.setItem(row, 0, mix_header)

            # Merge cells for header
            self.feed_usage_tab.feed_usage_table.setSpan(row, 0, 1, 3)

            # Thêm các thành phần mix
            for ingredient, amount in mix_ingredients.items():
                row = self.feed_usage_tab.feed_usage_table.rowCount()
                self.feed_usage_tab.feed_usage_table.insertRow(row)

                # Thêm tên thành phần
                name_item = QTableWidgetItem(ingredient)
                name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
                self.feed_usage_tab.feed_usage_table.setItem(row, 0, name_item)

                # Thêm số lượng
                amount_item = QTableWidgetItem(format_number(amount))
                amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                amount_item.setFlags(amount_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
                self.feed_usage_tab.feed_usage_table.setItem(row, 1, amount_item)

                # Thêm đơn vị
                unit_item = QTableWidgetItem("kg")
                unit_item.setFlags(unit_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
                self.feed_usage_tab.feed_usage_table.setItem(row, 2, unit_item)

    def update_inventory(self, inventory_type):
        """Update inventory items"""
        # Hiển thị hộp thoại xác nhận
        reply = QMessageBox.question(
            self,
            "Xác nhận cập nhật",
            f"Bạn có chắc chắn muốn cập nhật tồn kho {inventory_type}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        # Lấy dữ liệu từ bảng tồn kho
        if inventory_type == "feed":
            inventory_table = self.inventory_tab.feed_inventory_table
        else:
            inventory_table = self.inventory_tab.mix_inventory_table

        # Thu thập dữ liệu từ bảng
        inventory_data = {}
        for row in range(inventory_table.rowCount()):
            name_item = inventory_table.item(row, 0)
            amount_item = inventory_table.item(row, 1)

            if name_item and amount_item:
                name = name_item.text()
                # Chuyển đổi chuỗi thành số
                amount_text = amount_item.text().replace(",", "")
                try:
                    amount = float(amount_text) if amount_text else 0
                except ValueError:
                    amount = 0

                inventory_data[name] = amount

        # Cập nhật tồn kho
        for name, amount in inventory_data.items():
            self.inventory_manager.update_inventory(name, amount)

        # Lưu tồn kho
        self.inventory_manager.save_inventory()

        # Cập nhật giao diện
        self.update_feed_inventory_table()
        self.update_mix_inventory_table()

        # Hiển thị thông báo thành công
        QMessageBox.information(
            self,
            "Thành công",
            f"Đã cập nhật tồn kho {inventory_type}."
        )

        # Cập nhật trạng thái
        self.update_status(f"Đã cập nhật tồn kho {inventory_type}")

    def update_inventory_after_usage(self, ingredients_used):
        """Update inventory after usage"""
        # Hiển thị hộp thoại xác nhận
        reply = QMessageBox.question(
            self,
            "Xác nhận cập nhật tồn kho",
            "Bạn có muốn cập nhật tồn kho sau khi sử dụng cám?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        # Cập nhật tồn kho
        self.inventory_manager.use_ingredients(ingredients_used)

        # Cập nhật giao diện
        self.update_feed_inventory_table()
        self.update_mix_inventory_table()

        # Hiển thị thông báo thành công
        QMessageBox.information(
            self,
            "Thành công",
            "Đã cập nhật tồn kho sau khi sử dụng cám."
        )

        # Cập nhật trạng thái
        self.update_status("Đã cập nhật tồn kho sau khi sử dụng cám")

    def import_feed(self):
        """Import feed ingredient"""
        # Get values from the import tab
        ingredient = self.import_tab.feed_combo.currentText()
        amount = self.import_tab.feed_amount_spin.value()
        date = self.import_tab.feed_date_edit.date().toString("yyyy-MM-dd")
        note = self.import_tab.feed_note_edit.text()

        # Use import service to import feed
        self.import_service.import_feed(ingredient, amount)
        self.import_service.save_import_history("feed", ingredient, amount, date, note)

        # Update UI
        self.update_feed_inventory_table()
        self.load_import_history()

        # Reset input fields
        self.import_tab.feed_amount_spin.setValue(0)
        self.import_tab.feed_note_edit.clear()

    def import_mix(self):
        """Import mix ingredient"""
        # Get values from the import tab
        ingredient = self.import_tab.mix_combo.currentText()
        amount = self.import_tab.mix_amount_spin.value()
        date = self.import_tab.mix_date_edit.date().toString("yyyy-MM-dd")
        note = self.import_tab.mix_note_edit.text()

        # Use import service to import mix
        self.import_service.import_mix(ingredient, amount)
        self.import_service.save_import_history("mix", ingredient, amount, date, note)

        # Update UI
        self.update_mix_inventory_table()
        self.load_import_history()

        # Reset input fields
        self.import_tab.mix_amount_spin.setValue(0)
        self.import_tab.mix_note_edit.clear()

    def load_import_history(self):
        """Load import history data"""
        # Use import service to load history
        history = self.import_service.load_import_history()

        # Update UI
        self.import_tab.update_feed_import_history(history)
        self.import_tab.update_mix_import_history(history)

        # Update history dates
        self.update_history_dates()

    def update_feed_formula_table(self):
        """Update the feed formula table with current formula data"""
        # Get feed formula from formula manager
        formula = self.formula_manager.get_feed_formula()

        # Convert to the format expected by the formula tab
        formula_items = []
        for name, ratio in formula.items():
            formula_items.append({
                "name": name,
                "ratio": ratio,
                "unit": "kg"  # Assuming the unit is kg
            })

        # Update UI
        self.formula_tab.update_feed_formula_table(formula_items)

        # Update feed usage tab formula combos
        self.feed_usage_tab.update_formula_combos(self.formula_manager.get_feed_presets())

    def update_mix_formula_table(self):
        """Update the mix formula table with current formula data"""
        # Get mix formula from formula manager
        formula = self.formula_manager.get_mix_formula()

        # Convert to the format expected by the formula tab
        formula_items = []
        for name, ratio in formula.items():
            formula_items.append({
                "name": name,
                "ratio": ratio,
                "unit": "kg"  # Assuming the unit is kg
            })

        # Update UI
        self.formula_tab.update_mix_formula_table(formula_items)

    def update_feed_inventory_table(self):
        """Update the feed inventory table with current inventory data"""
        # Get inventory from inventory manager
        inventory = self.inventory_manager.get_inventory()

        # Convert to the format expected by the inventory tab
        inventory_items = []
        for name, amount in inventory.items():
            # For now, we'll consider all items as feed items
            # In a real implementation, you would filter based on some criteria
            inventory_items.append({
                "name": name,
                "amount": amount,
                "unit": "kg"  # Assuming the unit is kg
            })

        # Update UI
        self.inventory_tab.update_feed_inventory_table(inventory_items)

        # Update import tab feed combo
        self.import_tab.update_feed_combo(inventory_items)

    def update_mix_inventory_table(self):
        """Update the mix inventory table with current inventory data"""
        # Get inventory from inventory manager
        inventory = self.inventory_manager.get_inventory()

        # Convert to the format expected by the inventory tab
        inventory_items = []
        for name, amount in inventory.items():
            # For now, we'll consider all items as mix items
            # In a real implementation, you would filter based on some criteria
            inventory_items.append({
                "name": name,
                "amount": amount,
                "unit": "kg"  # Assuming the unit is kg
            })

        # Update UI
        self.inventory_tab.update_mix_inventory_table(inventory_items)

        # Update import tab mix combo
        self.import_tab.update_mix_combo(inventory_items)

    def update_feed_preset_combo(self):
        """Update feed preset combo box"""
        feed_presets = self.formula_manager.get_feed_presets()

        # Cập nhật combo box trong formula_tab
        if hasattr(self, 'formula_tab') and hasattr(self.formula_tab, 'feed_preset_combo'):
            self.formula_tab.feed_preset_combo.clear()
            self.formula_tab.feed_preset_combo.addItem("Chọn công thức...")
            for preset in feed_presets:
                self.formula_tab.feed_preset_combo.addItem(preset)

        # Cập nhật combo box công thức mặc định trong feed_usage_tab
        if hasattr(self, 'feed_usage_tab') and hasattr(self.feed_usage_tab, 'default_formula_combo'):
            current_text = self.feed_usage_tab.default_formula_combo.currentText()
            self.feed_usage_tab.default_formula_combo.clear()

            # Thêm tùy chọn trống
            self.feed_usage_tab.default_formula_combo.addItem("")

            # Thêm các công thức
            for preset in feed_presets:
                self.feed_usage_tab.default_formula_combo.addItem(preset)

            # Khôi phục lựa chọn trước đó nếu có thể
            if current_text:
                index = self.feed_usage_tab.default_formula_combo.findText(current_text)
                if index >= 0:
                    self.feed_usage_tab.default_formula_combo.setCurrentIndex(index)

        # Cập nhật tất cả combo box công thức trong bảng
        if hasattr(self, 'feed_usage_tab') and hasattr(self.feed_usage_tab, 'update_formula_combos'):
            self.feed_usage_tab.update_formula_combos(feed_presets)

    def update_mix_preset_combo(self):
        """Update the mix preset combo box with available presets"""
        # Get mix presets from formula manager
        presets = self.formula_manager.get_mix_presets()

        # Update UI
        self.formula_tab.update_mix_preset_combo(presets)

    def save_feed_formula(self):
        """Save the current feed formula"""
        # Get formula name from UI
        name = self.formula_tab.feed_formula_name_edit.text()

        # Check if name is provided
        if not name:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên công thức")
            return

        # Get formula items from UI
        items = []
        for row in range(self.formula_tab.feed_formula_table.rowCount()):
            name_item = self.formula_tab.feed_formula_table.item(row, 0)
            ratio_widget = self.formula_tab.feed_formula_table.cellWidget(row, 1)
            unit_item = self.formula_tab.feed_formula_table.item(row, 2)

            if name_item and ratio_widget and unit_item:
                items.append({
                    "name": name_item.text(),
                    "ratio": ratio_widget.value(),
                    "unit": unit_item.text()
                })

        # Save formula using formula manager
        self.formula_manager.save_feed_formula(name, items)

        # Update UI
        self.update_feed_preset_combo()
        self.update_feed_formula_table()

        # Show success message
        QMessageBox.information(self, "Thành công", f"Đã lưu công thức '{name}'")

    def save_mix_formula(self):
        """Save the current mix formula"""
        # Get formula name from UI
        name = self.formula_tab.mix_formula_name_edit.text()

        # Check if name is provided
        if not name:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên công thức")
            return

        # Get formula items from UI
        items = []
        for row in range(self.formula_tab.mix_formula_table.rowCount()):
            name_item = self.formula_tab.mix_formula_table.item(row, 0)
            ratio_widget = self.formula_tab.mix_formula_table.cellWidget(row, 1)
            unit_item = self.formula_tab.mix_formula_table.item(row, 2)

            if name_item and ratio_widget and unit_item:
                items.append({
                    "name": name_item.text(),
                    "ratio": ratio_widget.value(),
                    "unit": unit_item.text()
                })

        # Save formula using formula manager
        self.formula_manager.save_mix_formula(name, items)

        # Update UI
        self.update_mix_preset_combo()
        self.update_mix_formula_table()

        # Show success message
        QMessageBox.information(self, "Thành công", f"Đã lưu công thức '{name}'")

    def load_feed_preset(self):
        """Load the selected feed preset"""
        # Get selected preset name from UI
        preset_name = self.formula_tab.feed_preset_combo.currentText()

        # Check if a preset is selected
        if not preset_name:
            return

        # Load preset using formula manager
        preset_data = self.formula_manager.load_feed_preset(preset_name)

        # Check if preset exists
        if not preset_data:
            QMessageBox.warning(self, "Lỗi", f"Không tìm thấy công thức '{preset_name}'")
            return

        # Update UI
        self.formula_tab.feed_formula_name_edit.setText(preset_name)

        # Convert to the format expected by the formula tab
        formula_items = []
        for name, ratio in preset_data.items():
            formula_items.append({
                "name": name,
                "ratio": ratio,
                "unit": "kg"  # Assuming the unit is kg
            })

        self.formula_tab.update_feed_formula_table(formula_items)

    def load_mix_preset(self):
        """Load the selected mix preset"""
        # Get selected preset name from UI
        preset_name = self.formula_tab.mix_preset_combo.currentText()

        # Check if a preset is selected
        if not preset_name:
            return

        # Load preset using formula manager
        preset_data = self.formula_manager.load_mix_preset(preset_name)

        # Check if preset exists
        if not preset_data:
            QMessageBox.warning(self, "Lỗi", f"Không tìm thấy công thức '{preset_name}'")
            return

        # Update UI
        self.formula_tab.mix_formula_name_edit.setText(preset_name)

        # Convert to the format expected by the formula tab
        formula_items = []
        for name, ratio in preset_data.items():
            formula_items.append({
                "name": name,
                "ratio": ratio,
                "unit": "kg"  # Assuming the unit is kg
            })

        self.formula_tab.update_mix_formula_table(formula_items)

    def save_as_feed_preset(self):
        """Save the current feed formula as a new preset"""
        # Get formula name from UI
        name = self.formula_tab.feed_formula_name_edit.text()

        # Check if name is provided
        if not name:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên công thức")
            return

        # Get formula items from UI
        items = []
        for row in range(self.formula_tab.feed_formula_table.rowCount()):
            name_item = self.formula_tab.feed_formula_table.item(row, 0)
            ratio_widget = self.formula_tab.feed_formula_table.cellWidget(row, 1)
            unit_item = self.formula_tab.feed_formula_table.item(row, 2)

            if name_item and ratio_widget and unit_item:
                items.append({
                    "name": name_item.text(),
                    "ratio": ratio_widget.value(),
                    "unit": unit_item.text()
                })

        # Save preset using formula manager
        self.formula_manager.save_feed_preset(name, items)

        # Update UI
        self.update_feed_preset_combo()

        # Show success message
        QMessageBox.information(self, "Thành công", f"Đã lưu công thức '{name}' thành preset")

    def save_as_mix_preset(self):
        """Save the current mix formula as a new preset"""
        # Get formula name from UI
        name = self.formula_tab.mix_formula_name_edit.text()

        # Check if name is provided
        if not name:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên công thức")
            return

        # Get formula items from UI
        items = []
        for row in range(self.formula_tab.mix_formula_table.rowCount()):
            name_item = self.formula_tab.mix_formula_table.item(row, 0)
            ratio_widget = self.formula_tab.mix_formula_table.cellWidget(row, 1)
            unit_item = self.formula_tab.mix_formula_table.item(row, 2)

            if name_item and ratio_widget and unit_item:
                items.append({
                    "name": name_item.text(),
                    "ratio": ratio_widget.value(),
                    "unit": unit_item.text()
                })

        # Save preset using formula manager
        self.formula_manager.save_mix_preset(name, items)

        # Update UI
        self.update_mix_preset_combo()

        # Show success message
        QMessageBox.information(self, "Thành công", f"Đã lưu công thức '{name}' thành preset")

    def delete_feed_preset(self):
        """Delete the selected feed preset"""
        # Get selected preset name from UI
        preset_name = self.formula_tab.feed_preset_combo.currentText()

        # Check if a preset is selected
        if not preset_name:
            return

        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Xác nhận xóa",
            f"Bạn có chắc chắn muốn xóa công thức '{preset_name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Delete preset using formula manager
            self.formula_manager.delete_feed_preset(preset_name)

            # Update UI
            self.update_feed_preset_combo()

    def delete_mix_preset(self):
        """Delete the selected mix preset"""
        # Get selected preset name from UI
        preset_name = self.formula_tab.mix_preset_combo.currentText()

        # Check if a preset is selected
        if not preset_name:
            return

        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Xác nhận xóa",
            f"Bạn có chắc chắn muốn xóa công thức '{preset_name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Delete preset using formula manager
            self.formula_manager.delete_mix_preset(preset_name)

            # Update UI
            self.update_mix_preset_combo()

    def update_history_dates(self, combo_box=None):
        """Update history date combo boxes with available dates"""
        # Get available dates from history service
        dates = self.history_service.get_available_dates()

        # Update UI
        self.history_tab.update_date_combos(dates)

    def fill_table_by_date(self):
        """Fill history tables based on selected date"""
        # Check which date source is selected
        if self.history_tab.date_radio.isChecked():
            # Use date from combo box
            date_text = self.history_tab.date_combo.currentText()
            if not date_text:
                return
        else:
            # Use date from date edit
            date = self.history_tab.date_edit.date()
            date_text = date.toString("yyyy-MM-dd")

        # Load history data for selected date
        history_data = self.history_service.load_history_data(date_text)

        # Update UI
        self.history_tab.update_usage_table(history_data["usage"])
        self.history_tab.update_feed_table(history_data["feed"])
        self.history_tab.update_mix_table(history_data["mix"])

    def compare_history_data(self):
        """Compare history data between two dates"""
        # Get current date
        if self.history_tab.date_radio.isChecked():
            # Use date from combo box
            current_date = self.history_tab.date_combo.currentText()
        else:
            # Use date from date edit
            date = self.history_tab.date_edit.date()
            current_date = date.toString("yyyy-MM-dd")

        # Get compare date
        compare_date = self.history_tab.compare_date_combo.currentText()

        # Check if comparison is enabled
        if not compare_date or compare_date == "Không so sánh":
            # Just load current date data without comparison
            self.fill_table_by_date()
            return

        # Load data for both dates
        current_data, compare_data = self.history_service.compare_history_data(current_date, compare_date)

        # Update UI with comparison
        self.history_tab.update_usage_table(current_data["usage"], compare_data["usage"])
        self.history_tab.update_feed_table(current_data["feed"], compare_data["feed"])
        self.history_tab.update_mix_table(current_data["mix"], compare_data["mix"])

    def export_history_to_excel(self):
        """Export history data to Excel"""
        # Get current date for filename
        if self.history_tab.date_radio.isChecked():
            # Use date from combo box
            date_text = self.history_tab.date_combo.currentText()
        else:
            # Use date from date edit
            date = self.history_tab.date_edit.date()
            date_text = date.toString("yyyy-MM-dd")

        # Get save file path
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Lưu file Excel",
            f"Lịch sử {date_text}.xlsx",
            "Excel Files (*.xlsx)"
        )

        if not filename:
            return

        # Load history data
        history_data = self.history_service.load_history_data(date_text)

        # Export to Excel using export service
        self.export_service.export_history_to_excel(history_data, filename)

        # Show success message
        QMessageBox.information(self, "Thành công", f"Đã xuất dữ liệu ra file '{filename}'")

    def visualize_history_data(self):
        """Visualize history data"""
        # Get current date
        if self.history_tab.date_radio.isChecked():
            # Use date from combo box
            date_text = self.history_tab.date_combo.currentText()
        else:
            # Use date from date edit
            date = self.history_tab.date_edit.date()
            date_text = date.toString("yyyy-MM-dd")

        # Load history data
        history_data = self.history_service.load_history_data(date_text)

        # Launch visualization tool
        # This would typically call a separate visualization module
        # For now, just show a message
        QMessageBox.information(self, "Biểu đồ", "Chức năng biểu đồ đang được phát triển")

    def save_report(self):
        """Save the current report"""
        # Get current date
        date = datetime.now().strftime("%Y-%m-%d")

        # Create report data
        report_data = {
            "date": date,
            "usage": [],  # This would be populated with usage data
            "inventory": self.inventory_manager.get_inventory()
        }

        # Save report using report manager
        filepath = self.report_manager.save_report(report_data)

        # Show success message
        QMessageBox.information(self, "Thành công", f"Đã lưu báo cáo vào '{filepath}'")

        # Update history dates
        self.update_history_dates()

        # Update status
        self.update_status(f"Đã lưu báo cáo ngày {date}")

    def export_to_excel(self):
        """Export the current data to Excel"""
        # Get save file path
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Lưu file Excel",
            f"Báo cáo {datetime.now().strftime('%Y-%m-%d')}.xlsx",
            "Excel Files (*.xlsx)"
        )

        if not filename:
            return

        # Create data to export
        export_data = {
            "inventory": self.inventory_manager.get_inventory(),
            "formulas": {
                "feed": self.formula_manager.get_feed_formula(),
                "mix": self.formula_manager.get_mix_formula()
            }
        }

        # Export to Excel using export service
        self.export_service.export_to_excel(export_data, filename)

        # Show success message
        QMessageBox.information(self, "Thành công", f"Đã xuất dữ liệu ra file '{filename}'")

        # Update status
        self.update_status(f"Đã xuất dữ liệu ra file Excel: {filename}")

    def load_default_formula(self):
        """Tải công thức mặc định khi khởi động app"""
        if self.default_formula_loaded:
            return

        try:
            # Tải công thức mặc định từ cài đặt
            default_formula = self.formula_manager.get_default_feed_formula()
            print(f"Tải công thức cám mặc định: {default_formula}")

            # Kiểm tra xem default_formula_combo đã được tạo chưa
            if hasattr(self.feed_usage_tab, 'default_formula_combo'):
                # Cập nhật danh sách công thức trong combo box
                self.update_feed_preset_combo()

                # Kiểm tra xem công thức mặc định có tồn tại trong danh sách không
                found = False
                for i in range(self.feed_usage_tab.default_formula_combo.count()):
                    if self.feed_usage_tab.default_formula_combo.itemText(i) == default_formula:
                        found = True
                        break

                # Chỉ thiết lập khi có công thức mặc định và công thức tồn tại trong danh sách
                if default_formula and found:
                    self.feed_usage_tab.default_formula_combo.setCurrentText(default_formula)
                    print(f"Đã thiết lập công thức cám mặc định: {default_formula}")

                    # Tự động áp dụng công thức mặc định cho tất cả các ô
                    self.feed_usage_tab.apply_default_formula()
                elif default_formula:
                    print(f"Công thức cám mặc định '{default_formula}' không tồn tại trong danh sách")
                    QMessageBox.warning(self, "Cảnh báo",
                                      f"Công thức cám mặc định '{default_formula}' không tồn tại trong danh sách.\n"
                                      "Vui lòng chọn công thức mặc định khác.")
            else:
                print("default_formula_combo chưa được tạo")

            # Tải công thức mix theo cột
            if hasattr(self.formula_manager, 'column_mix_formulas'):
                print(f"Đã tải {len(self.formula_manager.column_mix_formulas)} công thức mix theo cột")

        except Exception as e:
            print(f"Lỗi khi tải công thức mặc định: {e}")
            import traceback
            traceback.print_exc()

        self.default_formula_loaded = True

    def on_feed_table_cell_clicked(self, row, column):
        """Handle feed table cell click"""
        # Lấy thông tin về cell được nhấp
        cell_key = f"{row}_{column}"

        # Hiển thị thông tin về cell trong thanh trạng thái
        spin_box = self.feed_usage_tab.feed_spinboxes.get(cell_key)
        formula_combo = self.feed_usage_tab.formula_combos.get(cell_key)

        if spin_box and formula_combo:
            value = spin_box.value()
            formula = formula_combo.currentText()

            if value > 0 and formula:
                self.update_status(f"Khu {column+1}, {SHIFTS[row]}: {value} ({formula})")
            else:
                self.update_status(f"Đã chọn Khu {column+1}, {SHIFTS[row]}")

    def show_cell_context_menu(self, row, column):
        """Show context menu for feed table cell"""
        # Nếu không có hàng hoặc cột hợp lệ, thoát
        if row < 0 or column < 0:
            return

        # Lấy thông tin về cell được nhấp
        cell_key = f"{row}_{column}"

        # Tạo menu ngữ cảnh
        context_menu = QMenu(self)

        # Thêm các hành động vào menu
        # Hành động reset cell
        reset_action = QAction("Reset ô này", self)
        reset_action.triggered.connect(lambda: self.reset_cell(cell_key))
        context_menu.addAction(reset_action)

        # Hành động áp dụng công thức
        apply_formula_menu = QMenu("Áp dụng công thức", self)

        # Lấy danh sách công thức từ formula_manager
        feed_formulas = self.formula_manager.get_feed_presets()

        # Thêm các công thức vào menu
        for formula in feed_formulas:
            formula_action = QAction(formula, self)
            formula_action.triggered.connect(lambda checked, f=formula: self.apply_formula_to_cell(cell_key, f))
            apply_formula_menu.addAction(formula_action)

        context_menu.addMenu(apply_formula_menu)

        # Hiển thị menu tại vị trí con trỏ
        context_menu.exec_(QCursor.pos())

    def reset_cell(self, cell_key):
        """Reset a cell to default values"""
        spin_box = self.feed_usage_tab.feed_spinboxes.get(cell_key)
        formula_combo = self.feed_usage_tab.formula_combos.get(cell_key)

        if spin_box:
            spin_box.setValue(0)

        if formula_combo:
            formula_combo.setCurrentIndex(0)

        # Cập nhật trạng thái
        row, column = map(int, cell_key.split("_"))
        self.update_status(f"Đã reset ô Khu {column+1}, {SHIFTS[row]}")

    def apply_formula_to_cell(self, cell_key, formula):
        """Apply a formula to a cell"""
        formula_combo = self.feed_usage_tab.formula_combos.get(cell_key)

        if formula_combo:
            # Tìm và chọn công thức trong combo box
            index = formula_combo.findText(formula)
            if index >= 0:
                formula_combo.setCurrentIndex(index)

                # Cập nhật trạng thái
                row, column = map(int, cell_key.split("_"))
                self.update_status(f"Đã áp dụng công thức '{formula}' cho ô Khu {column+1}, {SHIFTS[row]}")

    def auto_select_default_formula(self, value, combo):
        """Auto-select default formula based on value"""
        # Nếu giá trị > 0 và không có công thức nào được chọn, tự động chọn công thức mặc định
        if value > 0 and combo.currentText() == "":
            # Lấy công thức mặc định từ formula_manager
            default_formula = self.formula_manager.get_default_feed_formula()

            # Nếu có công thức mặc định, tìm và chọn nó trong combo box
            if default_formula:
                index = combo.findText(default_formula)
                if index >= 0:
                    combo.setCurrentIndex(index)
                    # Cập nhật trạng thái
                    self.update_status(f"Đã tự động chọn công thức mặc định: {default_formula}")

    def assign_mix_formulas_to_areas(self):
        """Hiển thị dialog cho người dùng chọn công thức mix cho từng khu/trại"""
        # Tạo dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Chọn công thức Mix mặc định theo khu")
        dialog.setMinimumWidth(700)
        dialog.setMinimumHeight(600)

        # Tạo layout
        main_layout = QVBoxLayout()

        # Thêm label hướng dẫn
        header_label = QLabel("Chọn công thức Mix mặc định cho từng khu và trại:")
        header_label.setFont(self.header_font)
        main_layout.addWidget(header_label)

        # Tạo scroll area để có thể cuộn khi có nhiều khu
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # Tạo dictionary để lưu các combo box
        combo_boxes = {}

        # Lấy danh sách các công thức mix
        mix_presets = self.formula_manager.get_mix_presets()

        # Lấy dữ liệu công thức mix theo cột đã lưu
        column_mix_formulas = {}
        if hasattr(self.formula_manager, 'column_mix_formulas'):
            column_mix_formulas = self.formula_manager.column_mix_formulas

        # Tạo các phần chọn công thức theo khu
        col_index = 0
        for khu_idx, farms in FARMS.items():
            khu_name = f"Khu {khu_idx + 1}"

            # Tạo section cho khu
            khu_group = QGroupBox(khu_name)
            khu_group.setFont(QFont("Arial", DEFAULT_FONT_SIZE, QFont.Bold))
            khu_layout = QVBoxLayout(khu_group)

            for farm_idx, farm_name in enumerate(farms):
                # Tạo layout ngang cho mỗi trại
                farm_layout = QHBoxLayout()

                # Tạo label cho trại
                farm_label = QLabel(f"{farm_name}:")
                farm_label.setFont(QFont("Arial", DEFAULT_FONT_SIZE - 1))
                farm_label.setMinimumWidth(150)
                farm_layout.addWidget(farm_label)

                # Tạo combo box cho trại
                combo = QComboBox()
                combo.setFont(QFont("Arial", DEFAULT_FONT_SIZE - 1))
                combo.setMinimumHeight(30)

                # Thêm tùy chọn "Không có công thức"
                combo.addItem("Không có công thức", "")

                # Thêm các công thức mix
                for preset in mix_presets:
                    combo.addItem(preset, preset)

                # Thêm vào layout
                farm_layout.addWidget(combo)

                # Lưu combo box
                col_key = f"{col_index}"
                combo_boxes[col_key] = combo

                # Cài đặt giá trị mặc định nếu đã có
                if col_key in column_mix_formulas:
                    preset = column_mix_formulas[col_key]
                    index = combo.findText(preset)
                    if index >= 0:
                        combo.setCurrentIndex(index)
                        print(f"Đã tải công thức mix cho {khu_name}, {farm_name}: {preset}")

                # Thêm layout trại vào layout khu
                khu_layout.addLayout(farm_layout)

                col_index += 1

            # Thêm section khu vào scroll area
            scroll_layout.addWidget(khu_group)

        # Thêm nút áp dụng cho tất cả các khu
        apply_all_layout = QHBoxLayout()
        apply_all_label = QLabel("Áp dụng một công thức cho tất cả:")
        apply_all_label.setFont(QFont("Arial", DEFAULT_FONT_SIZE, QFont.Bold))
        apply_all_layout.addWidget(apply_all_label)

        apply_all_combo = QComboBox()
        apply_all_combo.setFont(QFont("Arial", DEFAULT_FONT_SIZE))
        apply_all_combo.setMinimumHeight(30)
        apply_all_combo.addItem("Chọn công thức...", "")
        for preset in mix_presets:
            apply_all_combo.addItem(preset, preset)
        apply_all_layout.addWidget(apply_all_combo)

        apply_all_button = QPushButton("Áp dụng cho tất cả")
        apply_all_button.setFont(QFont("Arial", DEFAULT_FONT_SIZE))
        apply_all_button.setMinimumHeight(30)
        apply_all_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        apply_all_button.clicked.connect(lambda: self.apply_mix_formula_to_all_areas(apply_all_combo.currentData(), combo_boxes))
        apply_all_layout.addWidget(apply_all_button)

        scroll_layout.addLayout(apply_all_layout)

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
        """Lưu các lựa chọn công thức mix cho từng khu/trại"""
        # Khởi tạo hoặc lấy cấu trúc dữ liệu hiện có
        column_mix_formulas = {}

        # Lưu công thức mix cho từng cột
        for col_key, combo in combo_boxes.items():
            mix_formula_name = combo.currentData()
            if mix_formula_name:
                column_mix_formulas[col_key] = mix_formula_name

        # Lưu cài đặt công thức mix theo cột vào file cấu hình
        self.formula_manager.save_column_mix_formulas(column_mix_formulas)

        dialog.accept()

        # Hiển thị thông tin về công thức mix đã chọn
        if column_mix_formulas:
            mix_info = "Đã lưu công thức Mix cho các khu/trại:\n"
            count = 0
            for col, formula in column_mix_formulas.items():
                col_index = int(col)
                # Lấy thông tin khu và trại
                khu_item = self.feed_usage_tab.feed_table.item(0, col_index)
                farm_item = self.feed_usage_tab.feed_table.item(1, col_index)
                if khu_item and farm_item:
                    khu_name = khu_item.text()
                    farm_name = farm_item.text()
                    mix_info += f"- {khu_name}, {farm_name}: {formula}\n"
                    count += 1
                    if count >= 10:
                        mix_info += f"... và {len(column_mix_formulas) - 10} trại khác\n"
                        break
            QMessageBox.information(self, "Thông tin công thức Mix", mix_info)

    def apply_mix_formula_to_all_areas(self, mix_formula, combo_boxes):
        """Áp dụng một công thức mix cho tất cả các khu/trại"""
        if not mix_formula or mix_formula == "Chọn công thức...":
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một công thức mix để áp dụng.")
            return

        # Kiểm tra xác nhận
        reply = QMessageBox.question(
            self,
            "Xác nhận",
            f"Bạn có chắc chắn muốn áp dụng công thức mix '{mix_formula}' cho TẤT CẢ các khu/trại không?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Áp dụng công thức cho tất cả các combo box
            for combo in combo_boxes.values():
                index = combo.findText(mix_formula)
                if index >= 0:
                    combo.setCurrentIndex(index)

            QMessageBox.information(self, "Thành công", f"Đã áp dụng công thức mix '{mix_formula}' cho tất cả các khu/trại.")