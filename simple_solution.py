import os
import re

def add_feed_history_table():
    # Check if src/main.py exists
    if not os.path.exists('src/main.py'):
        print("src/main.py not found")
        return

    # Read the content of src/main.py
    with open('src/main.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Create a backup
    with open('src/main_backup.py', 'w', encoding='utf-8') as f:
        f.write(content)

    # Add the load_feed_usage_history method
    if 'def load_feed_usage_history(' not in content:
        # Find a good place to add the method (before the main function)
        main_pattern = r'def main\(\):'
        main_match = re.search(main_pattern, content)

        if main_match:
            load_feed_usage_history_method = '''
def load_feed_usage_history(self, show_message=True):
    """Tải lịch sử sử dụng cám từ các báo cáo đã lưu"""
    print("Tải lịch sử sử dụng cám")

    # Xóa dữ liệu cũ trong bảng
    if hasattr(self, 'feed_usage_history_table'):
        self.feed_usage_history_table.setRowCount(0)
    else:
        print("feed_usage_history_table not found")
        return

    # Reports directory
    reports_dir = "src/data/reports"

    # Check if reports directory exists
    if not os.path.exists(reports_dir):
        # Thử đường dẫn cũ
        reports_dir = "reports"
        if not os.path.exists(reports_dir):
            if show_message:
                QMessageBox.information(self, "Thông báo", "Không tìm thấy thư mục báo cáo!")
            return

    # Find all report files in the reports directory
    report_files = [os.path.join(reports_dir, f) for f in os.listdir(reports_dir)
                   if f.startswith('report_') and f.endswith('.json')]

    # Nếu không có file báo cáo
    if not report_files:
        if show_message:
            QMessageBox.information(self, "Thông báo", "Không tìm thấy báo cáo nào!")
        return

    # Sort by date (newest first)
    report_files.sort(reverse=True)

    # Danh sách lưu thông tin báo cáo
    history_data = []

    # Đọc dữ liệu từ các file báo cáo
    for report_file in report_files:
        try:
            # Extract date from filename (format: reports/report_YYYYMMDD.json)
            date_str = os.path.basename(report_file)[7:-5]  # Remove 'report_' and '.json'

            # Format date as DD/MM/YYYY for display
            if len(date_str) == 8:  # Đảm bảo đúng định dạng YYYYMMDD
                year = date_str[0:4]
                month = date_str[4:6]
                day = date_str[6:8]
                formatted_date = f"{day}/{month}/{year}"

                # Đọc dữ liệu báo cáo
                with open(report_file, 'r', encoding='utf-8') as f:
                    report_data = json.load(f)

                # Lấy tổng lượng cám và tổng số mẻ từ báo cáo
                total_feed = 0
                total_mix = 0
                batch_count = 0

                # Ưu tiên sử dụng dữ liệu đã tính toán sẵn trong báo cáo
                if "total_feed" in report_data and "total_mix" in report_data and "batch_count" in report_data:
                    total_feed = report_data["total_feed"]
                    total_mix = report_data["total_mix"]
                    batch_count = report_data["batch_count"]
                else:
                    # Nếu không có dữ liệu đã tính toán, tính từ dữ liệu sử dụng
                    if "feed_ingredients" in report_data:
                        # Tính tổng lượng cám từ thành phần
                        for ingredient, amount in report_data["feed_ingredients"].items():
                            if ingredient != "Nguyên liệu tổ hợp":  # Không tính mix
                                total_feed += amount

                    if "mix_ingredients" in report_data:
                        # Tính tổng lượng mix từ thành phần
                        for ingredient, amount in report_data["mix_ingredients"].items():
                            total_mix += amount

                    # Tính tổng số mẻ từ dữ liệu sử dụng
                    if "feed_usage" in report_data:
                        for khu, farms in report_data["feed_usage"].items():
                            for farm, shifts in farms.items():
                                for shift, value in shifts.items():
                                    batch_count += value

                # Thêm vào danh sách
                history_data.append({
                    "date": formatted_date,
                    "total_feed": total_feed,
                    "total_mix": total_mix,
                    "batch_count": batch_count,
                    "report_file": report_file
                })

        except Exception as e:
            print(f"Lỗi khi đọc file báo cáo {report_file}: {str(e)}")

    # Hiển thị dữ liệu lịch sử
    self.feed_usage_history_table.setRowCount(len(history_data))

    for row, data in enumerate(history_data):
        # Ngày báo cáo
        date_item = QTableWidgetItem(data["date"])
        date_item.setTextAlignment(Qt.AlignCenter)
        self.feed_usage_history_table.setItem(row, 0, date_item)

        # Tổng lượng cám
        total_feed_item = QTableWidgetItem(format_number(data["total_feed"]))
        total_feed_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.feed_usage_history_table.setItem(row, 1, total_feed_item)

        # Tổng lượng mix
        total_mix_item = QTableWidgetItem(format_number(data["total_mix"]))
        total_mix_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.feed_usage_history_table.setItem(row, 2, total_mix_item)

        # Tổng số mẻ
        batch_count_item = QTableWidgetItem(format_number(data["batch_count"]))
        batch_count_item.setTextAlignment(Qt.AlignCenter)
        self.feed_usage_history_table.setItem(row, 3, batch_count_item)

        # Lưu đường dẫn file báo cáo vào data của item
        date_item.setData(Qt.UserRole, data["report_file"])

    # Hiển thị thông báo
    if show_message:
        QMessageBox.information(self, "Thông báo", f"Tìm thấy {len(history_data)} báo cáo!")

def on_history_row_double_clicked(self, index):
    """Xử lý sự kiện khi double click vào hàng trong bảng lịch sử"""
    row = index.row()

    # Lấy đường dẫn file báo cáo từ item đầu tiên của hàng
    report_file = self.feed_usage_history_table.item(row, 0).data(Qt.UserRole)

    # Lấy ngày từ item đầu tiên của hàng
    date_text = self.feed_usage_history_table.item(row, 0).text()

    # Tải dữ liệu vào bảng cám
    self.load_feed_table_from_history(report_file, date_text)

def load_feed_table_from_history(self, report_file, date_text, show_message=False):
    """Tải dữ liệu từ báo cáo lịch sử vào bảng cám"""
    try:
        # Đọc dữ liệu báo cáo
        with open(report_file, 'r', encoding='utf-8') as f:
            report_data = json.load(f)

        # Reset bảng cám trước khi điền dữ liệu mới
        self.reset_feed_table()

        # Điền dữ liệu vào bảng cám
        if "feed_usage" in report_data:
            feed_usage = report_data["feed_usage"]

            # Duyệt qua từng khu và trại
            col_index = 0
            for khu_idx, farms in FARMS.items():
                khu_name = f"Khu {khu_idx + 1}"

                for farm_idx, farm in enumerate(farms):
                    # Nếu có dữ liệu cho khu và trại này
                    if khu_name in feed_usage and farm in feed_usage[khu_name]:
                        farm_data = feed_usage[khu_name][farm]

                        # Điền dữ liệu cho từng ca
                        for shift_idx, shift in enumerate(SHIFTS):
                            if shift in farm_data:
                                value = farm_data[shift]

                                # Lấy cell widget
                                cell_widget = self.feed_table.cellWidget(shift_idx + 2, col_index)
                                if cell_widget and hasattr(cell_widget, 'spin_box'):
                                    cell_widget.spin_box.setValue(value)

                                    # Nếu có dữ liệu công thức, cập nhật công thức
                                    if "formula_usage" in report_data and khu_name in report_data["formula_usage"] and farm in report_data["formula_usage"][khu_name] and shift in report_data["formula_usage"][khu_name][farm]:
                                        formula = report_data["formula_usage"][khu_name][farm][shift]
                                        if formula and hasattr(cell_widget, 'formula_combo'):
                                            # Tìm index của công thức trong combo box
                                            index = cell_widget.formula_combo.findText(formula)
                                            if index >= 0:
                                                cell_widget.formula_combo.setCurrentIndex(index)

                    col_index += 1

        # Nếu có dữ liệu công thức mix cho cột, cập nhật
        if "column_mix_formulas" in report_data:
            self.column_mix_formulas = report_data["column_mix_formulas"]

        # Nếu có dữ liệu công thức mix cho từng ô, cập nhật
        if "cell_mix_formulas" in report_data:
            self.cell_mix_formulas = report_data["cell_mix_formulas"]

        # Tính toán lại kết quả
        self.calculate_feed_usage()

        # Hiển thị thông báo
        if show_message:
            QMessageBox.information(self, "Thông báo", f"Đã điền bảng cám từ báo cáo ngày {date_text}")

    except Exception as e:
        print(f"Lỗi khi tải dữ liệu từ báo cáo: {str(e)}")
        if show_message:
            QMessageBox.warning(self, "Lỗi", f"Không thể tải dữ liệu từ báo cáo: {str(e)}")
'''

            # Insert the methods before the main function
            insert_pos = main_match.start()
            content = content[:insert_pos] + load_feed_usage_history_method + content[insert_pos:]

    # Modify the setup_feed_usage_tab method to add the feed history table
    setup_feed_usage_tab_pattern = r'def setup_feed_usage_tab\(self\):.*?self\.feed_usage_tab\.setLayout\(layout\)'
    setup_feed_usage_tab_match = re.search(setup_feed_usage_tab_pattern, content, re.DOTALL)

    if setup_feed_usage_tab_match:
        current_method = setup_feed_usage_tab_match.group(0)

        # Check if feed_usage_history_table is already in the method
        if 'self.feed_usage_history_table' not in current_method:
            # Replace layout.addWidget(self.feed_table) with GroupBoxes
            new_method = current_method.replace(
                'layout.addWidget(self.feed_table)',
                '''# Tạo GroupBox cho bảng nhập liệu cám
        feed_group = QGroupBox("Bảng Điền Mẻ Cám")
        feed_group.setFont(QFont("Arial", DEFAULT_FONT_SIZE, QFont.Bold))
        feed_layout = QVBoxLayout()
        feed_layout.addWidget(self.feed_table)
        feed_group.setLayout(feed_layout)

        # Tạo GroupBox cho bảng lịch sử cám
        history_group = QGroupBox("Lịch sử mẻ cám các ngày trước")
        history_group.setFont(QFont("Arial", DEFAULT_FONT_SIZE, QFont.Bold))
        history_layout = QVBoxLayout()

        # Tạo bảng lịch sử cám
        self.feed_usage_history_table = QTableWidget()
        self.feed_usage_history_table.setFont(TABLE_CELL_FONT)
        self.feed_usage_history_table.setColumnCount(4)
        self.feed_usage_history_table.setHorizontalHeaderLabels(["Ngày báo cáo", "Tổng lượng cám (kg)", "Tổng lượng mix (kg)", "Tổng số mẻ cám"])
        self.feed_usage_history_table.horizontalHeader().setFont(TABLE_HEADER_FONT)
        self.feed_usage_history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.feed_usage_history_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #aaa;
                selection-background-color: #e0e0ff;
                alternate-background-color: #f9f9f9;
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
        self.feed_usage_history_table.setAlternatingRowColors(True)
        self.feed_usage_history_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Chỉ đọc

        # Tăng chiều cao hàng cho bảng lịch sử
        self.feed_usage_history_table.verticalHeader().setDefaultSectionSize(40)

        # Kết nối sự kiện double click vào hàng để tải dữ liệu vào bảng cám
        self.feed_usage_history_table.doubleClicked.connect(self.on_history_row_double_clicked)

        history_layout.addWidget(self.feed_usage_history_table)
        history_group.setLayout(history_layout)

        # Thêm các GroupBox vào layout chính với tỷ lệ 20:70
        layout.addWidget(feed_group, 20)
        layout.addWidget(history_group, 70)'''
            )

            # Replace the old method with the new one
            content = content.replace(current_method, new_method)

    # Modify the init_ui method to load feed usage history on startup
    init_ui_pattern = r'def init_ui\(self\):.*?# Tự động tải báo cáo mới nhất khi khởi động.*?QTimer\.singleShot\(\d+, [^)]+\)'
    init_ui_match = re.search(init_ui_pattern, content, re.DOTALL)

    if init_ui_match:
        current_init_ui = init_ui_match.group(0)

        # Add code to load feed usage history on startup
        if 'load_feed_usage_history' not in current_init_ui:
            new_init_ui = current_init_ui + '\n        QTimer.singleShot(1500, lambda: self.load_feed_usage_history(show_message=False))'
            content = content.replace(current_init_ui, new_init_ui)

    # Modify the save_report method to save calculated totals
    save_report_pattern = r'def save_report\(self\):.*?return True, filename\s+except Exception as e:'
    save_report_match = re.search(save_report_pattern, content, re.DOTALL)

    if save_report_match:
        current_save_report = save_report_match.group(0)

        # Check if we already have the total_feed, total_mix, batch_count fields
        if 'total_feed' not in current_save_report or 'total_mix' not in current_save_report or 'batch_count' not in current_save_report:
            # Add the fields to the report_data
            new_save_report = current_save_report.replace(
                '"date": QDate.currentDate().toString(\'dd/MM/yyyy\'),',
                '"date": QDate.currentDate().toString(\'dd/MM/yyyy\'),\n'
                '            "total_feed": total_feed,\n'
                '            "total_mix": total_mix,\n'
                '            "batch_count": batch_count,'
            )

            # Add code to update history after saving
            new_save_report = new_save_report.replace(
                'return True, filename',
                '# Cập nhật lịch sử cám\n'
                '        self.load_feed_usage_history(show_message=False)\n'
                '            \n'
                '        return True, filename'
            )

            # Replace the old save_report with the new one
            content = content.replace(current_save_report, new_save_report)

    # Write the modified content back to the file
    with open('src/main.py', 'w', encoding='utf-8') as f:
        f.write(content)

    print("Successfully added feed history table to main.py")

if __name__ == "__main__":
    add_feed_history_table()