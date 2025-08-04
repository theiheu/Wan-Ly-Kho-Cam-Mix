#!/usr/bin/env python3
"""
Simple Daily Reports Dialog - Dialog đơn giản cho báo cáo theo ngày, khắc phục lỗi QWidget
"""

import os
import subprocess
from datetime import datetime, timedelta
from typing import List

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                            QGroupBox, QCheckBox, QMessageBox, QProgressBar,
                            QRadioButton, QButtonGroup, QComboBox, QSpinBox,
                            QApplication)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont

# Safe import of OptimizedExportService
OptimizedExportService = None
try:
    from src.services.optimized_export_service import OptimizedExportService
except ImportError:
    try:
        from services.optimized_export_service import OptimizedExportService
    except ImportError:
        print("Warning: OptimizedExportService not available")


class SimpleDailyExportWorker(QThread):
    """Simple worker thread for daily reports"""
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    export_completed = pyqtSignal(bool, str)

    def __init__(self, export_service, export_type, days_back=30, regions=None):
        super().__init__()
        self.export_service = export_service
        self.export_type = export_type
        self.days_back = days_back
        self.regions = regions or ['mien_bac', 'mien_trung', 'mien_nam']

    def run(self):
        """Execute daily report export"""
        try:
            import time
            start_time = time.time()

            # Progress callback
            def progress_callback(progress, status):
                self.progress_updated.emit(progress)
                self.status_updated.emit(status)

            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=self.days_back)

            success = False
            message = "Loại báo cáo không được hỗ trợ"

            try:
                if self.export_type == "daily_regional":
                    success, message = self.export_service.export_daily_regional_report(
                        start_date=start_date,
                        end_date=end_date,
                        selected_regions=self.regions,
                        include_feed=True,
                        include_mix=True,
                        progress_callback=progress_callback
                    )
                elif self.export_type == "feed_component":
                    success, message = self.export_service.export_feed_component_report(
                        start_date=start_date,
                        end_date=end_date,
                        selected_regions=self.regions,
                        progress_callback=progress_callback
                    )
                elif self.export_type == "mix_component":
                    success, message = self.export_service.export_mix_component_report(
                        start_date=start_date,
                        end_date=end_date,
                        selected_regions=self.regions,
                        progress_callback=progress_callback
                    )
            except Exception as export_error:
                success = False
                message = f"Lỗi trong quá trình xuất: {str(export_error)}"

            self.export_completed.emit(success, message)

        except Exception as e:
            self.export_completed.emit(False, f"Lỗi xuất báo cáo: {str(e)}")


class SimpleDailyReportsDialog(QDialog):
    """Dialog đơn giản cho báo cáo theo ngày - Khắc phục lỗi QWidget"""

    def __init__(self, parent=None, default_type="daily_regional"):
        super().__init__(parent)
        self.parent_app = parent
        self.default_type = default_type
        self.worker_thread = None

        # Ensure QApplication exists
        app = QApplication.instance()
        if app is None:
            print("Warning: No QApplication instance found")

        # Initialize export service
        self.export_service = None
        self.init_export_service()

        if self.export_service is None:
            self.show_service_error()
            return

        try:
            self.init_ui()
            self.set_default_type()
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

            # Ensure daily consumption data exists
            self.export_service._ensure_daily_consumption_data()

        except Exception as e:
            print(f"Error initializing OptimizedExportService: {e}")
            self.export_service = None

    def show_service_error(self):
        """Show service initialization error"""
        try:
            QMessageBox.critical(
                self,
                "Lỗi Khởi Tạo",
                "Không thể khởi tạo dịch vụ báo cáo theo ngày.\n\n"
                "Vui lòng kiểm tra:\n"
                "• Cài đặt pandas: pip install pandas\n"
                "• Cài đặt openpyxl: pip install openpyxl\n"
                "• Dữ liệu tiêu thụ hàng ngày"
            )
        except:
            print("Error: Cannot initialize daily reports service")

        self.reject()

    def show_init_error(self, error):
        """Show UI initialization error"""
        try:
            QMessageBox.critical(
                self,
                "Lỗi Giao Diện",
                f"Không thể khởi tạo giao diện báo cáo theo ngày:\n{str(error)}\n\n"
                "Vui lòng thử lại hoặc sử dụng báo cáo truyền thống."
            )
        except:
            print(f"Error initializing daily reports UI: {error}")

        self.reject()

    def init_ui(self):
        """Initialize simple UI for daily reports"""
        try:
            self.setWindowTitle("Báo Cáo Theo Ngày - Phiên Bản Đơn Giản")
            self.setModal(True)
            self.resize(500, 400)

            # Main layout
            layout = QVBoxLayout()
            layout.setSpacing(15)
            layout.setContentsMargins(20, 20, 20, 20)

            # Header
            self.create_header(layout)

            # Report type selection
            self.create_report_type_section(layout)

            # Time range selection
            self.create_time_range_section(layout)

            # Region selection
            self.create_region_section(layout)

            # Progress section
            self.create_progress_section(layout)

            # Buttons
            self.create_buttons_section(layout)

            self.setLayout(layout)

        except Exception as e:
            raise Exception(f"UI initialization failed: {str(e)}")

    def create_header(self, layout):
        """Create simple header"""
        try:
            header_label = QLabel("📅 BÁO CÁO THEO NGÀY")
            header_label.setFont(QFont("Arial", 14, QFont.Bold))
            header_label.setAlignment(Qt.AlignCenter)
            header_label.setStyleSheet("color: #1976D2; padding: 10px;")
            layout.addWidget(header_label)

            desc_label = QLabel("Xuất báo cáo tiêu thụ hàng ngày theo khu vực và thành phần")
            desc_label.setAlignment(Qt.AlignCenter)
            desc_label.setStyleSheet("color: #666; font-style: italic;")
            layout.addWidget(desc_label)

        except Exception as e:
            print(f"Error creating header: {e}")

    def create_report_type_section(self, layout):
        """Create report type selection"""
        try:
            type_group = QGroupBox("Chọn Loại Báo Cáo Theo Ngày")
            type_group.setFont(QFont("Arial", 11, QFont.Bold))
            type_layout = QVBoxLayout()

            self.report_type_group = QButtonGroup()

            # Daily regional report
            self.daily_regional_radio = QRadioButton("🌍 Báo Cáo Hàng Ngày Theo Khu Vực")
            self.daily_regional_radio.setToolTip("Sản lượng và tiêu thụ theo từng khu vực địa lý")
            self.report_type_group.addButton(self.daily_regional_radio, 0)
            type_layout.addWidget(self.daily_regional_radio)

            # Feed component report
            self.feed_component_radio = QRadioButton("🌾 Báo Cáo Thành Phần Cám")
            self.feed_component_radio.setToolTip("Phân tích chi tiết các thành phần dinh dưỡng trong cám")
            self.report_type_group.addButton(self.feed_component_radio, 1)
            type_layout.addWidget(self.feed_component_radio)

            # Mix component report
            self.mix_component_radio = QRadioButton("⚗️ Báo Cáo Thành Phần Mix")
            self.mix_component_radio.setToolTip("Phân tích hiệu quả sử dụng phụ gia và vitamin")
            self.report_type_group.addButton(self.mix_component_radio, 2)
            type_layout.addWidget(self.mix_component_radio)

            type_group.setLayout(type_layout)
            layout.addWidget(type_group)

        except Exception as e:
            raise Exception(f"Report type section creation failed: {str(e)}")

    def create_time_range_section(self, layout):
        """Create simple time range selection"""
        try:
            time_group = QGroupBox("Chọn Khoảng Thời Gian")
            time_group.setFont(QFont("Arial", 11, QFont.Bold))
            time_layout = QVBoxLayout()

            # Simple dropdown for time range
            time_controls_layout = QHBoxLayout()
            time_controls_layout.addWidget(QLabel("Khoảng thời gian:"))

            self.time_range_combo = QComboBox()
            self.time_range_combo.addItem("7 ngày qua", 7)
            self.time_range_combo.addItem("15 ngày qua", 15)
            self.time_range_combo.addItem("30 ngày qua", 30)
            self.time_range_combo.addItem("60 ngày qua", 60)
            self.time_range_combo.setCurrentIndex(2)  # Default to 30 days
            time_controls_layout.addWidget(self.time_range_combo)

            time_controls_layout.addStretch()
            time_layout.addLayout(time_controls_layout)

            time_group.setLayout(time_layout)
            layout.addWidget(time_group)

        except Exception as e:
            raise Exception(f"Time range section creation failed: {str(e)}")

    def create_region_section(self, layout):
        """Create region section - REMOVED per user request"""
        try:
            # User requested to remove region selection
            # Initialize empty region checkboxes for compatibility
            self.region_checkboxes = {}

            # Add a note that region selection has been removed
            note_group = QGroupBox("Phạm Vi Báo Cáo")
            note_group.setFont(QFont("Arial", 11, QFont.Bold))
            note_layout = QVBoxLayout()

            note_label = QLabel("📊 Báo cáo sẽ bao gồm tất cả khu vực (toàn quốc)")
            note_label.setStyleSheet("color: #666; font-style: italic; padding: 10px;")
            note_layout.addWidget(note_label)

            note_group.setLayout(note_layout)
            layout.addWidget(note_group)

        except Exception as e:
            print(f"Warning: Region section creation failed: {e}")
            # Initialize empty for safety
            self.region_checkboxes = {}

    def create_progress_section(self, layout):
        """Create progress section"""
        try:
            self.progress_group = QGroupBox("Tiến Trình")
            self.progress_group.setVisible(False)
            progress_layout = QVBoxLayout()

            self.progress_bar = QProgressBar()
            progress_layout.addWidget(self.progress_bar)

            self.status_label = QLabel("")
            self.status_label.setAlignment(Qt.AlignCenter)
            progress_layout.addWidget(self.status_label)

            self.progress_group.setLayout(progress_layout)
            layout.addWidget(self.progress_group)

        except Exception as e:
            print(f"Warning: Progress section creation failed: {e}")

    def create_buttons_section(self, layout):
        """Create buttons section"""
        try:
            button_layout = QHBoxLayout()

            # Export button
            self.export_button = QPushButton("🚀 Xuất Báo Cáo Theo Ngày")
            self.export_button.setFont(QFont("Arial", 11, QFont.Bold))
            self.export_button.setMinimumHeight(40)
            self.export_button.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
                QPushButton:disabled {
                    background-color: #cccccc;
                }
            """)
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
        """Set default report type"""
        try:
            if self.default_type == "feed_component":
                self.feed_component_radio.setChecked(True)
            elif self.default_type == "mix_component":
                self.mix_component_radio.setChecked(True)
            else:
                self.daily_regional_radio.setChecked(True)
        except Exception as e:
            print(f"Warning: Could not set default type: {e}")
            if hasattr(self, 'daily_regional_radio'):
                self.daily_regional_radio.setChecked(True)

    def get_export_type(self):
        """Get selected export type - Safe version"""
        try:
            # Safe radio button access - use isChecked(), not value()
            if hasattr(self, 'feed_component_radio') and self.feed_component_radio is not None:
                if hasattr(self.feed_component_radio, 'isChecked') and self.feed_component_radio.isChecked():
                    return "feed_component"

            if hasattr(self, 'mix_component_radio') and self.mix_component_radio is not None:
                if hasattr(self.mix_component_radio, 'isChecked') and self.mix_component_radio.isChecked():
                    return "mix_component"

            # Default to daily_regional
            return "daily_regional"
        except Exception as e:
            print(f"Warning: Could not get export type: {e}")
            return "daily_regional"

    def get_selected_regions(self) -> List[str]:
        """Get selected regions - ALWAYS return all regions (user removed region selection)"""
        try:
            # User requested to remove region selection
            # Always return all regions for comprehensive reporting
            selected_regions = ['mien_bac', 'mien_trung', 'mien_nam']
            return selected_regions
        except Exception as e:
            print(f"Warning: Could not get selected regions: {e}")
            return ['mien_bac', 'mien_trung', 'mien_nam']

    def get_days_back(self) -> int:
        """Get selected time range in days - Safe version"""
        try:
            if hasattr(self, 'time_range_combo') and self.time_range_combo is not None:
                # Use currentData() for QComboBox, not value()
                data = self.time_range_combo.currentData()
                if data is not None:
                    return int(data)
                else:
                    # Fallback to currentText parsing
                    text = self.time_range_combo.currentText()
                    if "7 ngày" in text:
                        return 7
                    elif "15 ngày" in text:
                        return 15
                    elif "60 ngày" in text:
                        return 60
                    else:
                        return 30
            else:
                print("Warning: time_range_combo not available")
                return 30
        except Exception as e:
            print(f"Warning: Could not get days back: {e}")
            return 30

    def start_export(self):
        """Start export process - Safe version"""
        try:
            # Get regions (always all regions now since user removed region selection)
            selected_regions = self.get_selected_regions()
            # No need to validate since we always use all regions

            # Update UI safely
            try:
                if hasattr(self, 'export_button') and self.export_button is not None:
                    self.export_button.setEnabled(False)
            except Exception as ui_error:
                print(f"Warning: Could not disable export button: {ui_error}")

            try:
                if hasattr(self, 'progress_group') and self.progress_group is not None:
                    self.progress_group.setVisible(True)
                if hasattr(self, 'progress_bar') and self.progress_bar is not None:
                    # Use setValue() for QProgressBar, not value()
                    self.progress_bar.setValue(0)
            except Exception as progress_error:
                print(f"Warning: Could not update progress UI: {progress_error}")

            # Get parameters safely
            export_type = self.get_export_type()
            days_back = self.get_days_back()

            print(f"Starting export: type={export_type}, days={days_back}, regions={selected_regions}")

            # Create and start worker
            self.worker_thread = SimpleDailyExportWorker(
                self.export_service,
                export_type,
                days_back,
                selected_regions
            )

            # Connect signals safely
            try:
                self.worker_thread.progress_updated.connect(self.on_progress_updated)
                self.worker_thread.status_updated.connect(self.on_status_updated)
                self.worker_thread.export_completed.connect(self.on_export_completed)
            except Exception as signal_error:
                print(f"Warning: Could not connect worker signals: {signal_error}")

            self.worker_thread.start()

        except Exception as e:
            # Restore UI state on error
            try:
                if hasattr(self, 'export_button') and self.export_button is not None:
                    self.export_button.setEnabled(True)
                if hasattr(self, 'progress_group') and self.progress_group is not None:
                    self.progress_group.setVisible(False)
            except:
                pass

            error_msg = f"Không thể bắt đầu xuất báo cáo:\n{str(e)}"
            print(f"Export start error: {error_msg}")
            QMessageBox.critical(self, "Lỗi", error_msg)

    def on_progress_updated(self, progress):
        """Update progress"""
        try:
            if hasattr(self, 'progress_bar'):
                self.progress_bar.setValue(progress)
        except Exception as e:
            print(f"Warning: Could not update progress: {e}")

    def on_status_updated(self, status):
        """Update status"""
        try:
            if hasattr(self, 'status_label'):
                self.status_label.setText(status)
        except Exception as e:
            print(f"Warning: Could not update status: {e}")

    def on_export_completed(self, success, message):
        """Handle export completion"""
        try:
            self.export_button.setEnabled(True)
            if hasattr(self, 'progress_group'):
                self.progress_group.setVisible(False)

            if success:
                reply = QMessageBox.question(
                    self,
                    "Thành Công",
                    f"Xuất báo cáo theo ngày thành công!\n\n{message}\n\n"
                    "Bạn có muốn mở thư mục chứa file không?",
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
        """Open export folder"""
        try:
            if hasattr(self.export_service, 'get_export_directory'):
                export_dir = self.export_service.get_export_directory()
                if os.name == 'nt':  # Windows
                    os.startfile(export_dir)
                elif os.name == 'posix':  # macOS and Linux
                    subprocess.call(['open', export_dir])
        except Exception as e:
            print(f"Warning: Could not open export folder: {e}")
