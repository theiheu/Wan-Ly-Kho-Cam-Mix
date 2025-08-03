#!/usr/bin/env python3
"""
Threshold Manager - Quản lý ngưỡng cảnh báo tồn kho
Cho phép người dùng cài đặt ngưỡng cho các mức cảnh báo khác nhau
"""

import json
import os
from typing import Dict, Tuple

class ThresholdManager:
    """Quản lý ngưỡng cảnh báo tồn kho"""

    def __init__(self):
        self.config_file = "src/data/threshold_config.json"
        self.individual_config_file = "src/data/individual_thresholds.json"
        self.default_thresholds = {
            # Ngưỡng cơ bản
            "critical_days": 7,      # Khẩn cấp: < 7 ngày
            "warning_days": 14,      # Sắp hết: 7-14 ngày
            "sufficient_days": 14,   # Đủ hàng: > 14 ngày
            "critical_stock": 0,     # Khẩn cấp: <= 0 kg
            "warning_stock": 100,    # Sắp hết: <= 100 kg
            "sufficient_stock": 500, # Đủ hàng: > 500 kg
            "use_days_based": True,  # Ưu tiên tính theo ngày
            "use_stock_based": False, # Tính theo số lượng tồn kho

            # Tùy chọn hiển thị
            "display_unit": "both",  # "days", "stock", "both"
            "show_days_in_table": True,
            "show_stock_in_table": True,

            # Tùy chọn âm thanh
            "sound_enabled": True,
            "sound_critical": True,   # Âm thanh cho cảnh báo khẩn cấp
            "sound_warning": False,   # Âm thanh cho cảnh báo sắp hết
            "sound_volume": 50,       # Âm lượng (0-100)

            # Tùy chọn kiểm tra tự động
            "auto_check_enabled": True,
            "check_frequency": "hourly",  # "hourly", "daily", "startup_only"
            "check_interval_hours": 1,    # Số giờ giữa các lần kiểm tra

            # Tùy chọn popup
            "popup_enabled": True,
            "popup_on_startup": True,
            "popup_on_critical": True,
            "popup_on_warning": False,

            # Tùy chọn báo cáo tự động
            "auto_report_enabled": False,
            "report_frequency": "daily",  # "daily", "weekly", "monthly"
            "report_time": "08:00",       # Thời gian xuất báo cáo (HH:MM)
            "report_path": "reports/alerts",  # Đường dẫn lưu báo cáo

            # Tùy chọn màu sắc
            "color_critical": "#f44336",  # Đỏ
            "color_warning": "#ff9800",   # Cam
            "color_sufficient": "#4caf50", # Xanh lá
            "color_no_data": "#9e9e9e",   # Xám
            "use_custom_colors": False,   # Sử dụng màu tùy chỉnh
        }
        self.thresholds = self.load_thresholds()
        self.individual_thresholds = self.load_individual_thresholds()

    def load_thresholds(self) -> Dict:
        """Tải cài đặt ngưỡng từ file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_thresholds = json.load(f)

                # Merge với default để đảm bảo có đầy đủ các key
                thresholds = self.default_thresholds.copy()
                thresholds.update(loaded_thresholds)

                print(f"[INFO] Đã tải cài đặt ngưỡng từ {self.config_file}")
                return thresholds
            else:
                print(f"[INFO] Không tìm thấy file cài đặt, sử dụng ngưỡng mặc định")
                return self.default_thresholds.copy()

        except Exception as e:
            print(f"[ERROR] Lỗi khi tải cài đặt ngưỡng: {e}")
            return self.default_thresholds.copy()

    def load_individual_thresholds(self) -> Dict:
        """Tải cài đặt ngưỡng riêng biệt cho từng thành phần"""
        try:
            if os.path.exists(self.individual_config_file):
                with open(self.individual_config_file, 'r', encoding='utf-8') as f:
                    individual_thresholds = json.load(f)

                print(f"[INFO] Đã tải cài đặt ngưỡng riêng biệt cho {len(individual_thresholds)} thành phần")
                return individual_thresholds
            else:
                print(f"[INFO] Chưa có cài đặt ngưỡng riêng biệt")
                return {}

        except Exception as e:
            print(f"[ERROR] Lỗi khi tải cài đặt ngưỡng riêng biệt: {e}")
            return {}

    def save_individual_thresholds(self) -> bool:
        """Lưu cài đặt ngưỡng riêng biệt vào file"""
        try:
            # Tạo thư mục nếu chưa tồn tại
            os.makedirs(os.path.dirname(self.individual_config_file), exist_ok=True)

            with open(self.individual_config_file, 'w', encoding='utf-8') as f:
                json.dump(self.individual_thresholds, f, indent=2, ensure_ascii=False)

            print(f"[SUCCESS] Đã lưu cài đặt ngưỡng riêng biệt cho {len(self.individual_thresholds)} thành phần")
            return True

        except Exception as e:
            print(f"[ERROR] Lỗi khi lưu cài đặt ngưỡng riêng biệt: {e}")
            return False

    def save_thresholds(self) -> bool:
        """Lưu cài đặt ngưỡng vào file"""
        try:
            # Tạo thư mục nếu chưa tồn tại
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)

            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.thresholds, f, indent=2, ensure_ascii=False)

            print(f"[SUCCESS] Đã lưu cài đặt ngưỡng vào {self.config_file}")
            return True

        except Exception as e:
            print(f"[ERROR] Lỗi khi lưu cài đặt ngưỡng: {e}")
            return False

    def get_thresholds(self) -> Dict:
        """Lấy cài đặt ngưỡng hiện tại"""
        return self.thresholds.copy()

    def update_thresholds(self, new_thresholds: Dict) -> bool:
        """Cập nhật cài đặt ngưỡng"""
        try:
            # Validate input
            required_keys = [
                "critical_days", "warning_days", "sufficient_days",
                "critical_stock", "warning_stock", "sufficient_stock",
                "use_days_based", "use_stock_based"
            ]

            for key in required_keys:
                if key not in new_thresholds:
                    print(f"[ERROR] Thiếu key bắt buộc: {key}")
                    return False

            # Validate logic
            if new_thresholds["critical_days"] >= new_thresholds["warning_days"]:
                print(f"[ERROR] Ngưỡng khẩn cấp ({new_thresholds['critical_days']}) phải nhỏ hơn ngưỡng cảnh báo ({new_thresholds['warning_days']})")
                return False

            if new_thresholds["warning_days"] >= new_thresholds["sufficient_days"]:
                print(f"[ERROR] Ngưỡng cảnh báo ({new_thresholds['warning_days']}) phải nhỏ hơn ngưỡng đủ hàng ({new_thresholds['sufficient_days']})")
                return False

            # Update thresholds
            self.thresholds.update(new_thresholds)

            # Save to file
            return self.save_thresholds()

        except Exception as e:
            print(f"[ERROR] Lỗi khi cập nhật ngưỡng: {e}")
            return False

    def set_individual_threshold(self, ingredient: str, threshold_type: str, value: float) -> bool:
        """
        Cài đặt ngưỡng riêng biệt cho một thành phần
        threshold_type: 'critical_days', 'warning_days', 'sufficient_days',
                       'critical_stock', 'warning_stock', 'sufficient_stock'
        """
        try:
            if ingredient not in self.individual_thresholds:
                self.individual_thresholds[ingredient] = {}

            self.individual_thresholds[ingredient][threshold_type] = value

            # Validate logic for this ingredient
            thresholds = self.get_ingredient_thresholds(ingredient)
            if thresholds["critical_days"] >= thresholds["warning_days"]:
                print(f"[ERROR] Ngưỡng khẩn cấp ({thresholds['critical_days']}) phải nhỏ hơn ngưỡng cảnh báo ({thresholds['warning_days']}) cho {ingredient}")
                return False

            return self.save_individual_thresholds()

        except Exception as e:
            print(f"[ERROR] Lỗi khi cài đặt ngưỡng cho {ingredient}: {e}")
            return False

    def get_individual_thresholds(self) -> Dict:
        """Lấy tất cả cài đặt ngưỡng riêng biệt"""
        return self.individual_thresholds.copy()

    def get_ingredient_thresholds(self, ingredient: str) -> Dict:
        """
        Lấy ngưỡng cho một thành phần cụ thể
        Ưu tiên ngưỡng riêng biệt, fallback về ngưỡng chung
        """
        # Bắt đầu với ngưỡng chung
        result = self.thresholds.copy()

        # Override với ngưỡng riêng biệt nếu có
        if ingredient in self.individual_thresholds:
            result.update(self.individual_thresholds[ingredient])

        return result

    def remove_individual_threshold(self, ingredient: str) -> bool:
        """Xóa cài đặt ngưỡng riêng biệt cho một thành phần"""
        try:
            if ingredient in self.individual_thresholds:
                del self.individual_thresholds[ingredient]
                return self.save_individual_thresholds()
            return True
        except Exception as e:
            print(f"[ERROR] Lỗi khi xóa ngưỡng riêng biệt cho {ingredient}: {e}")
            return False

    def get_status_by_days(self, days_remaining: float) -> Tuple[str, str]:
        """
        Xác định trạng thái dựa trên số ngày còn lại
        Returns: (status_text, color_info)
        """
        if days_remaining == float('inf'):
            return "Không có dữ liệu", "gray"
        elif days_remaining < self.thresholds["critical_days"]:
            return "Khẩn cấp", "red"
        elif days_remaining < self.thresholds["warning_days"]:
            return "Sắp hết", "yellow"
        else:
            return "Đủ hàng", "green"

    def get_status_by_stock(self, stock_amount: float) -> Tuple[str, str]:
        """
        Xác định trạng thái dựa trên số lượng tồn kho
        Returns: (status_text, color_info)
        """
        if stock_amount <= self.thresholds["critical_stock"]:
            return "Khẩn cấp", "red"
        elif stock_amount <= self.thresholds["warning_stock"]:
            return "Sắp hết", "yellow"
        elif stock_amount > self.thresholds["sufficient_stock"]:
            return "Đủ hàng", "green"
        else:
            return "Bình thường", "blue"

    def get_inventory_status(self, days_remaining: float, stock_amount: float, ingredient: str = None) -> Tuple[str, str]:
        """
        Xác định trạng thái tồn kho dựa trên cài đặt ưu tiên
        Sử dụng ngưỡng riêng biệt nếu có
        Returns: (status_text, color_info)
        """
        # Lấy ngưỡng cho thành phần cụ thể (hoặc chung nếu không có ingredient)
        if ingredient:
            thresholds = self.get_ingredient_thresholds(ingredient)
        else:
            thresholds = self.thresholds

        # Ưu tiên theo ngày nếu được bật và có dữ liệu
        if thresholds["use_days_based"] and days_remaining != float('inf'):
            return self.get_status_by_days_with_thresholds(days_remaining, thresholds)

        # Sử dụng tồn kho nếu được bật hoặc không có dữ liệu ngày
        elif thresholds["use_stock_based"] or days_remaining == float('inf'):
            return self.get_status_by_stock_with_thresholds(stock_amount, thresholds)

        # Fallback về ngày nếu có dữ liệu
        elif days_remaining != float('inf'):
            return self.get_status_by_days_with_thresholds(days_remaining, thresholds)

        # Không có dữ liệu gì
        else:
            return "Không có dữ liệu", "gray"

    def get_status_by_days_with_thresholds(self, days_remaining: float, thresholds: Dict) -> Tuple[str, str]:
        """Xác định trạng thái dựa trên số ngày còn lại với ngưỡng tùy chỉnh"""
        if days_remaining == float('inf'):
            return "Không có dữ liệu", "gray"
        elif days_remaining < thresholds["critical_days"]:
            return "Khẩn cấp", "red"
        elif days_remaining < thresholds["warning_days"]:
            return "Sắp hết", "yellow"
        else:
            return "Đủ hàng", "green"

    def get_status_by_stock_with_thresholds(self, stock_amount: float, thresholds: Dict) -> Tuple[str, str]:
        """Xác định trạng thái dựa trên số lượng tồn kho với ngưỡng tùy chỉnh"""
        if stock_amount <= thresholds["critical_stock"]:
            return "Khẩn cấp", "red"
        elif stock_amount <= thresholds["warning_stock"]:
            return "Sắp hết", "yellow"
        elif stock_amount > thresholds["sufficient_stock"]:
            return "Đủ hàng", "green"
        else:
            return "Bình thường", "blue"

    def get_alert_items(self, days_remaining_dict: Dict[str, float], inventory_dict: Dict[str, float]) -> Tuple[list, list]:
        """
        Lấy danh sách các mục cần cảnh báo sử dụng ngưỡng riêng biệt
        Returns: (critical_items, warning_items)
        """
        critical_items = []
        warning_items = []

        for ingredient in days_remaining_dict.keys():
            days = days_remaining_dict.get(ingredient, float('inf'))
            stock = inventory_dict.get(ingredient, 0)

            # Sử dụng ngưỡng riêng biệt cho từng thành phần
            status_text, color_info = self.get_inventory_status(days, stock, ingredient)

            item_data = {
                'name': ingredient,
                'stock': stock,
                'days': days,
                'status': status_text,
                'has_custom_threshold': ingredient in self.individual_thresholds
            }

            if color_info == "red":
                critical_items.append(item_data)
            elif color_info == "yellow":
                warning_items.append(item_data)

        # Sắp xếp theo mức độ ưu tiên
        if self.thresholds["use_days_based"]:
            critical_items.sort(key=lambda x: x['days'] if x['days'] != float('inf') else 999)
            warning_items.sort(key=lambda x: x['days'] if x['days'] != float('inf') else 999)
        else:
            critical_items.sort(key=lambda x: x['stock'])
            warning_items.sort(key=lambda x: x['stock'])

        return critical_items, warning_items

    def reset_to_defaults(self) -> bool:
        """Đặt lại về cài đặt mặc định"""
        try:
            self.thresholds = self.default_thresholds.copy()
            return self.save_thresholds()
        except Exception as e:
            print(f"[ERROR] Lỗi khi đặt lại cài đặt mặc định: {e}")
            return False

    def get_threshold_description(self) -> str:
        """Lấy mô tả cài đặt ngưỡng hiện tại"""
        if self.thresholds["use_days_based"]:
            return f"Theo ngày: Khẩn cấp <{self.thresholds['critical_days']} ngày, Cảnh báo <{self.thresholds['warning_days']} ngày"
        elif self.thresholds["use_stock_based"]:
            return f"Theo tồn kho: Khẩn cấp ≤{self.thresholds['critical_stock']} kg, Cảnh báo ≤{self.thresholds['warning_stock']} kg"
        else:
            return "Cài đặt hỗn hợp: Ưu tiên ngày, fallback tồn kho"

    # === Phương thức quản lý tùy chọn nâng cao ===

    def get_display_settings(self) -> Dict:
        """Lấy cài đặt hiển thị"""
        return {
            "display_unit": self.thresholds.get("display_unit", "both"),
            "show_days_in_table": self.thresholds.get("show_days_in_table", True),
            "show_stock_in_table": self.thresholds.get("show_stock_in_table", True),
        }

    def get_sound_settings(self) -> Dict:
        """Lấy cài đặt âm thanh"""
        return {
            "sound_enabled": self.thresholds.get("sound_enabled", True),
            "sound_critical": self.thresholds.get("sound_critical", True),
            "sound_warning": self.thresholds.get("sound_warning", False),
            "sound_volume": self.thresholds.get("sound_volume", 50),
        }

    def get_auto_check_settings(self) -> Dict:
        """Lấy cài đặt kiểm tra tự động"""
        return {
            "auto_check_enabled": self.thresholds.get("auto_check_enabled", True),
            "check_frequency": self.thresholds.get("check_frequency", "hourly"),
            "check_interval_hours": self.thresholds.get("check_interval_hours", 1),
        }

    def get_popup_settings(self) -> Dict:
        """Lấy cài đặt popup"""
        return {
            "popup_enabled": self.thresholds.get("popup_enabled", True),
            "popup_on_startup": self.thresholds.get("popup_on_startup", True),
            "popup_on_critical": self.thresholds.get("popup_on_critical", True),
            "popup_on_warning": self.thresholds.get("popup_on_warning", False),
        }

    def get_auto_report_settings(self) -> Dict:
        """Lấy cài đặt báo cáo tự động"""
        return {
            "auto_report_enabled": self.thresholds.get("auto_report_enabled", False),
            "report_frequency": self.thresholds.get("report_frequency", "daily"),
            "report_time": self.thresholds.get("report_time", "08:00"),
            "report_path": self.thresholds.get("report_path", "reports/alerts"),
        }

    def get_color_settings(self) -> Dict:
        """Lấy cài đặt màu sắc"""
        return {
            "color_critical": self.thresholds.get("color_critical", "#f44336"),
            "color_warning": self.thresholds.get("color_warning", "#ff9800"),
            "color_sufficient": self.thresholds.get("color_sufficient", "#4caf50"),
            "color_no_data": self.thresholds.get("color_no_data", "#9e9e9e"),
            "use_custom_colors": self.thresholds.get("use_custom_colors", False),
        }

    def update_display_settings(self, settings: Dict) -> bool:
        """Cập nhật cài đặt hiển thị"""
        try:
            self.thresholds.update(settings)
            return self.save_thresholds()
        except Exception as e:
            print(f"[ERROR] Lỗi khi cập nhật cài đặt hiển thị: {e}")
            return False

    def update_sound_settings(self, settings: Dict) -> bool:
        """Cập nhật cài đặt âm thanh"""
        try:
            # Validate volume range
            if "sound_volume" in settings:
                settings["sound_volume"] = max(0, min(100, settings["sound_volume"]))

            self.thresholds.update(settings)
            return self.save_thresholds()
        except Exception as e:
            print(f"[ERROR] Lỗi khi cập nhật cài đặt âm thanh: {e}")
            return False

    def update_auto_check_settings(self, settings: Dict) -> bool:
        """Cập nhật cài đặt kiểm tra tự động"""
        try:
            # Validate check interval
            if "check_interval_hours" in settings:
                settings["check_interval_hours"] = max(1, settings["check_interval_hours"])

            self.thresholds.update(settings)
            return self.save_thresholds()
        except Exception as e:
            print(f"[ERROR] Lỗi khi cập nhật cài đặt kiểm tra tự động: {e}")
            return False

    def update_popup_settings(self, settings: Dict) -> bool:
        """Cập nhật cài đặt popup"""
        try:
            self.thresholds.update(settings)
            return self.save_thresholds()
        except Exception as e:
            print(f"[ERROR] Lỗi khi cập nhật cài đặt popup: {e}")
            return False

    def update_auto_report_settings(self, settings: Dict) -> bool:
        """Cập nhật cài đặt báo cáo tự động"""
        try:
            # Validate time format
            if "report_time" in settings:
                time_str = settings["report_time"]
                try:
                    # Validate HH:MM format
                    hours, minutes = map(int, time_str.split(":"))
                    if not (0 <= hours <= 23 and 0 <= minutes <= 59):
                        raise ValueError("Invalid time range")
                except:
                    settings["report_time"] = "08:00"  # Default fallback

            self.thresholds.update(settings)
            return self.save_thresholds()
        except Exception as e:
            print(f"[ERROR] Lỗi khi cập nhật cài đặt báo cáo tự động: {e}")
            return False

    def update_color_settings(self, settings: Dict) -> bool:
        """Cập nhật cài đặt màu sắc"""
        try:
            # Validate color format (hex colors)
            color_keys = ["color_critical", "color_warning", "color_sufficient", "color_no_data"]
            for key in color_keys:
                if key in settings:
                    color = settings[key]
                    if not (color.startswith("#") and len(color) == 7):
                        # Reset to default if invalid
                        default_colors = {
                            "color_critical": "#f44336",
                            "color_warning": "#ff9800",
                            "color_sufficient": "#4caf50",
                            "color_no_data": "#9e9e9e"
                        }
                        settings[key] = default_colors.get(key, "#000000")

            self.thresholds.update(settings)
            return self.save_thresholds()
        except Exception as e:
            print(f"[ERROR] Lỗi khi cập nhật cài đặt màu sắc: {e}")
            return False

    def get_color_for_status(self, color_info: str) -> str:
        """Lấy màu sắc cho trạng thái dựa trên cài đặt"""
        if not self.thresholds.get("use_custom_colors", False):
            # Sử dụng màu mặc định
            color_map = {
                "red": "#f44336",
                "yellow": "#ff9800",
                "green": "#4caf50",
                "gray": "#9e9e9e",
                "blue": "#2196f3"
            }
            return color_map.get(color_info, "#000000")

        # Sử dụng màu tùy chỉnh
        color_map = {
            "red": self.thresholds.get("color_critical", "#f44336"),
            "yellow": self.thresholds.get("color_warning", "#ff9800"),
            "green": self.thresholds.get("color_sufficient", "#4caf50"),
            "gray": self.thresholds.get("color_no_data", "#9e9e9e"),
            "blue": self.thresholds.get("color_sufficient", "#4caf50")  # Use sufficient for blue
        }
        return color_map.get(color_info, "#000000")
