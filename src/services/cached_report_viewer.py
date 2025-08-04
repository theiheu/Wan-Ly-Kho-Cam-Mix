#!/usr/bin/env python3
"""
Cached Report Viewer - Trình xem báo cáo với cache
Tích hợp với UI để hiển thị báo cáo đã cache
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from collections import defaultdict

# Import services
try:
    from src.services.daily_report_calculator import daily_report_calculator
    from src.services.report_cache_manager import report_cache_manager
except ImportError:
    from services.daily_report_calculator import daily_report_calculator
    from services.report_cache_manager import report_cache_manager

class CachedReportViewer:
    """Trình xem báo cáo với hỗ trợ cache"""

    def __init__(self):
        """Khởi tạo viewer"""
        self.calculator = daily_report_calculator
        self.cache_manager = report_cache_manager

    def get_report_for_display(self, report_date: str, include_details: bool = True) -> Optional[Dict[str, Any]]:
        """Lấy báo cáo để hiển thị (tối ưu cho UI)"""
        try:
            if include_details:
                # Lấy báo cáo đầy đủ
                report = self.calculator.calculate_daily_report(report_date)
                if report:
                    # Thêm thông tin cache status
                    report['cache_info'] = {
                        'loaded_from_cache': report.get('metadata', {}).get('cached', False),
                        'cache_available': True
                    }
                return report
            else:
                # Chỉ lấy tóm tắt
                summary = self.calculator.get_report_summary(report_date)
                if summary:
                    summary['cache_info'] = {
                        'loaded_from_cache': summary.get('from_cache', False),
                        'cache_available': True
                    }
                return summary

        except Exception as e:
            print(f"Lỗi lấy báo cáo để hiển thị {report_date}: {e}")
            return None

    def get_feed_consumption_table(self, report_date: str) -> Optional[List[Dict[str, Any]]]:
        """Lấy bảng tiêu thụ cám để hiển thị trong UI"""
        try:
            report = self.get_report_for_display(report_date, include_details=True)
            if not report or 'feed_calculations' not in report:
                return None

            feed_data = report['raw_data'].get('feed_usage', {})
            feed_calculations = report['feed_calculations']

            table_data = []

            for area, farms in feed_data.items():
                area_total = feed_calculations['area_totals']['areas'][area]['total']

                for farm, shifts in farms.items():
                    farm_total = sum(float(amount or 0) for amount in shifts.values())

                    row = {
                        'area': area,
                        'farm': farm,
                        'morning': float(shifts.get('Sáng', 0)),
                        'afternoon': float(shifts.get('Chiều', 0)),
                        'farm_total': farm_total,
                        'area_total': area_total,
                        'percentage_of_area': (farm_total / area_total * 100) if area_total > 0 else 0
                    }
                    table_data.append(row)

            # Sắp xếp theo khu vực và tổng tiêu thụ
            table_data.sort(key=lambda x: (x['area'], -x['farm_total']))

            return table_data

        except Exception as e:
            print(f"Lỗi tạo bảng tiêu thụ cám {report_date}: {e}")
            return None

    def get_mix_consumption_table(self, report_date: str) -> Optional[List[Dict[str, Any]]]:
        """Lấy bảng tiêu thụ mix để hiển thị trong UI"""
        try:
            report = self.get_report_for_display(report_date, include_details=True)
            if not report:
                return None

            mix_data = report['raw_data'].get('mix_usage', {})
            if not mix_data:
                return []  # Return empty list instead of None for no mix data

            mix_calculations = report.get('mix_calculations', {})

            table_data = []

            for area, farms in mix_data.items():
                # Get area total safely
                area_total = 0
                if ('area_totals' in mix_calculations and
                    'areas' in mix_calculations['area_totals'] and
                    area in mix_calculations['area_totals']['areas']):
                    area_total = mix_calculations['area_totals']['areas'][area].get('total', 0)

                for farm, shifts in farms.items():
                    farm_total = sum(float(amount or 0) for amount in shifts.values())

                    row = {
                        'area': area,
                        'farm': farm,
                        'morning': float(shifts.get('Sáng', 0)),
                        'afternoon': float(shifts.get('Chiều', 0)),
                        'farm_total': farm_total,
                        'area_total': area_total,
                        'percentage_of_area': (farm_total / area_total * 100) if area_total > 0 else 0
                    }
                    table_data.append(row)

            # Sắp xếp theo khu vực và tổng tiêu thụ
            table_data.sort(key=lambda x: (x['area'], -x['farm_total']))

            return table_data

        except Exception as e:
            print(f"Lỗi tạo bảng tiêu thụ mix {report_date}: {e}")
            return None

    def get_area_summary(self, report_date: str) -> Optional[Dict[str, Any]]:
        """Lấy tóm tắt theo khu vực"""
        try:
            report = self.get_report_for_display(report_date, include_details=True)
            if not report:
                return None

            summary = {
                'feed_by_area': {},
                'mix_by_area': {},
                'total_by_area': {},
                'area_rankings': []
            }

            # Tổng hợp feed theo khu vực
            if 'feed_calculations' in report and 'area_totals' in report['feed_calculations']:
                feed_areas = report['feed_calculations']['area_totals'].get('areas', {})
                for area, data in feed_areas.items():
                    summary['feed_by_area'][area] = data.get('total', 0)

            # Tổng hợp mix theo khu vực
            if 'mix_calculations' in report and 'area_totals' in report['mix_calculations']:
                mix_areas = report['mix_calculations']['area_totals'].get('areas', {})
                for area, data in mix_areas.items():
                    summary['mix_by_area'][area] = data.get('total', 0)

            # Tính tổng theo khu vực
            all_areas = set(summary['feed_by_area'].keys()) | set(summary['mix_by_area'].keys())
            for area in all_areas:
                feed_total = summary['feed_by_area'].get(area, 0)
                mix_total = summary['mix_by_area'].get(area, 0)
                total = feed_total + mix_total

                summary['total_by_area'][area] = {
                    'feed': feed_total,
                    'mix': mix_total,
                    'total': total
                }

                summary['area_rankings'].append({
                    'area': area,
                    'total_consumption': total,
                    'feed_consumption': feed_total,
                    'mix_consumption': mix_total,
                    'feed_percentage': (feed_total / total * 100) if total > 0 else 0,
                    'mix_percentage': (mix_total / total * 100) if total > 0 else 0
                })

            # Sắp xếp theo tổng tiêu thụ
            summary['area_rankings'].sort(key=lambda x: x['total_consumption'], reverse=True)

            # Thêm thứ hạng
            for i, area_data in enumerate(summary['area_rankings'], 1):
                area_data['rank'] = i

            return summary

        except Exception as e:
            print(f"Lỗi tạo tóm tắt khu vực {report_date}: {e}")
            return None

    def get_performance_metrics(self, report_date: str) -> Optional[Dict[str, Any]]:
        """Lấy các chỉ số hiệu suất"""
        try:
            report = self.get_report_for_display(report_date, include_details=False)
            if not report:
                return None

            efficiency = report.get('efficiency_metrics', {})
            summary = report.get('summary', {})
            metadata = report.get('metadata', {})

            metrics = {
                'consumption_metrics': {
                    'total_feed': efficiency.get('feed_total', 0),
                    'total_mix': efficiency.get('mix_total', 0),
                    'total_consumption': efficiency.get('total_consumption', 0),
                    'feed_percentage': efficiency.get('feed_percentage', 0),
                    'mix_percentage': efficiency.get('mix_percentage', 0),
                    'feed_to_mix_ratio': efficiency.get('feed_to_mix_ratio', 0)
                },
                'operational_metrics': {
                    'active_areas': summary.get('active_areas', 0),
                    'active_farms': summary.get('active_farms', 0),
                    'top_farm': summary.get('top_consuming_farm', {})
                },
                'performance_info': {
                    'calculation_time': metadata.get('calculation_time_seconds', 0),
                    'cached': metadata.get('cached', False),
                    'calculated_at': metadata.get('calculated_at', ''),
                    'from_cache': report.get('cache_info', {}).get('loaded_from_cache', False)
                }
            }

            return metrics

        except Exception as e:
            print(f"Lỗi lấy chỉ số hiệu suất {report_date}: {e}")
            return None

    def refresh_report(self, report_date: str) -> bool:
        """Làm mới báo cáo (xóa cache và tính lại)"""
        try:
            # Xóa cache
            self.calculator.invalidate_report_cache(report_date)

            # Tính lại báo cáo
            new_report = self.calculator.calculate_daily_report(report_date, force_recalculate=True)

            return new_report is not None

        except Exception as e:
            print(f"Lỗi làm mới báo cáo {report_date}: {e}")
            return False

    def get_cache_status(self, report_date: str = None) -> Dict[str, Any]:
        """Lấy trạng thái cache"""
        try:
            cache_stats = self.cache_manager.get_cache_statistics()

            status = {
                'global_stats': cache_stats,
                'report_specific': None
            }

            if report_date:
                # Kiểm tra cache cho báo cáo cụ thể
                cached_report = self.cache_manager.get_cached_report(report_date, "daily_consumption")
                status['report_specific'] = {
                    'report_date': report_date,
                    'cached': cached_report is not None,
                    'cache_size': 0
                }

                if cached_report:
                    # Tính kích thước cache
                    cache_key = self.cache_manager._generate_cache_key(report_date, "daily_consumption")
                    cache_entry = self.cache_manager.cache_metadata['cache_entries'].get(cache_key, {})
                    status['report_specific']['cache_size'] = cache_entry.get('file_size', 0)
                    status['report_specific']['created_at'] = cache_entry.get('created_at', '')
                    status['report_specific']['last_accessed'] = cache_entry.get('last_accessed', '')

            return status

        except Exception as e:
            print(f"Lỗi lấy trạng thái cache: {e}")
            return {}

    def cleanup_old_cache(self, days_old: int = 7) -> int:
        """Dọn dẹp cache cũ"""
        try:
            return self.cache_manager.cleanup_expired_cache()
        except Exception as e:
            print(f"Lỗi dọn dẹp cache: {e}")
            return 0

# Global instance
cached_report_viewer = CachedReportViewer()

# Convenience functions
def get_cached_feed_table(report_date: str) -> Optional[List[Dict[str, Any]]]:
    """Lấy bảng tiêu thụ cám từ cache"""
    return cached_report_viewer.get_feed_consumption_table(report_date)

def get_cached_mix_table(report_date: str) -> Optional[List[Dict[str, Any]]]:
    """Lấy bảng tiêu thụ mix từ cache"""
    return cached_report_viewer.get_mix_consumption_table(report_date)

def get_cached_area_summary(report_date: str) -> Optional[Dict[str, Any]]:
    """Lấy tóm tắt khu vực từ cache"""
    return cached_report_viewer.get_area_summary(report_date)

def get_cached_performance_metrics(report_date: str) -> Optional[Dict[str, Any]]:
    """Lấy chỉ số hiệu suất từ cache"""
    return cached_report_viewer.get_performance_metrics(report_date)

def refresh_cached_report(report_date: str) -> bool:
    """Làm mới báo cáo cache"""
    return cached_report_viewer.refresh_report(report_date)

def get_report_cache_status(report_date: str = None) -> Dict[str, Any]:
    """Lấy trạng thái cache báo cáo"""
    return cached_report_viewer.get_cache_status(report_date)
