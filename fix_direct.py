import os
import re
import shutil

# Tạo backup
shutil.copy('src/main.py', 'src/main_backup_fix.py')

# Đọc nội dung file
with open('src/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Thêm phương thức on_history_row_double_clicked
on_history_method = '''
    def on_history_row_double_clicked(self, index):
        """Xử lý sự kiện khi double click vào hàng trong bảng lịch sử"""
        row = index.row()

        # Lấy đường dẫn file báo cáo từ item đầu tiên của hàng
        report_file = self.feed_usage_history_table.item(row, 0).data(Qt.UserRole)

        # Lấy ngày từ item đầu tiên của hàng
        date_text = self.feed_usage_history_table.item(row, 0).text()

        # Tải dữ liệu vào bảng cám
        self.load_feed_table_from_history(report_file, date_text)
'''

# Thêm phương thức load_feed_table_from_history
load_feed_method = '''
    def load_feed_table_from_history(self, report_file, date_text, show_message=False):
        """Tải dữ liệu từ báo cáo lịch sử vào bảng cám"""
        try:
            # Đọc dữ liệu báo cáo
            with open(report_file, 'r', encoding='utf-8') as f:
                report_data = json.load(f)

            # Reset bảng cám trước khi điền dữ liệu mới
            self.reset_feed_table_silent()

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

# Thêm phương thức reset_feed_table_silent
reset_feed_method = '''
    def reset_feed_table_silent(self):
        """Reset bảng cám mà không hiển thị thông báo"""
        # Xóa dữ liệu hiện tại trong bảng
        for col in range(self.feed_table.columnCount()):
            for row in range(2, 2 + len(SHIFTS)):
                cell_widget = self.feed_table.cellWidget(row, col)
                if cell_widget and hasattr(cell_widget, 'spin_box'):
                    cell_widget.spin_box.setValue(0)
                if cell_widget and hasattr(cell_widget, 'formula_combo'):
                    cell_widget.formula_combo.setCurrentText("")

        # Xóa dữ liệu công thức mix cho từng ô
        if hasattr(self, 'cell_mix_formulas'):
            self.cell_mix_formulas = {}
'''

# Thêm phương thức load_feed_usage_history
load_history_method = '''
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
        report_files = []
        for f in os.listdir(reports_dir):
            if f.startswith('report_') and f.endswith('.json'):
                report_files.append(os.path.join(reports_dir, f))

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
                file_name = os.path.basename(report_file)
                if file_name.startswith('report_') and file_name.endswith('.json'):
                    date_str = file_name[7:-5]  # Remove 'report_' and '.json'

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
                            print(f"Sử dụng dữ liệu tính sẵn cho {formatted_date}: {total_feed} kg cám, {total_mix} kg mix, {batch_count} mẻ")
                        else:
                            print(f"Không tìm thấy dữ liệu tính sẵn, tính lại từ dữ liệu gốc cho {formatted_date}")
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
                    else:
                        print(f"Định dạng ngày không hợp lệ trong file: {report_file}")

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
'''

# Tìm vị trí để thêm các phương thức
# Tìm vị trí kết thúc của class ChickenFarmApp
class_end_match = re.search(r'def main\(\):', content)
if class_end_match:
    insert_position = class_end_match.start()

    # Thêm các phương thức vào trước hàm main
    content = content[:insert_position] + on_history_method + load_feed_method + reset_feed_method + load_history_method + content[insert_position:]

# Sửa setup_feed_usage_tab để thay đổi tỷ lệ kích thước
setup_feed_pattern = r'# Thêm các GroupBox vào layout chính với tỷ lệ \d+:\d+'
setup_feed_match = re.search(setup_feed_pattern, content)
if setup_feed_match:
    old_ratio = setup_feed_match.group(0)
    new_ratio = '# Thêm các GroupBox vào layout chính với tỷ lệ 60:40'
    content = content.replace(old_ratio, new_ratio)

# Sửa tỷ lệ thực tế của các GroupBox
ratio_pattern = r'layout\.addWidget\(feed_group, \d+\)\s+layout\.addWidget\(history_group, \d+\)'
ratio_match = re.search(ratio_pattern, content)
if ratio_match:
    old_ratio_code = ratio_match.group(0)
    new_ratio_code = 'layout.addWidget(feed_group, 60)\n        layout.addWidget(history_group, 40)'
    content = content.replace(old_ratio_code, new_ratio_code)

# Thêm QTimer để tự động tải lịch sử cám khi khởi động
init_ui_pattern = r'QTimer\.singleShot\(\d+, .*?self\.load_latest_report.*?\)'
init_ui_match = re.search(init_ui_pattern, content)
if init_ui_match:
    latest_report_line = init_ui_match.group(0)
    # Thêm timer mới nếu chưa có
    if 'QTimer.singleShot(1500, lambda: self.load_feed_usage_history(show_message=False))' not in content:
        new_init_ui = content.replace(
            latest_report_line,
            f"{latest_report_line}\n        QTimer.singleShot(1500, lambda: self.load_feed_usage_history(show_message=False))"
        )
        content = new_init_ui

# Ghi nội dung đã sửa vào file
with open('src/main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Đã sửa xong file src/main.py")