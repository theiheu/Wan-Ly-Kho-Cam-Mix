#!/usr/bin/env python3
"""
Simple Warehouse Export Dialog - Dialog xuất báo cáo đơn giản không có lỗi QWidget
"""

import os
import subprocess
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                            QGroupBox, QCheckBox, QMessageBox, QProgressBar,
                            QRadioButton, QButtonGroup)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont

try:
    from src.services.warehouse_export_service import WarehouseExportService
except ImportError:
    try:
        from services.warehouse_export_service import WarehouseExportService
    except ImportError:
        WarehouseExportService = None


class SimpleExportWorker(QThread):
    """Worker thread đơn giản cho xuất báo cáo"""
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    export_completed = pyqtSignal(bool, str)
    
    def __init__(self, export_service, export_type, options):
        super().__init__()
        self.export_service = export_service
        self.export_type = export_type
        self.options = options
    
    def run(self):
        """Thực hiện xuất báo cáo"""
        try:
            self.status_updated.emit("Đang chuẩn bị...")
            self.progress_updated.emit(20)
            
            # Thực hiện xuất theo loại
            if self.export_type == "inventory":
                success, message = self.export_service.export_inventory_report(
                    include_feed=self.options.get('include_feed', True),
                    include_mix=self.options.get('include_mix', True)
                )
            elif self.export_type == "formula":
                success, message = self.export_service.export_formula_report(
                    include_feed=self.options.get('include_feed', True),
                    include_mix=self.options.get('include_mix', True)
                )
            elif self.export_type == "summary":
                success, message = self.export_service.export_summary_report()
            else:
                success, message = False, "Loại báo cáo không được hỗ trợ"
            
            self.progress_updated.emit(100)
            self.export_completed.emit(success, message)
            
        except Exception as e:
            self.export_completed.emit(False, f"Lỗi xuất báo cáo: {str(e)}")


class SimpleWarehouseExportDialog(QDialog):
    """Dialog xuất báo cáo đơn giản"""
    
    def __init__(self, parent=None, default_type="inventory"):
        super().__init__(parent)
        self.parent_app = parent
        self.default_type = default_type
        self.worker_thread = None
        
        # Khởi tạo export service
        if WarehouseExportService:
            try:
                self.export_service = WarehouseExportService()
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể khởi tạo dịch vụ xuất báo cáo:\n{str(e)}")
                self.reject()
                return
        else:
            QMessageBox.critical(self, "Lỗi", "Không thể tải dịch vụ xuất báo cáo.\nVui lòng kiểm tra cài đặt pandas và openpyxl.")
            self.reject()
            return
        
        self.init_ui()
        self.set_default_type()
    
    def init_ui(self):
        """Khởi tạo giao diện đơn giản"""
        self.setWindowTitle("Xuất Báo Cáo Excel")
        self.setModal(True)
        self.resize(400, 350)
        
        # Layout chính
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = QLabel("📊 Xuất Báo Cáo Excel")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("""
            QLabel {
                color: #1976D2;
                padding: 15px;
                background-color: #E3F2FD;
                border-radius: 8px;
                border: 2px solid #2196F3;
            }
        """)
        layout.addWidget(header)
        
        # Chọn loại báo cáo
        type_group = QGroupBox("Chọn Loại Báo Cáo")
        type_group.setFont(QFont("Arial", 12, QFont.Bold))
        type_layout = QVBoxLayout()
        
        self.report_type_group = QButtonGroup()
        
        self.inventory_radio = QRadioButton("📦 Báo Cáo Tồn Kho")
        self.inventory_radio.setFont(QFont("Arial", 11))
        self.report_type_group.addButton(self.inventory_radio, 0)
        type_layout.addWidget(self.inventory_radio)
        
        self.formula_radio = QRadioButton("🧪 Báo Cáo Công Thức")
        self.formula_radio.setFont(QFont("Arial", 11))
        self.report_type_group.addButton(self.formula_radio, 1)
        type_layout.addWidget(self.formula_radio)
        
        self.summary_radio = QRadioButton("📈 Báo Cáo Tổng Hợp")
        self.summary_radio.setFont(QFont("Arial", 11))
        self.report_type_group.addButton(self.summary_radio, 2)
        type_layout.addWidget(self.summary_radio)
        
        type_group.setLayout(type_layout)
        layout.addWidget(type_group)
        
        # Tùy chọn kho
        self.options_group = QGroupBox("Tùy Chọn")
        self.options_group.setFont(QFont("Arial", 12, QFont.Bold))
        options_layout = QVBoxLayout()
        
        self.feed_checkbox = QCheckBox("Bao gồm Kho Cám")
        self.feed_checkbox.setChecked(True)
        options_layout.addWidget(self.feed_checkbox)
        
        self.mix_checkbox = QCheckBox("Bao gồm Kho Mix")
        self.mix_checkbox.setChecked(True)
        options_layout.addWidget(self.mix_checkbox)
        
        self.options_group.setLayout(options_layout)
        layout.addWidget(self.options_group)
        
        # Kết nối sự kiện
        self.report_type_group.buttonClicked.connect(self.on_report_type_changed)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("")
        self.status_label.setVisible(False)
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Thông tin
        info_label = QLabel("📁 File sẽ được lưu trong thư mục src/data/exports/")
        info_label.setFont(QFont("Arial", 9))
        info_label.setStyleSheet("color: #666; padding: 10px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        # Nút mở thư mục
        open_folder_btn = QPushButton("📁 Mở Thư Mục")
        open_folder_btn.setFont(QFont("Arial", 10))
        open_folder_btn.clicked.connect(self.open_export_folder)
        button_layout.addWidget(open_folder_btn)
        
        button_layout.addStretch()
        
        # Nút xuất
        self.export_button = QPushButton("📤 Xuất Báo Cáo")
        self.export_button.setFont(QFont("Arial", 12, QFont.Bold))
        self.export_button.setMinimumHeight(40)
        self.export_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
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
        
        # Nút hủy
        cancel_button = QPushButton("Hủy")
        cancel_button.setFont(QFont("Arial", 11))
        cancel_button.setMinimumHeight(40)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
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
        else:
            self.options_group.setEnabled(True)
    
    def get_export_type(self):
        """Lấy loại báo cáo được chọn"""
        if self.formula_radio.isChecked():
            return "formula"
        elif self.summary_radio.isChecked():
            return "summary"
        else:
            return "inventory"
    
    def get_export_options(self):
        """Lấy tùy chọn xuất"""
        return {
            'include_feed': self.feed_checkbox.isChecked(),
            'include_mix': self.mix_checkbox.isChecked()
        }
    
    def validate_options(self):
        """Kiểm tra tùy chọn"""
        if self.summary_radio.isChecked():
            return True
        
        if not (self.feed_checkbox.isChecked() or self.mix_checkbox.isChecked()):
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn ít nhất một kho để xuất!")
            return False
        
        return True
    
    def start_export(self):
        """Bắt đầu xuất báo cáo"""
        if not self.validate_options():
            return
        
        # Vô hiệu hóa UI
        self.export_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.status_label.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Lấy thông tin xuất
        export_type = self.get_export_type()
        export_options = self.get_export_options()
        
        # Tạo và chạy worker thread
        self.worker_thread = SimpleExportWorker(self.export_service, export_type, export_options)
        self.worker_thread.progress_updated.connect(self.progress_bar.setValue)
        self.worker_thread.status_updated.connect(self.status_label.setText)
        self.worker_thread.export_completed.connect(self.on_export_completed)
        self.worker_thread.start()
    
    def on_export_completed(self, success, message):
        """Xử lý khi xuất xong"""
        # Kích hoạt lại UI
        self.export_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setVisible(False)
        
        if success:
            reply = QMessageBox.question(
                self, 
                "Thành công", 
                f"{message}\n\nBạn có muốn mở thư mục chứa file không?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                self.open_export_folder()
            
            self.accept()
        else:
            QMessageBox.critical(self, "Lỗi", f"Xuất báo cáo thất bại:\n{message}")
    
    def open_export_folder(self):
        """Mở thư mục chứa file xuất"""
        try:
            export_dir = self.export_service.get_export_directory()
            if os.name == 'nt':  # Windows
                os.startfile(export_dir)
            elif os.name == 'posix':  # macOS and Linux
                subprocess.call(['open', export_dir])
        except Exception as e:
            QMessageBox.warning(self, "Cảnh báo", f"Không thể mở thư mục:\n{str(e)}")
    
    def closeEvent(self, event):
        """Xử lý khi đóng dialog"""
        if self.worker_thread and self.worker_thread.isRunning():
            reply = QMessageBox.question(
                self, 
                "Xác nhận", 
                "Đang có tiến trình xuất báo cáo. Bạn có chắc muốn hủy?",
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
