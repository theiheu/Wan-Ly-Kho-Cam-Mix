#!/usr/bin/env python3
"""
Comprehensive Report Service - Dịch vụ báo cáo toàn diện
Tạo các báo cáo chi tiết từ tất cả dữ liệu có sẵn trong hệ thống
"""

import os
import json
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict

class ComprehensiveReportService:
    """Dịch vụ tạo báo cáo toàn diện từ tất cả dữ liệu hệ thống"""

    def __init__(self):
        """Khởi tạo dịch vụ báo cáo"""
        # Use persistent path manager for consistent paths
        from src.utils.persistent_paths import persistent_path_manager

        self.data_dir = persistent_path_manager.data_path
        self.config_dir = persistent_path_manager.config_path
        self.reports_dir = persistent_path_manager.reports_path
        self.exports_dir = persistent_path_manager.exports_path
        self.business_dir = self.data_dir / "business"
        self.imports_dir = self.data_dir / "imports"

        print(f"🔧 ComprehensiveReportService initialized:")
        print(f"   📁 Data dir: {self.data_dir}")
        print(f"   📁 Config dir: {self.config_dir}")
        print(f"   📁 Reports dir: {self.reports_dir}")
        print(f"   📁 Exports dir: {self.exports_dir}")

        # Đảm bảo thư mục tồn tại
        for directory in [self.config_dir, self.business_dir, self.reports_dir, self.imports_dir, self.exports_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    def _load_json_file(self, file_path: Path) -> Dict:
        """Tải file JSON với xử lý lỗi"""
        try:
            if file_path.exists() and file_path.stat().st_size > 0:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError, UnicodeDecodeError) as e:
            print(f"Lỗi đọc file {file_path}: {e}")
        return {}

    def _load_json_list(self, file_path: Path) -> List:
        """Tải file JSON dạng list với xử lý lỗi"""
        try:
            if file_path.exists() and file_path.stat().st_size > 0:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data if isinstance(data, list) else []
        except (json.JSONDecodeError, FileNotFoundError, UnicodeDecodeError) as e:
            print(f"Lỗi đọc file {file_path}: {e}")
        return []

    def get_inventory_summary(self) -> Dict[str, Any]:
        """Lấy tổng quan tồn kho"""
        summary = {
            'feed_inventory': {},
            'mix_inventory': {},
            'general_inventory': {},
            'total_items': 0,
            'low_stock_items': [],
            'out_of_stock_items': []
        }

        # Tải dữ liệu tồn kho cám
        feed_inventory = self._load_json_file(self.config_dir / "feed_inventory.json")
        summary['feed_inventory'] = feed_inventory

        # Tải dữ liệu tồn kho mix
        mix_inventory = self._load_json_file(self.config_dir / "mix_inventory.json")
        summary['mix_inventory'] = mix_inventory

        # Tải dữ liệu tồn kho chung
        general_inventory = self._load_json_file(self.config_dir / "inventory.json")
        summary['general_inventory'] = general_inventory

        # Tính tổng số mặt hàng
        all_items = {**feed_inventory, **mix_inventory, **general_inventory}
        summary['total_items'] = len(all_items)

        # Tìm các mặt hàng sắp hết và đã hết
        for item_name, quantity in all_items.items():
            if quantity == 0:
                summary['out_of_stock_items'].append(item_name)
            elif quantity < 100:  # Ngưỡng cảnh báo tạm thời
                summary['low_stock_items'].append({'name': item_name, 'quantity': quantity})

        return summary

    def get_employee_summary(self) -> Dict[str, Any]:
        """Lấy tổng quan nhân viên"""
        summary = {
            'employees': [],
            'total_employees': 0,
            'positions': {},
            'attendance_summary': {}
        }

        # Tải danh sách nhân viên
        employees = self._load_json_list(self.business_dir / "employees.json")
        summary['employees'] = employees
        summary['total_employees'] = len(employees)

        # Thống kê theo vị trí
        positions = defaultdict(int)
        for emp in employees:
            position = emp.get('position', 'Không xác định')
            positions[position] += 1
        summary['positions'] = dict(positions)

        # Tải dữ liệu chấm công
        attendance_data = self._load_json_file(self.business_dir / "attendance.json")
        if attendance_data and 'attendance_records' in attendance_data:
            attendance_records = attendance_data['attendance_records']
            summary['attendance_summary'] = {
                'total_records': sum(len(records) for records in attendance_records.values()),
                'employees_with_records': len(attendance_records)
            }

        return summary

    def _is_date_in_range(self, date_str: str, start_date: str = None, end_date: str = None) -> bool:
        """Kiểm tra ngày có trong khoảng thời gian không"""
        if not start_date and not end_date:
            return True

        try:
            # Chuyển đổi định dạng ngày từ YYYYMMDD
            if len(date_str) == 8:
                check_date = datetime.strptime(date_str, '%Y%m%d')
            else:
                return True

            if start_date:
                start = datetime.strptime(start_date, '%Y%m%d')
                if check_date < start:
                    return False

            if end_date:
                end = datetime.strptime(end_date, '%Y%m%d')
                if check_date > end:
                    return False

            return True
        except ValueError:
            return True

    def get_production_summary(self, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """Lấy tổng quan sản xuất từ báo cáo hàng ngày"""
        summary = {
            'total_reports': 0,
            'date_range': {'start': start_date, 'end': end_date},
            'feed_usage_by_area': defaultdict(float),
            'mix_usage_by_area': defaultdict(float),
            'total_feed_usage': 0,
            'total_mix_usage': 0,
            'daily_averages': {},
            'reports_data': []
        }

        # Lấy tất cả file báo cáo
        report_files = list(self.reports_dir.glob("report_*.json"))

        # Lọc theo ngày nếu có
        filtered_files = []
        for file in report_files:
            file_date = file.stem.replace('report_', '')
            if self._is_date_in_range(file_date, start_date, end_date):
                filtered_files.append(file)

        summary['total_reports'] = len(filtered_files)

        # Xử lý từng báo cáo
        for report_file in filtered_files:
            report_data = self._load_json_file(report_file)
            if not report_data:
                continue

            summary['reports_data'].append({
                'date': report_data.get('date', ''),
                'display_date': report_data.get('display_date', ''),
                'file_name': report_file.name
            })

            # Tính tổng sử dụng cám theo khu
            if 'feed_usage' in report_data:
                for area, farms in report_data['feed_usage'].items():
                    area_total = 0
                    for farm, shifts in farms.items():
                        for shift, amount in shifts.items():
                            area_total += float(amount or 0)
                    summary['feed_usage_by_area'][area] += area_total
                    summary['total_feed_usage'] += area_total

            # Tính tổng sử dụng mix theo khu
            if 'mix_usage' in report_data:
                for area, farms in report_data['mix_usage'].items():
                    area_total = 0
                    for farm, shifts in farms.items():
                        for shift, amount in shifts.items():
                            area_total += float(amount or 0)
                    summary['mix_usage_by_area'][area] += area_total
                    summary['total_mix_usage'] += area_total

        # Tính trung bình hàng ngày
        if summary['total_reports'] > 0:
            summary['daily_averages'] = {
                'feed_per_day': summary['total_feed_usage'] / summary['total_reports'],
                'mix_per_day': summary['total_mix_usage'] / summary['total_reports']
            }

        return summary

    def get_bonus_summary(self, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """Lấy tổng quan tính thưởng"""
        summary = {
            'total_months': 0,
            'employee_bonuses': defaultdict(dict),
            'monthly_totals': {},
            'ingredient_totals': defaultdict(float),
            'date_range': {'start': start_date, 'end': end_date}
        }

        # Tải dữ liệu tính thưởng
        bonus_data = self._load_json_file(self.business_dir / "bonus_calculation.json")

        for month_key, month_data in bonus_data.items():
            if not isinstance(month_data, dict) or 'employee_bonuses' not in month_data:
                continue

            # Lọc theo khoảng thời gian nếu có
            if start_date or end_date:
                try:
                    year = month_data.get('year', 0)
                    month = month_data.get('month', 0)
                    month_date = f"{year}{month:02d}01"
                    if not self._is_date_in_range(month_date, start_date, end_date):
                        continue
                except:
                    continue

            summary['total_months'] += 1
            month_total = 0

            # Xử lý thưởng từng nhân viên
            for emp_id, emp_bonuses in month_data['employee_bonuses'].items():
                for ingredient, amount in emp_bonuses.items():
                    summary['employee_bonuses'][emp_id][ingredient] = summary['employee_bonuses'][emp_id].get(ingredient, 0) + amount
                    summary['ingredient_totals'][ingredient] += amount
                    month_total += amount

            summary['monthly_totals'][month_key] = month_total

        return summary

    def get_formula_summary(self) -> Dict[str, Any]:
        """Lấy tổng quan công thức"""
        summary = {
            'feed_formulas': {},
            'mix_formulas': {},
            'total_formulas': 0,
            'formula_links': {},
            'packaging_info': {}
        }

        # Tải công thức cám
        feed_formulas = self._load_json_file(self.config_dir / "feed_formula.json")
        summary['feed_formulas'] = feed_formulas

        # Tải công thức mix
        mix_formulas = self._load_json_file(self.config_dir / "mix_formula.json")
        summary['mix_formulas'] = mix_formulas

        # Tải liên kết công thức
        formula_links = self._load_json_file(self.config_dir / "formula_links.json")
        summary['formula_links'] = formula_links

        # Tải thông tin đóng gói
        packaging_info = self._load_json_file(self.config_dir / "packaging_info.json")
        summary['packaging_info'] = packaging_info

        # Tính tổng số công thức
        summary['total_formulas'] = len(feed_formulas) + len(mix_formulas)

        return summary

    def get_import_summary(self, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """Lấy tổng quan nhập kho"""
        summary = {
            'total_imports': 0,
            'import_files': [],
            'date_range': {'start': start_date, 'end': end_date}
        }

        # Lấy tất cả file nhập kho
        import_files = list(self.imports_dir.glob("import_*.json"))

        # Lọc theo ngày nếu có
        filtered_files = []
        for file in import_files:
            # Trích xuất ngày từ tên file (import_YYYY-MM-DD.json)
            try:
                date_part = file.stem.replace('import_', '').replace('-', '')
                if self._is_date_in_range(date_part, start_date, end_date):
                    filtered_files.append(file)
            except:
                filtered_files.append(file)  # Bao gồm file không có định dạng ngày chuẩn

        summary['total_imports'] = len(filtered_files)

        # Xử lý từng file nhập kho
        for import_file in filtered_files:
            import_data = self._load_json_file(import_file)
            if import_data:
                summary['import_files'].append({
                    'file_name': import_file.name,
                    'data': import_data
                })

        return summary

    def generate_comprehensive_report(self,
                                    include_inventory: bool = True,
                                    include_employees: bool = True,
                                    include_production: bool = True,
                                    include_bonuses: bool = True,
                                    include_formulas: bool = True,
                                    include_imports: bool = True,
                                    start_date: str = None,
                                    end_date: str = None) -> Dict[str, Any]:
        """Tạo báo cáo toàn diện"""

        report = {
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'date_range': {'start': start_date, 'end': end_date},
            'sections': {}
        }

        try:
            if include_inventory:
                print("Đang tạo báo cáo tồn kho...")
                report['sections']['inventory'] = self.get_inventory_summary()

            if include_employees:
                print("Đang tạo báo cáo nhân viên...")
                report['sections']['employees'] = self.get_employee_summary()

            if include_production:
                print("Đang tạo báo cáo sản xuất...")
                report['sections']['production'] = self.get_production_summary(start_date, end_date)

            if include_bonuses:
                print("Đang tạo báo cáo thưởng...")
                report['sections']['bonuses'] = self.get_bonus_summary(start_date, end_date)

            if include_formulas:
                print("Đang tạo báo cáo công thức...")
                report['sections']['formulas'] = self.get_formula_summary()

            if include_imports:
                print("Đang tạo báo cáo nhập kho...")
                report['sections']['imports'] = self.get_import_summary(start_date, end_date)

            print("Báo cáo toàn diện đã được tạo thành công!")
            return report

        except Exception as e:
            print(f"Lỗi khi tạo báo cáo toàn diện: {e}")
            report['error'] = str(e)
            return report

    def export_daily_feed_consumption_report(self, report_date: str, filename: str = None,
                                           include_shift_analysis: bool = True,
                                           include_area_analysis: bool = True,
                                           include_mix_analysis: bool = True,
                                           include_ingredients_comparison: bool = True) -> Tuple[bool, str]:
        """Xuất báo cáo tiêu thụ cám hàng ngày ra Excel"""
        try:
            # Import daily feed excel exporter
            from src.services.daily_feed_excel_export import export_daily_feed_to_excel

            print(f"📊 [Comprehensive Report] Exporting daily feed consumption report for {report_date}...")

            # Gọi service xuất Excel
            success, message = export_daily_feed_to_excel(
                report_date=report_date,
                filename=filename,
                include_shift_analysis=include_shift_analysis,
                include_area_analysis=include_area_analysis,
                include_mix_analysis=include_mix_analysis,
                include_ingredients_comparison=include_ingredients_comparison
            )

            if success:
                print(f"✅ [Comprehensive Report] Daily feed export completed successfully")
            else:
                print(f"❌ [Comprehensive Report] Daily feed export failed: {message}")

            return success, message

        except Exception as e:
            error_msg = f"Lỗi xuất báo cáo tiêu thụ cám hàng ngày: {str(e)}"
            print(f"❌ [Comprehensive Report] {error_msg}")
            return False, error_msg


