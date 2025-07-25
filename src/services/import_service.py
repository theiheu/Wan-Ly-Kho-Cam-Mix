"""
Import Service for the Chicken Farm App
Handles importing feed and mix ingredients
"""

import os
import json
from datetime import datetime

class ImportService:
    """Service for importing feed and mix ingredients"""

    def __init__(self, inventory_manager, data_path="data"):
        """Initialize the import service with inventory manager and data path"""
        self.inventory_manager = inventory_manager

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

    def import_feed(self, ingredient, amount):
        """Import feed ingredient"""
        # Cập nhật tồn kho
        self.inventory_manager.update_inventory_item("feed", ingredient, amount)

        # Lưu lịch sử nhập
        date = datetime.now().strftime("%Y-%m-%d")
        self.save_import_history("feed", ingredient, amount, date, "")

        return True

    def import_mix(self, ingredient, amount):
        """Import mix ingredient"""
        # Cập nhật tồn kho
        self.inventory_manager.update_inventory_item("mix", ingredient, amount)

        # Lưu lịch sử nhập
        date = datetime.now().strftime("%Y-%m-%d")
        self.save_import_history("mix", ingredient, amount, date, "")

        return True

    def save_import_history(self, import_type, ingredient, amount, date, note=""):
        """Save import history to JSON file"""
        # Đọc lịch sử hiện tại
        history = []
        if os.path.exists(self.import_history_file):
            with open(self.import_history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)

        # Thêm bản ghi mới
        history.append({
            "type": import_type,
            "ingredient": ingredient,
            "amount": amount,
            "date": date,
            "note": note,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        # Lưu lại lịch sử
        with open(self.import_history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=4)

    def load_import_history(self):
        """Load import history from JSON file"""
        if not os.path.exists(self.import_history_file):
            return []

        with open(self.import_history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)

        return history