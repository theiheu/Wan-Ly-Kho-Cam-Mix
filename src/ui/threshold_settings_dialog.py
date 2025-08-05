#!/usr/bin/env python3
"""
Threshold Settings Dialog - Giao diện cài đặt ngưỡng cảnh báo tồn kho
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QSpinBox, QDoubleSpinBox, QCheckBox, QPushButton,
                             QGroupBox, QGridLayout, QMessageBox, QTabWidget,
                             QWidget, QTextEdit, QFrame, QComboBox, QSlider,
                             QTimeEdit, QLineEdit, QColorDialog, QTableWidget,
                             QTableWidgetItem, QHeaderView, QScrollArea)
from PyQt5.QtCore import Qt, QTime
from PyQt5.QtGui import QFont, QIcon, QColor

try:
    from src.core.threshold_manager import ThresholdManager
    from src.core.inventory_manager import InventoryManager
except ImportError:
    from core.threshold_manager import ThresholdManager
    from core.inventory_manager import InventoryManager

class ThresholdSettingsDialog(QDialog):
    """Dialog cài đặt ngưỡng cảnh báo tồn kho"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.threshold_manager = ThresholdManager()
        self.inventory_manager = InventoryManager()
        self.init_ui()
        self.load_current_settings()

    def init_ui(self):
        """Khởi tạo giao diện với kích thước tương đối"""
        self.setWindowTitle("⚙️ Cài Đặt Ngưỡng Tồn Kho - Thống Nhất")
        self.setModal(True)

        # Tính toán kích thước dựa trên parent window
        self.calculate_and_set_size()

        # Main layout với spacing tối ưu
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(25, 25, 25, 25)

        # Header
        header = QLabel("⚙️ Cài Đặt Ngưỡng Cảnh Báo Tồn Kho")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4CAF50, stop:1 #45a049);
                color: white;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(header)

        # Create tabs
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                background: white;
            }
            QTabBar::tab {
                background: #f0f0f0;
                border: 1px solid #ccc;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: #4CAF50;
                color: white;
            }
        """)

        # Tab 1: Cài đặt theo ngày
        self.create_days_tab()

        # Tab 2: Cài đặt theo tồn kho
        self.create_stock_tab()

        # Tab 3: Ngưỡng riêng biệt (di chuyển lên để tạo luồng logic)
        self.create_individual_threshold_tab()

        # Tab 4: Cài đặt ưu tiên
        self.create_priority_tab()

        # Tab 5: Cài đặt hiển thị
        self.create_display_tab()

        # Tab 6: Cài đặt âm thanh
        self.create_sound_tab()

        # Tab 7: Cài đặt tự động
        self.create_automation_tab()

        # Tab 8: Cài đặt màu sắc
        self.create_color_tab()

        layout.addWidget(self.tab_widget)

        # Current settings display
        self.create_current_settings_display(layout)

        # Buttons
        self.create_buttons(layout)

    def calculate_and_set_size(self):
        """Tính toán và đặt kích thước dialog dựa trên parent window"""
        try:
            # Lấy kích thước parent window
            if self.parent():
                parent_size = self.parent().size()
                parent_width = parent_size.width()
                parent_height = parent_size.height()

                # Tính toán kích thước dialog (80% width, 90% height)
                dialog_width = int(parent_width * 0.8)
                dialog_height = int(parent_height * 0.9)

                # Đảm bảo kích thước tối thiểu
                min_width = 1000
                min_height = 800

                dialog_width = max(dialog_width, min_width)
                dialog_height = max(dialog_height, min_height)

                # Đảm bảo không vượt quá kích thước màn hình
                screen = self.parent().screen() if self.parent() else None
                if screen:
                    screen_geometry = screen.availableGeometry()
                    max_width = int(screen_geometry.width() * 0.95)
                    max_height = int(screen_geometry.height() * 0.95)

                    dialog_width = min(dialog_width, max_width)
                    dialog_height = min(dialog_height, max_height)

                # Đặt kích thước tối thiểu và kích thước hiện tại
                self.setMinimumSize(min_width, min_height)
                self.resize(dialog_width, dialog_height)

                # Căn giữa dialog so với parent
                self.center_on_parent()

                print(f"[DEBUG] Dialog size calculated: {dialog_width}x{dialog_height} "
                      f"(parent: {parent_width}x{parent_height})")

            else:
                # Fallback nếu không có parent
                self.setMinimumSize(1000, 800)
                self.resize(1100, 850)
                print("[DEBUG] No parent window, using default size")

        except Exception as e:
            print(f"[ERROR] Error calculating dialog size: {e}")
            # Fallback về kích thước mặc định
            self.setMinimumSize(1000, 800)
            self.resize(1100, 850)

    def center_on_parent(self):
        """Căn giữa dialog so với parent window"""
        try:
            if self.parent():
                parent_geometry = self.parent().geometry()
                dialog_geometry = self.geometry()

                # Tính toán vị trí căn giữa
                x = parent_geometry.x() + (parent_geometry.width() - dialog_geometry.width()) // 2
                y = parent_geometry.y() + (parent_geometry.height() - dialog_geometry.height()) // 2

                # Đảm bảo dialog không ra ngoài màn hình
                screen = self.parent().screen() if self.parent() else None
                if screen:
                    screen_geometry = screen.availableGeometry()
                    x = max(screen_geometry.x(), min(x, screen_geometry.x() + screen_geometry.width() - dialog_geometry.width()))
                    y = max(screen_geometry.y(), min(y, screen_geometry.y() + screen_geometry.height() - dialog_geometry.height()))

                self.move(x, y)
                print(f"[DEBUG] Dialog centered at: {x}, {y}")

        except Exception as e:
            print(f"[ERROR] Error centering dialog: {e}")

    def resizeEvent(self, event):
        """Xử lý sự kiện thay đổi kích thước"""
        super().resizeEvent(event)
        # Có thể thêm logic xử lý khi dialog resize nếu cần

    def showEvent(self, event):
        """Xử lý sự kiện hiển thị dialog"""
        super().showEvent(event)
        # Tính toán lại kích thước khi dialog được hiển thị
        self.calculate_and_set_size()

    def create_days_tab(self):
        """Tạo tab cài đặt theo ngày"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Days-based settings group
        days_group = QGroupBox("📅 Cài Đặt Ngưỡng Theo Số Ngày Còn Lại")
        days_group.setFont(QFont("Arial", 12, QFont.Bold))
        days_layout = QGridLayout(days_group)
        days_layout.setSpacing(10)

        # Critical days
        days_layout.addWidget(QLabel("🔴 Khẩn cấp (ngày):"), 0, 0)
        self.critical_days_spin = QSpinBox()
        self.critical_days_spin.setRange(0, 30)
        self.critical_days_spin.setSuffix(" ngày")
        self.critical_days_spin.setStyleSheet("QSpinBox { padding: 5px; }")
        days_layout.addWidget(self.critical_days_spin, 0, 1)
        days_layout.addWidget(QLabel("Hàng sẽ được coi là khẩn cấp khi còn ít hơn số ngày này"), 0, 2)

        # Warning days
        days_layout.addWidget(QLabel("🟡 Sắp hết (ngày):"), 1, 0)
        self.warning_days_spin = QSpinBox()
        self.warning_days_spin.setRange(1, 60)
        self.warning_days_spin.setSuffix(" ngày")
        self.warning_days_spin.setStyleSheet("QSpinBox { padding: 5px; }")
        days_layout.addWidget(self.warning_days_spin, 1, 1)
        days_layout.addWidget(QLabel("Hàng sẽ được coi là sắp hết khi còn ít hơn số ngày này"), 1, 2)

        # Sufficient days
        days_layout.addWidget(QLabel("🟢 Đủ hàng (ngày):"), 2, 0)
        self.sufficient_days_spin = QSpinBox()
        self.sufficient_days_spin.setRange(1, 90)
        self.sufficient_days_spin.setSuffix(" ngày")
        self.sufficient_days_spin.setStyleSheet("QSpinBox { padding: 5px; }")
        days_layout.addWidget(self.sufficient_days_spin, 2, 1)
        days_layout.addWidget(QLabel("Hàng sẽ được coi là đủ khi còn nhiều hơn số ngày này"), 2, 2)

        layout.addWidget(days_group)

        # Example
        example_label = QLabel("💡 Ví dụ: Nếu đặt Khẩn cấp = 7, Sắp hết = 14, Đủ hàng = 14\n"
                              "-> <7 ngày: Khẩn cấp, 7-14 ngày: Sắp hết, >14 ngày: Đủ hàng")
        example_label.setStyleSheet("""
            QLabel {
                background-color: #e3f2fd;
                border: 1px solid #2196f3;
                border-radius: 6px;
                padding: 10px;
                color: #1976d2;
            }
        """)
        layout.addWidget(example_label)

        layout.addStretch()
        self.tab_widget.addTab(tab, "📅 Theo Ngày")

    def create_stock_tab(self):
        """Tạo tab cài đặt theo tồn kho"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Stock-based settings group
        stock_group = QGroupBox("📦 Cài Đặt Ngưỡng Theo Số Lượng Tồn Kho")
        stock_group.setFont(QFont("Arial", 12, QFont.Bold))
        stock_layout = QGridLayout(stock_group)
        stock_layout.setSpacing(10)

        # Critical stock
        stock_layout.addWidget(QLabel("🔴 Khẩn cấp (kg):"), 0, 0)
        self.critical_stock_spin = QDoubleSpinBox()
        self.critical_stock_spin.setRange(0, 10000)
        self.critical_stock_spin.setSuffix(" kg")
        self.critical_stock_spin.setDecimals(1)
        self.critical_stock_spin.setStyleSheet("QDoubleSpinBox { padding: 5px; }")
        stock_layout.addWidget(self.critical_stock_spin, 0, 1)
        stock_layout.addWidget(QLabel("Hàng sẽ được coi là khẩn cấp khi ≤ số lượng này"), 0, 2)

        # Warning stock
        stock_layout.addWidget(QLabel("🟡 Sắp hết (kg):"), 1, 0)
        self.warning_stock_spin = QDoubleSpinBox()
        self.warning_stock_spin.setRange(0, 10000)
        self.warning_stock_spin.setSuffix(" kg")
        self.warning_stock_spin.setDecimals(1)
        self.warning_stock_spin.setStyleSheet("QDoubleSpinBox { padding: 5px; }")
        stock_layout.addWidget(self.warning_stock_spin, 1, 1)
        stock_layout.addWidget(QLabel("Hàng sẽ được coi là sắp hết khi ≤ số lượng này"), 1, 2)

        # Sufficient stock
        stock_layout.addWidget(QLabel("🟢 Đủ hàng (kg):"), 2, 0)
        self.sufficient_stock_spin = QDoubleSpinBox()
        self.sufficient_stock_spin.setRange(0, 10000)
        self.sufficient_stock_spin.setSuffix(" kg")
        self.sufficient_stock_spin.setDecimals(1)
        self.sufficient_stock_spin.setStyleSheet("QDoubleSpinBox { padding: 5px; }")
        stock_layout.addWidget(self.sufficient_stock_spin, 2, 1)
        stock_layout.addWidget(QLabel("Hàng sẽ được coi là đủ khi > số lượng này"), 2, 2)

        layout.addWidget(stock_group)

        # Example
        example_label = QLabel("💡 Ví dụ: Nếu đặt Khẩn cấp = 0, Sắp hết = 100, Đủ hàng = 500\n"
                              "-> ≤0 kg: Khẩn cấp, ≤100 kg: Sắp hết, >500 kg: Đủ hàng")
        example_label.setStyleSheet("""
            QLabel {
                background-color: #e8f5e9;
                border: 1px solid #4caf50;
                border-radius: 6px;
                padding: 10px;
                color: #2e7d32;
            }
        """)
        layout.addWidget(example_label)

        layout.addStretch()
        self.tab_widget.addTab(tab, "📦 Theo Tồn Kho")

    def create_priority_tab(self):
        """Tạo tab cài đặt ưu tiên"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Priority settings group
        priority_group = QGroupBox("🎯 Cài Đặt Ưu Tiên Đánh Giá")
        priority_group.setFont(QFont("Arial", 12, QFont.Bold))
        priority_layout = QVBoxLayout(priority_group)
        priority_layout.setSpacing(15)

        # Days-based priority
        self.use_days_checkbox = QCheckBox("📅 Ưu tiên đánh giá theo số ngày còn lại")
        self.use_days_checkbox.setFont(QFont("Arial", 11))
        self.use_days_checkbox.setStyleSheet("QCheckBox { padding: 5px; }")
        priority_layout.addWidget(self.use_days_checkbox)

        days_desc = QLabel("   -> Sử dụng dữ liệu tiêu thụ để tính số ngày còn lại và đánh giá trạng thái")
        days_desc.setStyleSheet("color: #666; margin-left: 20px;")
        priority_layout.addWidget(days_desc)

        # Stock-based priority
        self.use_stock_checkbox = QCheckBox("📦 Sử dụng đánh giá theo số lượng tồn kho")
        self.use_stock_checkbox.setFont(QFont("Arial", 11))
        self.use_stock_checkbox.setStyleSheet("QCheckBox { padding: 5px; }")
        priority_layout.addWidget(self.use_stock_checkbox)

        stock_desc = QLabel("   -> Sử dụng số lượng tồn kho hiện tại để đánh giá trạng thái")
        stock_desc.setStyleSheet("color: #666; margin-left: 20px;")
        priority_layout.addWidget(stock_desc)

        layout.addWidget(priority_group)

        # Logic explanation
        logic_group = QGroupBox("🔍 Logic Đánh Giá")
        logic_group.setFont(QFont("Arial", 12, QFont.Bold))
        logic_layout = QVBoxLayout(logic_group)

        logic_text = QTextEdit()
        logic_text.setReadOnly(True)
        logic_text.setMaximumHeight(120)
        logic_text.setPlainText(
            "* Nếu chọn 'Ưu tiên theo ngày': Hệ thống sẽ ưu tiên sử dụng số ngày còn lại để đánh giá\n"
            "* Nếu không có dữ liệu ngày hoặc chọn 'Theo tồn kho': Sử dụng số lượng tồn kho\n"
            "* Có thể chọn cả hai để có đánh giá toàn diện\n"
            "* Khuyến nghị: Chọn 'Ưu tiên theo ngày' để có đánh giá chính xác hơn"
        )
        logic_text.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 6px;
                padding: 10px;
                color: #333;
            }
        """)
        logic_layout.addWidget(logic_text)
        layout.addWidget(logic_group)

        layout.addStretch()
        self.tab_widget.addTab(tab, "🎯 Ưu Tiên")

    def create_display_tab(self):
        """Tạo tab cài đặt hiển thị"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Display unit settings
        unit_group = QGroupBox("📊 Đơn Vị Hiển Thị")
        unit_group.setFont(QFont("Arial", 12, QFont.Bold))
        unit_layout = QGridLayout(unit_group)
        unit_layout.setSpacing(10)

        # Display unit combo
        unit_layout.addWidget(QLabel("Đơn vị ưu tiên:"), 0, 0)
        self.display_unit_combo = QComboBox()
        self.display_unit_combo.addItem("Cả ngày và kg", "both")
        self.display_unit_combo.addItem("Chỉ ngày", "days")
        self.display_unit_combo.addItem("Chỉ kg", "stock")
        self.display_unit_combo.setStyleSheet("QComboBox { padding: 5px; }")
        unit_layout.addWidget(self.display_unit_combo, 0, 1)

        # Show options
        self.show_days_checkbox = QCheckBox("📅 Hiển thị số ngày còn lại trong bảng")
        self.show_days_checkbox.setStyleSheet("QCheckBox { padding: 5px; }")
        unit_layout.addWidget(self.show_days_checkbox, 1, 0, 1, 2)

        self.show_stock_checkbox = QCheckBox("📦 Hiển thị số lượng tồn kho trong bảng")
        self.show_stock_checkbox.setStyleSheet("QCheckBox { padding: 5px; }")
        unit_layout.addWidget(self.show_stock_checkbox, 2, 0, 1, 2)

        layout.addWidget(unit_group)

        # Info
        info_label = QLabel("💡 Cài đặt này ảnh hưởng đến cách hiển thị thông tin trong bảng tồn kho")
        info_label.setStyleSheet("""
            QLabel {
                background-color: #e3f2fd;
                border: 1px solid #2196f3;
                border-radius: 6px;
                padding: 10px;
                color: #1976d2;
            }
        """)
        layout.addWidget(info_label)

        layout.addStretch()
        self.tab_widget.addTab(tab, "📊 Hiển Thị")

    def create_sound_tab(self):
        """Tạo tab cài đặt âm thanh"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Sound settings
        sound_group = QGroupBox("🔊 Cài Đặt Âm Thanh Cảnh Báo")
        sound_group.setFont(QFont("Arial", 12, QFont.Bold))
        sound_layout = QGridLayout(sound_group)
        sound_layout.setSpacing(10)

        # Enable sound
        self.sound_enabled_checkbox = QCheckBox("🔊 Bật âm thanh cảnh báo")
        self.sound_enabled_checkbox.setFont(QFont("Arial", 11, QFont.Bold))
        self.sound_enabled_checkbox.setStyleSheet("QCheckBox { padding: 5px; }")
        sound_layout.addWidget(self.sound_enabled_checkbox, 0, 0, 1, 2)

        # Critical sound
        self.sound_critical_checkbox = QCheckBox("🔴 Âm thanh cho cảnh báo khẩn cấp")
        self.sound_critical_checkbox.setStyleSheet("QCheckBox { padding: 5px; }")
        sound_layout.addWidget(self.sound_critical_checkbox, 1, 0, 1, 2)

        # Warning sound
        self.sound_warning_checkbox = QCheckBox("🟡 Âm thanh cho cảnh báo sắp hết")
        self.sound_warning_checkbox.setStyleSheet("QCheckBox { padding: 5px; }")
        sound_layout.addWidget(self.sound_warning_checkbox, 2, 0, 1, 2)

        # Volume
        sound_layout.addWidget(QLabel("🔊 Âm lượng:"), 3, 0)
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #B1B1B1, stop:1 #c4c4c4);
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #b4b4b4, stop:1 #8f8f8f);
                border: 1px solid #5c5c5c;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }
        """)
        sound_layout.addWidget(self.volume_slider, 3, 1)

        self.volume_label = QLabel("50%")
        self.volume_label.setMinimumWidth(40)
        sound_layout.addWidget(self.volume_label, 3, 2)

        # Connect volume slider
        self.volume_slider.valueChanged.connect(lambda v: self.volume_label.setText(f"{v}%"))

        layout.addWidget(sound_group)

        # Test button
        test_btn = QPushButton("🎵 Test Âm Thanh")
        test_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196f3;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #1976d2; }
        """)
        test_btn.clicked.connect(self.test_sound)
        layout.addWidget(test_btn)

        layout.addStretch()
        self.tab_widget.addTab(tab, "🔊 Âm Thanh")

    def create_automation_tab(self):
        """Tạo tab cài đặt tự động"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Auto check settings
        check_group = QGroupBox("⏰ Kiểm Tra Tự Động")
        check_group.setFont(QFont("Arial", 12, QFont.Bold))
        check_layout = QGridLayout(check_group)
        check_layout.setSpacing(10)

        # Enable auto check
        self.auto_check_checkbox = QCheckBox("⏰ Bật kiểm tra tồn kho tự động")
        self.auto_check_checkbox.setFont(QFont("Arial", 11, QFont.Bold))
        self.auto_check_checkbox.setStyleSheet("QCheckBox { padding: 5px; }")
        check_layout.addWidget(self.auto_check_checkbox, 0, 0, 1, 2)

        # Check frequency
        check_layout.addWidget(QLabel("Tần suất:"), 1, 0)
        self.check_frequency_combo = QComboBox()
        self.check_frequency_combo.addItem("Chỉ khi khởi động", "startup_only")
        self.check_frequency_combo.addItem("Mỗi giờ", "hourly")
        self.check_frequency_combo.addItem("Mỗi ngày", "daily")
        self.check_frequency_combo.setStyleSheet("QComboBox { padding: 5px; }")
        check_layout.addWidget(self.check_frequency_combo, 1, 1)

        # Check interval
        check_layout.addWidget(QLabel("Khoảng cách (giờ):"), 2, 0)
        self.check_interval_spin = QSpinBox()
        self.check_interval_spin.setRange(1, 24)
        self.check_interval_spin.setValue(1)
        self.check_interval_spin.setSuffix(" giờ")
        self.check_interval_spin.setStyleSheet("QSpinBox { padding: 5px; }")
        check_layout.addWidget(self.check_interval_spin, 2, 1)

        layout.addWidget(check_group)

        # Popup settings
        popup_group = QGroupBox("🔔 Cài Đặt Popup")
        popup_group.setFont(QFont("Arial", 12, QFont.Bold))
        popup_layout = QVBoxLayout(popup_group)
        popup_layout.setSpacing(10)

        self.popup_enabled_checkbox = QCheckBox("🔔 Bật popup cảnh báo")
        self.popup_enabled_checkbox.setFont(QFont("Arial", 11, QFont.Bold))
        self.popup_enabled_checkbox.setStyleSheet("QCheckBox { padding: 5px; }")
        popup_layout.addWidget(self.popup_enabled_checkbox)

        self.popup_startup_checkbox = QCheckBox("🚀 Hiển thị popup khi khởi động ứng dụng")
        self.popup_startup_checkbox.setStyleSheet("QCheckBox { padding: 5px; }")
        popup_layout.addWidget(self.popup_startup_checkbox)

        self.popup_critical_checkbox = QCheckBox("🔴 Popup cho cảnh báo khẩn cấp")
        self.popup_critical_checkbox.setStyleSheet("QCheckBox { padding: 5px; }")
        popup_layout.addWidget(self.popup_critical_checkbox)

        self.popup_warning_checkbox = QCheckBox("🟡 Popup cho cảnh báo sắp hết")
        self.popup_warning_checkbox.setStyleSheet("QCheckBox { padding: 5px; }")
        popup_layout.addWidget(self.popup_warning_checkbox)

        layout.addWidget(popup_group)

        # Auto report settings
        report_group = QGroupBox("📊 Báo Cáo Tự Động")
        report_group.setFont(QFont("Arial", 12, QFont.Bold))
        report_layout = QGridLayout(report_group)
        report_layout.setSpacing(10)

        # Enable auto report
        self.auto_report_checkbox = QCheckBox("📊 Bật xuất báo cáo tự động")
        self.auto_report_checkbox.setFont(QFont("Arial", 11, QFont.Bold))
        self.auto_report_checkbox.setStyleSheet("QCheckBox { padding: 5px; }")
        report_layout.addWidget(self.auto_report_checkbox, 0, 0, 1, 2)

        # Report frequency
        report_layout.addWidget(QLabel("Tần suất:"), 1, 0)
        self.report_frequency_combo = QComboBox()
        self.report_frequency_combo.addItem("Hàng ngày", "daily")
        self.report_frequency_combo.addItem("Hàng tuần", "weekly")
        self.report_frequency_combo.addItem("Hàng tháng", "monthly")
        self.report_frequency_combo.setStyleSheet("QComboBox { padding: 5px; }")
        report_layout.addWidget(self.report_frequency_combo, 1, 1)

        # Report time
        report_layout.addWidget(QLabel("Thời gian:"), 2, 0)
        self.report_time_edit = QTimeEdit()
        self.report_time_edit.setTime(QTime(8, 0))
        self.report_time_edit.setDisplayFormat("HH:mm")
        self.report_time_edit.setStyleSheet("QTimeEdit { padding: 5px; }")
        report_layout.addWidget(self.report_time_edit, 2, 1)

        # Report path
        report_layout.addWidget(QLabel("Thư mục lưu:"), 3, 0)
        self.report_path_edit = QLineEdit()
        self.report_path_edit.setText("reports/alerts")
        self.report_path_edit.setStyleSheet("QLineEdit { padding: 5px; }")
        report_layout.addWidget(self.report_path_edit, 3, 1)

        layout.addWidget(report_group)

        layout.addStretch()
        self.tab_widget.addTab(tab, "⚙️ Tự Động")

    def create_color_tab(self):
        """Tạo tab cài đặt màu sắc"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Color settings
        color_group = QGroupBox("🎨 Cài Đặt Màu Sắc")
        color_group.setFont(QFont("Arial", 12, QFont.Bold))
        color_layout = QGridLayout(color_group)
        color_layout.setSpacing(10)

        # Enable custom colors
        self.use_custom_colors_checkbox = QCheckBox("🎨 Sử dụng màu sắc tùy chỉnh")
        self.use_custom_colors_checkbox.setFont(QFont("Arial", 11, QFont.Bold))
        self.use_custom_colors_checkbox.setStyleSheet("QCheckBox { padding: 5px; }")
        color_layout.addWidget(self.use_custom_colors_checkbox, 0, 0, 1, 3)

        # Color buttons
        self.color_buttons = {}
        color_settings = [
            ("critical", "🔴 Khẩn cấp", "#f44336"),
            ("warning", "🟡 Sắp hết", "#ff9800"),
            ("sufficient", "🟢 Đủ hàng", "#4caf50"),
            ("no_data", "⚪ Không có dữ liệu", "#9e9e9e")
        ]

        for i, (key, label, default_color) in enumerate(color_settings):
            color_layout.addWidget(QLabel(label), i + 1, 0)

            color_btn = QPushButton()
            color_btn.setFixedSize(50, 30)
            color_btn.setStyleSheet(f"background-color: {default_color}; border: 2px solid #ccc; border-radius: 4px;")
            color_btn.clicked.connect(lambda checked, k=key: self.choose_color(k))
            color_layout.addWidget(color_btn, i + 1, 1)

            self.color_buttons[key] = color_btn

            # Reset button
            reset_btn = QPushButton("🔄 Mặc định")
            reset_btn.setStyleSheet("""
                QPushButton {
                    background-color: #9e9e9e;
                    color: white;
                    border: none;
                    padding: 5px 10px;
                    border-radius: 4px;
                }
                QPushButton:hover { background-color: #757575; }
            """)
            reset_btn.clicked.connect(lambda checked, k=key, c=default_color: self.reset_color(k, c))
            color_layout.addWidget(reset_btn, i + 1, 2)

        layout.addWidget(color_group)

        # Preview
        preview_group = QGroupBox("👁️ Xem Trước")
        preview_group.setFont(QFont("Arial", 12, QFont.Bold))
        preview_layout = QVBoxLayout(preview_group)

        self.color_preview_label = QLabel("Xem trước màu sắc sẽ được hiển thị ở đây")
        self.color_preview_label.setStyleSheet("""
            QLabel {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 6px;
                padding: 20px;
                text-align: center;
            }
        """)
        preview_layout.addWidget(self.color_preview_label)

        layout.addWidget(preview_group)

        layout.addStretch()
        self.tab_widget.addTab(tab, "🎨 Màu Sắc")

    def create_individual_threshold_tab(self):
        """Tạo tab ngưỡng riêng biệt với giao diện gọn gàng, tập trung vào chức năng"""
        tab = QWidget()
        main_layout = QVBoxLayout(tab)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Main content trong scroll area để responsive tốt hơn
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #f0f0f0;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #c0c0c0;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #a0a0a0;
            }
        """)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(20)
        scroll_layout.setContentsMargins(0, 0, 0, 0)

        # Control panel với thiết kế card-based
        self.create_individual_control_panel_improved(scroll_layout)

        # Table với thiết kế cải thiện
        self.create_individual_table_improved(scroll_layout)

        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        self.tab_widget.addTab(tab, "🎯 Ngưỡng Riêng Biệt")

    def create_individual_control_panel_improved(self, layout):
        """Tạo panel điều khiển với thiết kế card-based cải thiện"""
        # Main control card
        control_card = QFrame()
        control_card.setFrameShape(QFrame.Box)
        control_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #e9ecef;
                border-radius: 15px;
                padding: 20px;
            }
        """)

        control_layout = QVBoxLayout(control_card)
        control_layout.setSpacing(25)
        control_layout.setContentsMargins(30, 30, 30, 30)

        # Header với mode indicator
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)

        title_label = QLabel("🔧 Cài Đặt Ngưỡng")
        title_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 18px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        header_layout.addWidget(title_label)

        # Mode indicator
        self.mode_indicator = QLabel("➕ Thêm mới")
        self.mode_indicator.setStyleSheet("""
            QLabel {
                background-color: #28a745;
                color: white;
                padding: 8px 15px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: bold;
            }
        """)
        header_layout.addWidget(self.mode_indicator)
        header_layout.addStretch()

        control_layout.addLayout(header_layout)

        # Ingredient selection section
        self.create_ingredient_selection_section(control_layout)

        # Threshold settings section
        self.create_threshold_settings_section(control_layout)

        # Action buttons section
        self.create_action_buttons_section(control_layout)

        layout.addWidget(control_card)

    def create_ingredient_selection_section(self, layout):
        """Tạo section chọn nguyên liệu"""
        section_frame = QFrame()
        section_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 10px;
                padding: 15px;
            }
        """)

        section_layout = QVBoxLayout(section_frame)
        section_layout.setSpacing(15)
        section_layout.setContentsMargins(20, 20, 20, 20)

        # Section title
        title = QLabel("📦 Chọn Nguyên Liệu")
        title.setStyleSheet("""
            QLabel {
                color: #495057;
                font-size: 14px;
                font-weight: bold;
                margin-bottom: 5px;
            }
        """)
        section_layout.addWidget(title)

        # Ingredient combo với search functionality
        combo_layout = QHBoxLayout()
        combo_layout.setSpacing(10)

        self.individual_ingredient_combo = QComboBox()
        self.individual_ingredient_combo.setEditable(True)
        self.individual_ingredient_combo.setMinimumHeight(45)
        self.individual_ingredient_combo.setStyleSheet("""
            QComboBox {
                padding: 12px 15px;
                font-size: 14px;
                border: 2px solid #ced4da;
                border-radius: 8px;
                background-color: white;
                selection-background-color: #007bff;
            }
            QComboBox:focus {
                border-color: #007bff;
                outline: none;
            }
            QComboBox::drop-down {
                width: 35px;
                border: none;
                background-color: #f8f9fa;
                border-top-right-radius: 8px;
                border-bottom-right-radius: 8px;
            }
            QComboBox::down-arrow {
                image: none;
                border: 2px solid #6c757d;
                width: 8px;
                height: 8px;
                border-top: none;
                border-left: none;
                transform: rotate(45deg);
            }
        """)
        combo_layout.addWidget(self.individual_ingredient_combo, 1)

        # Clear button
        clear_btn = QPushButton("🗑️")
        clear_btn.setMinimumSize(45, 45)
        clear_btn.setMaximumSize(45, 45)
        clear_btn.setToolTip("Xóa lựa chọn")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
            QPushButton:pressed {
                background-color: #545b62;
            }
        """)
        clear_btn.clicked.connect(lambda: self.individual_ingredient_combo.setCurrentText(""))
        combo_layout.addWidget(clear_btn)

        section_layout.addLayout(combo_layout)

        # Help text
        help_text = QLabel("💡 Chọn từ danh sách hoặc nhập tên nguyên liệu mới")
        help_text.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 12px;
                font-style: italic;
            }
        """)
        section_layout.addWidget(help_text)

        layout.addWidget(section_frame)

    def create_threshold_settings_section(self, layout):
        """Tạo section cài đặt ngưỡng với thiết kế card"""
        # Container cho 2 cards
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)

        # Days threshold card
        days_card = self.create_threshold_card(
            "📅", "Ngưỡng Theo Ngày",
            [
                ("🔴 Khẩn cấp", "critical_days", "ngày", 0, 30, 7),
                ("🟡 Sắp hết", "warning_days", "ngày", 1, 60, 14)
            ]
        )
        cards_layout.addWidget(days_card)

        # Stock threshold card
        stock_card = self.create_threshold_card(
            "📦", "Ngưỡng Theo Tồn Kho",
            [
                ("🔴 Khẩn cấp", "critical_stock", "kg", 0, 10000, 0),
                ("🟡 Sắp hết", "warning_stock", "kg", 0, 10000, 100)
            ]
        )
        cards_layout.addWidget(stock_card)

        layout.addLayout(cards_layout)

    def create_threshold_card(self, icon, title, fields):
        """Tạo card cho một loại ngưỡng"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #e9ecef;
                border-radius: 12px;
                padding: 15px;
            }
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(20)
        card_layout.setContentsMargins(20, 20, 20, 20)

        # Card header
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 20px;")
        header_layout.addWidget(icon_label)

        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                color: #495057;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        card_layout.addLayout(header_layout)

        # Fields
        for label_text, field_name, suffix, min_val, max_val, default_val in fields:
            field_layout = QVBoxLayout()
            field_layout.setSpacing(8)

            # Label
            label = QLabel(label_text)
            label.setStyleSheet("""
                QLabel {
                    color: #6c757d;
                    font-size: 12px;
                    font-weight: 600;
                }
            """)
            field_layout.addWidget(label)

            # Input
            if "stock" in field_name:
                spin_box = QDoubleSpinBox()
                spin_box.setDecimals(1)
            else:
                spin_box = QSpinBox()

            spin_box.setRange(min_val, max_val)
            spin_box.setValue(default_val)
            spin_box.setSuffix(f" {suffix}")
            spin_box.setMinimumHeight(40)
            spin_box.setStyleSheet("""
                QSpinBox, QDoubleSpinBox {
                    padding: 10px 12px;
                    font-size: 14px;
                    font-weight: 500;
                    border: 2px solid #ced4da;
                    border-radius: 8px;
                    background-color: white;
                }
                QSpinBox:focus, QDoubleSpinBox:focus {
                    border-color: #007bff;
                    outline: none;
                }
                QSpinBox::up-button, QDoubleSpinBox::up-button,
                QSpinBox::down-button, QDoubleSpinBox::down-button {
                    width: 25px;
                    height: 15px;
                    border: none;
                    background-color: #f8f9fa;
                }
                QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
                QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
                    background-color: #e9ecef;
                }
            """)

            # Store reference to spin box
            setattr(self, f"individual_{field_name}_spin", spin_box)
            field_layout.addWidget(spin_box)

            card_layout.addLayout(field_layout)

        return card

    def create_action_buttons_section(self, layout):
        """Tạo section các nút hành động"""
        buttons_frame = QFrame()
        buttons_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 10px;
                padding: 15px;
            }
        """)

        buttons_layout = QHBoxLayout(buttons_frame)
        buttons_layout.setSpacing(15)
        buttons_layout.setContentsMargins(20, 15, 20, 15)

        # Primary action button
        self.add_update_btn = QPushButton("➕ Thêm Ngưỡng")
        self.add_update_btn.setMinimumHeight(45)
        self.add_update_btn.setMinimumWidth(150)
        self.add_update_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #218838;
                transform: translateY(-1px);
            }
            QPushButton:pressed {
                background-color: #1e7e34;
                transform: translateY(0px);
            }
        """)
        self.add_update_btn.clicked.connect(self.add_or_update_individual_threshold)
        buttons_layout.addWidget(self.add_update_btn)

        # Secondary buttons
        remove_btn = QPushButton("🗑️ Xóa")
        remove_btn.setMinimumHeight(45)
        remove_btn.setMinimumWidth(100)
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c82333;
                transform: translateY(-1px);
            }
            QPushButton:pressed {
                background-color: #bd2130;
                transform: translateY(0px);
            }
        """)
        remove_btn.clicked.connect(self.remove_individual_threshold)
        buttons_layout.addWidget(remove_btn)

        clear_all_btn = QPushButton("🗑️ Xóa Tất Cả")
        clear_all_btn.setMinimumHeight(45)
        clear_all_btn.setMinimumWidth(120)
        clear_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #5a6268;
                transform: translateY(-1px);
            }
            QPushButton:pressed {
                background-color: #545b62;
                transform: translateY(0px);
            }
        """)
        clear_all_btn.clicked.connect(self.clear_all_individual_thresholds)
        buttons_layout.addWidget(clear_all_btn)

        # Reset button
        reset_btn = QPushButton("🔄 Đặt Lại")
        reset_btn.setMinimumHeight(45)
        reset_btn.setMinimumWidth(100)
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #138496;
                transform: translateY(-1px);
            }
            QPushButton:pressed {
                background-color: #117a8b;
                transform: translateY(0px);
            }
        """)
        reset_btn.clicked.connect(self.reset_individual_form)
        buttons_layout.addWidget(reset_btn)

        buttons_layout.addStretch()
        layout.addWidget(buttons_frame)

    def create_individual_table_improved(self, layout):
        """Tạo bảng hiển thị với thiết kế cải thiện"""
        table_card = QFrame()
        table_card.setFrameShape(QFrame.Box)
        table_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #e9ecef;
                border-radius: 15px;
                padding: 20px;
            }
        """)

        table_layout = QVBoxLayout(table_card)
        table_layout.setSpacing(20)
        table_layout.setContentsMargins(25, 25, 25, 25)

        # Table header
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)

        title = QLabel("📊 Danh Sách Ngưỡng Riêng Biệt")
        title.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 18px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        header_layout.addWidget(title)

        # Search box
        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)

        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("font-size: 16px; color: #6c757d;")
        search_layout.addWidget(search_icon)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Tìm kiếm nguyên liệu...")
        self.search_box.setMinimumHeight(35)
        self.search_box.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                font-size: 14px;
                border: 2px solid #ced4da;
                border-radius: 8px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #007bff;
                outline: none;
            }
        """)
        self.search_box.textChanged.connect(self.filter_individual_table)
        search_layout.addWidget(self.search_box)

        header_layout.addLayout(search_layout)
        header_layout.addStretch()

        table_layout.addLayout(header_layout)

        # Table
        self.individual_table = QTableWidget()
        self.individual_table.setColumnCount(6)
        self.individual_table.setHorizontalHeaderLabels([
            "Thành phần", "🔴 Khẩn cấp\n(ngày)", "🟡 Sắp hết\n(ngày)",
            "🔴 Khẩn cấp\n(kg)", "🟡 Sắp hết\n(kg)", "Trạng thái\nhiện tại"
        ])

        # Enhanced table styling
        self.individual_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #e9ecef;
                selection-background-color: #e3f2fd;
                alternate-background-color: #f8f9fa;
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                font-size: 13px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #007bff, stop:1 #0056b3);
                color: white;
                padding: 12px 8px;
                border: 1px solid #0056b3;
                font-weight: bold;
                font-size: 12px;
                text-align: center;
            }
            QTableWidget::item {
                padding: 12px 8px;
                border-bottom: 1px solid #f1f3f4;
                text-align: center;
                font-size: 13px;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
                font-weight: 600;
            }
            QTableWidget::item:hover {
                background-color: #f5f5f5;
            }
        """)

        # Table configuration
        header = self.individual_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Ingredient name
        header.setSectionResizeMode(1, QHeaderView.Fixed)    # Critical days
        header.setSectionResizeMode(2, QHeaderView.Fixed)    # Warning days
        header.setSectionResizeMode(3, QHeaderView.Fixed)    # Critical stock
        header.setSectionResizeMode(4, QHeaderView.Fixed)    # Warning stock
        header.setSectionResizeMode(5, QHeaderView.Fixed)    # Status

        # Set column widths
        self.individual_table.setColumnWidth(1, 110)
        self.individual_table.setColumnWidth(2, 110)
        self.individual_table.setColumnWidth(3, 110)
        self.individual_table.setColumnWidth(4, 110)
        self.individual_table.setColumnWidth(5, 130)

        # Row configuration
        self.individual_table.verticalHeader().setDefaultSectionSize(50)
        self.individual_table.verticalHeader().setVisible(False)
        self.individual_table.setMinimumHeight(300)
        self.individual_table.setAlternatingRowColors(True)
        self.individual_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.individual_table.itemSelectionChanged.connect(self.on_individual_table_selection_changed_improved)

        table_layout.addWidget(self.individual_table)

        # Table footer với thông tin
        footer_layout = QHBoxLayout()
        footer_layout.setSpacing(20)

        self.table_info_label = QLabel("Tổng: 0 ngưỡng riêng biệt")
        self.table_info_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 12px;
                font-style: italic;
            }
        """)
        footer_layout.addWidget(self.table_info_label)

        footer_layout.addStretch()

        # Export button
        export_btn = QPushButton("📤 Xuất Excel")
        export_btn.setMinimumHeight(35)
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        export_btn.clicked.connect(self.export_individual_thresholds)
        footer_layout.addWidget(export_btn)

        table_layout.addLayout(footer_layout)
        layout.addWidget(table_card)

    def reset_individual_form(self):
        """Đặt lại form về trạng thái mặc định"""
        self.individual_ingredient_combo.setCurrentText("")
        self.individual_critical_days_spin.setValue(7)
        self.individual_warning_days_spin.setValue(14)
        self.individual_critical_stock_spin.setValue(0)
        self.individual_warning_stock_spin.setValue(100)

        # Update mode indicator
        self.mode_indicator.setText("➕ Thêm mới")
        self.mode_indicator.setStyleSheet("""
            QLabel {
                background-color: #28a745;
                color: white;
                padding: 8px 15px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: bold;
            }
        """)
        self.add_update_btn.setText("➕ Thêm Ngưỡng")

    def filter_individual_table(self):
        """Lọc bảng theo từ khóa tìm kiếm"""
        search_text = self.search_box.text().lower()

        for row in range(self.individual_table.rowCount()):
            item = self.individual_table.item(row, 0)  # Ingredient name column
            if item:
                ingredient_name = item.text().lower()
                should_show = search_text in ingredient_name
                self.individual_table.setRowHidden(row, not should_show)

    def export_individual_thresholds(self):
        """Xuất danh sách ngưỡng riêng biệt ra Excel"""
        try:
            from PyQt5.QtWidgets import QFileDialog
            import pandas as pd

            # Get data from table
            data = []
            for row in range(self.individual_table.rowCount()):
                if not self.individual_table.isRowHidden(row):
                    row_data = []
                    for col in range(self.individual_table.columnCount()):
                        item = self.individual_table.item(row, col)
                        row_data.append(item.text() if item else "")
                    data.append(row_data)

            if not data:
                QMessageBox.information(self, "Thông báo", "Không có dữ liệu để xuất!")
                return

            # Create DataFrame
            columns = ["Thành phần", "Khẩn cấp (ngày)", "Sắp hết (ngày)",
                      "Khẩn cấp (kg)", "Sắp hết (kg)", "Trạng thái hiện tại"]
            df = pd.DataFrame(data, columns=columns)

            # Save file
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Xuất danh sách ngưỡng riêng biệt",
                "nguong_rieng_biet.xlsx", "Excel files (*.xlsx)"
            )

            if file_path:
                df.to_excel(file_path, index=False)
                QMessageBox.information(self, "Thành công", f"Đã xuất dữ liệu ra {file_path}")

        except ImportError:
            QMessageBox.warning(self, "Lỗi", "Cần cài đặt pandas để xuất Excel!")
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể xuất file: {str(e)}")

    def on_individual_table_selection_changed_improved(self):
        """Xử lý khi chọn hàng trong bảng với UI cải thiện"""
        current_row = self.individual_table.currentRow()
        if current_row >= 0:
            # Load selected ingredient data to form
            ingredient = self.individual_table.item(current_row, 0).text()
            self.individual_ingredient_combo.setCurrentText(ingredient)

            # Load thresholds
            thresholds = self.threshold_manager.get_ingredient_thresholds(ingredient)
            self.individual_critical_days_spin.setValue(thresholds.get('critical_days', 7))
            self.individual_warning_days_spin.setValue(thresholds.get('warning_days', 14))
            self.individual_critical_stock_spin.setValue(thresholds.get('critical_stock', 0))
            self.individual_warning_stock_spin.setValue(thresholds.get('warning_stock', 100))

            # Update mode indicator
            self.mode_indicator.setText("✏️ Chỉnh sửa")
            self.mode_indicator.setStyleSheet("""
                QLabel {
                    background-color: #ffc107;
                    color: #212529;
                    padding: 8px 15px;
                    border-radius: 20px;
                    font-size: 12px;
                    font-weight: bold;
                }
            """)
            self.add_update_btn.setText("💾 Cập Nhật")
        else:
            # Reset to add mode
            self.reset_individual_form()

    def update_table_info(self):
        """Cập nhật thông tin bảng"""
        total_rows = self.individual_table.rowCount()
        visible_rows = sum(1 for row in range(total_rows) if not self.individual_table.isRowHidden(row))

        if hasattr(self, 'table_info_label'):
            if visible_rows == total_rows:
                self.table_info_label.setText(f"Tổng: {total_rows} ngưỡng riêng biệt")
            else:
                self.table_info_label.setText(f"Hiển thị: {visible_rows}/{total_rows} ngưỡng riêng biệt")



    def create_individual_control_panel(self, layout):
        """Tạo panel điều khiển cho ngưỡng riêng biệt với layout cải thiện"""
        control_group = QGroupBox("🔧 Thêm/Sửa Ngưỡng Riêng Biệt")
        control_group.setFont(QFont("Arial", 12, QFont.Bold))
        control_layout = QGridLayout(control_group)
        control_layout.setSpacing(15)
        control_layout.setContentsMargins(20, 20, 20, 20)

        # Ingredient selection với label rõ ràng và font size lớn hơn
        ingredient_label = QLabel("📦 Chọn thành phần:")
        ingredient_label.setFont(QFont("Arial", 12, QFont.Bold))
        control_layout.addWidget(ingredient_label, 0, 0)

        self.individual_ingredient_combo = QComboBox()
        self.individual_ingredient_combo.setEditable(True)
        self.individual_ingredient_combo.setMinimumWidth(250)
        self.individual_ingredient_combo.setMinimumHeight(40)
        self.individual_ingredient_combo.setStyleSheet("""
            QComboBox {
                padding: 15px;
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #ddd;
                border-radius: 6px;
            }
            QComboBox:focus { border-color: #4CAF50; }
            QComboBox::drop-down {
                width: 30px;
                border: none;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
            }
        """)
        control_layout.addWidget(self.individual_ingredient_combo, 0, 1, 1, 3)

        # Ngưỡng theo ngày với font size lớn hơn
        days_label = QLabel("📅 Ngưỡng theo ngày:")
        days_label.setFont(QFont("Arial", 12, QFont.Bold))
        control_layout.addWidget(days_label, 1, 0)

        # Critical days với kích thước cải thiện
        critical_days_label = QLabel("🔴 Khẩn cấp:")
        critical_days_label.setFont(QFont("Arial", 12, QFont.Bold))
        control_layout.addWidget(critical_days_label, 1, 1)
        self.individual_critical_days_spin = QSpinBox()
        self.individual_critical_days_spin.setRange(0, 30)
        self.individual_critical_days_spin.setValue(7)
        self.individual_critical_days_spin.setSuffix(" ngày")
        self.individual_critical_days_spin.setMinimumWidth(130)
        self.individual_critical_days_spin.setMinimumHeight(40)
        self.individual_critical_days_spin.setStyleSheet("""
            QSpinBox {
                padding: 15px;
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #ddd;
                border-radius: 6px;
            }
            QSpinBox:focus { border-color: #f44336; }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;
                height: 15px;
            }
        """)
        control_layout.addWidget(self.individual_critical_days_spin, 2, 1)

        # Warning days với kích thước cải thiện
        warning_days_label = QLabel("🟡 Sắp hết:")
        warning_days_label.setFont(QFont("Arial", 12, QFont.Bold))
        control_layout.addWidget(warning_days_label, 1, 2)
        self.individual_warning_days_spin = QSpinBox()
        self.individual_warning_days_spin.setRange(1, 60)
        self.individual_warning_days_spin.setValue(14)
        self.individual_warning_days_spin.setSuffix(" ngày")
        self.individual_warning_days_spin.setMinimumWidth(130)
        self.individual_warning_days_spin.setMinimumHeight(40)
        self.individual_warning_days_spin.setStyleSheet("""
            QSpinBox {
                padding: 15px;
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #ddd;
                border-radius: 6px;
            }
            QSpinBox:focus { border-color: #ff9800; }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;
                height: 15px;
            }
        """)
        control_layout.addWidget(self.individual_warning_days_spin, 2, 2)

        # Ngưỡng theo tồn kho với font size lớn hơn
        stock_label = QLabel("📦 Ngưỡng theo tồn kho:")
        stock_label.setFont(QFont("Arial", 12, QFont.Bold))
        control_layout.addWidget(stock_label, 3, 0)

        # Critical stock với kích thước cải thiện
        critical_stock_label = QLabel("🔴 Khẩn cấp:")
        critical_stock_label.setFont(QFont("Arial", 12, QFont.Bold))
        control_layout.addWidget(critical_stock_label, 3, 1)
        self.individual_critical_stock_spin = QDoubleSpinBox()
        self.individual_critical_stock_spin.setRange(0, 10000)
        self.individual_critical_stock_spin.setValue(0)
        self.individual_critical_stock_spin.setSuffix(" kg")
        self.individual_critical_stock_spin.setDecimals(1)
        self.individual_critical_stock_spin.setMinimumWidth(130)
        self.individual_critical_stock_spin.setMinimumHeight(40)
        self.individual_critical_stock_spin.setStyleSheet("""
            QDoubleSpinBox {
                padding: 15px;
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #ddd;
                border-radius: 6px;
            }
            QDoubleSpinBox:focus { border-color: #f44336; }
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                width: 20px;
                height: 15px;
            }
        """)
        control_layout.addWidget(self.individual_critical_stock_spin, 4, 1)

        # Warning stock với kích thước cải thiện
        warning_stock_label = QLabel("🟡 Sắp hết:")
        warning_stock_label.setFont(QFont("Arial", 12, QFont.Bold))
        control_layout.addWidget(warning_stock_label, 3, 2)
        self.individual_warning_stock_spin = QDoubleSpinBox()
        self.individual_warning_stock_spin.setRange(0, 10000)
        self.individual_warning_stock_spin.setValue(100)
        self.individual_warning_stock_spin.setSuffix(" kg")
        self.individual_warning_stock_spin.setDecimals(1)
        self.individual_warning_stock_spin.setMinimumWidth(130)
        self.individual_warning_stock_spin.setMinimumHeight(40)
        self.individual_warning_stock_spin.setStyleSheet("""
            QDoubleSpinBox {
                padding: 15px;
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #ddd;
                border-radius: 6px;
            }
            QDoubleSpinBox:focus { border-color: #ff9800; }
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                width: 20px;
                height: 15px;
            }
        """)
        control_layout.addWidget(self.individual_warning_stock_spin, 4, 2)

        # Action buttons với spacing cải thiện
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        button_layout.setContentsMargins(0, 20, 0, 0)

        add_btn = QPushButton("➕ Thêm/Cập Nhật")
        add_btn.setMinimumHeight(45)
        add_btn.setMinimumWidth(160)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 15px 25px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed { background-color: #3d8b40; }
        """)
        add_btn.clicked.connect(self.add_or_update_individual_threshold)
        button_layout.addWidget(add_btn)

        remove_btn = QPushButton("🗑️ Xóa")
        remove_btn.setMinimumHeight(45)
        remove_btn.setMinimumWidth(120)
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 15px 25px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:pressed { background-color: #c62828; }
        """)
        remove_btn.clicked.connect(self.remove_individual_threshold)
        button_layout.addWidget(remove_btn)

        clear_all_btn = QPushButton("🗑️ Xóa Tất Cả")
        clear_all_btn.setMinimumHeight(45)
        clear_all_btn.setMinimumWidth(140)
        clear_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #9e9e9e;
                color: white;
                border: none;
                padding: 15px 25px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #757575;
            }
            QPushButton:pressed { background-color: #616161; }
        """)
        clear_all_btn.clicked.connect(self.clear_all_individual_thresholds)
        button_layout.addWidget(clear_all_btn)

        button_layout.addStretch()
        control_layout.addLayout(button_layout, 5, 0, 1, 4)

        layout.addWidget(control_group)

    def create_individual_table(self, layout):
        """Tạo bảng hiển thị ngưỡng riêng biệt với layout cải thiện"""
        table_group = QGroupBox("📊 Danh Sách Ngưỡng Riêng Biệt")
        table_group.setFont(QFont("Arial", 12, QFont.Bold))
        table_layout = QVBoxLayout(table_group)
        table_layout.setContentsMargins(15, 15, 15, 15)

        self.individual_table = QTableWidget()
        self.individual_table.setColumnCount(6)
        self.individual_table.setHorizontalHeaderLabels([
            "Thành phần", "🔴 Khẩn cấp\n(ngày)", "🟡 Sắp hết\n(ngày)",
            "🔴 Khẩn cấp\n(kg)", "🟡 Sắp hết\n(kg)", "Trạng thái\nhiện tại"
        ])

        # Table styling với font size và kích thước cải thiện
        self.individual_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #e0e0e0;
                selection-background-color: #e3f2fd;
                alternate-background-color: #fafafa;
                background-color: white;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 500;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FF9800, stop:1 #F57C00);
                color: white;
                padding: 15px 10px;
                border: 1px solid #F57C00;
                font-weight: bold;
                font-size: 12px;
                text-align: center;
            }
            QTableWidget::item {
                padding: 15px 10px;
                border-bottom: 1px solid #f0f0f0;
                text-align: center;
                font-size: 13px;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
                font-weight: bold;
            }
        """)

        # Cải thiện column resize với kích thước cố định
        header = self.individual_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Ingredient name - stretch
        header.setSectionResizeMode(1, QHeaderView.Fixed)    # Critical days - fixed
        header.setSectionResizeMode(2, QHeaderView.Fixed)    # Warning days - fixed
        header.setSectionResizeMode(3, QHeaderView.Fixed)    # Critical stock - fixed
        header.setSectionResizeMode(4, QHeaderView.Fixed)    # Warning stock - fixed
        header.setSectionResizeMode(5, QHeaderView.Fixed)    # Status - fixed

        # Đặt kích thước cột cố định với kích thước lớn hơn để text hiển thị đầy đủ
        self.individual_table.setColumnWidth(1, 120)  # Critical days
        self.individual_table.setColumnWidth(2, 120)  # Warning days
        self.individual_table.setColumnWidth(3, 120)  # Critical stock
        self.individual_table.setColumnWidth(4, 120)  # Warning stock
        self.individual_table.setColumnWidth(5, 140)  # Status

        # Cải thiện row height để text hiển thị tốt hơn với font size lớn
        self.individual_table.verticalHeader().setDefaultSectionSize(50)
        self.individual_table.verticalHeader().setVisible(False)

        # Đặt minimum height cho table lớn hơn
        self.individual_table.setMinimumHeight(250)

        self.individual_table.setAlternatingRowColors(True)
        self.individual_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.individual_table.itemSelectionChanged.connect(self.on_individual_table_selection_changed)

        table_layout.addWidget(self.individual_table)
        layout.addWidget(table_group)

    def create_current_settings_display(self, layout):
        """Tạo hiển thị cài đặt hiện tại với styling cải thiện"""
        self.current_settings_label = QLabel()
        self.current_settings_label.setWordWrap(True)
        self.current_settings_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
                color: #495057;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 11px;
                line-height: 1.4;
            }
        """)
        layout.addWidget(self.current_settings_label)

    def create_buttons(self, layout):
        """Tạo các nút điều khiển với styling cải thiện"""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        button_layout.setContentsMargins(0, 20, 0, 0)

        # Reset button
        reset_btn = QPushButton("🔄 Đặt Lại Mặc Định")
        reset_btn.setMinimumHeight(45)
        reset_btn.setMinimumWidth(160)
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
            QPushButton:pressed { background-color: #545b62; }
        """)
        reset_btn.clicked.connect(self.reset_to_defaults)
        button_layout.addWidget(reset_btn)

        button_layout.addStretch()

        # Cancel button
        cancel_btn = QPushButton("❌ Hủy")
        cancel_btn.setMinimumHeight(45)
        cancel_btn.setMinimumWidth(120)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed { background-color: #bd2130; }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        # Save button
        save_btn = QPushButton("💾 Lưu Cài Đặt")
        save_btn.setMinimumHeight(45)
        save_btn.setMinimumWidth(140)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed { background-color: #1e7e34; }
        """)
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)

    def load_current_settings(self):
        """Tải cài đặt hiện tại vào giao diện"""
        thresholds = self.threshold_manager.get_thresholds()

        # Load days settings
        self.critical_days_spin.setValue(thresholds["critical_days"])
        self.warning_days_spin.setValue(thresholds["warning_days"])
        self.sufficient_days_spin.setValue(thresholds["sufficient_days"])

        # Load stock settings
        self.critical_stock_spin.setValue(thresholds["critical_stock"])
        self.warning_stock_spin.setValue(thresholds["warning_stock"])
        self.sufficient_stock_spin.setValue(thresholds["sufficient_stock"])

        # Load priority settings
        self.use_days_checkbox.setChecked(thresholds["use_days_based"])
        self.use_stock_checkbox.setChecked(thresholds["use_stock_based"])

        # Load advanced settings
        self.load_advanced_settings()

        # Load individual threshold settings
        self.load_individual_ingredients()
        self.load_individual_threshold_settings()

        # Update display
        self.update_current_settings_display()

    def load_advanced_settings(self):
        """Tải các cài đặt nâng cao"""
        # Display settings
        display_settings = self.threshold_manager.get_display_settings()
        self.set_combo_by_data(self.display_unit_combo, display_settings["display_unit"])
        self.show_days_checkbox.setChecked(display_settings["show_days_in_table"])
        self.show_stock_checkbox.setChecked(display_settings["show_stock_in_table"])

        # Sound settings
        sound_settings = self.threshold_manager.get_sound_settings()
        self.sound_enabled_checkbox.setChecked(sound_settings["sound_enabled"])
        self.sound_critical_checkbox.setChecked(sound_settings["sound_critical"])
        self.sound_warning_checkbox.setChecked(sound_settings["sound_warning"])
        self.volume_slider.setValue(sound_settings["sound_volume"])

        # Auto check settings
        auto_check_settings = self.threshold_manager.get_auto_check_settings()
        self.auto_check_checkbox.setChecked(auto_check_settings["auto_check_enabled"])
        self.set_combo_by_data(self.check_frequency_combo, auto_check_settings["check_frequency"])
        self.check_interval_spin.setValue(auto_check_settings["check_interval_hours"])

        # Popup settings
        popup_settings = self.threshold_manager.get_popup_settings()
        self.popup_enabled_checkbox.setChecked(popup_settings["popup_enabled"])
        self.popup_startup_checkbox.setChecked(popup_settings["popup_on_startup"])
        self.popup_critical_checkbox.setChecked(popup_settings["popup_on_critical"])
        self.popup_warning_checkbox.setChecked(popup_settings["popup_on_warning"])

        # Auto report settings
        auto_report_settings = self.threshold_manager.get_auto_report_settings()
        self.auto_report_checkbox.setChecked(auto_report_settings["auto_report_enabled"])
        self.set_combo_by_data(self.report_frequency_combo, auto_report_settings["report_frequency"])

        # Parse time string
        time_str = auto_report_settings["report_time"]
        try:
            hours, minutes = map(int, time_str.split(":"))
            self.report_time_edit.setTime(QTime(hours, minutes))
        except:
            self.report_time_edit.setTime(QTime(8, 0))

        self.report_path_edit.setText(auto_report_settings["report_path"])

        # Color settings
        color_settings = self.threshold_manager.get_color_settings()
        self.use_custom_colors_checkbox.setChecked(color_settings["use_custom_colors"])

        # Update color buttons
        color_map = {
            "critical": color_settings["color_critical"],
            "warning": color_settings["color_warning"],
            "sufficient": color_settings["color_sufficient"],
            "no_data": color_settings["color_no_data"]
        }

        for key, color in color_map.items():
            if key in self.color_buttons:
                self.color_buttons[key].setStyleSheet(
                    f"background-color: {color}; border: 2px solid #ccc; border-radius: 4px;"
                )

        self.update_color_preview()

    def load_individual_ingredients(self):
        """Tải danh sách nguyên liệu cho tab ngưỡng riêng biệt với thứ tự nhất quán"""
        try:
            # Get consistently sorted ingredients
            ingredients = self.inventory_manager.get_sorted_unified_ingredients()

            self.individual_ingredient_combo.clear()
            self.individual_ingredient_combo.addItems(ingredients)

        except Exception as e:
            print(f"[ERROR] Lỗi khi tải danh sách nguyên liệu: {e}")
            # Fallback to basic sorting
            try:
                inventory = self.inventory_manager.get_inventory()
                ingredients = sorted(inventory.keys())
                self.individual_ingredient_combo.clear()
                self.individual_ingredient_combo.addItems(ingredients)
            except Exception as fallback_e:
                print(f"[ERROR] Lỗi fallback khi tải danh sách nguyên liệu: {fallback_e}")

    def load_individual_threshold_settings(self):
        """Tải cài đặt ngưỡng riêng biệt vào bảng"""
        try:
            individual_thresholds = self.threshold_manager.get_individual_thresholds()

            self.individual_table.setRowCount(len(individual_thresholds))

            # Get current inventory status for display
            avg_daily_usage = self.inventory_manager.analyze_consumption_patterns(7)
            days_remaining = self.inventory_manager.calculate_days_until_empty(avg_daily_usage)
            inventory = self.inventory_manager.get_inventory()

            row = 0
            for ingredient, thresholds in individual_thresholds.items():
                # Ingredient name
                self.individual_table.setItem(row, 0, QTableWidgetItem(ingredient))

                # Critical days
                critical_days = thresholds.get('critical_days', 'Chung')
                self.individual_table.setItem(row, 1, QTableWidgetItem(str(critical_days)))

                # Warning days
                warning_days = thresholds.get('warning_days', 'Chung')
                self.individual_table.setItem(row, 2, QTableWidgetItem(str(warning_days)))

                # Critical stock
                critical_stock = thresholds.get('critical_stock', 'Chung')
                self.individual_table.setItem(row, 3, QTableWidgetItem(str(critical_stock)))

                # Warning stock
                warning_stock = thresholds.get('warning_stock', 'Chung')
                self.individual_table.setItem(row, 4, QTableWidgetItem(str(warning_stock)))

                # Current status
                days = days_remaining.get(ingredient, float('inf'))
                stock = inventory.get(ingredient, 0)
                status_text, color_info = self.threshold_manager.get_inventory_status(days, stock, ingredient)

                status_item = QTableWidgetItem(status_text)
                if color_info == "red":
                    status_item.setBackground(QColor("#ffebee"))
                    status_item.setForeground(QColor("#c62828"))
                elif color_info == "yellow":
                    status_item.setBackground(QColor("#fff8e1"))
                    status_item.setForeground(QColor("#f57c00"))
                elif color_info == "green":
                    status_item.setBackground(QColor("#e8f5e9"))
                    status_item.setForeground(QColor("#2e7d32"))

                self.individual_table.setItem(row, 5, status_item)

                row += 1

            # Update table info
            self.update_table_info()

        except Exception as e:
            print(f"[ERROR] Lỗi khi tải cài đặt ngưỡng riêng biệt: {e}")

    def on_individual_table_selection_changed(self):
        """Xử lý khi chọn hàng trong bảng ngưỡng riêng biệt"""
        current_row = self.individual_table.currentRow()
        if current_row >= 0:
            # Load selected ingredient data to form
            ingredient = self.individual_table.item(current_row, 0).text()
            self.individual_ingredient_combo.setCurrentText(ingredient)

            # Load thresholds
            thresholds = self.threshold_manager.get_ingredient_thresholds(ingredient)
            self.individual_critical_days_spin.setValue(thresholds.get('critical_days', 7))
            self.individual_warning_days_spin.setValue(thresholds.get('warning_days', 14))
            self.individual_critical_stock_spin.setValue(thresholds.get('critical_stock', 0))
            self.individual_warning_stock_spin.setValue(thresholds.get('warning_stock', 100))

    def add_or_update_individual_threshold(self):
        """Thêm hoặc cập nhật ngưỡng riêng biệt"""
        ingredient = self.individual_ingredient_combo.currentText().strip()
        if not ingredient:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn hoặc nhập tên thành phần!")
            return

        # Validate values
        critical_days = self.individual_critical_days_spin.value()
        warning_days = self.individual_warning_days_spin.value()

        if critical_days >= warning_days:
            QMessageBox.warning(self, "Lỗi",
                              f"Ngưỡng khẩn cấp ({critical_days}) phải nhỏ hơn ngưỡng cảnh báo ({warning_days})!")
            return

        # Set individual thresholds
        success = True
        success &= self.threshold_manager.set_individual_threshold(ingredient, 'critical_days', critical_days)
        success &= self.threshold_manager.set_individual_threshold(ingredient, 'warning_days', warning_days)
        success &= self.threshold_manager.set_individual_threshold(ingredient, 'critical_stock', self.individual_critical_stock_spin.value())
        success &= self.threshold_manager.set_individual_threshold(ingredient, 'warning_stock', self.individual_warning_stock_spin.value())

        if success:
            # Show success message with better styling
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Thành công")
            msg.setText(f"✅ Đã cài đặt ngưỡng riêng biệt cho '{ingredient}'!")
            msg.setDetailedText(f"Khẩn cấp: {critical_days} ngày, {self.individual_critical_stock_spin.value()} kg\n"
                               f"Sắp hết: {warning_days} ngày, {self.individual_warning_stock_spin.value()} kg")
            msg.exec_()

            self.load_individual_threshold_settings()
            self.reset_individual_form()
        else:
            QMessageBox.warning(self, "Lỗi", "❌ Không thể cài đặt ngưỡng!")

    def remove_individual_threshold(self):
        """Xóa ngưỡng riêng biệt"""
        ingredient = self.individual_ingredient_combo.currentText().strip()
        if not ingredient:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn thành phần để xóa!")
            return

        reply = QMessageBox.question(self, "Xác nhận",
                                   f"🗑️ Bạn có chắc muốn xóa ngưỡng riêng biệt cho '{ingredient}'?\n"
                                   f"Thành phần này sẽ sử dụng ngưỡng chung.",
                                   QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            if self.threshold_manager.remove_individual_threshold(ingredient):
                QMessageBox.information(self, "Thành công",
                                      f"✅ Đã xóa ngưỡng riêng biệt cho '{ingredient}'!")
                self.load_individual_threshold_settings()
                self.reset_individual_form()
            else:
                QMessageBox.warning(self, "Lỗi", "❌ Không thể xóa ngưỡng!")

    def clear_all_individual_thresholds(self):
        """Xóa tất cả ngưỡng riêng biệt"""
        reply = QMessageBox.question(self, "Xác nhận",
                                   "🗑️ Bạn có chắc muốn xóa TẤT CẢ ngưỡng riêng biệt?\n"
                                   "Tất cả thành phần sẽ sử dụng ngưỡng chung.",
                                   QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.threshold_manager.individual_thresholds = {}
            if self.threshold_manager.save_individual_thresholds():
                QMessageBox.information(self, "Thành công",
                                      "✅ Đã xóa tất cả ngưỡng riêng biệt!")
                self.load_individual_threshold_settings()
                self.reset_individual_form()
            else:
                QMessageBox.warning(self, "Lỗi", "❌ Không thể xóa ngưỡng!")

    def set_combo_by_data(self, combo, data_value):
        """Thiết lập ComboBox theo giá trị data"""
        for i in range(combo.count()):
            if combo.itemData(i) == data_value:
                combo.setCurrentIndex(i)
                return
        # Nếu không tìm thấy, thử tìm theo text
        index = combo.findText(data_value)
        if index >= 0:
            combo.setCurrentIndex(index)

    def test_sound(self):
        """Test âm thanh cảnh báo"""
        try:
            # Simple beep for testing
            import winsound
            if self.sound_enabled_checkbox.isChecked():
                volume = self.volume_slider.value()
                # Play system beep (frequency based on volume)
                frequency = 800 + (volume * 10)  # 800-1800 Hz
                duration = 500  # 0.5 seconds
                winsound.Beep(int(frequency), duration)
            else:
                QMessageBox.information(self, "Test Âm Thanh", "Âm thanh đã bị tắt!")
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể phát âm thanh: {str(e)}")

    def choose_color(self, color_key):
        """Chọn màu sắc tùy chỉnh"""
        current_color = self.color_buttons[color_key].palette().button().color()
        color = QColorDialog.getColor(current_color, self, f"Chọn màu cho {color_key}")

        if color.isValid():
            color_hex = color.name()
            self.color_buttons[color_key].setStyleSheet(
                f"background-color: {color_hex}; border: 2px solid #ccc; border-radius: 4px;"
            )
            self.update_color_preview()

    def reset_color(self, color_key, default_color):
        """Đặt lại màu mặc định"""
        self.color_buttons[color_key].setStyleSheet(
            f"background-color: {default_color}; border: 2px solid #ccc; border-radius: 4px;"
        )
        self.update_color_preview()

    def update_color_preview(self):
        """Cập nhật xem trước màu sắc"""
        if not self.use_custom_colors_checkbox.isChecked():
            self.color_preview_label.setText("Sử dụng màu mặc định của hệ thống")
            return

        # Get current colors from buttons
        colors = {}
        for key, button in self.color_buttons.items():
            style = button.styleSheet()
            # Extract color from stylesheet
            import re
            match = re.search(r'background-color:\s*(#[0-9a-fA-F]{6})', style)
            if match:
                colors[key] = match.group(1)

        # Create preview text
        preview_html = f"""
        <div style="text-align: center;">
            <span style="color: {colors.get('critical', '#f44336')}; font-weight: bold;">🔴 Khẩn cấp</span><br>
            <span style="color: {colors.get('warning', '#ff9800')}; font-weight: bold;">🟡 Sắp hết</span><br>
            <span style="color: {colors.get('sufficient', '#4caf50')}; font-weight: bold;">🟢 Đủ hàng</span><br>
            <span style="color: {colors.get('no_data', '#9e9e9e')}; font-weight: bold;">⚪ Không có dữ liệu</span>
        </div>
        """
        self.color_preview_label.setText(preview_html)

    def update_current_settings_display(self):
        """Cập nhật hiển thị cài đặt hiện tại"""
        desc = self.threshold_manager.get_threshold_description()
        thresholds = self.threshold_manager.get_thresholds()

        display_text = f"📊 Cài đặt hiện tại: {desc}\n"
        display_text += f"🔴 Khẩn cấp: <{thresholds['critical_days']} ngày hoặc ≤{thresholds['critical_stock']} kg\n"
        display_text += f"🟡 Sắp hết: <{thresholds['warning_days']} ngày hoặc ≤{thresholds['warning_stock']} kg\n"
        display_text += f"🟢 Đủ hàng: >{thresholds['sufficient_days']} ngày hoặc >{thresholds['sufficient_stock']} kg"

        self.current_settings_label.setText(display_text)

    def save_settings(self):
        """Lưu tất cả cài đặt"""
        try:
            # Basic thresholds
            new_thresholds = {
                "critical_days": self.critical_days_spin.value(),
                "warning_days": self.warning_days_spin.value(),
                "sufficient_days": self.sufficient_days_spin.value(),
                "critical_stock": self.critical_stock_spin.value(),
                "warning_stock": self.warning_stock_spin.value(),
                "sufficient_stock": self.sufficient_stock_spin.value(),
                "use_days_based": self.use_days_checkbox.isChecked(),
                "use_stock_based": self.use_stock_checkbox.isChecked()
            }

            # Display settings
            display_settings = {
                "display_unit": self.display_unit_combo.currentData() or "both",
                "show_days_in_table": self.show_days_checkbox.isChecked(),
                "show_stock_in_table": self.show_stock_checkbox.isChecked()
            }

            # Sound settings
            sound_settings = {
                "sound_enabled": self.sound_enabled_checkbox.isChecked(),
                "sound_critical": self.sound_critical_checkbox.isChecked(),
                "sound_warning": self.sound_warning_checkbox.isChecked(),
                "sound_volume": self.volume_slider.value()
            }

            # Auto check settings
            auto_check_settings = {
                "auto_check_enabled": self.auto_check_checkbox.isChecked(),
                "check_frequency": self.check_frequency_combo.currentData() or "hourly",
                "check_interval_hours": self.check_interval_spin.value()
            }

            # Popup settings
            popup_settings = {
                "popup_enabled": self.popup_enabled_checkbox.isChecked(),
                "popup_on_startup": self.popup_startup_checkbox.isChecked(),
                "popup_on_critical": self.popup_critical_checkbox.isChecked(),
                "popup_on_warning": self.popup_warning_checkbox.isChecked()
            }

            # Auto report settings
            auto_report_settings = {
                "auto_report_enabled": self.auto_report_checkbox.isChecked(),
                "report_frequency": self.report_frequency_combo.currentData() or "daily",
                "report_time": self.report_time_edit.time().toString("HH:mm"),
                "report_path": self.report_path_edit.text().strip()
            }

            # Color settings
            color_settings = {
                "use_custom_colors": self.use_custom_colors_checkbox.isChecked()
            }

            # Extract colors from buttons
            for key, button in self.color_buttons.items():
                style = button.styleSheet()
                import re
                match = re.search(r'background-color:\s*(#[0-9a-fA-F]{6})', style)
                if match:
                    color_settings[f"color_{key}"] = match.group(1)

            # Save all settings
            success = True
            success &= self.threshold_manager.update_thresholds(new_thresholds)
            success &= self.threshold_manager.update_display_settings(display_settings)
            success &= self.threshold_manager.update_sound_settings(sound_settings)
            success &= self.threshold_manager.update_auto_check_settings(auto_check_settings)
            success &= self.threshold_manager.update_popup_settings(popup_settings)
            success &= self.threshold_manager.update_auto_report_settings(auto_report_settings)
            success &= self.threshold_manager.update_color_settings(color_settings)

            if success:
                QMessageBox.information(self, "Thành công",
                                      "✅ Đã lưu tất cả cài đặt ngưỡng cảnh báo thành công!\n"
                                      "Hệ thống sẽ áp dụng các cài đặt mới ngay lập tức.")
                self.accept()
            else:
                QMessageBox.warning(self, "Lỗi",
                                  "❌ Không thể lưu một số cài đặt. Vui lòng kiểm tra lại các giá trị.")

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"❌ Lỗi khi lưu cài đặt: {str(e)}")

    def reset_to_defaults(self):
        """Đặt lại về cài đặt mặc định"""
        reply = QMessageBox.question(self, "Xác nhận",
                                   "🔄 Bạn có chắc muốn đặt lại về cài đặt mặc định?\n"
                                   "Tất cả cài đặt hiện tại sẽ bị mất.",
                                   QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            if self.threshold_manager.reset_to_defaults():
                self.load_current_settings()
                QMessageBox.information(self, "Thành công",
                                      "✅ Đã đặt lại về cài đặt mặc định thành công!")
            else:
                QMessageBox.warning(self, "Lỗi",
                                  "❌ Không thể đặt lại cài đặt mặc định.")
