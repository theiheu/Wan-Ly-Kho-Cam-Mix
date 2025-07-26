"""
Feed Usage Tab for the Chicken Farm App
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
                           QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
                           QComboBox, QGroupBox, QDoubleSpinBox, QFrame, QSplitter,
                           QMessageBox, QAbstractSpinBox, QMenu, QAction)
from PyQt5.QtCore import Qt, QDate, QSize
from PyQt5.QtGui import QFont, QColor, QCursor, QIcon

from src.utils.constants import (AREAS, SHIFTS, FARMS, DEFAULT_FONT_SIZE, HEADER_FONT_SIZE,
                               BUTTON_FONT_SIZE, TABLE_HEADER_FONT_SIZE, TABLE_CELL_FONT_SIZE,
                               TABLE_ROW_HEIGHT, TABLE_HEADER_HEIGHT, UI_PADDING, UI_SPACING,
                               BUTTON_MIN_HEIGHT, BUTTON_MIN_WIDTH)
from src.ui.widgets.custom_spinbox import CustomDoubleSpinBox
from src.utils.formatting import format_number

class FeedUsageTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        # Dictionaries để lưu trữ các widget
        self.feed_spinboxes = {}
        self.formula_combos = {}
        self.formula_labels = {}

        # Biến để lưu cell được chọn
        self.selected_cell = None

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(UI_PADDING, UI_PADDING, UI_PADDING, UI_PADDING)
        layout.setSpacing(UI_SPACING)

        # Thêm tiêu đề
        title_label = QLabel("Quản lý sử dụng cám")
        title_font = QFont("Arial", HEADER_FONT_SIZE, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setProperty("header", True)  # Để áp dụng CSS từ stylesheet
        layout.addWidget(title_label)

        # Thêm đường kẻ ngang
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        # Tạo splitter để chia màn hình thành hai phần
        splitter = QSplitter(Qt.Vertical)

        # Phần 1: Nhập liệu sử dụng cám
        feed_input_group = QGroupBox("Nhập liệu sử dụng cám")
        feed_input_layout = QVBoxLayout()
        feed_input_layout.setContentsMargins(UI_PADDING, UI_PADDING, UI_PADDING, UI_PADDING)
        feed_input_layout.setSpacing(UI_SPACING)

        # Thêm nhãn ngày
        date_layout = QHBoxLayout()
        date_label = QLabel(f"Ngày: {QDate.currentDate().toString('dd/MM/yyyy')}")
        date_label.setFont(QFont("Arial", DEFAULT_FONT_SIZE, QFont.Bold))
        date_layout.addWidget(date_label)
        date_layout.addStretch()

        # Thêm nút Điền Mẻ Cám Theo Ngày
        fill_by_date_button = QPushButton(QIcon.fromTheme("document-open"), "Điền Mẻ Cám Theo Ngày")
        fill_by_date_button.setFont(QFont("Arial", BUTTON_FONT_SIZE, QFont.Bold))
        fill_by_date_button.setMinimumHeight(BUTTON_MIN_HEIGHT)
        fill_by_date_button.setMinimumWidth(BUTTON_MIN_WIDTH)
        fill_by_date_button.setCursor(QCursor(Qt.PointingHandCursor))
        fill_by_date_button.clicked.connect(self.parent.fill_table_by_date if hasattr(self.parent, 'fill_table_by_date') else lambda: None)
        date_layout.addWidget(fill_by_date_button)

        # Thêm nút Reset
        reset_button = QPushButton(QIcon.fromTheme("edit-clear"), "Reset Bảng")
        reset_button.setFont(QFont("Arial", BUTTON_FONT_SIZE, QFont.Bold))
        reset_button.setMinimumHeight(BUTTON_MIN_HEIGHT)
        reset_button.setMinimumWidth(BUTTON_MIN_WIDTH)
        reset_button.setCursor(QCursor(Qt.PointingHandCursor))
        reset_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        reset_button.clicked.connect(self.reset_feed_table)
        date_layout.addWidget(reset_button)

        feed_input_layout.addLayout(date_layout)

        # Thêm combo box chọn công thức mặc định
        default_formula_layout = QHBoxLayout()
        default_formula_label = QLabel("Công thức cám mặc định:")
        default_formula_label.setFont(QFont("Arial", DEFAULT_FONT_SIZE, QFont.Bold))
        default_formula_layout.addWidget(default_formula_label)

        self.default_formula_combo = QComboBox()
        self.default_formula_combo.setFont(QFont("Arial", DEFAULT_FONT_SIZE))
        self.default_formula_combo.setMinimumWidth(200)
        self.default_formula_combo.setMinimumHeight(BUTTON_MIN_HEIGHT)
        self.default_formula_combo.currentIndexChanged.connect(self.apply_default_formula)
        default_formula_layout.addWidget(self.default_formula_combo)

        # Thêm nút áp dụng công thức mặc định
        apply_default_button = QPushButton("Áp dụng cho tất cả")
        apply_default_button.setFont(QFont("Arial", BUTTON_FONT_SIZE, QFont.Bold))
        apply_default_button.setMinimumHeight(BUTTON_MIN_HEIGHT)
        apply_default_button.setMinimumWidth(BUTTON_MIN_WIDTH)
        apply_default_button.setCursor(QCursor(Qt.PointingHandCursor))
        apply_default_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        apply_default_button.clicked.connect(self.apply_default_formula)
        default_formula_layout.addWidget(apply_default_button)

        default_formula_layout.addStretch()

        feed_input_layout.addLayout(default_formula_layout)

        # Tạo bảng nhập liệu
        self.setup_feed_table()
        feed_input_layout.addWidget(self.feed_table)

        # Thêm các nút chức năng
        buttons_layout = QHBoxLayout()

        # Nút chọn công thức mix theo khu
        mix_formula_button = QPushButton(QIcon.fromTheme("preferences-system"), "Chọn Công Thức Mix Theo Khu")
        mix_formula_button.setFont(QFont("Arial", BUTTON_FONT_SIZE, QFont.Bold))
        mix_formula_button.setMinimumHeight(40)
        mix_formula_button.clicked.connect(self.parent.assign_mix_formulas_to_areas if hasattr(self.parent, 'assign_mix_formulas_to_areas') else lambda: None)
        buttons_layout.addWidget(mix_formula_button)

        # Nút tính toán
        calculate_button = QPushButton(QIcon.fromTheme("accessories-calculator"), "Tính Toán")
        calculate_button.setFont(QFont("Arial", BUTTON_FONT_SIZE, QFont.Bold))
        calculate_button.setMinimumHeight(40)
        calculate_button.clicked.connect(self.parent.calculate_feed_usage if hasattr(self.parent, 'calculate_feed_usage') else lambda: None)
        buttons_layout.addWidget(calculate_button)

        feed_input_layout.addLayout(buttons_layout)
        feed_input_group.setLayout(feed_input_layout)

        # Phần 2: Kết quả tính toán
        feed_usage_group = QGroupBox("Tổng hợp sử dụng cám")
        feed_usage_layout = QVBoxLayout()

        # Tạo bảng kết quả
        self.setup_feed_usage_table()
        feed_usage_layout.addWidget(self.feed_usage_table)

        # Thêm các nút chức năng
        usage_buttons_layout = QHBoxLayout()

        # Nút lưu báo cáo
        save_report_button = QPushButton(QIcon.fromTheme("document-save"), "Lưu Báo Cáo")
        save_report_button.setFont(QFont("Arial", BUTTON_FONT_SIZE, QFont.Bold))
        save_report_button.setMinimumHeight(40)
        save_report_button.clicked.connect(self.parent.save_report if hasattr(self.parent, 'save_report') else lambda: None)
        usage_buttons_layout.addWidget(save_report_button)

        # Nút xuất Excel
        export_button = QPushButton(QIcon.fromTheme("x-office-spreadsheet"), "Xuất Excel")
        export_button.setFont(QFont("Arial", BUTTON_FONT_SIZE, QFont.Bold))
        export_button.setMinimumHeight(40)
        export_button.clicked.connect(self.parent.export_to_excel if hasattr(self.parent, 'export_to_excel') else lambda: None)
        usage_buttons_layout.addWidget(export_button)

        feed_usage_layout.addLayout(usage_buttons_layout)
        feed_usage_group.setLayout(feed_usage_layout)

        # Thêm các phần vào splitter
        splitter.addWidget(feed_input_group)
        splitter.addWidget(feed_usage_group)

        # Thiết lập tỷ lệ kích thước ban đầu
        splitter.setSizes([600, 400])

        layout.addWidget(splitter)
        self.setLayout(layout)

    def setup_feed_table(self):
        """Thiết lập bảng nhập liệu cám"""
        self.feed_table = QTableWidget()
        self.feed_table.setFont(QFont("Arial", TABLE_CELL_FONT_SIZE))

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
        self.feed_table.verticalHeader().setFont(QFont("Arial", TABLE_HEADER_FONT_SIZE, QFont.Bold))

        # Thiết lập kích thước cho header dọc
        self.feed_table.verticalHeader().setMinimumWidth(100)
        self.feed_table.verticalHeader().setDefaultSectionSize(TABLE_ROW_HEIGHT)

        # Tạo các ô cho khu và trại
        col_index = 0
        for khu_idx, farms in FARMS.items():
            khu_name = f"Khu {khu_idx + 1}"

            # Kiểm tra xem danh sách trại có trống không
            if not farms or (len(farms) == 1 and not farms[0]):
                print(f"Danh sách trại trống cho {khu_name}")
                continue

            # Tạo các ô cho khu
            for farm_idx, farm in enumerate(farms):
                # Kiểm tra xem tên trại có hợp lệ không
                if not farm:
                    print(f"Tên trại trống cho {khu_name}, farm_idx={farm_idx}")
                    continue

                khu_item = QTableWidgetItem(khu_name)
                khu_item.setTextAlignment(Qt.AlignCenter)
                khu_item.setFont(QFont("Arial", TABLE_HEADER_FONT_SIZE, QFont.Bold))
                self.feed_table.setItem(0, col_index, khu_item)

                farm_item = QTableWidgetItem(farm)
                farm_item.setTextAlignment(Qt.AlignCenter)
                farm_item.setFont(QFont("Arial", TABLE_HEADER_FONT_SIZE, QFont.Bold))
                self.feed_table.setItem(1, col_index, farm_item)

                col_index += 1

        print(f"Đã tạo {col_index} cột cho bảng feed_table")

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

            # Bỏ qua khu không có trại hợp lệ
            if not farms or (len(farms) == 1 and not farms[0]):
                continue

            color = khu_colors[khu_idx % len(khu_colors)]

            for farm_idx, farm in enumerate(farms):
                # Bỏ qua trại không hợp lệ
                if not farm:
                    continue

                # Thiết lập màu nền cho hàng khu và trại
                for row in range(2):
                    item = self.feed_table.item(row, col_index)
                    if item:
                        item.setBackground(color)

                # Tạo các ô nhập liệu cho các ca
                for shift_idx in range(len(SHIFTS)):
                    row = 2 + shift_idx  # Bắt đầu từ hàng thứ 3 (index 2)

                    # Tạo container cho mỗi ô
                    container = QWidget()
                    container.setStyleSheet(f"background-color: {color.name()};")

                    # Tạo layout cho container
                    container_layout = QVBoxLayout()
                    container_layout.setContentsMargins(1, 1, 1, 1)
                    container_layout.setSpacing(0)

                    # Tạo spin box cho nhập số mẻ
                    spin_box = CustomDoubleSpinBox()
                    spin_box.setFont(QFont("Arial", DEFAULT_FONT_SIZE + 2, QFont.Bold))  # Tăng kích thước font
                    spin_box.setDecimals(1)
                    spin_box.setMinimum(0)
                    spin_box.setMaximum(100)
                    spin_box.setSingleStep(0.5)
                    spin_box.setAlignment(Qt.AlignCenter)
                    spin_box.setButtonSymbols(QAbstractSpinBox.NoButtons)  # Ẩn nút tăng/giảm
                    spin_box.setStyleSheet("""
                        QDoubleSpinBox {
                            border: none;
                            border-radius: 5px;
                            padding: 8px;
                            background-color: transparent;
                            font-weight: bold;
                        }
                    """)

                    # Tạo label hiển thị tên công thức
                    formula_label = QLabel("")
                    formula_label.setFont(QFont("Arial", DEFAULT_FONT_SIZE, QFont.Bold))
                    formula_label.setAlignment(Qt.AlignCenter)
                    formula_label.setStyleSheet("color: #0277bd; font-weight: bold;")
                    formula_label.setVisible(False)  # Ban đầu ẩn label

                    # Tạo combo box chọn công thức (ẩn)
                    formula_combo = QComboBox()
                    formula_combo.setFont(QFont("Arial", DEFAULT_FONT_SIZE))
                    formula_combo.setVisible(False)  # Ẩn combo box
                    formula_combo.setStyleSheet("""
                        QComboBox {
                            border: 1px solid #bdc3c7;
                            border-radius: 5px;
                            padding: 5px;
                            background-color: white;
                        }
                    """)

                    # Thêm các widget vào layout
                    container_layout.addWidget(spin_box)
                    container_layout.addWidget(formula_label)
                    container_layout.addWidget(formula_combo)

                    # Thiết lập tỷ lệ không gian
                    container_layout.setStretch(0, 60)  # 60% cho spin_box
                    container_layout.setStretch(1, 40)  # 40% cho formula_label
                    container_layout.setStretch(2, 0)   # 0% cho formula_combo (ẩn)

                    container.setLayout(container_layout)

                    # Lưu reference đến các widget
                    container.spin_box = spin_box
                    container.formula_combo = formula_combo
                    container.formula_label = formula_label

                    # Đặt container vào bảng
                    self.feed_table.setCellWidget(row, col_index, container)

                    # Lưu các widget vào dictionaries để dễ truy cập
                    cell_key = f"{shift_idx}_{col_index}"
                    self.feed_spinboxes[cell_key] = spin_box
                    self.formula_combos[cell_key] = formula_combo
                    self.formula_labels[cell_key] = formula_label

                    # Kết nối sự kiện
                    spin_box.valueChanged.connect(lambda value, r=shift_idx, c=col_index: self.on_value_changed(value, r, c))

                    # Thiết lập prefix ban đầu để ẩn số 0
                    if spin_box.value() == 0:
                        spin_box.setPrefix(" ")
                    else:
                        spin_box.setPrefix("")

                col_index += 1

        # Kết nối sự kiện click vào cell
        self.feed_table.cellClicked.connect(self.on_feed_table_cell_clicked)

        # Kết nối sự kiện chuột phải
        self.feed_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.feed_table.customContextMenuRequested.connect(self.show_context_menu)

        # Thiết lập kích thước cột và hàng
        self.feed_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.feed_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        # Thiết lập chiều cao cho các hàng
        for row in range(self.feed_table.rowCount()):
            if row < 2:  # Hàng khu và trại
                self.feed_table.setRowHeight(row, TABLE_HEADER_HEIGHT)
            else:  # Hàng ca
                self.feed_table.setRowHeight(row, TABLE_ROW_HEIGHT)

    def setup_feed_usage_table(self):
        """Thiết lập bảng kết quả sử dụng cám"""
        self.feed_usage_table = QTableWidget()
        self.feed_usage_table.setFont(QFont("Arial", TABLE_CELL_FONT_SIZE))

        # Thiết lập số cột và tiêu đề
        self.feed_usage_table.setColumnCount(3)
        self.feed_usage_table.setHorizontalHeaderLabels(["Thành phần", "Số lượng (kg)", "Đơn vị"])
        self.feed_usage_table.horizontalHeader().setFont(QFont("Arial", TABLE_HEADER_FONT_SIZE, QFont.Bold))

        # Thiết lập kích thước cột
        self.feed_usage_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Thiết lập style cho bảng
        self.feed_usage_table.setAlternatingRowColors(True)
        self.feed_usage_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #d0d0d0;
                background-color: white;
                alternate-background-color: #f5f5f5;
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

    def on_value_changed(self, value, row, col):
        """Xử lý sự kiện khi giá trị trong spin box thay đổi"""
        # Lấy thông tin về cell
        cell_key = f"{row}_{col}"
        spin_box = self.feed_spinboxes.get(cell_key)
        formula_combo = self.formula_combos.get(cell_key)
        formula_label = self.formula_labels.get(cell_key)

        if spin_box and formula_combo and formula_label:
            # Thiết lập prefix để ẩn số 0
            if value == 0:
                spin_box.setPrefix(" ")
            else:
                spin_box.setPrefix("")

            # Hiển thị/ẩn combo box và label tùy thuộc vào giá trị
            if value > 0:
                # Nếu chưa có công thức được chọn, tự động chọn công thức mặc định
                if not formula_combo.currentText() and hasattr(self.parent, 'auto_select_default_formula'):
                    self.parent.auto_select_default_formula(value, formula_combo)

                # Hiển thị tên công thức
                formula_text = formula_combo.currentText()
                formula_label.setText(formula_text)
                formula_label.setVisible(True)

                # Hiển thị combo box khi click vào cell
                if self.selected_cell == (row+2, col):  # +2 vì 2 hàng đầu là khu và trại
                    formula_combo.setVisible(True)
                    formula_label.setVisible(False)
                else:
                    formula_combo.setVisible(False)
                    formula_label.setVisible(True)
            else:
                # Ẩn combo box và label khi giá trị = 0
                formula_combo.setVisible(False)
                formula_label.setVisible(False)

            # Cập nhật trạng thái
            if hasattr(self.parent, 'update_status'):
                # Lấy thông tin khu và trại từ header
                khu_item = self.feed_table.item(0, col)
                farm_item = self.feed_table.item(1, col)

                khu_name = khu_item.text() if khu_item else f"Khu {col+1}"
                farm_name = farm_item.text() if farm_item else f"Trại {col+1}"

                formula_text = formula_combo.currentText()
                if value > 0 and formula_text:
                    self.parent.update_status(f"Đã cập nhật {khu_name}, {farm_name}, {SHIFTS[row]}: {value} ({formula_text})")
                elif value > 0:
                    self.parent.update_status(f"Cần chọn công thức cho {khu_name}, {farm_name}, {SHIFTS[row]}")
                else:
                    self.parent.update_status(f"Đã xóa giá trị cho {khu_name}, {farm_name}, {SHIFTS[row]}")

    def on_feed_table_cell_clicked(self, row, col):
        """Xử lý sự kiện khi người dùng click vào ô trong bảng cám"""
        # Bỏ qua các ô trong 2 hàng đầu (khu và trại)
        if row < 2:
            return

        # Lưu lại ô đang được chọn
        self.selected_cell = (row, col)

        # Hiển thị thông tin về cell trong thanh trạng thái
        if hasattr(self.parent, 'update_status'):
            # Lấy thông tin về cell
            cell_key = f"{row-2}_{col}"  # Trừ 2 vì 2 hàng đầu là khu và trại
            spin_box = self.feed_spinboxes.get(cell_key)
            formula_combo = self.formula_combos.get(cell_key)

            if spin_box and formula_combo:
                value = spin_box.value()
                formula = formula_combo.currentText()

                # Lấy thông tin khu và trại từ header
                khu_item = self.feed_table.item(0, col)
                farm_item = self.feed_table.item(1, col)

                khu_name = khu_item.text() if khu_item else f"Khu {col+1}"
                farm_name = farm_item.text() if farm_item else f"Trại {col+1}"

                if value > 0 and formula:
                    self.parent.update_status(f"{khu_name}, {farm_name}, {SHIFTS[row-2]}: {value} ({formula})")
                else:
                    self.parent.update_status(f"Đã chọn {khu_name}, {farm_name}, {SHIFTS[row-2]}")

    def show_context_menu(self, pos):
        """Hiển thị menu ngữ cảnh khi nhấp chuột phải vào bảng"""
        # Lấy vị trí ô được nhấp
        index = self.feed_table.indexAt(pos)
        row, col = index.row(), index.column()

        # Nếu nhấp vào vùng trống, thoát
        if row < 0 or col < 0:
            return

        # Lưu ô được chọn
        self.selected_cell = (row, col)

        # Tạo menu ngữ cảnh
        context_menu = QMenu(self)

        # Thêm các hành động
        reset_action = QAction("Reset ô này", self)
        reset_action.triggered.connect(lambda: self.reset_cell(row, col))
        context_menu.addAction(reset_action)

        # Thêm menu áp dụng công thức
        apply_formula_menu = QMenu("Áp dụng công thức", self)

        # Lấy danh sách công thức
        if hasattr(self.parent, 'formula_manager') and hasattr(self.parent.formula_manager, 'get_feed_presets'):
            feed_formulas = self.parent.formula_manager.get_feed_presets()

            # Thêm các công thức vào menu
            for formula in feed_formulas:
                formula_action = QAction(formula, self)
                formula_action.triggered.connect(lambda checked, f=formula: self.apply_formula_to_cell(row, col, f))
                apply_formula_menu.addAction(formula_action)

            context_menu.addMenu(apply_formula_menu)

        # Hiển thị menu tại vị trí con trỏ
        context_menu.exec_(self.feed_table.viewport().mapToGlobal(pos))

    def reset_cell(self, row, col):
        """Reset một ô về giá trị mặc định"""
        # Bỏ qua các ô trong 2 hàng đầu (khu và trại)
        if row < 2:
            return

        # Lấy thông tin về cell
        cell_key = f"{row-2}_{col}"  # Trừ 2 vì 2 hàng đầu là khu và trại
        spin_box = self.feed_spinboxes.get(cell_key)
        formula_combo = self.formula_combos.get(cell_key)

        if spin_box:
            spin_box.setValue(0)

        if formula_combo:
            formula_combo.setCurrentIndex(0)

        # Lấy thông tin khu và trại từ header
        khu_item = self.feed_table.item(0, col)
        farm_item = self.feed_table.item(1, col)

        khu_name = khu_item.text() if khu_item else f"Khu {col+1}"
        farm_name = farm_item.text() if farm_item else f"Trại {col+1}"

        # Cập nhật trạng thái
        if hasattr(self.parent, 'update_status'):
            self.parent.update_status(f"Đã reset ô {khu_name}, {farm_name}, {SHIFTS[row-2]}")

    def apply_formula_to_cell(self, row, col, formula):
        """Áp dụng công thức cho một ô"""
        # Bỏ qua các ô trong 2 hàng đầu (khu và trại)
        if row < 2:
            return

        # Lấy thông tin về cell
        cell_key = f"{row-2}_{col}"  # Trừ 2 vì 2 hàng đầu là khu và trại
        formula_combo = self.formula_combos.get(cell_key)

        if formula_combo:
            # Tìm và chọn công thức
            index = formula_combo.findText(formula)
            if index >= 0:
                formula_combo.setCurrentIndex(index)

                # Lấy thông tin khu và trại từ header
                khu_item = self.feed_table.item(0, col)
                farm_item = self.feed_table.item(1, col)

                khu_name = khu_item.text() if khu_item else f"Khu {col+1}"
                farm_name = farm_item.text() if farm_item else f"Trại {col+1}"

                # Cập nhật trạng thái
                if hasattr(self.parent, 'update_status'):
                    self.parent.update_status(f"Đã áp dụng công thức '{formula}' cho ô {khu_name}, {farm_name}, {SHIFTS[row-2]}")

    def reset_feed_table(self):
        """Reset toàn bộ bảng"""
        # Hiển thị hộp thoại xác nhận
        reply = QMessageBox.question(
            self,
            "Xác nhận reset",
            "Bạn có chắc chắn muốn xóa toàn bộ dữ liệu đã nhập trong bảng không?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Reset tất cả các ô
            for row in range(2, self.feed_table.rowCount()):  # Bắt đầu từ hàng thứ 3 (index 2)
                for col in range(self.feed_table.columnCount()):
                    cell_key = f"{row-2}_{col}"  # Trừ 2 vì 2 hàng đầu là khu và trại
                    spin_box = self.feed_spinboxes.get(cell_key)
                    formula_combo = self.formula_combos.get(cell_key)

                    if spin_box:
                        spin_box.setValue(0)

                    if formula_combo:
                        formula_combo.setCurrentIndex(0)

            # Thông báo thành công
            QMessageBox.information(self, "Thành công", "Đã xóa toàn bộ dữ liệu trong bảng!")

            # Cập nhật trạng thái
            if hasattr(self.parent, 'update_status'):
                self.parent.update_status("Đã reset bảng nhập liệu cám")

    def apply_default_formula(self):
        """Áp dụng công thức mặc định cho tất cả các ô"""
        if not hasattr(self, 'default_formula_combo'):
            return

        default_formula = self.default_formula_combo.currentText()

        # Nếu không có công thức mặc định được chọn, hiển thị thông báo và thoát
        if not default_formula:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một công thức cám mặc định trước khi áp dụng.")
            return

        # Lưu công thức mặc định
        if hasattr(self.parent, 'formula_manager') and hasattr(self.parent.formula_manager, 'save_default_feed_formula'):
            self.parent.formula_manager.save_default_feed_formula(default_formula)
            print(f"Đã lưu công thức cám mặc định: {default_formula}")

        # Đếm số ô đã áp dụng
        applied_count = 0

        # Áp dụng cho tất cả các ô trong bảng
        for row in range(2, self.feed_table.rowCount()):  # Bắt đầu từ hàng thứ 3 (index 2) vì 2 hàng đầu là khu và trại
            for col in range(self.feed_table.columnCount()):
                cell_key = f"{row-2}_{col}"  # Trừ 2 vì 2 hàng đầu là khu và trại
                formula_combo = self.formula_combos.get(cell_key)

                if formula_combo:
                    # Tìm và chọn công thức
                    index = formula_combo.findText(default_formula)
                    if index >= 0:
                        formula_combo.setCurrentIndex(index)
                        applied_count += 1

        # Hiển thị thông báo thành công
        QMessageBox.information(self, "Thành công",
                              f"Đã cài đặt và áp dụng công thức cám mặc định: {default_formula}\n"
                              f"Đã áp dụng cho {applied_count} ô trong bảng.")

        # Cập nhật trạng thái
        if hasattr(self.parent, 'update_status'):
            self.parent.update_status(f"Đã áp dụng công thức cám mặc định '{default_formula}' cho tất cả các ô")

    def update_formula_combos(self, formulas):
        """Cập nhật danh sách công thức trong tất cả các combo box"""
        for combo in self.formula_combos.values():
            current_text = combo.currentText()
            combo.clear()

            for formula in formulas:
                if isinstance(formula, dict):
                    combo.addItem(formula["name"])
                else:
                    combo.addItem(formula)

            # Giữ lại lựa chọn trước đó nếu có thể
            index = combo.findText(current_text)
            if index >= 0:
                combo.setCurrentIndex(index)