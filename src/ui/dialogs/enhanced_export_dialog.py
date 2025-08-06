#!/usr/bin/env python3
"""
Enhanced Export Dialog - Dialog xuất báo cáo được tối ưu hóa với nhiều tính năng nâng cao
"""

import os
import subprocess
from typing import List
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                            QGroupBox, QCheckBox, QMessageBox, QProgressBar,
                            QRadioButton, QButtonGroup, QComboBox, QSpinBox,
                            QTabWidget, QWidget, QTextEdit, QSlider, QFrame,
                            QDateEdit, QListWidget, QListWidgetItem, QSplitter)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QDate
from PyQt5.QtGui import QFont, QPixmap, QIcon

try:
    from src.services.optimized_export_service import OptimizedExportService
except ImportError:
    try:
        from services.optimized_export_service import OptimizedExportService
    except ImportError:
        OptimizedExportService = None


class EnhancedExportWorker(QThread):
    """Worker thread nâng cao với progress callback chi tiết"""
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    export_completed = pyqtSignal(bool, str)
    performance_stats = pyqtSignal(dict)

    def __init__(self, export_service, export_type, options):
        super().__init__()
        self.export_service = export_service
        self.export_type = export_type
        self.options = options

    def run(self):
        """Thực hiện xuất báo cáo với progress callback"""
        try:
            import time
            start_time = time.time()

            # Progress callback function
            def progress_callback(progress, status):
                self.progress_updated.emit(progress)
                self.status_updated.emit(status)

            # Execute export based on type
            if self.export_type == "inventory":
                success, message = self.export_service.export_inventory_report_optimized(
                    include_feed=self.options.get('include_feed', True),
                    include_mix=self.options.get('include_mix', True),
                    progress_callback=progress_callback
                )
            elif self.export_type == "formula":
                success, message = self.export_service.export_formula_report_optimized(
                    include_feed=self.options.get('include_feed', True),
                    include_mix=self.options.get('include_mix', True),
                    progress_callback=progress_callback
                )
            elif self.export_type == "summary":
                success, message = self.export_service.export_summary_report_optimized(
                    progress_callback=progress_callback
                )
            elif self.export_type == "daily_regional":
                from datetime import datetime
                start_date = datetime.combine(self.options.get('start_date'), datetime.min.time())
                end_date = datetime.combine(self.options.get('end_date'), datetime.min.time())

                success, message = self.export_service.export_daily_regional_report(
                    start_date=start_date,
                    end_date=end_date,
                    selected_regions=self.options.get('selected_regions', []),
                    include_feed=self.options.get('daily_include_feed', True),
                    include_mix=self.options.get('daily_include_mix', True),
                    progress_callback=progress_callback
                )
            elif self.export_type == "feed_component":
                from datetime import datetime
                start_date = datetime.combine(self.options.get('start_date'), datetime.min.time())
                end_date = datetime.combine(self.options.get('end_date'), datetime.min.time())

                success, message = self.export_service.export_feed_component_report(
                    start_date=start_date,
                    end_date=end_date,
                    selected_regions=self.options.get('selected_regions', []),
                    progress_callback=progress_callback
                )
            elif self.export_type == "mix_component":
                from datetime import datetime
                start_date = datetime.combine(self.options.get('start_date'), datetime.min.time())
                end_date = datetime.combine(self.options.get('end_date'), datetime.min.time())

                success, message = self.export_service.export_mix_component_report(
                    start_date=start_date,
                    end_date=end_date,
                    selected_regions=self.options.get('selected_regions', []),
                    progress_callback=progress_callback
                )
            else:
                success, message = False, "Loại báo cáo không được hỗ trợ"

            # Send performance statistics
            end_time = time.time()
            stats = {
                'processing_time': round(end_time - start_time, 2),
                'export_type': self.export_type,
                'success': success
            }
            self.performance_stats.emit(stats)

            self.export_completed.emit(success, message)

        except Exception as e:
            self.export_completed.emit(False, f"Lỗi xuất báo cáo: {str(e)}")


class EnhancedExportDialog(QDialog):
    """Dialog xuất báo cáo nâng cao với nhiều tính năng tối ưu"""

    def __init__(self, parent=None, default_type="inventory"):
        super().__init__(parent)
        self.parent_app = parent
        self.default_type = default_type
        self.worker_thread = None
        self.performance_stats = []

        # Initialize optimized export service
        if OptimizedExportService:
            try:
                self.export_service = OptimizedExportService()
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể khởi tạo dịch vụ xuất báo cáo tối ưu:\n{str(e)}")
                self.reject()
                return
        else:
            QMessageBox.critical(self, "Lỗi", "Không thể tải dịch vụ xuất báo cáo tối ưu.\nVui lòng kiểm tra cài đặt.")
            self.reject()
            return

        self.init_ui()
        self.set_default_type()
        self.load_recent_exports()

    def init_ui(self):
        """Khởi tạo giao diện nâng cao"""
        self.setWindowTitle("Xuất Báo Cáo Excel - Phiên Bản Tối Ưu")
        self.setModal(True)
        self.resize(600, 550)

        # Main layout
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header with performance indicator
        self.create_enhanced_header(layout)

        # Tab widget for organized options
        self.create_tabbed_interface(layout)

        # Enhanced progress section
        self.create_enhanced_progress_section(layout)

        # Performance monitoring
        self.create_performance_section(layout)

        # Enhanced buttons
        self.create_enhanced_buttons_section(layout)

        self.setLayout(layout)

    def create_enhanced_header(self, layout):
        """Tạo header nâng cao với performance indicator"""
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #E3F2FD, stop:1 #BBDEFB);
                border: 2px solid #2196F3;
                border-radius: 12px;
                padding: 15px;
            }
        """)

        header_layout = QVBoxLayout()

        # Main title
        title = QLabel("📊 XUẤT BÁO CÁO EXCEL - PHIÊN BẢN TỐI ƯU")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #1976D2; background: transparent; border: none;")

        # Subtitle with features
        subtitle = QLabel("✨ Hiệu suất cao • Định dạng chuyên nghiệp • Phân tích thông minh")
        subtitle.setFont(QFont("Arial", 10))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #666; background: transparent; border: none;")

        # Performance indicator
        self.perf_indicator = QLabel("🚀 Sẵn sàng xuất báo cáo")
        self.perf_indicator.setFont(QFont("Arial", 9))
        self.perf_indicator.setAlignment(Qt.AlignCenter)
        self.perf_indicator.setStyleSheet("color: #4CAF50; background: transparent; border: none;")

        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        header_layout.addWidget(self.perf_indicator)
        header_frame.setLayout(header_layout)

        layout.addWidget(header_frame)

    def create_tabbed_interface(self, layout):
        """Tạo giao diện tab để tổ chức tùy chọn"""
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            QTabBar::tab {
                background: #f0f0f0;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background: #2196F3;
                color: white;
            }
        """)

        # Tab 1: Report Type & Options
        self.create_report_options_tab()

        # Tab 2: Advanced Settings
        self.create_advanced_settings_tab()

        # Tab 3: Daily Reports
        self.create_daily_reports_tab()

        # Tab 4: Recent Exports
        self.create_recent_exports_tab()

        layout.addWidget(self.tab_widget)

    def create_report_options_tab(self):
        """Tạo tab tùy chọn báo cáo"""
        tab1 = QWidget()
        tab1_layout = QVBoxLayout()

        # Report type selection
        type_group = QGroupBox("Chọn Loại Báo Cáo")
        type_group.setFont(QFont("Arial", 12, QFont.Bold))
        type_layout = QVBoxLayout()

        self.report_type_group = QButtonGroup()

        # Enhanced radio buttons with descriptions
        self.inventory_radio = QRadioButton("📦 Báo Cáo Tồn Kho")
        self.inventory_radio.setFont(QFont("Arial", 11))
        self.inventory_radio.setToolTip("Xuất danh sách chi tiết nguyên liệu với trạng thái và giá trị ước tính")
        self.report_type_group.addButton(self.inventory_radio, 0)
        type_layout.addWidget(self.inventory_radio)

        inv_desc = QLabel("   → Bao gồm: Số lượng, trạng thái, giá trị ước tính, phân tích tồn kho")
        inv_desc.setFont(QFont("Arial", 9))
        inv_desc.setStyleSheet("color: #666; margin-left: 20px;")
        type_layout.addWidget(inv_desc)

        self.formula_radio = QRadioButton("🧪 Báo Cáo Công Thức")
        self.formula_radio.setFont(QFont("Arial", 11))
        self.formula_radio.setToolTip("Xuất công thức sản xuất với phân tích khả năng sản xuất")
        self.report_type_group.addButton(self.formula_radio, 1)
        type_layout.addWidget(self.formula_radio)

        form_desc = QLabel("   → Bao gồm: Tỷ lệ, tồn kho hiện tại, khả năng sản xuất, phân tích hạn chế")
        form_desc.setFont(QFont("Arial", 9))
        form_desc.setStyleSheet("color: #666; margin-left: 20px;")
        type_layout.addWidget(form_desc)

        self.summary_radio = QRadioButton("📈 Báo Cáo Tổng Hợp")
        self.summary_radio.setFont(QFont("Arial", 11))
        self.summary_radio.setToolTip("Xuất thống kê tổng quan với nhiều sheet phân tích")
        self.report_type_group.addButton(self.summary_radio, 2)
        type_layout.addWidget(self.summary_radio)

        summ_desc = QLabel("   → Bao gồm: Thống kê tổng quan, phân tích trạng thái, biểu đồ phân bố")
        summ_desc.setFont(QFont("Arial", 9))
        summ_desc.setStyleSheet("color: #666; margin-left: 20px;")
        type_layout.addWidget(summ_desc)

        # Daily reports radio buttons
        self.daily_regional_radio = QRadioButton("🌍 Báo Cáo Hàng Ngày Theo Khu Vực")
        self.daily_regional_radio.setFont(QFont("Arial", 11))
        self.daily_regional_radio.setToolTip("Xuất báo cáo tiêu thụ hàng ngày theo khu vực địa lý")
        self.report_type_group.addButton(self.daily_regional_radio, 3)
        type_layout.addWidget(self.daily_regional_radio)

        daily_desc = QLabel("   → Bao gồm: Sản lượng theo khu vực, xu hướng tiêu thụ, phân tích theo ngày")
        daily_desc.setFont(QFont("Arial", 9))
        daily_desc.setStyleSheet("color: #666; margin-left: 20px;")
        type_layout.addWidget(daily_desc)

        self.feed_component_radio = QRadioButton("🌾 Báo Cáo Thành Phần Cám")
        self.feed_component_radio.setFont(QFont("Arial", 11))
        self.feed_component_radio.setToolTip("Xuất báo cáo chi tiết thành phần cám với phân tích dinh dưỡng")
        self.report_type_group.addButton(self.feed_component_radio, 4)
        type_layout.addWidget(self.feed_component_radio)

        feed_comp_desc = QLabel("   → Bao gồm: Thành phần dinh dưỡng, xu hướng tiêu thụ, so sánh công thức")
        feed_comp_desc.setFont(QFont("Arial", 9))
        feed_comp_desc.setStyleSheet("color: #666; margin-left: 20px;")
        type_layout.addWidget(feed_comp_desc)

        self.mix_component_radio = QRadioButton("⚗️ Báo Cáo Thành Phần Mix")
        self.mix_component_radio.setFont(QFont("Arial", 11))
        self.mix_component_radio.setToolTip("Xuất báo cáo chi tiết thành phần mix với phân tích hiệu quả")
        self.report_type_group.addButton(self.mix_component_radio, 5)
        type_layout.addWidget(self.mix_component_radio)

        mix_comp_desc = QLabel("   → Bao gồm: Chức năng phụ gia, liều lượng khuyến nghị, phân tích hiệu quả")
        mix_comp_desc.setFont(QFont("Arial", 9))
        mix_comp_desc.setStyleSheet("color: #666; margin-left: 20px;")
        type_layout.addWidget(mix_comp_desc)

        type_group.setLayout(type_layout)
        tab1_layout.addWidget(type_group)

        # Warehouse selection with enhanced options
        self.options_group = QGroupBox("Tùy Chọn Kho")
        self.options_group.setFont(QFont("Arial", 12, QFont.Bold))
        options_layout = QVBoxLayout()

        warehouse_layout = QHBoxLayout()

        self.feed_checkbox = QCheckBox("Kho Cám")
        self.feed_checkbox.setChecked(True)
        self.feed_checkbox.setToolTip("Bao gồm dữ liệu từ kho nguyên liệu cám")
        warehouse_layout.addWidget(self.feed_checkbox)

        self.mix_checkbox = QCheckBox("Kho Mix")
        self.mix_checkbox.setChecked(True)
        self.mix_checkbox.setToolTip("Bao gồm dữ liệu từ kho phụ gia mix")
        warehouse_layout.addWidget(self.mix_checkbox)

        warehouse_layout.addStretch()
        options_layout.addLayout(warehouse_layout)

        self.options_group.setLayout(options_layout)
        tab1_layout.addWidget(self.options_group)

        # Connect events
        self.report_type_group.buttonClicked.connect(self.on_report_type_changed)

        tab1_layout.addStretch()
        tab1.setLayout(tab1_layout)
        self.tab_widget.addTab(tab1, "📋 Tùy Chọn Báo Cáo")

    def create_advanced_settings_tab(self):
        """Tạo tab cài đặt nâng cao"""
        tab2 = QWidget()
        tab2_layout = QVBoxLayout()

        # Performance settings
        perf_group = QGroupBox("Cài Đặt Hiệu Suất")
        perf_group.setFont(QFont("Arial", 12, QFont.Bold))
        perf_layout = QVBoxLayout()

        # Cache settings
        cache_layout = QHBoxLayout()
        cache_layout.addWidget(QLabel("Cache dữ liệu:"))

        self.cache_enabled = QCheckBox("Bật cache để tăng tốc")
        self.cache_enabled.setChecked(True)
        self.cache_enabled.setToolTip("Lưu cache dữ liệu để xuất nhanh hơn lần sau")
        cache_layout.addWidget(self.cache_enabled)

        clear_cache_btn = QPushButton("Xóa Cache")
        clear_cache_btn.clicked.connect(self.clear_cache)
        clear_cache_btn.setToolTip("Xóa cache để tải lại dữ liệu mới")
        cache_layout.addWidget(clear_cache_btn)

        cache_layout.addStretch()
        perf_layout.addLayout(cache_layout)

        perf_group.setLayout(perf_layout)
        tab2_layout.addWidget(perf_group)

        # Formatting settings
        format_group = QGroupBox("Cài Đặt Định Dạng")
        format_group.setFont(QFont("Arial", 12, QFont.Bold))
        format_layout = QVBoxLayout()

        self.advanced_formatting = QCheckBox("Định dạng nâng cao (màu sắc, borders, styles)")
        self.advanced_formatting.setChecked(True)
        format_layout.addWidget(self.advanced_formatting)

        self.include_summary = QCheckBox("Bao gồm phần tóm tắt")
        self.include_summary.setChecked(True)
        format_layout.addWidget(self.include_summary)

        self.include_analysis = QCheckBox("Bao gồm phân tích chi tiết")
        self.include_analysis.setChecked(True)
        format_layout.addWidget(self.include_analysis)

        format_group.setLayout(format_layout)
        tab2_layout.addWidget(format_group)

        tab2_layout.addStretch()
        tab2.setLayout(tab2_layout)
        self.tab_widget.addTab(tab2, "⚙️ Cài Đặt Nâng Cao")

    def create_recent_exports_tab(self):
        """Tạo tab file đã xuất gần đây"""
        tab3 = QWidget()
        tab3_layout = QVBoxLayout()

        recent_group = QGroupBox("File Đã Xuất Gần Đây")
        recent_group.setFont(QFont("Arial", 12, QFont.Bold))
        recent_layout = QVBoxLayout()

        self.recent_files_list = QTextEdit()
        self.recent_files_list.setMaximumHeight(150)
        self.recent_files_list.setReadOnly(True)
        self.recent_files_list.setStyleSheet("""
            QTextEdit {
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Courier New';
                font-size: 9pt;
            }
        """)
        recent_layout.addWidget(self.recent_files_list)

        # Buttons for recent files
        recent_buttons_layout = QHBoxLayout()

        refresh_btn = QPushButton("🔄 Làm Mới")
        refresh_btn.clicked.connect(self.load_recent_exports)
        recent_buttons_layout.addWidget(refresh_btn)

        open_folder_btn = QPushButton("📁 Mở Thư Mục")
        open_folder_btn.clicked.connect(self.open_export_folder)
        recent_buttons_layout.addWidget(open_folder_btn)

        recent_buttons_layout.addStretch()
        recent_layout.addLayout(recent_buttons_layout)

        recent_group.setLayout(recent_layout)
        tab3_layout.addWidget(recent_group)

        # Export directory info
        info_group = QGroupBox("Thông Tin Thư Mục")
        info_group.setFont(QFont("Arial", 12, QFont.Bold))
        info_layout = QVBoxLayout()

        export_dir = self.export_service.get_export_directory()
        dir_info = QLabel(f"📁 Thư mục xuất: {export_dir}")
        dir_info.setWordWrap(True)
        dir_info.setStyleSheet("padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        info_layout.addWidget(dir_info)

        info_group.setLayout(info_layout)
        tab3_layout.addWidget(info_group)

        tab3_layout.addStretch()
        tab3.setLayout(tab3_layout)
        self.tab_widget.addTab(tab3, "📅 Báo Cáo Hàng Ngày")

    def create_daily_reports_tab(self):
        """Tạo tab báo cáo hàng ngày"""
        tab3 = QWidget()
        tab3_layout = QVBoxLayout()

        # Date range selection
        date_group = QGroupBox("Chọn Khoảng Thời Gian")
        date_group.setFont(QFont("Arial", 12, QFont.Bold))
        date_layout = QVBoxLayout()

        # Date range controls
        date_controls_layout = QHBoxLayout()

        date_controls_layout.addWidget(QLabel("Từ ngày:"))
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        self.start_date.setCalendarPopup(True)
        self.start_date.setStyleSheet("QDateEdit { padding: 5px; }")
        date_controls_layout.addWidget(self.start_date)

        date_controls_layout.addWidget(QLabel("Đến ngày:"))
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        self.end_date.setStyleSheet("QDateEdit { padding: 5px; }")
        date_controls_layout.addWidget(self.end_date)

        # Quick date selection buttons
        quick_date_layout = QHBoxLayout()

        last_7_days_btn = QPushButton("7 ngày qua")
        last_7_days_btn.clicked.connect(lambda: self.set_date_range(7))
        quick_date_layout.addWidget(last_7_days_btn)

        last_30_days_btn = QPushButton("30 ngày qua")
        last_30_days_btn.clicked.connect(lambda: self.set_date_range(30))
        quick_date_layout.addWidget(last_30_days_btn)

        this_month_btn = QPushButton("Tháng này")
        this_month_btn.clicked.connect(self.set_current_month)
        quick_date_layout.addWidget(this_month_btn)

        quick_date_layout.addStretch()

        date_layout.addLayout(date_controls_layout)
        date_layout.addLayout(quick_date_layout)
        date_group.setLayout(date_layout)
        tab3_layout.addWidget(date_group)

        # Region selection
        region_group = QGroupBox("Chọn Khu Vực")
        region_group.setFont(QFont("Arial", 12, QFont.Bold))
        region_layout = QVBoxLayout()

        # Region selection list
        self.region_list = QListWidget()
        self.region_list.setMaximumHeight(120)
        self.region_list.setSelectionMode(QListWidget.MultiSelection)

        # Add regions
        regions = [
            ("mien_bac", "🏔️ Miền Bắc"),
            ("mien_trung", "🏖️ Miền Trung"),
            ("mien_nam", "🌴 Miền Nam")
        ]

        for region_id, region_name in regions:
            item = QListWidgetItem(region_name)
            item.setData(Qt.UserRole, region_id)
            item.setSelected(True)  # Select all by default
            self.region_list.addItem(item)

        region_layout.addWidget(self.region_list)

        # Region selection buttons
        region_buttons_layout = QHBoxLayout()

        select_all_regions_btn = QPushButton("Chọn tất cả")
        select_all_regions_btn.clicked.connect(self.select_all_regions)
        region_buttons_layout.addWidget(select_all_regions_btn)

        clear_regions_btn = QPushButton("Bỏ chọn tất cả")
        clear_regions_btn.clicked.connect(self.clear_all_regions)
        region_buttons_layout.addWidget(clear_regions_btn)

        region_buttons_layout.addStretch()

        region_layout.addLayout(region_buttons_layout)
        region_group.setLayout(region_layout)
        tab3_layout.addWidget(region_group)

        # Component selection for daily reports
        component_group = QGroupBox("Tùy Chọn Thành Phần")
        component_group.setFont(QFont("Arial", 12, QFont.Bold))
        component_layout = QVBoxLayout()

        self.daily_include_feed = QCheckBox("Bao gồm thành phần cám")
        self.daily_include_feed.setChecked(True)
        self.daily_include_feed.setToolTip("Bao gồm phân tích thành phần cám trong báo cáo")
        component_layout.addWidget(self.daily_include_feed)

        self.daily_include_mix = QCheckBox("Bao gồm thành phần mix")
        self.daily_include_mix.setChecked(True)
        self.daily_include_mix.setToolTip("Bao gồm phân tích thành phần mix trong báo cáo")
        component_layout.addWidget(self.daily_include_mix)

        self.include_trends = QCheckBox("Bao gồm phân tích xu hướng")
        self.include_trends.setChecked(True)
        self.include_trends.setToolTip("Thêm biểu đồ và phân tích xu hướng tiêu thụ")
        component_layout.addWidget(self.include_trends)

        self.include_cost_analysis = QCheckBox("Bao gồm phân tích chi phí")
        self.include_cost_analysis.setChecked(True)
        self.include_cost_analysis.setToolTip("Thêm phân tích chi phí nguyên liệu")
        component_layout.addWidget(self.include_cost_analysis)

        component_group.setLayout(component_layout)
        tab3_layout.addWidget(component_group)

        # Preview section
        preview_group = QGroupBox("Xem Trước Dữ Liệu")
        preview_group.setFont(QFont("Arial", 12, QFont.Bold))
        preview_layout = QVBoxLayout()

        self.data_preview = QTextEdit()
        self.data_preview.setMaximumHeight(100)
        self.data_preview.setReadOnly(True)
        self.data_preview.setStyleSheet("""
            QTextEdit {
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 5px;
                font-family: 'Courier New';
                font-size: 9pt;
            }
        """)
        self.data_preview.setText("Chọn khoảng thời gian và nhấn 'Xem trước' để hiển thị dữ liệu...")
        preview_layout.addWidget(self.data_preview)

        preview_btn = QPushButton("🔍 Xem Trước Dữ Liệu")
        preview_btn.clicked.connect(self.preview_daily_data)
        preview_layout.addWidget(preview_btn)

        preview_group.setLayout(preview_layout)
        tab3_layout.addWidget(preview_group)

        tab3_layout.addStretch()
        tab3.setLayout(tab3_layout)
        self.tab_widget.addTab(tab3, "📅 Báo Cáo Hàng Ngày")

    def create_recent_exports_tab(self):
        """Tạo tab file đã xuất gần đây"""
        tab4 = QWidget()
        tab4_layout = QVBoxLayout()

        recent_group = QGroupBox("File Đã Xuất Gần Đây")
        recent_group.setFont(QFont("Arial", 12, QFont.Bold))
        recent_layout = QVBoxLayout()

        self.recent_files_list = QTextEdit()
        self.recent_files_list.setMaximumHeight(150)
        self.recent_files_list.setReadOnly(True)
        self.recent_files_list.setStyleSheet("""
            QTextEdit {
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Courier New';
                font-size: 9pt;
            }
        """)
        recent_layout.addWidget(self.recent_files_list)

        # Buttons for recent files
        recent_buttons_layout = QHBoxLayout()

        refresh_btn = QPushButton("🔄 Làm Mới")
        refresh_btn.clicked.connect(self.load_recent_exports)
        recent_buttons_layout.addWidget(refresh_btn)

        open_folder_btn = QPushButton("📁 Mở Thư Mục")
        open_folder_btn.clicked.connect(self.open_export_folder)
        recent_buttons_layout.addWidget(open_folder_btn)

        recent_buttons_layout.addStretch()
        recent_layout.addLayout(recent_buttons_layout)

        recent_group.setLayout(recent_layout)
        tab4_layout.addWidget(recent_group)

        # Export directory info
        info_group = QGroupBox("Thông Tin Thư Mục")
        info_group.setFont(QFont("Arial", 12, QFont.Bold))
        info_layout = QVBoxLayout()

        export_dir = self.export_service.get_export_directory()
        dir_info = QLabel(f"📁 Thư mục xuất: {export_dir}")
        dir_info.setWordWrap(True)
        dir_info.setStyleSheet("padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        info_layout.addWidget(dir_info)

        info_group.setLayout(info_layout)
        tab4_layout.addWidget(info_group)

        tab4_layout.addStretch()
        tab4.setLayout(tab4_layout)
        self.tab_widget.addTab(tab4, "📄 File Gần Đây")

    def create_enhanced_progress_section(self, layout):
        """Tạo phần hiển thị tiến trình nâng cao"""
        self.progress_frame = QFrame()
        self.progress_frame.setVisible(False)
        progress_layout = QVBoxLayout()

        # Enhanced progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ddd;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                height: 25px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4CAF50, stop:1 #8BC34A);
                border-radius: 6px;
            }
        """)
        progress_layout.addWidget(self.progress_bar)

        # Status with icon
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-style: italic;
                padding: 5px;
                background-color: #f9f9f9;
                border-radius: 5px;
            }
        """)
        progress_layout.addWidget(self.status_label)

        self.progress_frame.setLayout(progress_layout)
        layout.addWidget(self.progress_frame)

    def create_performance_section(self, layout):
        """Tạo phần hiển thị thông tin hiệu suất"""
        self.perf_frame = QFrame()
        self.perf_frame.setVisible(False)
        perf_layout = QHBoxLayout()

        self.perf_time_label = QLabel("⏱️ Thời gian: --")
        self.perf_time_label.setStyleSheet("color: #2196F3; font-weight: bold;")
        perf_layout.addWidget(self.perf_time_label)

        self.perf_items_label = QLabel("📊 Số mục: --")
        self.perf_items_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        perf_layout.addWidget(self.perf_items_label)

        perf_layout.addStretch()

        self.perf_frame.setLayout(perf_layout)
        layout.addWidget(self.perf_frame)

    def create_enhanced_buttons_section(self, layout):
        """Tạo phần nút bấm nâng cao"""
        button_layout = QHBoxLayout()

        # Quick export buttons
        quick_layout = QVBoxLayout()
        quick_label = QLabel("Xuất Nhanh:")
        quick_label.setFont(QFont("Arial", 9, QFont.Bold))
        quick_layout.addWidget(quick_label)

        quick_buttons_layout = QHBoxLayout()

        quick_inv_btn = QPushButton("📦")
        quick_inv_btn.setToolTip("Xuất nhanh báo cáo tồn kho")
        quick_inv_btn.setMaximumWidth(40)
        quick_inv_btn.clicked.connect(lambda: self.quick_export("inventory"))
        quick_buttons_layout.addWidget(quick_inv_btn)

        quick_form_btn = QPushButton("🧪")
        quick_form_btn.setToolTip("Xuất nhanh báo cáo công thức")
        quick_form_btn.setMaximumWidth(40)
        quick_form_btn.clicked.connect(lambda: self.quick_export("formula"))
        quick_buttons_layout.addWidget(quick_form_btn)

        quick_summ_btn = QPushButton("📈")
        quick_summ_btn.setToolTip("Xuất nhanh báo cáo tổng hợp")
        quick_summ_btn.setMaximumWidth(40)
        quick_summ_btn.clicked.connect(lambda: self.quick_export("summary"))
        quick_buttons_layout.addWidget(quick_summ_btn)

        quick_daily_btn = QPushButton("🌍")
        quick_daily_btn.setToolTip("Xuất nhanh báo cáo hàng ngày theo khu vực")
        quick_daily_btn.setMaximumWidth(40)
        quick_daily_btn.clicked.connect(lambda: self.quick_export("daily_regional"))
        quick_buttons_layout.addWidget(quick_daily_btn)

        quick_feed_comp_btn = QPushButton("🌾")
        quick_feed_comp_btn.setToolTip("Xuất nhanh báo cáo thành phần cám")
        quick_feed_comp_btn.setMaximumWidth(40)
        quick_feed_comp_btn.clicked.connect(lambda: self.quick_export("feed_component"))
        quick_buttons_layout.addWidget(quick_feed_comp_btn)

        quick_mix_comp_btn = QPushButton("⚗️")
        quick_mix_comp_btn.setToolTip("Xuất nhanh báo cáo thành phần mix")
        quick_mix_comp_btn.setMaximumWidth(40)
        quick_mix_comp_btn.clicked.connect(lambda: self.quick_export("mix_component"))
        quick_buttons_layout.addWidget(quick_mix_comp_btn)

        quick_layout.addLayout(quick_buttons_layout)
        button_layout.addLayout(quick_layout)

        button_layout.addStretch()

        # Main export button
        self.export_button = QPushButton("🚀 Xuất Báo Cáo Tối Ưu")
        self.export_button.setFont(QFont("Arial", 12, QFont.Bold))
        self.export_button.setMinimumHeight(45)
        self.export_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4CAF50, stop:1 #45a049);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #45a049, stop:1 #3d8b40);
            }
            QPushButton:disabled {
                background: #cccccc;
            }
        """)
        self.export_button.clicked.connect(self.start_export)
        button_layout.addWidget(self.export_button)

        # Cancel button
        cancel_button = QPushButton("Hủy")
        cancel_button.setFont(QFont("Arial", 11))
        cancel_button.setMinimumHeight(45)
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

    def set_default_type(self):
        """Đặt loại báo cáo mặc định"""
        if self.default_type == "formula":
            self.formula_radio.setChecked(True)
        elif self.default_type == "summary":
            self.summary_radio.setChecked(True)
        else:
            self.inventory_radio.setChecked(True)

        self.on_report_type_changed()

    def on_report_type_changed(self):
        """Xử lý khi thay đổi loại báo cáo"""
        # Báo cáo tổng hợp không cần tùy chọn kho
        if self.summary_radio.isChecked():
            self.options_group.setEnabled(False)
            self.perf_indicator.setText("📈 Báo cáo tổng hợp - Phân tích toàn diện")
        elif self.formula_radio.isChecked():
            self.options_group.setEnabled(True)
            self.perf_indicator.setText("🧪 Báo cáo công thức - Phân tích sản xuất")
        elif self.daily_regional_radio.isChecked():
            self.options_group.setEnabled(False)
            self.perf_indicator.setText("🌍 Báo cáo hàng ngày - Phân tích theo khu vực")
        elif self.feed_component_radio.isChecked():
            self.options_group.setEnabled(False)
            self.perf_indicator.setText("🌾 Báo cáo thành phần cám - Phân tích dinh dưỡng")
        elif self.mix_component_radio.isChecked():
            self.options_group.setEnabled(False)
            self.perf_indicator.setText("⚗️ Báo cáo thành phần mix - Phân tích hiệu quả")
        else:
            self.options_group.setEnabled(True)
            self.perf_indicator.setText("📦 Báo cáo tồn kho - Theo dõi nguyên liệu")

    def get_export_type(self):
        """Lấy loại báo cáo được chọn"""
        if self.formula_radio.isChecked():
            return "formula"
        elif self.summary_radio.isChecked():
            return "summary"
        elif self.daily_regional_radio.isChecked():
            return "daily_regional"
        elif self.feed_component_radio.isChecked():
            return "feed_component"
        elif self.mix_component_radio.isChecked():
            return "mix_component"
        else:
            return "inventory"

    def get_export_options(self):
        """Lấy tùy chọn xuất nâng cao"""
        options = {
            'include_feed': self.feed_checkbox.isChecked(),
            'include_mix': self.mix_checkbox.isChecked(),
            'cache_enabled': self.cache_enabled.isChecked(),
            'advanced_formatting': self.advanced_formatting.isChecked(),
            'include_summary': self.include_summary.isChecked(),
            'include_analysis': self.include_analysis.isChecked()
        }

        # Add daily report specific options
        if hasattr(self, 'daily_include_feed'):
            options.update({
                'daily_include_feed': self.daily_include_feed.isChecked(),
                'daily_include_mix': self.daily_include_mix.isChecked(),
                'include_trends': self.include_trends.isChecked(),
                'include_cost_analysis': self.include_cost_analysis.isChecked(),
                'start_date': self.start_date.date().toPyDate(),
                'end_date': self.end_date.date().toPyDate(),
                'selected_regions': self.get_selected_regions()
            })

        return options

    def validate_options(self):
        """Kiểm tra tùy chọn nâng cao"""
        export_type = self.get_export_type()

        # Validate traditional reports
        if export_type in ["inventory", "formula"]:
            if not (self.feed_checkbox.isChecked() or self.mix_checkbox.isChecked()):
                QMessageBox.warning(self, "Cảnh báo",
                                  "Vui lòng chọn ít nhất một kho để xuất!\n\n"
                                  "💡 Mẹo: Bạn có thể chọn cả hai kho để có báo cáo đầy đủ.")
                return False

        # Validate daily reports
        elif export_type in ["daily_regional", "feed_component", "mix_component"]:
            # Check date range
            start_date = self.start_date.date().toPyDate()
            end_date = self.end_date.date().toPyDate()

            if start_date > end_date:
                QMessageBox.warning(self, "Cảnh báo",
                                  "Ngày bắt đầu không thể lớn hơn ngày kết thúc!\n\n"
                                  "💡 Vui lòng chọn lại khoảng thời gian.")
                return False

            # Check date range not too large
            date_diff = (end_date - start_date).days
            if date_diff > 365:
                reply = QMessageBox.question(self, "Xác nhận",
                                           f"Khoảng thời gian được chọn là {date_diff} ngày.\n"
                                           "Báo cáo có thể mất nhiều thời gian để tạo.\n\n"
                                           "Bạn có muốn tiếp tục không?",
                                           QMessageBox.Yes | QMessageBox.No,
                                           QMessageBox.No)
                if reply == QMessageBox.No:
                    return False

            # Check regions selected
            selected_regions = self.get_selected_regions()
            if not selected_regions:
                QMessageBox.warning(self, "Cảnh báo",
                                  "Vui lòng chọn ít nhất một khu vực!\n\n"
                                  "💡 Mẹo: Chọn 'Chọn tất cả' để bao gồm tất cả khu vực.")
                return False

            # Check components for daily regional reports
            if export_type == "daily_regional":
                if not (self.daily_include_feed.isChecked() or self.daily_include_mix.isChecked()):
                    QMessageBox.warning(self, "Cảnh báo",
                                      "Vui lòng chọn ít nhất một loại thành phần!\n\n"
                                      "💡 Chọn 'Bao gồm thành phần cám' hoặc 'Bao gồm thành phần mix'.")
                    return False

        return True

    def quick_export(self, export_type):
        """Xuất nhanh với cài đặt mặc định"""
        # Set export type
        if export_type == "inventory":
            self.inventory_radio.setChecked(True)
        elif export_type == "formula":
            self.formula_radio.setChecked(True)
        elif export_type == "summary":
            self.summary_radio.setChecked(True)

        self.on_report_type_changed()

        # Start export immediately
        self.start_export()

    def start_export(self):
        """Bắt đầu xuất báo cáo với tính năng nâng cao"""
        if not self.validate_options():
            return

        # Update UI for export mode
        self.export_button.setEnabled(False)
        self.progress_frame.setVisible(True)
        self.perf_frame.setVisible(True)
        self.progress_bar.setValue(0)

        # Update performance indicator
        self.perf_indicator.setText("🔄 Đang xử lý...")

        # Get export parameters
        export_type = self.get_export_type()
        export_options = self.get_export_options()

        # Clear cache if disabled
        if not export_options.get('cache_enabled', True):
            self.export_service.clear_cache()

        # Create and start enhanced worker thread
        self.worker_thread = EnhancedExportWorker(self.export_service, export_type, export_options)
        self.worker_thread.progress_updated.connect(self.on_progress_updated)
        self.worker_thread.status_updated.connect(self.on_status_updated)
        self.worker_thread.performance_stats.connect(self.on_performance_stats)
        self.worker_thread.export_completed.connect(self.on_export_completed)
        self.worker_thread.start()

    def on_progress_updated(self, progress):
        """Cập nhật progress bar với animation"""
        self.progress_bar.setValue(progress)

        # Update progress bar color based on progress
        if progress < 30:
            color = "#FF9800"  # Orange
        elif progress < 70:
            color = "#2196F3"  # Blue
        else:
            color = "#4CAF50"  # Green

        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid #ddd;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                height: 25px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {color}, stop:1 {color});
                border-radius: 6px;
            }}
        """)

    def on_status_updated(self, status):
        """Cập nhật status với icon động"""
        icons = ["⏳", "🔄", "⚡", "✨"]
        import random
        icon = random.choice(icons)
        self.status_label.setText(f"{icon} {status}")

    def on_performance_stats(self, stats):
        """Hiển thị thống kê hiệu suất"""
        processing_time = stats.get('processing_time', 0)
        self.perf_time_label.setText(f"⏱️ Thời gian: {processing_time}s")

        # Store stats for history
        self.performance_stats.append(stats)

    def on_export_completed(self, success, message):
        """Xử lý khi xuất xong với enhanced feedback"""
        # Re-enable UI
        self.export_button.setEnabled(True)
        self.progress_frame.setVisible(False)

        if success:
            # Update performance indicator
            self.perf_indicator.setText("✅ Xuất báo cáo thành công!")

            # Enhanced success dialog
            reply = QMessageBox.question(
                self,
                "🎉 Xuất Báo Cáo Thành Công",
                f"{message}\n\n"
                "🎯 Tính năng đã sử dụng:\n"
                f"• Định dạng nâng cao: {'✅' if self.advanced_formatting.isChecked() else '❌'}\n"
                f"• Phân tích chi tiết: {'✅' if self.include_analysis.isChecked() else '❌'}\n"
                f"• Cache dữ liệu: {'✅' if self.cache_enabled.isChecked() else '❌'}\n\n"
                "Bạn có muốn mở thư mục chứa file không?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )

            if reply == QMessageBox.Yes:
                self.open_export_folder()

            # Refresh recent files
            self.load_recent_exports()

            self.accept()
        else:
            self.perf_indicator.setText("❌ Xuất báo cáo thất bại")

            # Enhanced error dialog
            error_dialog = QMessageBox(self)
            error_dialog.setIcon(QMessageBox.Critical)
            error_dialog.setWindowTitle("❌ Lỗi Xuất Báo Cáo")
            error_dialog.setText("Xuất báo cáo thất bại!")
            error_dialog.setDetailedText(f"Chi tiết lỗi:\n{message}\n\n"
                                       "💡 Gợi ý khắc phục:\n"
                                       "• Kiểm tra quyền ghi file\n"
                                       "• Đảm bảo đủ dung lượng ổ cứng\n"
                                       "• Thử tắt cache và xuất lại\n"
                                       "• Kiểm tra dữ liệu đầu vào")
            error_dialog.exec_()

    def clear_cache(self):
        """Xóa cache với feedback"""
        self.export_service.clear_cache()
        QMessageBox.information(self, "Thông báo",
                              "✅ Đã xóa cache thành công!\n\n"
                              "Lần xuất tiếp theo sẽ tải lại dữ liệu mới từ file.")

    def load_recent_exports(self):
        """Tải danh sách file đã xuất gần đây"""
        try:
            recent_files = self.export_service.list_exported_files()

            if recent_files:
                files_text = "📄 File đã xuất gần đây:\n\n"
                for i, filename in enumerate(recent_files[:10], 1):
                    # Parse filename for info
                    if "ton_kho" in filename:
                        icon = "📦"
                        type_name = "Tồn kho"
                    elif "cong_thuc" in filename:
                        icon = "🧪"
                        type_name = "Công thức"
                    elif "tong_hop" in filename:
                        icon = "📈"
                        type_name = "Tổng hợp"
                    else:
                        icon = "📄"
                        type_name = "Khác"

                    files_text += f"{i:2d}. {icon} {type_name}: {filename}\n"

                if len(recent_files) > 10:
                    files_text += f"\n... và {len(recent_files) - 10} file khác"
            else:
                files_text = "📭 Chưa có file nào được xuất.\n\nHãy thử xuất báo cáo đầu tiên!"

            self.recent_files_list.setText(files_text)

        except Exception as e:
            self.recent_files_list.setText(f"❌ Lỗi tải danh sách file: {str(e)}")

    def open_export_folder(self):
        """Mở thư mục chứa file xuất với error handling"""
        try:
            export_dir = self.export_service.get_export_directory()
            if os.name == 'nt':  # Windows
                os.startfile(export_dir)
            elif os.name == 'posix':  # macOS and Linux
                subprocess.call(['open', export_dir])
        except Exception as e:
            QMessageBox.warning(self, "Cảnh báo",
                              f"Không thể mở thư mục:\n{str(e)}\n\n"
                              f"📁 Đường dẫn thủ công:\n{export_dir}")

    def closeEvent(self, event):
        """Xử lý khi đóng dialog với confirmation"""
        if self.worker_thread and self.worker_thread.isRunning():
            reply = QMessageBox.question(
                self,
                "⚠️ Xác Nhận Đóng",
                "Đang có tiến trình xuất báo cáo đang chạy.\n\n"
                "Bạn có chắc muốn hủy và đóng dialog?\n\n"
                "⚠️ Lưu ý: Tiến trình xuất sẽ bị dừng và file có thể không hoàn chỉnh.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.worker_thread.terminate()
                self.worker_thread.wait()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    # Daily reports helper methods
    def set_date_range(self, days: int):
        """Đặt khoảng thời gian nhanh"""
        end_date = QDate.currentDate()
        start_date = end_date.addDays(-days)

        self.start_date.setDate(start_date)
        self.end_date.setDate(end_date)

    def set_current_month(self):
        """Đặt tháng hiện tại"""
        current_date = QDate.currentDate()
        start_of_month = QDate(current_date.year(), current_date.month(), 1)

        self.start_date.setDate(start_of_month)
        self.end_date.setDate(current_date)

    def select_all_regions(self):
        """Chọn tất cả khu vực"""
        for i in range(self.region_list.count()):
            item = self.region_list.item(i)
            item.setSelected(True)

    def clear_all_regions(self):
        """Bỏ chọn tất cả khu vực"""
        for i in range(self.region_list.count()):
            item = self.region_list.item(i)
            item.setSelected(False)

    def get_selected_regions(self) -> List[str]:
        """Lấy danh sách khu vực được chọn"""
        selected_regions = []
        for i in range(self.region_list.count()):
            item = self.region_list.item(i)
            if item.isSelected():
                region_id = item.data(Qt.UserRole)
                selected_regions.append(region_id)
        return selected_regions

    def preview_daily_data(self):
        """Xem trước dữ liệu hàng ngày"""
        try:
            start_date = self.start_date.date().toPyDate()
            end_date = self.end_date.date().toPyDate()
            selected_regions = self.get_selected_regions()

            if not selected_regions:
                self.data_preview.setText("❌ Vui lòng chọn ít nhất một khu vực")
                return

            # Load sample data for preview
            from datetime import datetime
            daily_data = self.export_service._load_daily_consumption_data(
                datetime.combine(start_date, datetime.min.time()),
                datetime.combine(end_date, datetime.min.time())
            )

            if not daily_data:
                self.data_preview.setText("❌ Không có dữ liệu trong khoảng thời gian đã chọn")
                return

            # Create preview text
            preview_text = f"📅 Khoảng thời gian: {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}\n"
            preview_text += f"📊 Số ngày có dữ liệu: {len(daily_data)}\n"
            preview_text += f"🌍 Khu vực được chọn: {len(selected_regions)}\n\n"

            # Sample data from first available day
            if daily_data:
                first_date = min(daily_data.keys())
                first_day_data = daily_data[first_date]

                preview_text += f"📋 Dữ liệu mẫu ({first_date}):\n"

                for region_id in selected_regions:
                    if region_id in first_day_data.get('regions', {}):
                        region_data = first_day_data['regions'][region_id]
                        region_name = region_data.get('region_name', region_id)
                        production = region_data.get('total_production', 0)

                        preview_text += f"  • {region_name}: {production:,.1f} kg\n"

                # Show top feed components
                all_feed_components = {}
                for region_id in selected_regions:
                    if region_id in first_day_data.get('regions', {}):
                        feed_consumption = first_day_data['regions'][region_id].get('feed_consumption', {})
                        for component, amount in feed_consumption.items():
                            if component not in all_feed_components:
                                all_feed_components[component] = 0
                            all_feed_components[component] += amount

                if all_feed_components:
                    preview_text += f"\n🌾 Top 3 thành phần cám:\n"
                    sorted_components = sorted(all_feed_components.items(), key=lambda x: x[1], reverse=True)[:3]
                    for component, amount in sorted_components:
                        preview_text += f"  • {component}: {amount:.1f} kg\n"

            self.data_preview.setText(preview_text)

        except Exception as e:
            self.data_preview.setText(f"❌ Lỗi xem trước dữ liệu: {str(e)}")

    def quick_export(self, export_type):
        """Xuất nhanh với cài đặt mặc định"""
        # Set export type
        if export_type == "inventory":
            self.inventory_radio.setChecked(True)
        elif export_type == "formula":
            self.formula_radio.setChecked(True)
        elif export_type == "summary":
            self.summary_radio.setChecked(True)
        elif export_type == "daily_regional":
            self.daily_regional_radio.setChecked(True)
        elif export_type == "feed_component":
            self.feed_component_radio.setChecked(True)
        elif export_type == "mix_component":
            self.mix_component_radio.setChecked(True)

        self.on_report_type_changed()

        # Start export immediately
        self.start_export()
