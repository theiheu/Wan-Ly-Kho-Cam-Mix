#!/usr/bin/env python3
"""
Report Cache Integration - Tích hợp cache báo cáo vào ứng dụng chính
Cung cấp các hàm tiện ích để tích hợp cache vào UI
"""

import os
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable

# Import cache services
try:
    from src.services.daily_report_calculator import daily_report_calculator
    from src.services.cached_report_viewer import cached_report_viewer
    from src.services.report_cache_manager import report_cache_manager, monitor_and_invalidate_cache
except ImportError:
    from services.daily_report_calculator import daily_report_calculator
    from services.cached_report_viewer import cached_report_viewer
    from services.report_cache_manager import report_cache_manager, monitor_and_invalidate_cache

class ReportCacheIntegration:
    """Tích hợp cache báo cáo vào ứng dụng chính"""
    
    def __init__(self):
        """Khởi tạo integration"""
        self.calculator = daily_report_calculator
        self.viewer = cached_report_viewer
        self.cache_manager = report_cache_manager
        
        # Callback functions for UI updates
        self.progress_callback = None
        self.status_callback = None
    
    def set_progress_callback(self, callback: Callable[[int], None]):
        """Thiết lập callback cho progress bar"""
        self.progress_callback = callback
    
    def set_status_callback(self, callback: Callable[[str], None]):
        """Thiết lập callback cho status updates"""
        self.status_callback = callback
    
    def _update_progress(self, value: int):
        """Cập nhật progress"""
        if self.progress_callback:
            self.progress_callback(value)
    
    def _update_status(self, message: str):
        """Cập nhật status"""
        if self.status_callback:
            self.status_callback(message)
        print(f"[Cache Integration] {message}")
    
    def load_daily_report_for_ui(self, report_date: str, show_progress: bool = True) -> Optional[Dict[str, Any]]:
        """Tải báo cáo hàng ngày cho UI với progress tracking"""
        try:
            if show_progress:
                self._update_progress(10)
                self._update_status("Đang kiểm tra cache...")
            
            # Kiểm tra cache trước
            cached_report = self.cache_manager.get_cached_report(report_date, "daily_consumption")
            
            if cached_report:
                if show_progress:
                    self._update_progress(100)
                    self._update_status("Đã tải từ cache")
                return cached_report
            
            if show_progress:
                self._update_progress(30)
                self._update_status("Đang tính toán báo cáo...")
            
            # Tính toán báo cáo mới
            report = self.calculator.calculate_daily_report(report_date)
            
            if show_progress:
                self._update_progress(100)
                self._update_status("Hoàn thành")
            
            return report
            
        except Exception as e:
            self._update_status(f"Lỗi: {str(e)}")
            return None
    
    def get_feed_consumption_for_table(self, report_date: str) -> List[Dict[str, Any]]:
        """Lấy dữ liệu tiêu thụ cám cho bảng UI"""
        try:
            self._update_status("Đang tải dữ liệu tiêu thụ cám...")
            table_data = self.viewer.get_feed_consumption_table(report_date)
            
            if table_data:
                self._update_status(f"Đã tải {len(table_data)} dòng dữ liệu cám")
                return table_data
            else:
                self._update_status("Không có dữ liệu tiêu thụ cám")
                return []
                
        except Exception as e:
            self._update_status(f"Lỗi tải dữ liệu cám: {str(e)}")
            return []
    
    def get_mix_consumption_for_table(self, report_date: str) -> List[Dict[str, Any]]:
        """Lấy dữ liệu tiêu thụ mix cho bảng UI"""
        try:
            self._update_status("Đang tải dữ liệu tiêu thụ mix...")
            table_data = self.viewer.get_mix_consumption_table(report_date)
            
            if table_data:
                self._update_status(f"Đã tải {len(table_data)} dòng dữ liệu mix")
                return table_data
            else:
                self._update_status("Không có dữ liệu tiêu thụ mix")
                return []
                
        except Exception as e:
            self._update_status(f"Lỗi tải dữ liệu mix: {str(e)}")
            return []
    
    def get_summary_for_dashboard(self, report_date: str) -> Dict[str, Any]:
        """Lấy tóm tắt cho dashboard"""
        try:
            self._update_status("Đang tải tóm tắt báo cáo...")
            
            # Lấy metrics
            metrics = self.viewer.get_performance_metrics(report_date)
            if not metrics:
                return {}
            
            # Lấy area summary
            area_summary = self.viewer.get_area_summary(report_date)
            
            dashboard_data = {
                'consumption_summary': {
                    'total_feed': metrics['consumption_metrics']['total_feed'],
                    'total_mix': metrics['consumption_metrics']['total_mix'],
                    'total_consumption': metrics['consumption_metrics']['total_consumption'],
                    'feed_percentage': metrics['consumption_metrics']['feed_percentage'],
                    'mix_percentage': metrics['consumption_metrics']['mix_percentage']
                },
                'operational_summary': {
                    'active_areas': metrics['operational_metrics']['active_areas'],
                    'active_farms': metrics['operational_metrics']['active_farms'],
                    'top_farm': metrics['operational_metrics']['top_farm']
                },
                'area_rankings': area_summary.get('area_rankings', []) if area_summary else [],
                'cache_info': {
                    'from_cache': metrics['performance_info']['from_cache'],
                    'calculation_time': metrics['performance_info']['calculation_time']
                }
            }
            
            self._update_status("Tóm tắt đã sẵn sàng")
            return dashboard_data
            
        except Exception as e:
            self._update_status(f"Lỗi tải tóm tắt: {str(e)}")
            return {}
    
    def refresh_report_data(self, report_date: str) -> bool:
        """Làm mới dữ liệu báo cáo (xóa cache và tính lại)"""
        try:
            self._update_status("Đang làm mới dữ liệu...")
            success = self.viewer.refresh_report(report_date)
            
            if success:
                self._update_status("Dữ liệu đã được làm mới")
            else:
                self._update_status("Không thể làm mới dữ liệu")
            
            return success
            
        except Exception as e:
            self._update_status(f"Lỗi làm mới: {str(e)}")
            return False
    
    def get_cache_info_for_ui(self, report_date: str = None) -> Dict[str, Any]:
        """Lấy thông tin cache cho UI"""
        try:
            cache_status = self.viewer.get_cache_status(report_date)
            cache_stats = cache_status.get('global_stats', {})
            
            ui_info = {
                'total_cached_reports': cache_stats.get('total_entries', 0),
                'cache_size_mb': cache_stats.get('total_size_mb', 0),
                'recent_reports': cache_stats.get('recent_entries_24h', 0),
                'cache_validity_hours': cache_stats.get('cache_validity_hours', 24),
                'specific_report': None
            }
            
            if report_date and cache_status.get('report_specific'):
                specific = cache_status['report_specific']
                ui_info['specific_report'] = {
                    'date': specific['report_date'],
                    'cached': specific['cached'],
                    'size_kb': round(specific['cache_size'] / 1024, 1) if specific['cache_size'] else 0,
                    'created_at': specific.get('created_at', ''),
                    'last_accessed': specific.get('last_accessed', '')
                }
            
            return ui_info
            
        except Exception as e:
            self._update_status(f"Lỗi lấy thông tin cache: {str(e)}")
            return {}
    
    def cleanup_old_cache(self) -> Dict[str, Any]:
        """Dọn dẹp cache cũ"""
        try:
            self._update_status("Đang dọn dẹp cache cũ...")
            
            # Dọn dẹp cache hết hạn
            removed_count = self.cache_manager.cleanup_expired_cache()
            
            # Kiểm tra và vô hiệu hóa cache cho file đã thay đổi
            invalidation_result = monitor_and_invalidate_cache()
            
            result = {
                'expired_removed': removed_count,
                'invalidated_reports': invalidation_result.get('invalidated_reports', []),
                'total_invalidated': invalidation_result.get('total_invalidated', 0),
                'success': True
            }
            
            self._update_status(f"Dọn dẹp hoàn thành: {removed_count} cache hết hạn, {result['total_invalidated']} cache vô hiệu")
            return result
            
        except Exception as e:
            self._update_status(f"Lỗi dọn dẹp cache: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_available_reports_with_cache_info(self) -> List[Dict[str, Any]]:
        """Lấy danh sách báo cáo có sẵn với thông tin cache"""
        try:
            available_dates = self.calculator.get_available_reports()
            reports_info = []
            
            for date in available_dates:
                # Kiểm tra cache status
                cached_report = self.cache_manager.get_cached_report(date, "daily_consumption")
                
                info = {
                    'date': date,
                    'display_date': self._format_display_date(date),
                    'cached': cached_report is not None,
                    'cache_size': 0
                }
                
                if cached_report:
                    # Lấy thông tin cache
                    cache_key = self.cache_manager._generate_cache_key(date, "daily_consumption")
                    cache_entry = self.cache_manager.cache_metadata['cache_entries'].get(cache_key, {})
                    info['cache_size'] = cache_entry.get('file_size', 0)
                    info['cached_at'] = cache_entry.get('created_at', '')
                
                reports_info.append(info)
            
            return reports_info
            
        except Exception as e:
            self._update_status(f"Lỗi lấy danh sách báo cáo: {str(e)}")
            return []
    
    def _format_display_date(self, date_str: str) -> str:
        """Định dạng ngày hiển thị"""
        try:
            if len(date_str) == 8:
                year = date_str[:4]
                month = date_str[4:6]
                day = date_str[6:8]
                return f"{day}/{month}/{year}"
        except:
            pass
        return date_str

# Global integration instance
report_cache_integration = ReportCacheIntegration()

# Convenience functions for UI integration
def load_cached_daily_report(report_date: str, progress_callback=None, status_callback=None) -> Optional[Dict[str, Any]]:
    """Tải báo cáo hàng ngày với cache cho UI"""
    if progress_callback:
        report_cache_integration.set_progress_callback(progress_callback)
    if status_callback:
        report_cache_integration.set_status_callback(status_callback)
    
    return report_cache_integration.load_daily_report_for_ui(report_date)

def get_cached_feed_table_data(report_date: str) -> List[Dict[str, Any]]:
    """Lấy dữ liệu bảng tiêu thụ cám"""
    return report_cache_integration.get_feed_consumption_for_table(report_date)

def get_cached_mix_table_data(report_date: str) -> List[Dict[str, Any]]:
    """Lấy dữ liệu bảng tiêu thụ mix"""
    return report_cache_integration.get_mix_consumption_for_table(report_date)

def get_dashboard_summary(report_date: str) -> Dict[str, Any]:
    """Lấy tóm tắt cho dashboard"""
    return report_cache_integration.get_summary_for_dashboard(report_date)

def refresh_report_cache(report_date: str) -> bool:
    """Làm mới cache báo cáo"""
    return report_cache_integration.refresh_report_data(report_date)

def get_cache_info() -> Dict[str, Any]:
    """Lấy thông tin cache"""
    return report_cache_integration.get_cache_info_for_ui()

def cleanup_cache() -> Dict[str, Any]:
    """Dọn dẹp cache"""
    return report_cache_integration.cleanup_old_cache()
