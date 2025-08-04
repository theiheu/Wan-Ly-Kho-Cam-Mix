#!/usr/bin/env python3
"""
Daily Report Calculator - Tính toán báo cáo tiêu thụ hàng ngày
Tích hợp với hệ thống cache để tối ưu hiệu suất
"""

import os
import json
import time
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
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

    def _validate_report_file_path(self, report_date: str) -> Path:
        """Validate and return the correct report file path"""
        try:
            # Primary path (should be used for both read and write)
            primary_path = self.reports_dir / f"report_{report_date}.json"

            # Check for legacy paths that might contain data
            legacy_paths = [
                Path("src/data/reports") / f"report_{report_date}.json",
                Path("installer/output/reports") / f"report_{report_date}.json",
                Path(__file__).parent.parent / "data" / "reports" / f"report_{report_date}.json"
            ]

            print(f"🔍 Validating report file path for {report_date}")
            print(f"   Primary path: {primary_path}")

            # If primary path exists, use it
            if primary_path.exists():
                print(f"✅ Using primary path: {primary_path}")
                return primary_path

            # Check legacy paths for existing data
            for legacy_path in legacy_paths:
                if legacy_path.exists():
                    print(f"📁 Found legacy report at: {legacy_path}")

                    # Migrate the file to primary location
                    try:
                        primary_path.parent.mkdir(parents=True, exist_ok=True)
                        import shutil
                        shutil.copy2(legacy_path, primary_path)
                        print(f"🔄 Migrated report from {legacy_path} to {primary_path}")
                        return primary_path
                    except Exception as e:
                        print(f"⚠️ Failed to migrate {legacy_path}: {e}")
                        # Return legacy path if migration fails
                        return legacy_path

            # No existing file found, return primary path for new file
            print(f"📝 No existing report found, will create at: {primary_path}")
            return primary_path

        except Exception as e:
            print(f"❌ Error validating report file path: {e}")
            return self.reports_dir / f"report_{report_date}.json"

    def _load_existing_report(self, report_date: str) -> Optional[Dict]:
        """Load existing report with path validation and metadata normalization"""
        try:
            report_file = self._validate_report_file_path(report_date)

            if report_file.exists() and report_file.stat().st_size > 0:
                print(f"📖 Loading existing report from: {report_file}")

                with open(report_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)

                # Validate data integrity
                if existing_data.get('date') == report_date:
                    # Ensure metadata exists
                    if 'metadata' not in existing_data:
                        existing_data['metadata'] = {}

                    # Add missing metadata fields
                    if 'last_accessed' not in existing_data['metadata']:
                        existing_data['metadata']['last_accessed'] = datetime.now().isoformat()

                    if 'preserved_user_data' not in existing_data['metadata']:
                        existing_data['metadata']['preserved_user_data'] = True

                    print(f"✅ Loaded valid existing report for {report_date}")
                    print(f"   Total feed: {existing_data.get('total_feed', 'N/A')}")
                    print(f"   Generated at: {existing_data.get('generated_at', 'N/A')}")
                    return existing_data
                else:
                    print(f"⚠️ Report date mismatch in file: expected {report_date}, got {existing_data.get('date')}")

            return None

        except Exception as e:
            print(f"❌ Error loading existing report {report_date}: {e}")
            return None

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
        """Tính toán báo cáo tiêu thụ hàng ngày với bảo toàn dữ liệu người dùng"""
        try:
            print(f"📊 Calculating daily report for {report_date}")

            # Load existing report first to preserve user modifications
            existing_report = self._load_existing_report(report_date)

            # Check cache if not forcing recalculation
            if not force_recalculate:
                cached_report = report_cache_manager.get_cached_report(report_date, "daily_consumption")
                if cached_report:
                    print(f"📋 Using cached report for {report_date}")

                    # If we have existing file data that's newer, prefer it
                    if existing_report:
                        existing_time = existing_report.get('generated_at', 0)
                        cached_time = cached_report.get('generated_at', 0)

                        # Convert to comparable format if needed
                        if isinstance(existing_time, str):
                            try:
                                existing_time = datetime.fromisoformat(existing_time).timestamp()
                            except:
                                existing_time = 0

                        if isinstance(cached_time, str):
                            try:
                                cached_time = datetime.fromisoformat(cached_time).timestamp()
                            except:
                                cached_time = 0

                        if existing_time > cached_time:
                            print(f"🔄 Existing file is newer than cache, using file data")
                            return existing_report

                    return cached_report

            start_time = time.time()

            # Load configuration files
            print("📖 Loading configuration files...")
            feed_formula = self._load_json_file(self.config_dir / "feed_formula.json")
            mix_formula = self._load_json_file(self.config_dir / "mix_formula.json")
            inventory = self._load_json_file(self.config_dir / "inventory.json")

            if not feed_formula and not mix_formula:
                print("❌ Missing both feed and mix formula data")
                return existing_report  # Return existing data if available

            # Start with existing report structure if available and not forcing recalculation
            if existing_report and not force_recalculate:
                calculated_report = existing_report.copy()
                print(f"🔄 Preserving existing report data (total_feed: {calculated_report.get('total_feed', 'N/A')})")

                # Ensure metadata exists
                if 'metadata' not in calculated_report:
                    calculated_report['metadata'] = {}

                # Update metadata only
                calculated_report['metadata']['last_accessed'] = datetime.now().isoformat()
                calculated_report['metadata']['preserved_user_data'] = True

            else:
                # Create new report structure
                calculated_report = {
                    'date': report_date,
                    'display_date': self._format_display_date(report_date),
                    'generated_at': datetime.now().isoformat(),
                    'metadata': {
                        'calculation_time': 0,
                        'cached': False,
                        'preserved_user_data': False,
                        'data_sources': {
                            'feed_formula': bool(feed_formula),
                            'mix_formula': bool(mix_formula),
                            'inventory': bool(inventory)
                        }
                    }
                }

                # Calculate feed consumption if formula available
                if feed_formula:
                    feed_data = self._calculate_feed_consumption(feed_formula, inventory)
                    calculated_report.update(feed_data)

                # Calculate mix consumption if formula available
                if mix_formula:
                    mix_data = self._calculate_mix_consumption(mix_formula, inventory)
                    calculated_report.update(mix_data)

                # Calculate efficiency metrics
                efficiency_metrics = self._calculate_efficiency_metrics(calculated_report)
                calculated_report['efficiency_metrics'] = efficiency_metrics

                # Create summary
                calculated_report['summary'] = self._create_report_summary(calculated_report)

            calculation_time = time.time() - start_time
            calculated_report['metadata']['calculation_time'] = round(calculation_time, 2)

            # Always save to the validated path
            report_file = self._validate_report_file_path(report_date)
            save_success = self._save_report_to_validated_path(report_date, calculated_report, report_file)

            if save_success:
                calculated_report['metadata']['saved_to_file'] = True
                calculated_report['metadata']['file_path'] = str(report_file)
            else:
                calculated_report['metadata']['saved_to_file'] = False
                print("⚠️ Report calculation completed but file save failed")

            # Update cache
            cache_success = report_cache_manager.cache_report(report_date, calculated_report, "daily_consumption")
            if cache_success:
                calculated_report['metadata']['cached'] = True

            print(f"✅ Daily report processed in {calculation_time:.2f}s for {report_date}")
            return calculated_report

        except Exception as e:
            print(f"❌ Error calculating daily report {report_date}: {e}")
            import traceback
            traceback.print_exc()

            # Return existing report if calculation fails
            existing_report = self._load_existing_report(report_date)
            if existing_report:
                print(f"🔄 Returning existing report due to calculation error")
                return existing_report

            return None

    def _save_report_to_validated_path(self, report_date: str, report_data: Dict, report_file: Path) -> bool:
        """Save report to validated path with backup"""
        try:
            # Ensure directory exists
            report_file.parent.mkdir(parents=True, exist_ok=True)

            print(f"💾 Saving report to validated path: {report_file}")

            # Create backup if file exists
            if report_file.exists():
                backup_file = report_file.parent / f"report_{report_date}_backup_{int(time.time())}.json"
                import shutil
                shutil.copy2(report_file, backup_file)
                print(f"🔄 Created backup: {backup_file}")

            # Save report with atomic write
            temp_file = report_file.parent / f"report_{report_date}_temp.json"

            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)

            # Atomic move
            temp_file.replace(report_file)

            # Verify save
            if report_file.exists() and report_file.stat().st_size > 0:
                print(f"✅ Report saved successfully: {report_file} ({report_file.stat().st_size} bytes)")

                # Verify data integrity
                with open(report_file, 'r', encoding='utf-8') as f:
                    saved_data = json.load(f)

                if saved_data.get('date') == report_date:
                    print(f"✅ Data integrity verified for {report_date}")
                    return True
                else:
                    print(f"❌ Data integrity check failed for {report_date}")
                    return False
            else:
                print(f"❌ Report file not created or empty: {report_file}")
                return False

        except Exception as e:
            print(f"❌ Error saving report to validated path {report_date}: {e}")
            import traceback
            traceback.print_exc()
            return False

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

    def _format_display_date(self, report_date: str) -> str:
        """Format date for display (YYYYMMDD -> DD/MM/YYYY)"""
        try:
            if len(report_date) == 8:
                year = report_date[:4]
                month = report_date[4:6]
                day = report_date[6:8]
                return f"{day}/{month}/{year}"
            return report_date
        except:
            return report_date

    def _create_report_summary(self, report_data: Dict) -> Dict:
        """Create summary section for report"""
        try:
            return {
                'total_feed': report_data.get('total_feed', 0),
                'total_mix': report_data.get('total_mix', 0),
                'total_consumption': report_data.get('total_feed', 0) + report_data.get('total_mix', 0),
                'feed_ingredients_count': len(report_data.get('feed_ingredients', {})),
                'mix_ingredients_count': len(report_data.get('mix_ingredients', {}))
            }
        except:
            return {}

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








