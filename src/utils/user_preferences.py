#!/usr/bin/env python3
"""
User Preferences Manager - Quản lý cài đặt người dùng
Lưu trữ và khôi phục các tùy chọn cá nhân của người dùng
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

class UserPreferencesManager:
    """Quản lý cài đặt người dùng"""

    def __init__(self):
        """Khởi tạo manager cài đặt người dùng"""
        # Xác định đường dẫn file cài đặt
        self.preferences_dir = self._get_preferences_directory()
        self.preferences_file = self.preferences_dir / "user_preferences.json"

        # Đảm bảo thư mục tồn tại
        self.preferences_dir.mkdir(parents=True, exist_ok=True)

        # Tải cài đặt hiện tại
        self.preferences = self._load_preferences()

    def _get_preferences_directory(self) -> Path:
        """Lấy thư mục lưu trữ cài đặt người dùng"""
        # Kiểm tra xem có đang chạy trong chế độ cài đặt chuyên nghiệp không
        if 'CFM_CONFIG_PATH' in os.environ:
            # Sử dụng đường dẫn từ biến môi trường
            return Path(os.environ['CFM_CONFIG_PATH'])
        else:
            # Sử dụng đường dẫn tương đối cho chế độ phát triển
            return Path(__file__).parent.parent / "data" / "config"

    def _load_preferences(self) -> Dict[str, Any]:
        """Tải cài đặt từ file"""
        try:
            if self.preferences_file.exists():
                with open(self.preferences_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError, UnicodeDecodeError) as e:
            print(f"Cảnh báo: Không thể tải cài đặt người dùng: {e}")

        # Trả về cài đặt mặc định
        return self._get_default_preferences()

    def _get_default_preferences(self) -> Dict[str, Any]:
        """Lấy cài đặt mặc định"""
        return {
            "export_folder_path": "",  # Rỗng = sử dụng đường dẫn mặc định
            "last_report_type": "complete",  # complete, inventory, production, employee
            "auto_open_after_export": True,
            "show_report_summary": True,
            "default_date_filter": False,
            "default_date_range_days": 30,
            "window_geometry": {},
            "dialog_positions": {}
        }

    def _save_preferences(self) -> bool:
        """Lưu cài đặt vào file"""
        try:
            with open(self.preferences_file, 'w', encoding='utf-8') as f:
                json.dump(self.preferences, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Lỗi khi lưu cài đặt người dùng: {e}")
            return False

    def get_export_folder_path(self) -> Optional[str]:
        """Lấy đường dẫn thư mục xuất file đã lưu"""
        path = self.preferences.get("export_folder_path", "")
        return path if path else None

    def set_export_folder_path(self, folder_path: str) -> bool:
        """Lưu đường dẫn thư mục xuất file"""
        try:
            # Kiểm tra đường dẫn có tồn tại không (chỉ cảnh báo, vẫn lưu)
            if folder_path and not Path(folder_path).exists():
                print(f"Cảnh báo: Đường dẫn không tồn tại: {folder_path}")
                # Vẫn lưu đường dẫn để người dùng có thể tạo thư mục sau

            self.preferences["export_folder_path"] = folder_path
            return self._save_preferences()
        except Exception as e:
            print(f"Lỗi khi lưu đường dẫn xuất file: {e}")
            return False

    def reset_export_folder_path(self) -> bool:
        """Đặt lại đường dẫn xuất file về mặc định"""
        return self.set_export_folder_path("")

    def get_last_report_type(self) -> str:
        """Lấy loại báo cáo được sử dụng lần cuối"""
        return self.preferences.get("last_report_type", "complete")

    def set_last_report_type(self, report_type: str) -> bool:
        """Lưu loại báo cáo được sử dụng lần cuối"""
        valid_types = ["complete", "inventory", "production", "employee"]
        if report_type in valid_types:
            self.preferences["last_report_type"] = report_type
            return self._save_preferences()
        return False

    def get_auto_open_after_export(self) -> bool:
        """Lấy cài đặt tự động mở file sau khi xuất"""
        return self.preferences.get("auto_open_after_export", True)

    def set_auto_open_after_export(self, auto_open: bool) -> bool:
        """Lưu cài đặt tự động mở file sau khi xuất"""
        self.preferences["auto_open_after_export"] = auto_open
        return self._save_preferences()

    def get_show_report_summary(self) -> bool:
        """Lấy cài đặt hiển thị tóm tắt báo cáo"""
        return self.preferences.get("show_report_summary", True)

    def set_show_report_summary(self, show_summary: bool) -> bool:
        """Lưu cài đặt hiển thị tóm tắt báo cáo"""
        self.preferences["show_report_summary"] = show_summary
        return self._save_preferences()

    def get_default_date_filter(self) -> bool:
        """Lấy cài đặt lọc ngày mặc định"""
        return self.preferences.get("default_date_filter", False)

    def set_default_date_filter(self, use_filter: bool) -> bool:
        """Lưu cài đặt lọc ngày mặc định"""
        self.preferences["default_date_filter"] = use_filter
        return self._save_preferences()

    def get_default_date_range_days(self) -> int:
        """Lấy số ngày mặc định cho lọc ngày"""
        return self.preferences.get("default_date_range_days", 30)

    def set_default_date_range_days(self, days: int) -> bool:
        """Lưu số ngày mặc định cho lọc ngày"""
        if days > 0:
            self.preferences["default_date_range_days"] = days
            return self._save_preferences()
        return False

    def get_preference(self, key: str, default_value: Any = None) -> Any:
        """Lấy cài đặt tùy chỉnh"""
        return self.preferences.get(key, default_value)

    def set_preference(self, key: str, value: Any) -> bool:
        """Lưu cài đặt tùy chỉnh"""
        try:
            self.preferences[key] = value
            return self._save_preferences()
        except Exception as e:
            print(f"Lỗi khi lưu cài đặt {key}: {e}")
            return False

    def reset_all_preferences(self) -> bool:
        """Đặt lại tất cả cài đặt về mặc định"""
        self.preferences = self._get_default_preferences()
        return self._save_preferences()

    def get_preferences_file_path(self) -> str:
        """Lấy đường dẫn file cài đặt"""
        return str(self.preferences_file)

    def export_preferences(self, export_path: str) -> bool:
        """Xuất cài đặt ra file"""
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self.preferences, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Lỗi khi xuất cài đặt: {e}")
            return False

    def import_preferences(self, import_path: str) -> bool:
        """Nhập cài đặt từ file"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_prefs = json.load(f)

            # Kiểm tra tính hợp lệ của cài đặt nhập vào
            if isinstance(imported_prefs, dict):
                self.preferences.update(imported_prefs)
                return self._save_preferences()
            else:
                print("Lỗi: File cài đặt không hợp lệ")
                return False
        except Exception as e:
            print(f"Lỗi khi nhập cài đặt: {e}")
            return False

# Global instance
user_preferences_manager = UserPreferencesManager()

# Convenience functions
def get_export_folder_path() -> Optional[str]:
    """Lấy đường dẫn thư mục xuất file đã lưu"""
    return user_preferences_manager.get_export_folder_path()

def set_export_folder_path(folder_path: str) -> bool:
    """Lưu đường dẫn thư mục xuất file"""
    return user_preferences_manager.set_export_folder_path(folder_path)

def reset_export_folder_path() -> bool:
    """Đặt lại đường dẫn xuất file về mặc định"""
    return user_preferences_manager.reset_export_folder_path()

def get_last_report_type() -> str:
    """Lấy loại báo cáo được sử dụng lần cuối"""
    return user_preferences_manager.get_last_report_type()

def set_last_report_type(report_type: str) -> bool:
    """Lưu loại báo cáo được sử dụng lần cuối"""
    return user_preferences_manager.set_last_report_type(report_type)
