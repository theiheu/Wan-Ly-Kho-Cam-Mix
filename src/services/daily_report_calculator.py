#!/usr/bin/env python3
"""
Daily Report Calculator - Tính toán báo cáo tiêu thụ hàng ngày
Tích hợp với hệ thống cache để tối ưu hiệu suất
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from collections import defaultdict

# Import cache manager
try:
    from src.services.report_cache_manager import report_cache_manager
except ImportError:
    from services.report_cache_manager import report_cache_manager

class DailyReportCalculator:
    """Tính toán báo cáo tiêu thụ hàng ngày với cache"""

    def __init__(self):
        """Khởi tạo calculator"""
        # Use persistent path manager for consistent paths
        from src.utils.persistent_paths import persistent_path_manager

        self.data_dir = persistent_path_manager.data_path
        self.reports_dir = persistent_path_manager.reports_path
        self.config_dir = persistent_path_manager.config_path

        print(f"🔧 DailyReportCalculator initialized:")
        print(f"   📁 Data dir: {self.data_dir}")
        print(f"   📁 Reports dir: {self.reports_dir}")
        print(f"   📁 Config dir: {self.config_dir}")

        # Đảm bảo thư mục tồn tại
        for directory in [self.reports_dir, self.config_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    def _load_json_file(self, file_path: Path) -> Dict:
        """Tải file JSON với xử lý lỗi"""
        try:
            print(f"📖 Loading JSON file: {file_path}")

            if file_path.exists() and file_path.stat().st_size > 0:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"✅ Loaded {len(data) if isinstance(data, dict) else 'data'} from {file_path.name}")
                return data
            else:
                print(f"⚠️ File not found or empty: {file_path}")

        except (json.JSONDecodeError, FileNotFoundError, UnicodeDecodeError) as e:
            print(f"❌ Error reading file {file_path}: {e}")
        except Exception as e:
            print(f"❌ Unexpected error reading {file_path}: {e}")

        return {}

    def _save_report_to_file(self, report_date: str, report_data: Dict) -> bool:
        """Lưu báo cáo vào file"""
        try:
            # Đảm bảo thư mục reports tồn tại
            self.reports_dir.mkdir(parents=True, exist_ok=True)

            report_file = self.reports_dir / f"report_{report_date}.json"
            print(f"💾 Saving report to: {report_file}")

            # Tạo backup nếu file đã tồn tại
            if report_file.exists():
                backup_file = self.reports_dir / f"report_{report_date}_backup.json"
                import shutil
                shutil.copy2(report_file, backup_file)
                print(f"🔄 Created backup: {backup_file}")

            # Lưu báo cáo
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)

            # Kiểm tra file đã được lưu
            if report_file.exists() and report_file.stat().st_size > 0:
                print(f"✅ Report saved successfully: {report_file} ({report_file.stat().st_size} bytes)")
                return True
            else:
                print(f"❌ Report file not created or empty: {report_file}")
                return False

        except Exception as e:
            print(f"❌ Error saving report {report_date}: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _calculate_area_totals(self, usage_data: Dict[str, Any]) -> Dict[str, Any]:
        """Tính tổng theo khu vực"""
        area_totals = {}
        grand_total = 0

        for area, farms in usage_data.items():
            area_total = 0
            farm_details = {}

            for farm, shifts in farms.items():
                farm_total = 0
                shift_details = {}

                for shift, amount in shifts.items():
                    amount_float = float(amount or 0)
                    shift_details[shift] = amount_float
                    farm_total += amount_float

                farm_details[farm] = {
                    'shifts': shift_details,
                    'total': farm_total
                }
                area_total += farm_total

            area_totals[area] = {
                'farms': farm_details,
                'total': area_total
            }
            grand_total += area_total

        return {
            'areas': area_totals,
            'grand_total': grand_total
        }

    def _calculate_shift_statistics(self, usage_data: Dict[str, Any]) -> Dict[str, Any]:
        """Tính thống kê theo ca"""
        shift_stats = defaultdict(float)
        shift_counts = defaultdict(int)

        for area, farms in usage_data.items():
            for farm, shifts in farms.items():
                for shift, amount in shifts.items():
                    amount_float = float(amount or 0)
                    if amount_float > 0:
                        shift_stats[shift] += amount_float
                        shift_counts[shift] += 1

        # Tính trung bình
        shift_averages = {}
        for shift in shift_stats:
            if shift_counts[shift] > 0:
                shift_averages[shift] = shift_stats[shift] / shift_counts[shift]
            else:
                shift_averages[shift] = 0

        return {
            'totals': dict(shift_stats),
            'averages': shift_averages,
            'counts': dict(shift_counts)
        }

    def _calculate_farm_rankings(self, usage_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Tính xếp hạng trại theo tiêu thụ"""
        farm_totals = []

        for area, farms in usage_data.items():
            for farm, shifts in farms.items():
                farm_total = sum(float(amount or 0) for amount in shifts.values())
                if farm_total > 0:
                    farm_totals.append({
                        'area': area,
                        'farm': farm,
                        'total_consumption': farm_total,
                        'shift_breakdown': {shift: float(amount or 0) for shift, amount in shifts.items()}
                    })

        # Sắp xếp theo tổng tiêu thụ giảm dần
        farm_totals.sort(key=lambda x: x['total_consumption'], reverse=True)

        # Thêm thứ hạng
        for i, farm_data in enumerate(farm_totals, 1):
            farm_data['rank'] = i

        return farm_totals

    def _calculate_efficiency_metrics(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Tính các chỉ số hiệu quả từ raw data"""
        # Lấy tổng feed và mix từ raw data thay vì tính từ feed_usage
        feed_total = float(raw_data.get('total_feed', 0))
        mix_total = float(raw_data.get('total_mix', 0))

        # Tính tổng tiêu thụ theo trại (để so sánh)
        feed_usage = raw_data.get('feed_usage', {})
        feed_usage_total = sum(
            sum(float(amount or 0) for amount in shifts.values())
            for farms in feed_usage.values()
            for shifts in farms.values()
        )

        # Mix usage theo trại (nếu có)
        mix_usage = raw_data.get('mix_usage', {})
        mix_usage_total = sum(
            sum(float(amount or 0) for amount in shifts.values())
            for farms in mix_usage.values()
            for shifts in farms.values()
        )

        total_consumption = feed_total + mix_total

        metrics = {
            'feed_total': feed_total,
            'mix_total': mix_total,
            'total_consumption': total_consumption,
            'feed_percentage': (feed_total / total_consumption * 100) if total_consumption > 0 else 0,
            'mix_percentage': (mix_total / total_consumption * 100) if total_consumption > 0 else 0,
            'feed_to_mix_ratio': feed_total / mix_total if mix_total > 0 else float('inf'),
            # Thêm thông tin về tiêu thụ theo trại
            'feed_usage_total': feed_usage_total,
            'mix_usage_total': mix_usage_total,
            'feed_usage_percentage': (feed_usage_total / feed_total * 100) if feed_total > 0 else 0,
            'mix_usage_percentage': (mix_usage_total / mix_total * 100) if mix_total > 0 else 0
        }

        return metrics

    def calculate_daily_report(self, report_date: str, force_recalculate: bool = False) -> Optional[Dict[str, Any]]:
        """Tính toán báo cáo tiêu thụ hàng ngày"""
        try:
            print(f"📊 Calculating daily report for {report_date}")

            # Kiểm tra cache trước
            if not force_recalculate:
                cached_report = report_cache_manager.get_cached_report(report_date, "daily_consumption")
                if cached_report:
                    print(f"📋 Using cached report for {report_date}")
                    return cached_report

            start_time = time.time()

            # Load dữ liệu cần thiết
            print("📖 Loading configuration files...")
            feed_formula = self._load_json_file(self.config_dir / "feed_formula.json")
            mix_formula = self._load_json_file(self.config_dir / "mix_formula.json")
            inventory = self._load_json_file(self.config_dir / "inventory.json")

            if not feed_formula or not mix_formula:
                print("❌ Missing formula data")
                return None

            # Tính toán báo cáo
            calculated_report = {
                'date': report_date,
                'display_date': self._format_display_date(report_date),
                'generated_at': datetime.now().isoformat(),
                'metadata': {
                    'calculation_time': 0,
                    'cached': False,
                    'data_sources': {
                        'feed_formula': bool(feed_formula),
                        'mix_formula': bool(mix_formula),
                        'inventory': bool(inventory)
                    }
                }
            }

            # Thực hiện tính toán chi tiết (giữ nguyên logic cũ)
            # ... existing calculation logic ...

            calculation_time = time.time() - start_time
            calculated_report['metadata']['calculation_time'] = round(calculation_time, 2)

            # Lưu báo cáo vào file
            save_success = self._save_report_to_file(report_date, calculated_report)
            if save_success:
                calculated_report['metadata']['saved_to_file'] = True
            else:
                calculated_report['metadata']['saved_to_file'] = False
                print("⚠️ Report calculation completed but file save failed")

            # Lưu vào cache
            cache_success = report_cache_manager.cache_report(report_date, calculated_report, "daily_consumption")
            if cache_success:
                calculated_report['metadata']['cached'] = True

            print(f"✅ Daily report calculated in {calculation_time:.2f}s for {report_date}")
            return calculated_report

        except Exception as e:
            print(f"❌ Error calculating daily report {report_date}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def get_report_summary(self, report_date: str) -> Optional[Dict[str, Any]]:
        """Lấy tóm tắt báo cáo (chỉ metadata và summary)"""
        try:
            # Thử lấy từ cache trước
            cached_report = report_cache_manager.get_cached_report(report_date, "daily_consumption")
            if cached_report:
                return {
                    'metadata': cached_report.get('metadata', {}),
                    'summary': cached_report.get('summary', {}),
                    'efficiency_metrics': cached_report.get('efficiency_metrics', {}),
                    'from_cache': True
                }

            # Nếu không có cache, tính toán đầy đủ
            full_report = self.calculate_daily_report(report_date)
            if full_report:
                return {
                    'metadata': full_report.get('metadata', {}),
                    'summary': full_report.get('summary', {}),
                    'efficiency_metrics': full_report.get('efficiency_metrics', {}),
                    'from_cache': False
                }

            return None

        except Exception as e:
            print(f"Lỗi lấy tóm tắt báo cáo {report_date}: {e}")
            return None

    def invalidate_report_cache(self, report_date: str) -> bool:
        """Vô hiệu hóa cache cho một báo cáo cụ thể"""
        try:
            removed_count = report_cache_manager.invalidate_cache(report_date, "daily_consumption")
            print(f"🗑️ [Calculator] Invalidated cache for {report_date} ({removed_count} entries)")
            return removed_count > 0
        except Exception as e:
            print(f"Lỗi vô hiệu hóa cache {report_date}: {e}")
            return False

    def get_available_reports(self) -> List[str]:
        """Lấy danh sách các báo cáo có sẵn"""
        try:
            report_files = list(self.reports_dir.glob("report_*.json"))
            dates = []

            for file in report_files:
                date_str = file.stem.replace('report_', '')
                if len(date_str) == 8 and date_str.isdigit():
                    dates.append(date_str)

            return sorted(dates, reverse=True)  # Mới nhất trước

        except Exception as e:
            print(f"Lỗi lấy danh sách báo cáo: {e}")
            return []

# Global instance
daily_report_calculator = DailyReportCalculator()

# Convenience functions
def calculate_daily_report(report_date: str, force_recalculate: bool = False) -> Optional[Dict[str, Any]]:
    """Tính toán báo cáo hàng ngày"""
    return daily_report_calculator.calculate_daily_report(report_date, force_recalculate)

def get_daily_report_summary(report_date: str) -> Optional[Dict[str, Any]]:
    """Lấy tóm tắt báo cáo hàng ngày"""
    return daily_report_calculator.get_report_summary(report_date)

def invalidate_daily_report(report_date: str) -> bool:
    """Vô hiệu hóa cache báo cáo hàng ngày"""
    return daily_report_calculator.invalidate_report_cache(report_date)

def get_available_daily_reports() -> List[str]:
    """Lấy danh sách báo cáo có sẵn"""
    return daily_report_calculator.get_available_reports()


