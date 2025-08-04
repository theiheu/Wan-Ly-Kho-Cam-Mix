#!/usr/bin/env python3
"""
Comprehensive Report Dialog - Dialog báo cáo toàn diện
Giao diện cho phép người dùng chọn các loại báo cáo và xuất Excel
"""

import os
import sys
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
                            QLabel, QPushButton, QCheckBox, QDateEdit, QComboBox,
                            QGroupBox, QProgressBar, QTextEdit, QTabWidget, QWidget,
                            QMessageBox, QFileDialog, QFrame, QScrollArea, QSizePolicy)
from PyQt5.QtCore import Qt, QDate, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPixmap, QIcon

# Import services
try:
    from src.services.comprehensive_report_service import ComprehensiveReportService
    from src.services.excel_export_service import ExcelExportService
    from src.utils.user_preferences import user_preferences_manager
except ImportError:
    from services.comprehensive_report_service import ComprehensiveReportService
    from services.excel_export_service import ExcelExportService
    from utils.user_preferences import user_preferences_manager

class ReportGenerationWorker(QThread):
    """Worker thread để tạo báo cáo không chặn UI"""

    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    report_completed = pyqtSignal(bool, str, dict)

    def __init__(self, report_options):
        super().__init__()
        self.report_options = report_options
        self.report_service = ComprehensiveReportService()
        self.excel_service = ExcelExportService()

    def run(self):
        """Chạy quá trình tạo báo cáo"""
        try:
            self.status_updated.emit("Đang khởi tạo dịch vụ báo cáo...")
            self.progress_updated.emit(10)

            # Tạo báo cáo toàn diện
            self.status_updated.emit("Đang thu thập dữ liệu...")
            self.progress_updated.emit(30)

            report_data = self.report_service.generate_comprehensive_report(
                include_inventory=self.report_options.get('include_inventory', True),
                include_employees=self.report_options.get('include_employees', True),
                include_production=self.report_options.get('include_production', True),
                include_bonuses=self.report_options.get('include_bonuses', True),
                include_formulas=self.report_options.get('include_formulas', True),
                include_imports=self.report_options.get('include_imports', True),
                start_date=self.report_options.get('start_date'),
                end_date=self.report_options.get('end_date')
            )

            self.progress_updated.emit(70)

            # Xuất Excel nếu được yêu cầu
            if self.report_options.get('export_excel', True):
                self.status_updated.emit("Đang xuất file Excel...")
                self.progress_updated.emit(80)

                filename = self.report_options.get('filename')
                custom_export_dir = self.report_options.get('custom_export_dir')
                success, message = self.excel_service.export_comprehensive_report(
                    report_data,
                    filename,
                    custom_export_dir
                )

                if not success:
                    self.report_completed.emit(False, message, {})
                    return

            self.progress_updated.emit(100)
            self.status_updated.emit("Hoàn thành!")

            success_message = "Báo cáo toàn diện đã được tạo thành công!"
            if self.report_options.get('export_excel', True):
                success_message += f"\nFile Excel đã được lưu tại: {self.excel_service.exports_dir}"

            self.report_completed.emit(True, success_message, report_data)

        except Exception as e:
            self.report_completed.emit(False, f"Lỗi khi tạo báo cáo: {str(e)}", {})

class ComprehensiveReportDialog(QDialog):
    """Dialog báo cáo toàn diện với nhiều tùy chọn"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = parent
        self.worker_thread = None

        # Thiết lập dialog
        self.setWindowTitle("Báo Cáo Toàn Diện - Xuất Excel")
        self.setModal(True)
        self.resize(700, 600)

        # Khởi tạo biến export folder
        self.export_folder = None

        # Khởi tạo UI
        self.init_ui()

        # Thiết lập giá trị mặc định và tải cài đặt đã lưu
        self.setup_default_values()
        self.load_user_preferences()

    def init_ui(self):
        """Khởi tạo giao diện"""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        self.create_header(layout)

        # Tab widget cho các tùy chọn
        self.create_tabs(layout)

        # Progress section
        self.create_progress_section(layout)

        # Buttons
        self.create_buttons_section(layout)

        self.setLayout(layout)

    def create_header(self, layout):
        """Tạo header với tiêu đề và mô tả"""
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #E3F2FD;
                border: 2px solid #2196F3;
                border-radius: 10px;
                padding: 10px;
            }
        """)

        header_layout = QVBoxLayout(header_frame)

        # Tiêu đề chính
        title_label = QLabel("📊 BÁO CÁO TOÀN DIỆN HỆ THỐNG")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #1976D2; background: transparent; border: none;")
        header_layout.addWidget(title_label)

        # Mô tả
        desc_label = QLabel("Tạo báo cáo chi tiết từ tất cả dữ liệu trong hệ thống và xuất ra file Excel")
        desc_label.setFont(QFont("Arial", 11))
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet("color: #424242; background: transparent; border: none;")
        header_layout.addWidget(desc_label)

        layout.addWidget(header_frame)

    def create_tabs(self, layout):
        """Tạo tab widget cho các tùy chọn"""
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
            }
            QTabBar::tab {
                background: #f0f0f0;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: #2196F3;
                color: white;
            }
        """)

        # Tab 1: Chọn loại báo cáo
        self.create_report_types_tab()

        # Tab 2: Khoảng thời gian
        self.create_date_range_tab()

        # Tab 3: Tùy chọn xuất
        self.create_export_options_tab()

        layout.addWidget(self.tab_widget)

    def create_report_types_tab(self):
        """Tạo tab chọn loại báo cáo"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Nhóm chọn loại báo cáo
        report_group = QGroupBox("Chọn Loại Báo Cáo")
        report_group.setFont(QFont("Arial", 12, QFont.Bold))
        report_layout = QGridLayout(report_group)

        # Các checkbox cho từng loại báo cáo
        self.inventory_cb = QCheckBox("📦 Báo cáo Tồn Kho")
        self.inventory_cb.setToolTip("Bao gồm thông tin tồn kho cám, mix và cảnh báo")
        self.inventory_cb.setChecked(True)
        report_layout.addWidget(self.inventory_cb, 0, 0)

        self.employees_cb = QCheckBox("👥 Báo cáo Nhân Viên")
        self.employees_cb.setToolTip("Bao gồm danh sách nhân viên và thống kê chấm công")
        self.employees_cb.setChecked(True)
        report_layout.addWidget(self.employees_cb, 0, 1)

        self.production_cb = QCheckBox("🏭 Báo cáo Sản Xuất")
        self.production_cb.setToolTip("Bao gồm dữ liệu sử dụng cám và mix hàng ngày")
        self.production_cb.setChecked(True)
        report_layout.addWidget(self.production_cb, 1, 0)

        self.bonuses_cb = QCheckBox("💰 Báo cáo Thưởng")
        self.bonuses_cb.setToolTip("Bao gồm thông tin tính thưởng theo tháng")
        self.bonuses_cb.setChecked(True)
        report_layout.addWidget(self.bonuses_cb, 1, 1)

        self.formulas_cb = QCheckBox("🧪 Báo cáo Công Thức")
        self.formulas_cb.setToolTip("Bao gồm công thức cám và mix")
        self.formulas_cb.setChecked(True)
        report_layout.addWidget(self.formulas_cb, 2, 0)

        self.imports_cb = QCheckBox("📥 Báo cáo Nhập Kho")
        self.imports_cb.setToolTip("Bao gồm lịch sử nhập kho")
        self.imports_cb.setChecked(True)
        report_layout.addWidget(self.imports_cb, 2, 1)

        layout.addWidget(report_group)

        # Nút preset báo cáo
        preset_group = QGroupBox("Preset Báo Cáo")
        preset_group.setFont(QFont("Arial", 12, QFont.Bold))
        preset_layout = QGridLayout(preset_group)

        # Preset buttons
        inventory_preset_btn = QPushButton("📦 Chỉ Tồn Kho")
        inventory_preset_btn.setToolTip("Chỉ xuất báo cáo tồn kho và cảnh báo")
        inventory_preset_btn.clicked.connect(self.set_inventory_preset)
        preset_layout.addWidget(inventory_preset_btn, 0, 0)

        production_preset_btn = QPushButton("🏭 Sản Xuất")
        production_preset_btn.setToolTip("Xuất báo cáo sản xuất và công thức")
        production_preset_btn.clicked.connect(self.set_production_preset)
        preset_layout.addWidget(production_preset_btn, 0, 1)

        employee_preset_btn = QPushButton("👥 Nhân Viên")
        employee_preset_btn.setToolTip("Xuất báo cáo nhân viên và thưởng")
        employee_preset_btn.clicked.connect(self.set_employee_preset)
        preset_layout.addWidget(employee_preset_btn, 1, 0)

        complete_preset_btn = QPushButton("📋 Toàn Diện")
        complete_preset_btn.setToolTip("Xuất tất cả loại báo cáo")
        complete_preset_btn.clicked.connect(self.set_complete_preset)
        preset_layout.addWidget(complete_preset_btn, 1, 1)

        layout.addWidget(preset_group)

        # Nút chọn tất cả / bỏ chọn tất cả
        buttons_layout = QHBoxLayout()

        select_all_btn = QPushButton("Chọn Tất Cả")
        select_all_btn.clicked.connect(self.select_all_reports)
        buttons_layout.addWidget(select_all_btn)

        deselect_all_btn = QPushButton("Bỏ Chọn Tất Cả")
        deselect_all_btn.clicked.connect(self.deselect_all_reports)
        buttons_layout.addWidget(deselect_all_btn)

        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

        layout.addStretch()
        self.tab_widget.addTab(tab, "📋 Loại Báo Cáo")

    def create_date_range_tab(self):
        """Tạo tab chọn khoảng thời gian"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Nhóm khoảng thời gian
        date_group = QGroupBox("Khoảng Thời Gian")
        date_group.setFont(QFont("Arial", 12, QFont.Bold))
        date_layout = QGridLayout(date_group)

        # Checkbox để bật/tắt lọc theo ngày
        self.use_date_filter_cb = QCheckBox("Lọc theo khoảng thời gian")
        self.use_date_filter_cb.setChecked(False)
        self.use_date_filter_cb.toggled.connect(self.toggle_date_filter)
        date_layout.addWidget(self.use_date_filter_cb, 0, 0, 1, 2)

        # Ngày bắt đầu
        date_layout.addWidget(QLabel("Từ ngày:"), 1, 0)
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDate(QDate.currentDate().addDays(-30))
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setEnabled(False)
        date_layout.addWidget(self.start_date_edit, 1, 1)

        # Ngày kết thúc
        date_layout.addWidget(QLabel("Đến ngày:"), 2, 0)
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setEnabled(False)
        date_layout.addWidget(self.end_date_edit, 2, 1)

        layout.addWidget(date_group)

        # Các preset thời gian
        preset_group = QGroupBox("Preset Thời Gian")
        preset_group.setFont(QFont("Arial", 12, QFont.Bold))
        preset_layout = QGridLayout(preset_group)

        # Nút preset
        last_7_days_btn = QPushButton("7 ngày qua")
        last_7_days_btn.clicked.connect(lambda: self.set_date_preset(7))
        preset_layout.addWidget(last_7_days_btn, 0, 0)

        last_30_days_btn = QPushButton("30 ngày qua")
        last_30_days_btn.clicked.connect(lambda: self.set_date_preset(30))
        preset_layout.addWidget(last_30_days_btn, 0, 1)

        last_90_days_btn = QPushButton("90 ngày qua")
        last_90_days_btn.clicked.connect(lambda: self.set_date_preset(90))
        preset_layout.addWidget(last_90_days_btn, 1, 0)

        this_month_btn = QPushButton("Tháng này")
        this_month_btn.clicked.connect(self.set_this_month)
        preset_layout.addWidget(this_month_btn, 1, 1)

        layout.addWidget(preset_group)
        layout.addStretch()

        self.tab_widget.addTab(tab, "📅 Thời Gian")

    def create_export_options_tab(self):
        """Tạo tab tùy chọn xuất"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Nhóm tùy chọn xuất
        export_group = QGroupBox("Tùy Chọn Xuất File")
        export_group.setFont(QFont("Arial", 12, QFont.Bold))
        export_layout = QGridLayout(export_group)

        # Checkbox xuất Excel
        self.export_excel_cb = QCheckBox("Xuất file Excel (.xlsx)")
        self.export_excel_cb.setChecked(True)
        self.export_excel_cb.setToolTip("Tạo file Excel với nhiều worksheet")
        export_layout.addWidget(self.export_excel_cb, 0, 0, 1, 2)

        # Tên file
        export_layout.addWidget(QLabel("Tên file:"), 1, 0)
        self.filename_edit = QComboBox()
        self.filename_edit.setEditable(True)
        self.filename_edit.addItems([
            f"BaoCao_ToanDien_{datetime.now().strftime('%Y%m%d')}",
            f"BaoCao_KhoHang_{datetime.now().strftime('%Y%m%d')}",
            f"BaoCao_SanXuat_{datetime.now().strftime('%Y%m%d')}"
        ])
        export_layout.addWidget(self.filename_edit, 1, 1)

        # Nút chọn thư mục và reset
        folder_buttons_layout = QHBoxLayout()

        self.folder_btn = QPushButton("📁 Chọn Thư Mục Lưu")
        self.folder_btn.clicked.connect(self.choose_export_folder)
        folder_buttons_layout.addWidget(self.folder_btn)

        self.reset_folder_btn = QPushButton("🔄 Đặt Lại")
        self.reset_folder_btn.setToolTip("Đặt lại về thư mục mặc định")
        self.reset_folder_btn.clicked.connect(self.reset_export_folder)
        folder_buttons_layout.addWidget(self.reset_folder_btn)

        export_layout.addLayout(folder_buttons_layout, 2, 0, 1, 2)

        # Hiển thị thư mục hiện tại
        self.folder_label = QLabel("Thư mục: src/data/exports")
        self.folder_label.setStyleSheet("color: #666; font-style: italic;")
        self.folder_label.setWordWrap(True)  # Cho phép xuống dòng với đường dẫn dài
        export_layout.addWidget(self.folder_label, 3, 0, 1, 2)

        layout.addWidget(export_group)

        # Nhóm tùy chọn nâng cao
        advanced_group = QGroupBox("Tùy Chọn Nâng Cao")
        advanced_group.setFont(QFont("Arial", 12, QFont.Bold))
        advanced_layout = QVBoxLayout(advanced_group)

        self.open_after_export_cb = QCheckBox("Mở file sau khi xuất")
        self.open_after_export_cb.setChecked(True)
        advanced_layout.addWidget(self.open_after_export_cb)

        self.show_summary_cb = QCheckBox("Hiển thị tóm tắt báo cáo")
        self.show_summary_cb.setChecked(True)
        advanced_layout.addWidget(self.show_summary_cb)

        layout.addWidget(advanced_group)
        layout.addStretch()

        self.tab_widget.addTab(tab, "⚙️ Tùy Chọn")

    def create_progress_section(self, layout):
        """Tạo phần hiển thị tiến trình"""
        progress_group = QGroupBox("Tiến Trình")
        progress_group.setFont(QFont("Arial", 12, QFont.Bold))
        progress_layout = QVBoxLayout(progress_group)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel("Sẵn sàng tạo báo cáo")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        progress_layout.addWidget(self.status_label)

        layout.addWidget(progress_group)

    def create_buttons_section(self, layout):
        """Tạo phần nút bấm"""
        buttons_layout = QHBoxLayout()

        # Nút tạo báo cáo
        self.generate_btn = QPushButton("🚀 Tạo Báo Cáo")
        self.generate_btn.setFont(QFont("Arial", 12, QFont.Bold))
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.generate_btn.clicked.connect(self.generate_report)
        buttons_layout.addWidget(self.generate_btn)

        # Nút hủy
        cancel_btn = QPushButton("❌ Hủy")
        cancel_btn.setFont(QFont("Arial", 12))
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)

        layout.addLayout(buttons_layout)

    def setup_default_values(self):
        """Thiết lập giá trị mặc định"""
        # Thiết lập ngày mặc định
        self.start_date_edit.setDate(QDate.currentDate().addDays(-30))
        self.end_date_edit.setDate(QDate.currentDate())

    def load_user_preferences(self):
        """Tải cài đặt người dùng đã lưu"""
        try:
            # Tải đường dẫn xuất file đã lưu
            saved_export_path = user_preferences_manager.get_export_folder_path()
            if saved_export_path and os.path.exists(saved_export_path):
                self.export_folder = saved_export_path
                self.folder_label.setText(f"Thư mục: {saved_export_path}")
            else:
                # Sử dụng đường dẫn mặc định
                self.export_folder = None
                self.folder_label.setText("Thư mục: src/data/exports (mặc định)")

            # Tải các cài đặt khác
            self.open_after_export_cb.setChecked(user_preferences_manager.get_auto_open_after_export())
            self.show_summary_cb.setChecked(user_preferences_manager.get_show_report_summary())

            # Tải cài đặt lọc ngày
            if user_preferences_manager.get_default_date_filter():
                self.use_date_filter_cb.setChecked(True)
                self.toggle_date_filter(True)
                days = user_preferences_manager.get_default_date_range_days()
                self.set_date_preset(days)

        except Exception as e:
            print(f"Lỗi khi tải cài đặt người dùng: {e}")

    def save_user_preferences(self):
        """Lưu cài đặt người dùng hiện tại"""
        try:
            # Lưu đường dẫn xuất file
            if self.export_folder:
                user_preferences_manager.set_export_folder_path(self.export_folder)
            else:
                user_preferences_manager.reset_export_folder_path()

            # Lưu các cài đặt khác
            user_preferences_manager.set_auto_open_after_export(self.open_after_export_cb.isChecked())
            user_preferences_manager.set_show_report_summary(self.show_summary_cb.isChecked())
            user_preferences_manager.set_default_date_filter(self.use_date_filter_cb.isChecked())

            if self.use_date_filter_cb.isChecked():
                # Tính số ngày giữa start và end date
                start_date = self.start_date_edit.date()
                end_date = self.end_date_edit.date()
                days_diff = start_date.daysTo(end_date)
                if days_diff > 0:
                    user_preferences_manager.set_default_date_range_days(days_diff)

        except Exception as e:
            print(f"Lỗi khi lưu cài đặt người dùng: {e}")

    def select_all_reports(self):
        """Chọn tất cả loại báo cáo"""
        self.inventory_cb.setChecked(True)
        self.employees_cb.setChecked(True)
        self.production_cb.setChecked(True)
        self.bonuses_cb.setChecked(True)
        self.formulas_cb.setChecked(True)
        self.imports_cb.setChecked(True)

    def deselect_all_reports(self):
        """Bỏ chọn tất cả loại báo cáo"""
        self.inventory_cb.setChecked(False)
        self.employees_cb.setChecked(False)
        self.production_cb.setChecked(False)
        self.bonuses_cb.setChecked(False)
        self.formulas_cb.setChecked(False)
        self.imports_cb.setChecked(False)

    def set_inventory_preset(self):
        """Thiết lập preset báo cáo tồn kho"""
        self.deselect_all_reports()
        self.inventory_cb.setChecked(True)
        self.imports_cb.setChecked(True)  # Include imports for inventory tracking

        # Update filename
        self.filename_edit.setEditText(f"BaoCao_TonKho_{datetime.now().strftime('%Y%m%d')}")

    def set_production_preset(self):
        """Thiết lập preset báo cáo sản xuất"""
        self.deselect_all_reports()
        self.production_cb.setChecked(True)
        self.formulas_cb.setChecked(True)
        self.inventory_cb.setChecked(True)  # Include inventory for production planning

        # Update filename
        self.filename_edit.setEditText(f"BaoCao_SanXuat_{datetime.now().strftime('%Y%m%d')}")

        # Set date filter to last 30 days for production reports
        self.use_date_filter_cb.setChecked(True)
        self.toggle_date_filter(True)
        self.set_date_preset(30)

    def set_employee_preset(self):
        """Thiết lập preset báo cáo nhân viên"""
        self.deselect_all_reports()
        self.employees_cb.setChecked(True)
        self.bonuses_cb.setChecked(True)

        # Update filename
        self.filename_edit.setEditText(f"BaoCao_NhanVien_{datetime.now().strftime('%Y%m%d')}")

    def set_complete_preset(self):
        """Thiết lập preset báo cáo toàn diện"""
        self.select_all_reports()

        # Update filename
        self.filename_edit.setEditText(f"BaoCao_ToanDien_{datetime.now().strftime('%Y%m%d')}")

    def toggle_date_filter(self, enabled):
        """Bật/tắt lọc theo ngày"""
        self.start_date_edit.setEnabled(enabled)
        self.end_date_edit.setEnabled(enabled)

    def set_date_preset(self, days):
        """Thiết lập preset ngày"""
        self.use_date_filter_cb.setChecked(True)
        self.toggle_date_filter(True)
        self.start_date_edit.setDate(QDate.currentDate().addDays(-days))
        self.end_date_edit.setDate(QDate.currentDate())

    def set_this_month(self):
        """Thiết lập tháng hiện tại"""
        self.use_date_filter_cb.setChecked(True)
        self.toggle_date_filter(True)
        current_date = QDate.currentDate()
        first_day = QDate(current_date.year(), current_date.month(), 1)
        self.start_date_edit.setDate(first_day)
        self.end_date_edit.setDate(current_date)

    def choose_export_folder(self):
        """Chọn thư mục xuất file"""
        # Bắt đầu từ thư mục hiện tại hoặc thư mục mặc định
        start_dir = self.export_folder if self.export_folder else "src/data/exports"

        folder = QFileDialog.getExistingDirectory(
            self,
            "Chọn Thư Mục Lưu File",
            start_dir
        )

        if folder:
            self.export_folder = folder
            self.folder_label.setText(f"Thư mục: {folder}")

            # Lưu ngay vào cài đặt người dùng
            user_preferences_manager.set_export_folder_path(folder)
            print(f"Đã lưu đường dẫn xuất file: {folder}")

    def reset_export_folder(self):
        """Đặt lại thư mục xuất file về mặc định"""
        self.export_folder = None
        self.folder_label.setText("Thư mục: src/data/exports (mặc định)")

        # Xóa đường dẫn đã lưu
        user_preferences_manager.reset_export_folder_path()
        print("Đã đặt lại đường dẫn xuất file về mặc định")

    def generate_report(self):
        """Tạo báo cáo"""
        # Kiểm tra ít nhất một loại báo cáo được chọn
        if not any([
            self.inventory_cb.isChecked(),
            self.employees_cb.isChecked(),
            self.production_cb.isChecked(),
            self.bonuses_cb.isChecked(),
            self.formulas_cb.isChecked(),
            self.imports_cb.isChecked()
        ]):
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn ít nhất một loại báo cáo!")
            return

        # Chuẩn bị tùy chọn báo cáo
        report_options = {
            'include_inventory': self.inventory_cb.isChecked(),
            'include_employees': self.employees_cb.isChecked(),
            'include_production': self.production_cb.isChecked(),
            'include_bonuses': self.bonuses_cb.isChecked(),
            'include_formulas': self.formulas_cb.isChecked(),
            'include_imports': self.imports_cb.isChecked(),
            'export_excel': self.export_excel_cb.isChecked(),
            'filename': self.filename_edit.currentText(),
            'custom_export_dir': self.export_folder
        }

        # Thêm khoảng thời gian nếu được chọn
        if self.use_date_filter_cb.isChecked():
            start_date = self.start_date_edit.date().toString('yyyyMMdd')
            end_date = self.end_date_edit.date().toString('yyyyMMdd')
            report_options['start_date'] = start_date
            report_options['end_date'] = end_date

        # Bắt đầu tạo báo cáo
        self.start_report_generation(report_options)

    def start_report_generation(self, report_options):
        """Bắt đầu quá trình tạo báo cáo"""
        # Vô hiệu hóa nút tạo báo cáo
        self.generate_btn.setEnabled(False)
        self.generate_btn.setText("⏳ Đang Tạo...")

        # Hiển thị progress bar
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # Tạo và chạy worker thread
        self.worker_thread = ReportGenerationWorker(report_options)
        self.worker_thread.progress_updated.connect(self.progress_bar.setValue)
        self.worker_thread.status_updated.connect(self.status_label.setText)
        self.worker_thread.report_completed.connect(self.on_report_completed)
        self.worker_thread.start()

    def on_report_completed(self, success, message, report_data):
        """Xử lý khi báo cáo hoàn thành"""
        # Kích hoạt lại nút
        self.generate_btn.setEnabled(True)
        self.generate_btn.setText("🚀 Tạo Báo Cáo")

        # Ẩn progress bar
        self.progress_bar.setVisible(False)

        if success:
            # Lưu cài đặt người dùng khi xuất thành công
            self.save_user_preferences()

            # Hiển thị thông báo thành công
            QMessageBox.information(self, "Thành công", message)

            # Mở file nếu được yêu cầu
            if self.open_after_export_cb.isChecked() and self.export_excel_cb.isChecked():
                self.open_export_folder()

            # Hiển thị tóm tắt nếu được yêu cầu
            if self.show_summary_cb.isChecked():
                self.show_report_summary(report_data)

            # Đóng dialog
            self.accept()
        else:
            # Hiển thị lỗi
            QMessageBox.critical(self, "Lỗi", message)
            self.status_label.setText("Có lỗi xảy ra")

    def open_export_folder(self):
        """Mở thư mục chứa file xuất"""
        try:
            # Sử dụng thư mục tùy chỉnh nếu có, ngược lại dùng mặc định
            if self.export_folder and os.path.exists(self.export_folder):
                export_dir = self.export_folder
            else:
                export_dir = "src/data/exports"

            # Đảm bảo thư mục tồn tại
            if not os.path.exists(export_dir):
                os.makedirs(export_dir, exist_ok=True)

            if os.name == 'nt':  # Windows
                os.startfile(export_dir)
            elif os.name == 'posix':  # macOS and Linux
                os.system(f'open "{export_dir}"')
        except Exception as e:
            QMessageBox.warning(self, "Cảnh báo", f"Không thể mở thư mục: {str(e)}")

    def show_report_summary(self, report_data):
        """Hiển thị tóm tắt báo cáo"""
        summary_dialog = QDialog(self)
        summary_dialog.setWindowTitle("Tóm Tắt Báo Cáo")
        summary_dialog.resize(500, 400)

        layout = QVBoxLayout(summary_dialog)

        # Text area để hiển thị tóm tắt
        summary_text = QTextEdit()
        summary_text.setReadOnly(True)

        # Tạo nội dung tóm tắt
        summary_content = f"Báo cáo được tạo lúc: {report_data.get('generated_at', 'N/A')}\n\n"

        sections = report_data.get('sections', {})
        if 'inventory' in sections:
            inv_data = sections['inventory']
            summary_content += f"📦 Tồn kho: {inv_data.get('total_items', 0)} mặt hàng\n"

        if 'employees' in sections:
            emp_data = sections['employees']
            summary_content += f"👥 Nhân viên: {emp_data.get('total_employees', 0)} người\n"

        if 'production' in sections:
            prod_data = sections['production']
            summary_content += f"🏭 Sản xuất: {prod_data.get('total_reports', 0)} báo cáo\n"

        summary_text.setPlainText(summary_content)
        layout.addWidget(summary_text)

        # Nút đóng
        close_btn = QPushButton("Đóng")
        close_btn.clicked.connect(summary_dialog.accept)
        layout.addWidget(close_btn)

        summary_dialog.exec_()
