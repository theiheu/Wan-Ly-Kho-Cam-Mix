#!/usr/bin/env python3
"""
Demo script for Responsive Threshold Dialog
Cho phép người dùng test tính năng responsive sizing của dialog ngưỡng tồn kho
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QPushButton, QLabel, QSpinBox, QGroupBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from ui.threshold_settings_dialog import ThresholdSettingsDialog

class ResponsiveDialogDemo(QMainWindow):
    """Demo window để test responsive dialog"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Khởi tạo giao diện demo"""
        self.setWindowTitle("🎯 Demo Responsive Threshold Dialog")
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header = QLabel("🎯 Demo Responsive Threshold Dialog")
        header.setFont(QFont("Arial", 18, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #4CAF50, stop:1 #45a049);
                color: white;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
            }
        """)
        layout.addWidget(header)
        
        # Description
        desc = QLabel(
            "Thử nghiệm tính năng responsive sizing của dialog cài đặt ngưỡng tồn kho.\n"
            "Dialog sẽ tự động điều chỉnh kích thước theo cửa sổ chính:\n"
            "• Chiều rộng: 80% của cửa sổ chính\n"
            "• Chiều cao: 90% của cửa sổ chính\n"
            "• Vị trí: Căn giữa tự động\n"
            "• Kích thước tối thiểu: 1000x800"
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("""
            QLabel {
                background-color: #e3f2fd;
                border: 2px solid #2196f3;
                border-radius: 8px;
                padding: 15px;
                color: #1976d2;
                font-size: 12px;
                line-height: 1.4;
            }
        """)
        layout.addWidget(desc)
        
        # Controls
        self.create_controls(layout)
        
        # Current size display
        self.create_size_display(layout)
        
        # Test button
        test_btn = QPushButton("🚀 Mở Dialog Ngưỡng Tồn Kho")
        test_btn.setMinimumHeight(50)
        test_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #F57C00; }
            QPushButton:pressed { background-color: #E65100; }
        """)
        test_btn.clicked.connect(self.open_threshold_dialog)
        layout.addWidget(test_btn)
        
        layout.addStretch()
        
        # Update size display
        self.update_size_display()
    
    def create_controls(self, layout):
        """Tạo controls để thay đổi kích thước window"""
        controls_group = QGroupBox("🔧 Điều Khiển Kích Thước Cửa Sổ")
        controls_group.setFont(QFont("Arial", 12, QFont.Bold))
        controls_layout = QVBoxLayout(controls_group)
        
        # Preset sizes
        presets_layout = QHBoxLayout()
        
        preset_sizes = [
            (1000, 700, "Nhỏ"),
            (1200, 800, "Vừa"),
            (1600, 1000, "Lớn"),
            (1920, 1080, "Full HD")
        ]
        
        for width, height, name in preset_sizes:
            btn = QPushButton(f"{name}\n{width}x{height}")
            btn.setMinimumHeight(60)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    padding: 10px;
                    border-radius: 6px;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #1976D2; }
            """)
            btn.clicked.connect(lambda checked, w=width, h=height: self.resize_window(w, h))
            presets_layout.addWidget(btn)
        
        controls_layout.addLayout(presets_layout)
        
        # Custom size controls
        custom_layout = QHBoxLayout()
        
        custom_layout.addWidget(QLabel("Tùy chỉnh:"))
        
        custom_layout.addWidget(QLabel("Rộng:"))
        self.width_spin = QSpinBox()
        self.width_spin.setRange(800, 3000)
        self.width_spin.setValue(1200)
        self.width_spin.setSuffix(" px")
        custom_layout.addWidget(self.width_spin)
        
        custom_layout.addWidget(QLabel("Cao:"))
        self.height_spin = QSpinBox()
        self.height_spin.setRange(600, 2000)
        self.height_spin.setValue(800)
        self.height_spin.setSuffix(" px")
        custom_layout.addWidget(self.height_spin)
        
        apply_btn = QPushButton("Áp dụng")
        apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        apply_btn.clicked.connect(self.apply_custom_size)
        custom_layout.addWidget(apply_btn)
        
        custom_layout.addStretch()
        controls_layout.addLayout(custom_layout)
        
        layout.addWidget(controls_group)
    
    def create_size_display(self, layout):
        """Tạo hiển thị kích thước hiện tại"""
        self.size_label = QLabel()
        self.size_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
                color: #495057;
                font-family: 'Courier New', monospace;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.size_label)
    
    def resize_window(self, width, height):
        """Thay đổi kích thước cửa sổ"""
        self.resize(width, height)
        self.width_spin.setValue(width)
        self.height_spin.setValue(height)
        self.update_size_display()
    
    def apply_custom_size(self):
        """Áp dụng kích thước tùy chỉnh"""
        width = self.width_spin.value()
        height = self.height_spin.value()
        self.resize(width, height)
        self.update_size_display()
    
    def update_size_display(self):
        """Cập nhật hiển thị kích thước"""
        size = self.size()
        width = size.width()
        height = size.height()
        
        # Tính toán kích thước dialog dự kiến
        dialog_width = max(int(width * 0.8), 1000)
        dialog_height = max(int(height * 0.9), 800)
        
        display_text = f"""📏 Kích Thước Cửa Sổ Hiện Tại:
   Cửa sổ chính: {width} x {height} px
   
🎯 Kích Thước Dialog Dự Kiến:
   Chiều rộng: {dialog_width} px (80% của {width} px, tối thiểu 1000 px)
   Chiều cao: {dialog_height} px (90% của {height} px, tối thiểu 800 px)
   
📍 Vị trí Dialog:
   Căn giữa tự động so với cửa sổ chính"""
        
        self.size_label.setText(display_text)
    
    def resizeEvent(self, event):
        """Xử lý sự kiện thay đổi kích thước"""
        super().resizeEvent(event)
        self.update_size_display()
    
    def open_threshold_dialog(self):
        """Mở dialog ngưỡng tồn kho"""
        try:
            dialog = ThresholdSettingsDialog(self)
            dialog.exec_()
        except Exception as e:
            print(f"Error opening dialog: {e}")

def main():
    """Chạy demo responsive dialog"""
    app = QApplication(sys.argv)
    
    # Tạo demo window
    demo = ResponsiveDialogDemo()
    demo.show()
    
    print("🎯 Demo Responsive Threshold Dialog")
    print("=" * 50)
    print("Hướng dẫn sử dụng:")
    print("1. Thay đổi kích thước cửa sổ bằng các nút preset hoặc tùy chỉnh")
    print("2. Quan sát thông tin kích thước dialog dự kiến")
    print("3. Nhấn 'Mở Dialog Ngưỡng Tồn Kho' để test")
    print("4. Dialog sẽ tự động điều chỉnh kích thước và căn giữa")
    print("5. Thử với nhiều kích thước khác nhau để test responsive")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
