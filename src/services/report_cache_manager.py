#!/usr/bin/env python3
"""
Report Cache Manager - Quản lý cache báo cáo
Lưu trữ và quản lý cache cho các báo cáo tiêu thụ hàng ngày
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from collections import defaultdict

class ReportCacheManager:
    """Quản lý cache báo cáo tiêu thụ hàng ngày"""

    def __init__(self):
        """Khởi tạo manager cache báo cáo"""
        # Use persistent path manager for consistent paths
        from src.utils.persistent_paths import persistent_path_manager

        self.data_dir = persistent_path_manager.data_path
        self.cache_dir = self.data_dir / "cache" / "reports"
        self.reports_dir = persistent_path_manager.reports_path

        print(f"🔧 ReportCacheManager initialized:")
        print(f"   📁 Data dir: {self.data_dir}")
        print(f"   📁 Cache dir: {self.cache_dir}")
        print(f"   📁 Reports dir: {self.reports_dir}")

        # Đảm bảo thư mục cache tồn tại
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Thời gian cache hợp lệ (giờ)
        self.cache_validity_hours = 24

        # Metadata cache
        self.cache_metadata_file = self.cache_dir / "cache_metadata.json"
        self.cache_metadata = self._load_cache_metadata()

    def _load_cache_metadata(self) -> Dict[str, Any]:
        """Tải metadata cache"""
        try:
            if self.cache_metadata_file.exists():
                with open(self.cache_metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Lỗi tải metadata cache: {e}")

        return {
            'cache_entries': {},
            'last_cleanup': datetime.now().isoformat(),
            'total_cache_size': 0
        }

    def _save_cache_metadata(self):
        """Lưu metadata cache"""
        try:
            with open(self.cache_metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache_metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Lỗi lưu metadata cache: {e}")

    def _generate_cache_key(self, report_date: str, report_type: str = "daily_consumption",
                          additional_params: Dict = None) -> str:
        """Tạo key cache duy nhất"""
        # Tạo chuỗi để hash
        key_data = {
            'date': report_date,
            'type': report_type,
            'params': additional_params or {}
        }

        # Tạo hash MD5
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode('utf-8')).hexdigest()

    def _get_source_file_hash(self, report_date: str) -> Optional[str]:
        """Lấy hash của file báo cáo gốc"""
        try:
            # Sử dụng persistent path thay vì relative path
            from src.utils.persistent_paths import persistent_path_manager
            report_file = persistent_path_manager.reports_path / f"report_{report_date}.json"

            print(f"🔍 Checking report file: {report_file}")

            if not report_file.exists():
                print(f"⚠️ Report file not found: {report_file}")
                return None

            # Tạo hash từ nội dung file và thời gian sửa đổi
            with open(report_file, 'r', encoding='utf-8') as f:
                content = f.read()

            mtime = report_file.stat().st_mtime
            hash_data = f"{content}_{mtime}"

            hash_value = hashlib.md5(hash_data.encode('utf-8')).hexdigest()
            print(f"✅ Generated hash for {report_date}: {hash_value[:8]}...")
            return hash_value

        except Exception as e:
            print(f"❌ Error generating hash for {report_date}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _is_cache_valid(self, cache_key: str, source_hash: str) -> bool:
        """Kiểm tra cache có hợp lệ không"""
        if cache_key not in self.cache_metadata['cache_entries']:
            return False

        cache_entry = self.cache_metadata['cache_entries'][cache_key]

        # Kiểm tra thời gian
        cached_time = datetime.fromisoformat(cache_entry['created_at'])
        now = datetime.now()

        if (now - cached_time).total_seconds() > self.cache_validity_hours * 3600:
            return False

        # Kiểm tra hash file nguồn
        if cache_entry.get('source_hash') != source_hash:
            return False

        # Kiểm tra file cache có tồn tại không
        cache_file = self.cache_dir / f"{cache_key}.json"
        if not cache_file.exists():
            return False

        return True

    def get_cached_report(self, report_date: str, report_type: str = "daily_consumption",
                         additional_params: Dict = None) -> Optional[Dict[str, Any]]:
        """Lấy báo cáo từ cache"""
        try:
            # Tạo cache key
            cache_key = self._generate_cache_key(report_date, report_type, additional_params)

            # Lấy hash file nguồn
            source_hash = self._get_source_file_hash(report_date)
            if not source_hash:
                return None

            # Kiểm tra cache có hợp lệ không
            if not self._is_cache_valid(cache_key, source_hash):
                return None

            # Tải dữ liệu cache
            cache_file = self.cache_dir / f"{cache_key}.json"
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)

            # Cập nhật thời gian truy cập
            self.cache_metadata['cache_entries'][cache_key]['last_accessed'] = datetime.now().isoformat()
            self._save_cache_metadata()

            print(f"📋 [Cache] Loaded cached report for {report_date} ({report_type})")
            return cached_data

        except Exception as e:
            print(f"Lỗi tải cache báo cáo {report_date}: {e}")
            return None

    def cache_report(self, report_date: str, report_data: Dict[str, Any],
                    report_type: str = "daily_consumption", additional_params: Dict = None) -> bool:
        """Lưu báo cáo vào cache"""
        try:
            print(f"💾 Caching report for {report_date} ({report_type})")

            # Tạo cache key
            cache_key = self._generate_cache_key(report_date, report_type, additional_params)
            print(f"🔑 Cache key: {cache_key}")

            # Lấy hash file nguồn
            source_hash = self._get_source_file_hash(report_date)
            if not source_hash:
                print(f"⚠️ Cannot generate hash for source file {report_date}")
                # Tạo hash từ dữ liệu báo cáo thay vì file nguồn
                import json
                data_str = json.dumps(report_data, sort_keys=True)
                source_hash = hashlib.md5(data_str.encode('utf-8')).hexdigest()
                print(f"🔄 Using data hash instead: {source_hash[:8]}...")

            # Đảm bảo cache directory tồn tại
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            print(f"📁 Cache directory: {self.cache_dir}")

            # Lưu dữ liệu cache
            cache_file = self.cache_dir / f"{cache_key}.json"
            print(f"💾 Saving cache to: {cache_file}")

            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)

            # Tính kích thước file
            file_size = cache_file.stat().st_size

            # Cập nhật metadata
            self.cache_metadata['cache_entries'][cache_key] = {
                'report_date': report_date,
                'report_type': report_type,
                'source_hash': source_hash,
                'created_at': datetime.now().isoformat(),
                'last_accessed': datetime.now().isoformat(),
                'file_size': file_size,
                'additional_params': additional_params or {}
            }

            # Cập nhật tổng kích thước cache
            self.cache_metadata['total_cache_size'] = sum(
                entry.get('file_size', 0) for entry in self.cache_metadata['cache_entries'].values()
            )

            # Lưu metadata
            self._save_cache_metadata()

            print(f"✅ Report cached successfully: {cache_file.name} ({file_size} bytes)")
            return True

        except Exception as e:
            print(f"❌ Error caching report {report_date}: {e}")
            import traceback
            traceback.print_exc()
            return False

    def invalidate_cache(self, report_date: str = None, report_type: str = None) -> int:
        """Vô hiệu hóa cache"""
        try:
            removed_count = 0
            keys_to_remove = []

            for cache_key, cache_entry in self.cache_metadata['cache_entries'].items():
                should_remove = False

                # Nếu chỉ định ngày cụ thể
                if report_date and cache_entry['report_date'] == report_date:
                    should_remove = True

                # Nếu chỉ định loại báo cáo cụ thể
                if report_type and cache_entry['report_type'] == report_type:
                    should_remove = True

                # Nếu không chỉ định gì, xóa tất cả
                if not report_date and not report_type:
                    should_remove = True

                if should_remove:
                    # Xóa file cache
                    cache_file = self.cache_dir / cache_entry['cache_file']
                    if cache_file.exists():
                        cache_file.unlink()

                    keys_to_remove.append(cache_key)
                    removed_count += 1

            # Xóa entries khỏi metadata
            for key in keys_to_remove:
                del self.cache_metadata['cache_entries'][key]

            # Cập nhật tổng kích thước
            self.cache_metadata['total_cache_size'] = sum(
                entry.get('file_size', 0) for entry in self.cache_metadata['cache_entries'].values()
            )

            self._save_cache_metadata()

            print(f"🗑️ [Cache] Invalidated {removed_count} cache entries")
            return removed_count

        except Exception as e:
            print(f"Lỗi vô hiệu hóa cache: {e}")
            return 0

    def cleanup_expired_cache(self) -> int:
        """Dọn dẹp cache hết hạn"""
        try:
            removed_count = 0
            keys_to_remove = []
            now = datetime.now()

            for cache_key, cache_entry in self.cache_metadata['cache_entries'].items():
                cached_time = datetime.fromisoformat(cache_entry['created_at'])

                # Kiểm tra thời gian hết hạn
                if (now - cached_time).total_seconds() > self.cache_validity_hours * 3600:
                    # Xóa file cache
                    cache_file = self.cache_dir / cache_entry['cache_file']
                    if cache_file.exists():
                        cache_file.unlink()

                    keys_to_remove.append(cache_key)
                    removed_count += 1

            # Xóa entries khỏi metadata
            for key in keys_to_remove:
                del self.cache_metadata['cache_entries'][key]

            # Cập nhật metadata
            self.cache_metadata['last_cleanup'] = now.isoformat()
            self.cache_metadata['total_cache_size'] = sum(
                entry.get('file_size', 0) for entry in self.cache_metadata['cache_entries'].values()
            )

            self._save_cache_metadata()

            if removed_count > 0:
                print(f"🧹 [Cache] Cleaned up {removed_count} expired cache entries")

            return removed_count

        except Exception as e:
            print(f"Lỗi dọn dẹp cache: {e}")
            return 0

    def get_cache_statistics(self) -> Dict[str, Any]:
        """Lấy thống kê cache"""
        try:
            total_entries = len(self.cache_metadata['cache_entries'])
            total_size = self.cache_metadata.get('total_cache_size', 0)

            # Thống kê theo loại báo cáo
            type_stats = defaultdict(int)
            for entry in self.cache_metadata['cache_entries'].values():
                type_stats[entry['report_type']] += 1

            # Thống kê theo ngày
            recent_entries = 0
            now = datetime.now()
            for entry in self.cache_metadata['cache_entries'].values():
                cached_time = datetime.fromisoformat(entry['created_at'])
                if (now - cached_time).total_seconds() < 24 * 3600:  # 24 giờ qua
                    recent_entries += 1

            return {
                'total_entries': total_entries,
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'recent_entries_24h': recent_entries,
                'cache_validity_hours': self.cache_validity_hours,
                'type_breakdown': dict(type_stats),
                'last_cleanup': self.cache_metadata.get('last_cleanup'),
                'cache_directory': str(self.cache_dir)
            }

        except Exception as e:
            print(f"Lỗi lấy thống kê cache: {e}")
            return {}

# Global instance
report_cache_manager = ReportCacheManager()

# Convenience functions
def get_cached_daily_report(report_date: str, additional_params: Dict = None) -> Optional[Dict[str, Any]]:
    """Lấy báo cáo hàng ngày từ cache"""
    return report_cache_manager.get_cached_report(report_date, "daily_consumption", additional_params)

def cache_daily_report(report_date: str, report_data: Dict[str, Any], additional_params: Dict = None) -> bool:
    """Lưu báo cáo hàng ngày vào cache"""
    return report_cache_manager.cache_report(report_date, report_data, "daily_consumption", additional_params)

def invalidate_daily_report_cache(report_date: str = None) -> int:
    """Vô hiệu hóa cache báo cáo hàng ngày"""
    return report_cache_manager.invalidate_cache(report_date, "daily_consumption")

def cleanup_report_cache() -> int:
    """Dọn dẹp cache báo cáo hết hạn"""
    return report_cache_manager.cleanup_expired_cache()

def get_cache_stats() -> Dict[str, Any]:
    """Lấy thống kê cache"""
    return report_cache_manager.get_cache_statistics()

class CacheInvalidationService:
    """Dịch vụ tự động vô hiệu hóa cache khi dữ liệu thay đổi"""

    def __init__(self):
        """Khởi tạo dịch vụ"""
        self.cache_manager = report_cache_manager

        # Use persistent path manager for consistent paths
        from src.utils.persistent_paths import persistent_path_manager
        self.reports_dir = persistent_path_manager.reports_path

        print(f"🔧 CacheInvalidationService initialized:")
        print(f"   📁 Reports dir: {self.reports_dir}")

        self.file_timestamps = {}
        self._load_file_timestamps()

    def _load_file_timestamps(self):
        """Tải timestamps của các file báo cáo"""
        try:
            if self.reports_dir.exists():
                for report_file in self.reports_dir.glob("report_*.json"):
                    if report_file.is_file():
                        self.file_timestamps[str(report_file)] = report_file.stat().st_mtime
                        print(f"📊 Loaded timestamp for: {report_file.name}")
        except Exception as e:
            print(f"❌ Lỗi tải timestamps: {e}")

    def check_and_invalidate_changed_files(self) -> List[str]:
        """Kiểm tra và vô hiệu hóa cache cho các file đã thay đổi"""
        invalidated_reports = []

        try:
            if not self.reports_dir.exists():
                print(f"⚠️ Reports directory does not exist: {self.reports_dir}")
                return invalidated_reports

            for report_file in self.reports_dir.glob("report_*.json"):
                if not report_file.is_file():
                    continue

                file_path = str(report_file)
                current_mtime = report_file.stat().st_mtime

                # Kiểm tra file mới hoặc đã thay đổi
                if (file_path not in self.file_timestamps or
                    self.file_timestamps[file_path] != current_mtime):

                    # Trích xuất ngày từ tên file
                    report_date = report_file.stem.replace('report_', '')

                    # Vô hiệu hóa cache
                    removed_count = self.cache_manager.invalidate_cache(report_date, "daily_consumption")

                    if removed_count > 0:
                        invalidated_reports.append(report_date)
                        print(f"🔄 [Cache Invalidation] Invalidated cache for {report_date} (file changed)")

                    # Cập nhật timestamp
                    self.file_timestamps[file_path] = current_mtime

        except Exception as e:
            print(f"❌ Lỗi kiểm tra thay đổi file: {e}")

        return invalidated_reports

    def monitor_file_changes(self) -> Dict[str, Any]:
        """Giám sát thay đổi file và trả về thống kê"""
        invalidated = self.check_and_invalidate_changed_files()

        return {
            'invalidated_reports': invalidated,
            'total_invalidated': len(invalidated),
            'monitored_files': len(self.file_timestamps),
            'last_check': datetime.now().isoformat()
        }

# Global cache invalidation service
cache_invalidation_service = CacheInvalidationService()

def monitor_and_invalidate_cache() -> Dict[str, Any]:
    """Giám sát và vô hiệu hóa cache tự động"""
    return cache_invalidation_service.monitor_file_changes()



