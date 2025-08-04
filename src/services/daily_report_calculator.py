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
        self.data_dir = Path("src/data")
        self.reports_dir = self.data_dir / "reports"
        self.config_dir = self.data_dir / "config"

        # Đảm bảo thư mục tồn tại
        for directory in [self.reports_dir, self.config_dir]:
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
        """Tính toán báo cáo hàng ngày với cache"""
        try:
            # Kiểm tra cache trước nếu không bắt buộc tính lại
            if not force_recalculate:
                cached_report = report_cache_manager.get_cached_report(report_date, "daily_consumption")
                if cached_report:
                    return cached_report

            print(f"📊 [Calculator] Calculating daily report for {report_date}...")

            # Tải dữ liệu báo cáo gốc
            report_file = self.reports_dir / f"report_{report_date}.json"
            if not report_file.exists():
                print(f"Không tìm thấy file báo cáo: {report_file}")
                return None

            raw_data = self._load_json_file(report_file)
            if not raw_data:
                print(f"Không thể tải dữ liệu từ file: {report_file}")
                return None

            # Bắt đầu tính toán
            calculation_start = datetime.now()

            # Tính toán cho feed usage
            feed_calculations = {}
            if 'feed_usage' in raw_data:
                feed_calculations = {
                    'area_totals': self._calculate_area_totals(raw_data['feed_usage']),
                    'shift_statistics': self._calculate_shift_statistics(raw_data['feed_usage']),
                    'farm_rankings': self._calculate_farm_rankings(raw_data['feed_usage'])
                }

            # Tính toán cho mix usage
            mix_calculations = {}
            if 'mix_usage' in raw_data:
                mix_calculations = {
                    'area_totals': self._calculate_area_totals(raw_data['mix_usage']),
                    'shift_statistics': self._calculate_shift_statistics(raw_data['mix_usage']),
                    'farm_rankings': self._calculate_farm_rankings(raw_data['mix_usage'])
                }

            # Tính các chỉ số hiệu quả
            efficiency_metrics = self._calculate_efficiency_metrics(raw_data)

            # Tính thời gian xử lý
            calculation_time = (datetime.now() - calculation_start).total_seconds()

            # Tạo báo cáo tính toán hoàn chỉnh
            calculated_report = {
                'metadata': {
                    'report_date': report_date,
                    'display_date': raw_data.get('display_date', ''),
                    'calculated_at': datetime.now().isoformat(),
                    'calculation_time_seconds': calculation_time,
                    'source_file': f"report_{report_date}.json",
                    'cache_enabled': True
                },
                'raw_data': raw_data,
                'feed_calculations': feed_calculations,
                'mix_calculations': mix_calculations,
                'efficiency_metrics': efficiency_metrics,
                'summary': {
                    'total_feed_consumption': efficiency_metrics['feed_total'],
                    'total_mix_consumption': efficiency_metrics['mix_total'],
                    'total_consumption': efficiency_metrics['total_consumption'],
                    'active_areas': len(raw_data.get('feed_usage', {})),
                    'active_farms': sum(
                        len(farms) for farms in raw_data.get('feed_usage', {}).values()
                    ),
                    'top_consuming_farm': feed_calculations.get('farm_rankings', [{}])[0] if feed_calculations.get('farm_rankings') else None
                }
            }

            # Lưu vào cache
            cache_success = report_cache_manager.cache_report(report_date, calculated_report, "daily_consumption")
            if cache_success:
                calculated_report['metadata']['cached'] = True

            print(f"✅ [Calculator] Daily report calculated in {calculation_time:.2f}s for {report_date}")
            return calculated_report

        except Exception as e:
            print(f"Lỗi tính toán báo cáo hàng ngày {report_date}: {e}")
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
