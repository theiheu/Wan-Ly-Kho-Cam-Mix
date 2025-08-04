#!/usr/bin/env python3
"""
Warehouse Export Dialog - Dialog xuất báo cáo kho hàng
Phiên bản mới được thiết kế đơn giản và đáng tin cậy
"""

import os
import subprocess
import sys
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                            QGroupBox, QCheckBox, QMessageBox, QProgressBar,
                            QRadioButton, QButtonGroup, QFrame, QTextEdit)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPixmap, QIcon

try:
    from src.services.warehouse_export_service import WarehouseExportService
except ImportError:
    try:
        from services.warehouse_export_service import WarehouseExportService
    except ImportError:
        WarehouseExportService = None


class ExportWorkerThread(QThread):
    """Thread worker để xuất báo cáo"""
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
            self.status_updated.emit("Đang khởi tạo...")
            self.progress_updated.emit(10)
            
            self.status_updated.emit("Đang chuẩn bị dữ liệu...")
            self.progress_updated.emit(30)
            
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
            
            self.progress_updated.emit(90)
            self.status_updated.emit("Đang hoàn tất...")
            
            self.progress_updated.emit(100)
            self.export_completed.emit(success, message)
            
        except Exception as e:
            self.export_completed.emit(False, f"Lỗi không mong muốn: {str(e)}")


class WarehouseExportDialog(QDialog):
    """Dialog xuất báo cáo kho hàng"""
    
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
                QMessageBox.critical(self, "Lỗi", f"Không thể khởi tạo dịch vụ xuất báo cáo: {str(e)}")
                self.reject()
                return
        else:
            QMessageBox.critical(self, "Lỗi", "Không thể tải dịch vụ xuất báo cáo")
            self.reject()
            return
        
        self.init_ui()
        self.set_default_type()
    
    def init_ui(self):
        """Khởi tạo giao diện"""
        self.setWindowTitle("Xuất Báo Cáo Kho Hàng")
        self.setModal(True)
        self.resize(500, 450)
        
        # Layout chính
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header với icon
        self.create_header(main_layout)
        
        # Phần chọn loại báo cáo
        self.create_report_type_section(main_layout)
        
        # Phần tùy chọn
        self.create_options_section(main_layout)
        
        # Phần tiến trình
        self.create_progress_section(main_layout)
        
        # Phần thông tin
        self.create_info_section(main_layout)
        
        # Phần nút bấm
        self.create_buttons_section(main_layout)
        
        self.setLayout(main_layout)
    
    def create_header(self, layout):
        """Tạo header"""
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #E3F2FD;
                border: 2px solid #2196F3;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        
        header_layout = QVBoxLayout()
        
        title = QLabel("📊 XUẤT BÁO CÁO KHO HÀNG")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #1976D2; background: transparent; border: none;")
        
        subtitle = QLabel("Tạo báo cáo Excel cho quản lý kho hàng")
        subtitle.setFont(QFont("Arial", 10))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #666; background: transparent; border: none;")
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        header_frame.setLayout(header_layout)
        
        layout.addWidget(header_frame)
    
    def create_report_type_section(self, layout):
        """Tạo phần chọn loại báo cáo"""
        type_group = QGroupBox("Chọn Loại Báo Cáo")
        type_group.setFont(QFont("Arial", 12, QFont.Bold))
        type_layout = QVBoxLayout()
        
        self.report_type_group = QButtonGroup()
        
        # Báo cáo tồn kho
        self.inventory_radio = QRadioButton("📦 Báo Cáo Tồn Kho")
        self.inventory_radio.setFont(QFont("Arial", 11))
        self.inventory_radio.setToolTip("Xuất danh sách nguyên liệu và số lượng tồn kho")
        self.report_type_group.addButton(self.inventory_radio, 0)
        type_layout.addWidget(self.inventory_radio)
        
        # Báo cáo công thức
        self.formula_radio = QRadioButton("🧪 Báo Cáo Công Thức")
        self.formula_radio.setFont(QFont("Arial", 11))
        self.formula_radio.setToolTip("Xuất công thức sản xuất và tỷ lệ nguyên liệu")
        self.report_type_group.addButton(self.formula_radio, 1)
        type_layout.addWidget(self.formula_radio)
        
        # Báo cáo tổng hợp
        self.summary_radio = QRadioButton("📈 Báo Cáo Tổng Hợp")
        self.summary_radio.setFont(QFont("Arial", 11))
        self.summary_radio.setToolTip("Xuất thống kê tổng quan về kho hàng")
        self.report_type_group.addButton(self.summary_radio, 2)
        type_layout.addWidget(self.summary_radio)
        
        type_group.setLayout(type_layout)
        layout.addWidget(type_group)
    
    def create_options_section(self, layout):
        """Tạo phần tùy chọn"""
        self.options_group = QGroupBox("Tùy Chọn Xuất")
        self.options_group.setFont(QFont("Arial", 12, QFont.Bold))
        options_layout = QVBoxLayout()
        
        # Tùy chọn kho
        warehouse_layout = QHBoxLayout()
        warehouse_layout.addWidget(QLabel("Chọn kho:"))
        
        self.feed_checkbox = QCheckBox("Kho Cám")
        self.feed_checkbox.setChecked(True)
        self.feed_checkbox.setToolTip("Bao gồm dữ liệu kho cám")
        warehouse_layout.addWidget(self.feed_checkbox)
        
        self.mix_checkbox = QCheckBox("Kho Mix")
        self.mix_checkbox.setChecked(True)
        self.mix_checkbox.setToolTip("Bao gồm dữ liệu kho mix")
        warehouse_layout.addWidget(self.mix_checkbox)
        
        warehouse_layout.addStretch()
        options_layout.addLayout(warehouse_layout)
        
        # Kết nối sự kiện thay đổi loại báo cáo
        self.report_type_group.buttonClicked.connect(self.on_report_type_changed)
        
        self.options_group.setLayout(options_layout)
        layout.addWidget(self.options_group)
    
    def create_progress_section(self, layout):
        """Tạo phần hiển thị tiến trình"""
        self.progress_frame = QFrame()
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ddd;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("")
        self.status_label.setVisible(False)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        progress_layout.addWidget(self.status_label)
        
        self.progress_frame.setLayout(progress_layout)
        layout.addWidget(self.progress_frame)
    
    def create_info_section(self, layout):
        """Tạo phần thông tin"""
        info_group = QGroupBox("Thông Tin")
        info_group.setFont(QFont("Arial", 10, QFont.Bold))
        info_layout = QVBoxLayout()
        
        export_dir = self.export_service.get_export_directory()
        info_text = f"📁 File sẽ được lưu tại:\n{export_dir}"
        
        exported_files = self.export_service.list_exported_files()
        if exported_files:
            info_text += f"\n\n📄 File gần đây ({len(exported_files)} file):\n"
            for i, filename in enumerate(exported_files[:3]):
                info_text += f"• {filename}\n"
            if len(exported_files) > 3:
                info_text += f"... và {len(exported_files) - 3} file khác"
        
        info_label = QLabel(info_text)
        info_label.setFont(QFont("Arial", 9))
        info_label.setStyleSheet("color: #555; padding: 10px;")
        info_label.setWordWrap(True)
        
        info_layout.addWidget(info_label)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
    
    def create_buttons_section(self, layout):
        """Tạo phần nút bấm"""
        button_layout = QHBoxLayout()
        
        # Nút mở thư mục
        self.open_folder_button = QPushButton("📁 Mở Thư Mục")
        self.open_folder_button.setFont(QFont("Arial", 10))
        self.open_folder_button.setMinimumHeight(35)
        self.open_folder_button.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        self.open_folder_button.clicked.connect(self.open_export_folder)
        button_layout.addWidget(self.open_folder_button)
        
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
        self.cancel_button = QPushButton("Hủy")
        self.cancel_button.setFont(QFont("Arial", 11))
        self.cancel_button.setMinimumHeight(40)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
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
            return True  # Báo cáo tổng hợp không cần kiểm tra
        
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
        self.worker_thread = ExportWorkerThread(self.export_service, export_type, export_options)
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
            # Hiển thị thông báo thành công với tùy chọn mở file
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
            QMessageBox.warning(self, "Cảnh báo", f"Không thể mở thư mục: {str(e)}")
    
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
