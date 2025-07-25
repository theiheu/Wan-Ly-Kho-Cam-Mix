"""
History Service for the Chicken Farm App
Handles loading, saving, and managing history data
"""

import os
import json
from datetime import datetime, timedelta

class HistoryService:
    """Service for managing history data"""

    def __init__(self, data_path="data"):
        """Initialize the history service with data path"""
        # Kiểm tra xem đang chạy từ thư mục gốc hay từ thư mục src
        if os.path.exists("src"):
            self.data_path = os.path.join("src", data_path)
        else:
            self.data_path = data_path

        # Đảm bảo thư mục history tồn tại
        self.history_dir = os.path.join(self.data_path, "history")
        os.makedirs(self.history_dir, exist_ok=True)

        # File lưu lịch sử nhập
        self.import_history_file = os.path.join(self.history_dir, "import_history.json")

        # Tạo file lịch sử nhập nếu chưa tồn tại
        if not os.path.exists(self.import_history_file):
            with open(self.import_history_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=4)

    def load_history_data(self, start_date=None, end_date=None):
        """Load history data for a date range"""
        # If no dates provided, use today
        if start_date is None:
            start_date = datetime.now().strftime("%Y-%m-%d")
        if end_date is None:
            end_date = start_date

        # Convert to datetime objects for comparison
        try:
            # Try with format "%Y-%m-%d"
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            try:
                # Try with format "%Y%m%d"
                start_dt = datetime.strptime(start_date, "%Y%m%d")
            except ValueError:
                # Default to today
                start_dt = datetime.now()
                start_date = start_dt.strftime("%Y-%m-%d")

        try:
            # Try with format "%Y-%m-%d"
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            try:
                # Try with format "%Y%m%d"
                end_dt = datetime.strptime(end_date, "%Y%m%d")
            except ValueError:
                # Default to today
                end_dt = datetime.now()
                end_date = end_dt.strftime("%Y-%m-%d")

        # Load import history
        import_history = self.load_import_history()

        # Filter by date range
        filtered_history = []
        for item in import_history:
            item_date = datetime.strptime(item["date"], "%Y-%m-%d")
            if start_dt <= item_date <= end_dt:
                filtered_history.append(item)

        # Separate by type
        feed_history = [item for item in filtered_history if item["type"] == "feed"]
        mix_history = [item for item in filtered_history if item["type"] == "mix"]

        # Load usage history from reports
        reports_dir = os.path.join(self.data_path, "reports")
        usage_history = []

        # Iterate through each day in the date range
        current_date = start_dt
        while current_date <= end_dt:
            date_str = current_date.strftime("%Y-%m-%d")
            report_file = os.path.join(reports_dir, f"report_{date_str}.json")

            if os.path.exists(report_file):
                with open(report_file, 'r', encoding='utf-8') as f:
                    report_data = json.load(f)
                    if "usage" in report_data:
                        for usage_item in report_data["usage"]:
                            usage_item["date"] = date_str
                            usage_history.append(usage_item)

            current_date += timedelta(days=1)

        # Return all history data
        return {
            "feed": feed_history,
            "mix": mix_history,
            "usage": usage_history
        }

    def load_import_history(self):
        """Load import history from JSON file"""
        if not os.path.exists(self.import_history_file):
            return []

        with open(self.import_history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)

        return history

    def get_available_dates(self):
        """Get a list of dates for which history data is available"""
        dates = set()

        # Check import history
        if os.path.exists(self.import_history_file):
            with open(self.import_history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
                for item in history:
                    dates.add(item["date"])

        # Check reports
        reports_dir = os.path.join(self.data_path, "reports")
        if os.path.exists(reports_dir):
            for filename in os.listdir(reports_dir):
                if filename.startswith("report_") and filename.endswith(".json"):
                    date_text = filename[7:-5]  # Remove "report_" and ".json"
                    dates.add(date_text)

        # Sort dates in descending order (newest first)
        return sorted(list(dates), reverse=True)

    def compare_history_data(self, current_date, compare_date):
        """Compare history data between two dates"""
        # Load data for both dates
        current_data = self.load_history_data(current_date, current_date)
        compare_data = self.load_history_data(compare_date, compare_date)

        return current_data, compare_data