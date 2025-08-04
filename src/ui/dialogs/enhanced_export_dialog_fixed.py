#!/usr/bin/env python3
"""
Enhanced Export Dialog - Fixed Version - Dialog xuất báo cáo được tối ưu hóa với sửa lỗi QWidget
"""

import os
import subprocess
import sys
from datetime import datetime
from typing import List

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                            QGroupBox, QCheckBox, QMessageBox, QProgressBar,
                            QRadioButton, QButtonGroup, QComboBox, QSpinBox,
                            QTabWidget, QWidget, QTextEdit, QSlider, QFrame,
                            QDateEdit, QListWidget, QListWidgetItem, QSplitter,
                            QApplication)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QDate
from PyQt5.QtGui import QFont, QPixmap, QIcon

# Safe import of OptimizedExportService
OptimizedExportService = None
try:
    from src.services.optimized_export_service import OptimizedExportService
except ImportError:
    try:
        from services.optimized_export_service import OptimizedExportService
    except ImportError:
        print("Warning: OptimizedExportService not available")


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
            success = False
            message = "Loại báo cáo không được hỗ trợ"

            try:
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
                    start_date = datetime.combine(self.options.get('start_date'), datetime.min.time())
                    end_date = datetime.combine(self.options.get('end_date'), datetime.min.time())

                    success, message = self.export_service.export_feed_component_report(
                        start_date=start_date,
                        end_date=end_date,
                        selected_regions=self.options.get('selected_regions', []),
                        progress_callback=progress_callback
                    )
                elif self.export_type == "mix_component":
                    start_date = datetime.combine(self.options.get('start_date'), datetime.min.time())
                    end_date = datetime.combine(self.options.get('end_date'), datetime.min.time())

                    success, message = self.export_service.export_mix_component_report(
                        start_date=start_date,
                        end_date=end_date,
                        selected_regions=self.options.get('selected_regions', []),
                        progress_callback=progress_callback
                    )
            except Exception as export_error:
                success = False
                message = f"Lỗi trong quá trình xuất: {str(export_error)}"

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
    """Dialog xuất báo cáo nâng cao với nhiều tính năng tối ưu - Fixed Version"""

    def __init__(self, parent=None, default_type="inventory"):
        super().__init__(parent)
        self.parent_app = parent
        self.default_type = default_type
        self.worker_thread = None
        self.performance_stats = []

        # Ensure QApplication exists
        app = QApplication.instance()
        if app is None:
            print("Warning: No QApplication instance found")

        # Initialize optimized export service with error handling
        self.export_service = None
        self.init_export_service()

        if self.export_service is None:
            self.show_service_error()
            return

        try:
            self.init_ui()
            self.set_default_type()
            self.load_recent_exports()
        except Exception as e:
            self.show_init_error(e)

    def init_export_service(self):
        """Initialize export service with real data managers"""
        if OptimizedExportService is None:
            return

        try:
            # Get data managers from parent app
            inventory_manager = None
            formula_manager = None
            threshold_manager = None
            remaining_usage_calculator = None

            if self.parent_app and hasattr(self.parent_app, 'inventory_manager'):
                inventory_manager = self.parent_app.inventory_manager

            if self.parent_app and hasattr(self.parent_app, 'formula_manager'):
                formula_manager = self.parent_app.formula_manager

            if self.parent_app and hasattr(self.parent_app, 'threshold_manager'):
                threshold_manager = self.parent_app.threshold_manager

            if self.parent_app and hasattr(self.parent_app, 'remaining_usage_calculator'):
                remaining_usage_calculator = self.parent_app.remaining_usage_calculator

            # Initialize export service with real data managers
            self.export_service = OptimizedExportService(
                inventory_manager=inventory_manager,
                formula_manager=formula_manager,
                threshold_manager=threshold_manager,
                remaining_usage_calculator=remaining_usage_calculator
            )
        except Exception as e:
            print(f"Error initializing OptimizedExportService: {e}")
            self.export_service = None

    def show_service_error(self):
        """Show service initialization error"""
        try:
            QMessageBox.critical(
                self,
                "Lỗi Khởi Tạo",
                "Không thể khởi tạo dịch vụ xuất báo cáo.\n\n"
                "Vui lòng kiểm tra:\n"
                "• Cài đặt pandas: pip install pandas\n"
                "• Cài đặt openpyxl: pip install openpyxl\n"
                "• Khởi động lại ứng dụng"
            )
        except:
            print("Error: Cannot initialize export service")

        self.reject()

    def show_init_error(self, error):
        """Show UI initialization error"""
        try:
            QMessageBox.critical(
                self,
                "Lỗi Giao Diện",
                f"Không thể khởi tạo giao diện:\n{str(error)}\n\n"
                "Vui lòng thử lại hoặc khởi động lại ứng dụng."
            )
        except:
            print(f"Error initializing UI: {error}")

        self.reject()

    def init_ui(self):
        """Khởi tạo giao diện nâng cao với error handling"""
        try:
            self.setWindowTitle("Xuất Báo Cáo Excel - Phiên Bản Tối Ưu")
            self.setModal(True)
            self.resize(600, 550)

            # Main layout
            layout = QVBoxLayout()
            layout.setSpacing(15)
            layout.setContentsMargins(20, 20, 20, 20)

            # Header
            self.create_header(layout)

            # Tab widget
            self.create_tabs(layout)

            # Progress section
            self.create_progress_section(layout)

            # Buttons
            self.create_buttons_section(layout)

            self.setLayout(layout)

        except Exception as e:
            raise Exception(f"UI initialization failed: {str(e)}")

    def create_header(self, layout):
        """Tạo header đơn giản"""
        try:
            header_label = QLabel("📊 XUẤT BÁO CÁO EXCEL - PHIÊN BẢN TỐI ƯU")
            header_label.setFont(QFont("Arial", 14, QFont.Bold))
            header_label.setAlignment(Qt.AlignCenter)
            header_label.setStyleSheet("color: #1976D2; padding: 10px;")
            layout.addWidget(header_label)
        except Exception as e:
            print(f"Error creating header: {e}")

    def create_tabs(self, layout):
        """Tạo tab widget đơn giản"""
        try:
            self.tab_widget = QTabWidget()

            # Tab 1: Report Options
            self.create_report_options_tab()

            # Tab 2: Daily Reports (if available)
            try:
                self.create_daily_reports_tab()
            except Exception as e:
                print(f"Warning: Could not create daily reports tab: {e}")

            layout.addWidget(self.tab_widget)

        except Exception as e:
            raise Exception(f"Tab creation failed: {str(e)}")

    def create_report_options_tab(self):
        """Tạo tab tùy chọn báo cáo cơ bản"""
        try:
            tab1 = QWidget()
            tab1_layout = QVBoxLayout()

            # Report type selection
            type_group = QGroupBox("Chọn Loại Báo Cáo")
            type_layout = QVBoxLayout()

            self.report_type_group = QButtonGroup()

            # Basic radio buttons
            self.inventory_radio = QRadioButton("📦 Báo Cáo Tồn Kho")
            self.report_type_group.addButton(self.inventory_radio, 0)
            type_layout.addWidget(self.inventory_radio)

            self.formula_radio = QRadioButton("🧪 Báo Cáo Công Thức")
            self.report_type_group.addButton(self.formula_radio, 1)
            type_layout.addWidget(self.formula_radio)

            self.summary_radio = QRadioButton("📈 Báo Cáo Tổng Hợp")
            self.report_type_group.addButton(self.summary_radio, 2)
            type_layout.addWidget(self.summary_radio)

            # Daily reports (if service supports it)
            if hasattr(self.export_service, 'export_daily_regional_report'):
                self.daily_regional_radio = QRadioButton("🌍 Báo Cáo Hàng Ngày Theo Khu Vực")
                self.report_type_group.addButton(self.daily_regional_radio, 3)
                type_layout.addWidget(self.daily_regional_radio)

                self.feed_component_radio = QRadioButton("🌾 Báo Cáo Thành Phần Cám")
                self.report_type_group.addButton(self.feed_component_radio, 4)
                type_layout.addWidget(self.feed_component_radio)

                self.mix_component_radio = QRadioButton("⚗️ Báo Cáo Thành Phần Mix")
                self.report_type_group.addButton(self.mix_component_radio, 5)
                type_layout.addWidget(self.mix_component_radio)

            type_group.setLayout(type_layout)
            tab1_layout.addWidget(type_group)

            # Warehouse selection
            self.options_group = QGroupBox("Tùy Chọn Kho")
            options_layout = QVBoxLayout()

            self.feed_checkbox = QCheckBox("Kho Cám")
            self.feed_checkbox.setChecked(True)
            options_layout.addWidget(self.feed_checkbox)

            self.mix_checkbox = QCheckBox("Kho Mix")
            self.mix_checkbox.setChecked(True)
            options_layout.addWidget(self.mix_checkbox)

            self.options_group.setLayout(options_layout)
            tab1_layout.addWidget(self.options_group)

            tab1_layout.addStretch()
            tab1.setLayout(tab1_layout)
            self.tab_widget.addTab(tab1, "📋 Tùy Chọn Báo Cáo")

        except Exception as e:
            raise Exception(f"Report options tab creation failed: {str(e)}")

    def create_daily_reports_tab(self):
        """Tạo tab báo cáo hàng ngày (nếu có)"""
        if not hasattr(self.export_service, 'export_daily_regional_report'):
            return

        try:
            tab2 = QWidget()
            tab2_layout = QVBoxLayout()

            # Date range selection
            date_group = QGroupBox("Chọn Khoảng Thời Gian")
            date_layout = QVBoxLayout()

            date_controls_layout = QHBoxLayout()

            date_controls_layout.addWidget(QLabel("Từ ngày:"))
            self.start_date = QDateEdit()
            self.start_date.setDate(QDate.currentDate().addDays(-30))
            self.start_date.setCalendarPopup(True)
            date_controls_layout.addWidget(self.start_date)

            date_controls_layout.addWidget(QLabel("Đến ngày:"))
            self.end_date = QDateEdit()
            self.end_date.setDate(QDate.currentDate())
            self.end_date.setCalendarPopup(True)
            date_controls_layout.addWidget(self.end_date)

            date_layout.addLayout(date_controls_layout)
            date_group.setLayout(date_layout)
            tab2_layout.addWidget(date_group)

            # Region selection - REMOVED per user request
            region_group = QGroupBox("Phạm Vi Báo Cáo")
            region_layout = QVBoxLayout()

            # Add note that all regions will be included
            region_note = QLabel("📊 Báo cáo sẽ bao gồm tất cả khu vực (toàn quốc)")
            region_note.setStyleSheet("color: #666; font-style: italic; padding: 10px;")
            region_layout.addWidget(region_note)

            region_group.setLayout(region_layout)
            tab2_layout.addWidget(region_group)

            # Initialize region_list as None for compatibility
            self.region_list = None

            # Component options
            component_group = QGroupBox("Tùy Chọn Thành Phần")
            component_layout = QVBoxLayout()

            self.daily_include_feed = QCheckBox("Bao gồm thành phần cám")
            self.daily_include_feed.setChecked(True)
            component_layout.addWidget(self.daily_include_feed)

            self.daily_include_mix = QCheckBox("Bao gồm thành phần mix")
            self.daily_include_mix.setChecked(True)
            component_layout.addWidget(self.daily_include_mix)

            component_group.setLayout(component_layout)
            tab2_layout.addWidget(component_group)

            tab2_layout.addStretch()
            tab2.setLayout(tab2_layout)
            self.tab_widget.addTab(tab2, "📅 Báo Cáo Hàng Ngày")

        except Exception as e:
            print(f"Warning: Daily reports tab creation failed: {e}")

    def create_progress_section(self, layout):
        """Tạo phần progress"""
        try:
            self.progress_frame = QFrame()
            self.progress_frame.setVisible(False)
            progress_layout = QVBoxLayout()

            self.progress_bar = QProgressBar()
            progress_layout.addWidget(self.progress_bar)

            self.status_label = QLabel("")
            self.status_label.setAlignment(Qt.AlignCenter)
            progress_layout.addWidget(self.status_label)

            self.progress_frame.setLayout(progress_layout)
            layout.addWidget(self.progress_frame)

        except Exception as e:
            print(f"Warning: Progress section creation failed: {e}")

    def create_buttons_section(self, layout):
        """Tạo phần nút bấm"""
        try:
            button_layout = QHBoxLayout()

            # Export button
            self.export_button = QPushButton("🚀 Xuất Báo Cáo")
            self.export_button.setMinimumHeight(40)
            self.export_button.clicked.connect(self.start_export)
            button_layout.addWidget(self.export_button)

            # Cancel button
            cancel_button = QPushButton("Hủy")
            cancel_button.setMinimumHeight(40)
            cancel_button.clicked.connect(self.reject)
            button_layout.addWidget(cancel_button)

            layout.addLayout(button_layout)

        except Exception as e:
            raise Exception(f"Buttons section creation failed: {str(e)}")

    def set_default_type(self):
        """Đặt loại báo cáo mặc định"""
        try:
            if self.default_type == "formula":
                self.formula_radio.setChecked(True)
            elif self.default_type == "summary":
                self.summary_radio.setChecked(True)
            elif hasattr(self, 'daily_regional_radio') and self.default_type == "daily_regional":
                self.daily_regional_radio.setChecked(True)
            elif hasattr(self, 'feed_component_radio') and self.default_type == "feed_component":
                self.feed_component_radio.setChecked(True)
            elif hasattr(self, 'mix_component_radio') and self.default_type == "mix_component":
                self.mix_component_radio.setChecked(True)
            else:
                self.inventory_radio.setChecked(True)
        except Exception as e:
            print(f"Warning: Could not set default type: {e}")
            if hasattr(self, 'inventory_radio'):
                self.inventory_radio.setChecked(True)

    def load_recent_exports(self):
        """Tải danh sách file gần đây"""
        try:
            if hasattr(self.export_service, 'list_exported_files'):
                recent_files = self.export_service.list_exported_files()
                print(f"Found {len(recent_files)} recent export files")
        except Exception as e:
            print(f"Warning: Could not load recent exports: {e}")

    def get_export_type(self):
        """Lấy loại báo cáo được chọn"""
        try:
            if self.formula_radio.isChecked():
                return "formula"
            elif self.summary_radio.isChecked():
                return "summary"
            elif hasattr(self, 'daily_regional_radio') and self.daily_regional_radio.isChecked():
                return "daily_regional"
            elif hasattr(self, 'feed_component_radio') and self.feed_component_radio.isChecked():
                return "feed_component"
            elif hasattr(self, 'mix_component_radio') and self.mix_component_radio.isChecked():
                return "mix_component"
            else:
                return "inventory"
        except Exception as e:
            print(f"Warning: Could not get export type: {e}")
            return "inventory"

    def get_export_options(self):
        """Lấy tùy chọn xuất"""
        try:
            options = {
                'include_feed': self.feed_checkbox.isChecked(),
                'include_mix': self.mix_checkbox.isChecked()
            }

            # Add daily report options if available
            if hasattr(self, 'daily_include_feed'):
                options.update({
                    'daily_include_feed': self.daily_include_feed.isChecked(),
                    'daily_include_mix': self.daily_include_mix.isChecked(),
                    'start_date': self.start_date.date().toPyDate(),
                    'end_date': self.end_date.date().toPyDate(),
                    'selected_regions': self.get_selected_regions()
                })

            return options
        except Exception as e:
            print(f"Warning: Could not get export options: {e}")
            return {'include_feed': True, 'include_mix': True}

    def get_selected_regions(self) -> List[str]:
        """Lấy danh sách khu vực - ALWAYS return all regions (user removed region selection)"""
        try:
            # User requested to remove region selection
            # Always return all regions for comprehensive reporting
            return ['mien_bac', 'mien_trung', 'mien_nam']
        except Exception as e:
            print(f"Warning: Could not get selected regions: {e}")
            return ['mien_bac', 'mien_trung', 'mien_nam']

    def start_export(self):
        """Bắt đầu xuất báo cáo"""
        try:
            # Get export type
            export_type = self.get_export_type()
            # No need to validate regions since user removed region selection
            # All reports will include all regions by default

            # Update UI
            self.export_button.setEnabled(False)
            if hasattr(self, 'progress_frame'):
                self.progress_frame.setVisible(True)
                self.progress_bar.setValue(0)

            # Get options
            export_options = self.get_export_options()

            # Create and start worker
            self.worker_thread = EnhancedExportWorker(self.export_service, export_type, export_options)
            self.worker_thread.progress_updated.connect(self.on_progress_updated)
            self.worker_thread.status_updated.connect(self.on_status_updated)
            self.worker_thread.export_completed.connect(self.on_export_completed)
            self.worker_thread.start()

        except Exception as e:
            self.export_button.setEnabled(True)
            if hasattr(self, 'progress_frame'):
                self.progress_frame.setVisible(False)
            QMessageBox.critical(self, "Lỗi", f"Không thể bắt đầu xuất báo cáo:\n{str(e)}")

    def on_progress_updated(self, progress):
        """Cập nhật progress"""
        try:
            if hasattr(self, 'progress_bar'):
                self.progress_bar.setValue(progress)
        except Exception as e:
            print(f"Warning: Could not update progress: {e}")

    def on_status_updated(self, status):
        """Cập nhật status"""
        try:
            if hasattr(self, 'status_label'):
                self.status_label.setText(status)
        except Exception as e:
            print(f"Warning: Could not update status: {e}")

    def on_export_completed(self, success, message):
        """Xử lý khi xuất xong"""
        try:
            self.export_button.setEnabled(True)
            if hasattr(self, 'progress_frame'):
                self.progress_frame.setVisible(False)

            if success:
                reply = QMessageBox.question(
                    self,
                    "Thành Công",
                    f"{message}\n\nBạn có muốn mở thư mục chứa file không?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )

                if reply == QMessageBox.Yes:
                    self.open_export_folder()

                self.accept()
            else:
                QMessageBox.critical(self, "Lỗi", f"Xuất báo cáo thất bại:\n{message}")

        except Exception as e:
            print(f"Warning: Could not handle export completion: {e}")

    def open_export_folder(self):
        """Mở thư mục xuất"""
        try:
            if hasattr(self.export_service, 'get_export_directory'):
                export_dir = self.export_service.get_export_directory()
                if os.name == 'nt':  # Windows
                    os.startfile(export_dir)
                elif os.name == 'posix':  # macOS and Linux
                    subprocess.call(['open', export_dir])
        except Exception as e:
            print(f"Warning: Could not open export folder: {e}")
