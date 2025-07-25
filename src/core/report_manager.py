"""
Report Manager for the Chicken Farm App
Handles report generation, loading, and management
"""

import os
import json
from datetime import datetime
import pandas as pd

class ReportManager:
    """Manages report data, generation, loading, and exporting"""

    def __init__(self, data_path="data"):
        """Initialize the report manager with the data path"""
        # Kiểm tra xem đang chạy từ thư mục gốc hay từ thư mục src
        if os.path.exists("src"):
            self.data_path = os.path.join("src", data_path)
        else:
            self.data_path = data_path

        # Đảm bảo thư mục reports tồn tại
        self.reports_dir = os.path.join(self.data_path, "reports")
        os.makedirs(self.reports_dir, exist_ok=True)

    def save_report(self, report_data):
        """Save report data to a JSON file"""
        # Lấy ngày từ report_data
        date = report_data.get("date", datetime.now().strftime("%Y-%m-%d"))

        # Tạo tên file từ ngày
        filename = f"report_{date}.json"
        filepath = os.path.join(self.reports_dir, filename)

        # Lưu dữ liệu vào file JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=4)

        return filepath

    def load_report(self, date_text):
        """Load a report from a specific date"""
        # Tạo tên file từ ngày
        filename = f"report_{date_text}.json"
        filepath = os.path.join(self.reports_dir, filename)

        # Kiểm tra xem file có tồn tại không
        if not os.path.exists(filepath):
            return None

        # Đọc dữ liệu từ file JSON
        with open(filepath, 'r', encoding='utf-8') as f:
            report_data = json.load(f)

        return report_data

    def get_available_dates(self):
        """Get a list of dates for which reports are available"""
        dates = []

        # Lấy danh sách các file báo cáo
        for filename in os.listdir(self.reports_dir):
            if filename.startswith("report_") and filename.endswith(".json"):
                # Trích xuất ngày từ tên file
                date_text = filename[7:-5]  # Loại bỏ "report_" và ".json"
                dates.append(date_text)

        # Sắp xếp theo ngày giảm dần (mới nhất trước)
        dates.sort(reverse=True)
        return dates

    def export_to_excel(self, report_data, output_path=None):
        """Export report data to Excel file"""
        # Nếu không có đường dẫn output, tạo tên file từ ngày
        if output_path is None:
            date = report_data.get("date", datetime.now().strftime("%Y-%m-%d"))
            output_path = f"Báo cáo {date}.xlsx"

        # Tạo Excel writer
        writer = pd.ExcelWriter(output_path, engine='xlsxwriter')

        # TODO: Implement Excel export logic
        # This will be implemented based on the specific report format

        writer.close()
        return output_path