import re
import os
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem
from PyQt5.QtCore import Qt
import json

# Đọc nội dung file
with open('src/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Tìm vị trí để thêm phương thức
class_end_match = re.search(r'def main\(\):', content)
if class_end_match:
    insert_position = class_end_match.start()

    # Phương thức load_feed_usage_history
    method_to_add = '''
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

    # Thêm phương thức vào trước hàm main
    content = content[:insert_position] + method_to_add + '\n' + content[insert_position:]

    # Ghi nội dung đã sửa vào file
    with open('src/main.py', 'w', encoding='utf-8') as f:
        f.write(content)

    print("Đã thêm phương thức load_feed_usage_history vào lớp ChickenFarmApp")