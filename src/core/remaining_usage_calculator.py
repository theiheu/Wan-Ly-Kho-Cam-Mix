#!/usr/bin/env python3
"""
Remaining Ingredient Usage Calculator for Warehouse Management System

This module calculates remaining ingredient quantities and estimated days remaining
based on current inventory levels and historical usage patterns from production reports.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Handle imports for both development and executable environments
try:
    from src.utils.persistent_paths import persistent_path_manager, get_config_file_path
except ImportError:
    try:
        from utils.persistent_paths import persistent_path_manager, get_config_file_path
    except ImportError:
        # Fallback for executable environment
        import sys
        current_dir = Path(__file__).parent
        sys.path.insert(0, str(current_dir.parent))

        try:
            from utils.persistent_paths import persistent_path_manager, get_config_file_path
        except ImportError:
            # Ultimate fallback
            class MockPathManager:
                def __init__(self):
                    if getattr(sys, 'frozen', False):
                        app_name = "Quan_Ly_Kho_Cam_&_Mix"
                        appdata_path = Path(os.environ.get('APPDATA', '')) / app_name
                        self.data_path = appdata_path / "data"
                        self.config_path = appdata_path / "data" / "config"
                        self.reports_path = appdata_path / "reports"
                    else:
                        self.data_path = Path(__file__).parent.parent / "data"
                        self.config_path = self.data_path / "config"
                        self.reports_path = self.data_path / "reports"

            persistent_path_manager = MockPathManager()

            def get_config_file_path(filename):
                return persistent_path_manager.config_path / filename

class RemainingUsageCalculator:
    """Calculator for remaining usage days based on inventory and consumption patterns"""

    def __init__(self):
        """Initialize calculator with proper data paths"""
        try:
            # Use persistent path manager for correct paths
            self.config_path = persistent_path_manager.config_path
            self.reports_path = persistent_path_manager.reports_path
            self.data_path = persistent_path_manager.data_path

            print(f"🔧 [Usage Calculator] Initialized with paths:")
            print(f"   Config: {self.config_path}")
            print(f"   Reports: {self.reports_path}")
            print(f"   Data: {self.data_path}")

            # Ensure directories exist
            self.config_path.mkdir(parents=True, exist_ok=True)
            self.reports_path.mkdir(parents=True, exist_ok=True)

        except Exception as e:
            print(f"❌ [Usage Calculator] Error initializing paths: {e}")
            # Fallback paths
            self.config_path = Path("data/config")
            self.reports_path = Path("data/reports")
            self.data_path = Path("data")

    def load_current_inventory(self) -> Tuple[Dict[str, float], Dict[str, float]]:
        """Load current inventory from config files using correct paths"""
        try:
            # Use get_config_file_path for proper path resolution
            feed_inventory_path = get_config_file_path("feed_inventory.json")
            mix_inventory_path = get_config_file_path("mix_inventory.json")

            print(f"📂 [Usage Calculator] Loading inventory from:")
            print(f"   Feed: {feed_inventory_path}")
            print(f"   Mix: {mix_inventory_path}")

            # Load feed inventory
            feed_inventory = {}
            if feed_inventory_path.exists():
                with open(feed_inventory_path, 'r', encoding='utf-8') as f:
                    feed_inventory = json.load(f)
                print(f"✅ [Usage Calculator] Loaded {len(feed_inventory)} feed items")
            else:
                print(f"⚠️ [Usage Calculator] Feed inventory file not found: {feed_inventory_path}")

            # Load mix inventory
            mix_inventory = {}
            if mix_inventory_path.exists():
                with open(mix_inventory_path, 'r', encoding='utf-8') as f:
                    mix_inventory = json.load(f)
                print(f"✅ [Usage Calculator] Loaded {len(mix_inventory)} mix items")
            else:
                print(f"⚠️ [Usage Calculator] Mix inventory file not found: {mix_inventory_path}")

            return feed_inventory, mix_inventory

        except Exception as e:
            print(f"❌ [Usage Calculator] Error loading inventory: {e}")
            return {}, {}

    def load_packaging_info(self) -> Tuple[Dict[str, int], Dict[str, int]]:
        """Load packaging information from both warehouses"""
        try:
            # Load feed packaging
            feed_pkg_file = self.config_path / "feed_packaging_info.json"
            if feed_pkg_file.exists():
                with open(feed_pkg_file, 'r', encoding='utf-8') as f:
                    self._feed_packaging = json.load(f)
            else:
                self._feed_packaging = {}

            # Load mix packaging
            mix_pkg_file = self.config_path / "mix_packaging_info.json"
            if mix_pkg_file.exists():
                with open(mix_pkg_file, 'r', encoding='utf-8') as f:
                    self._mix_packaging = json.load(f)
            else:
                self._mix_packaging = {}

            print(f"📋 [Usage Calculator] Loaded packaging info: {len(self._feed_packaging)} feed, {len(self._mix_packaging)} mix items")
            return self._feed_packaging, self._mix_packaging

        except Exception as e:
            print(f"❌ [Usage Calculator] Error loading packaging info: {e}")
            return {}, {}

    def load_usage_history(self, days: int = 7) -> List[Dict]:
        """Load usage history from report files using correct reports path"""
        try:
            print(f"📊 [Usage Calculator] Loading {days} days of usage history from: {self.reports_path}")

            usage_data = []
            today = datetime.now()

            for i in range(days):
                date = today - timedelta(days=i)
                date_str = date.strftime("%Y%m%d")
                report_file = self.reports_path / f"report_{date_str}.json"

                print(f"🔍 [Usage Calculator] Checking report: {report_file}")

                if report_file.exists():
                    try:
                        with open(report_file, 'r', encoding='utf-8') as f:
                            report_data = json.load(f)

                        # Extract consumption data
                        consumption_data = {
                            "date": date_str,
                            "feed_ingredients": report_data.get("feed_ingredients", {}),
                            "mix_ingredients": report_data.get("mix_ingredients", {})
                        }

                        usage_data.append(consumption_data)
                        print(f"✅ [Usage Calculator] Loaded report for {date_str}")

                    except Exception as e:
                        print(f"⚠️ [Usage Calculator] Error reading report {date_str}: {e}")
                else:
                    print(f"⚠️ [Usage Calculator] Report not found: {report_file}")

            print(f"📊 [Usage Calculator] Loaded {len(usage_data)} days of usage data")
            return usage_data

        except Exception as e:
            print(f"❌ [Usage Calculator] Error loading usage history: {e}")
            return []

    def calculate_average_daily_usage(self, usage_history: List[Dict]) -> Dict[str, float]:
        """Calculate average daily usage for each ingredient from usage history list"""
        try:
            # Aggregate usage data by ingredient
            ingredient_usage = {}

            for daily_data in usage_history:
                # Process feed ingredients
                feed_ingredients = daily_data.get("feed_ingredients", {})
                for ingredient, amount in feed_ingredients.items():
                    if isinstance(amount, (int, float)) and amount > 0:
                        key = f"feed_{ingredient}"
                        if key not in ingredient_usage:
                            ingredient_usage[key] = []
                        ingredient_usage[key].append(amount)

                # Process mix ingredients
                mix_ingredients = daily_data.get("mix_ingredients", {})
                for ingredient, amount in mix_ingredients.items():
                    if isinstance(amount, (int, float)) and amount > 0:
                        key = f"mix_{ingredient}"
                        if key not in ingredient_usage:
                            ingredient_usage[key] = []
                        ingredient_usage[key].append(amount)

            # Calculate daily averages
            daily_averages = {}

            for ingredient_key, usage_list in ingredient_usage.items():
                if usage_list:
                    # Calculate average daily usage
                    total_usage = sum(usage_list)
                    days_count = len(usage_list)
                    average_daily = total_usage / days_count

                    daily_averages[ingredient_key] = average_daily

                    # Extract warehouse and ingredient name for logging
                    if ingredient_key.startswith("feed_"):
                        warehouse = "feed"
                        ingredient = ingredient_key[5:]  # Remove "feed_" prefix
                    elif ingredient_key.startswith("mix_"):
                        warehouse = "mix"
                        ingredient = ingredient_key[4:]   # Remove "mix_" prefix
                    else:
                        warehouse = "unknown"
                        ingredient = ingredient_key

                    print(f"📈 [Usage Calculator] {warehouse.upper()} - {ingredient}: {average_daily:.2f} kg/day (from {days_count} days)")

            print(f"📊 [Usage Calculator] Calculated averages for {len(daily_averages)} ingredients")
            return daily_averages

        except Exception as e:
            print(f"❌ [Usage Calculator] Error calculating daily averages: {e}")
            import traceback
            traceback.print_exc()
            return {}

    def calculate_remaining_days(self, current_inventory: Dict[str, float],
                               daily_usage: Dict[str, float],
                               warehouse_type: str) -> Dict[str, Dict[str, float]]:
        """Calculate remaining days for ingredients in a specific warehouse"""
        try:
            remaining_data = {}

            for ingredient, current_amount in current_inventory.items():
                # Create the usage key for this warehouse and ingredient
                usage_key = f"{warehouse_type}_{ingredient}"

                # Get daily usage for this ingredient
                daily_consumption = daily_usage.get(usage_key, 0.0)

                # Calculate remaining days
                if daily_consumption > 0:
                    remaining_days = current_amount / daily_consumption
                else:
                    # If no usage data, assume infinite (or very high number)
                    remaining_days = 999.0

                # Determine status based on remaining days
                if remaining_days <= 1:
                    status = "critical"
                elif remaining_days <= 3:
                    status = "low"
                elif remaining_days <= 7:
                    status = "warning"
                else:
                    status = "good"

                remaining_data[ingredient] = {
                    "current_amount": current_amount,
                    "daily_usage": daily_consumption,
                    "remaining_days": remaining_days,
                    "status": status,
                    "warehouse": warehouse_type
                }

            return remaining_data

        except Exception as e:
            print(f"❌ [Usage Calculator] Error calculating remaining days for {warehouse_type}: {e}")
            return {}

    def get_comprehensive_usage_analysis(self, days_history: int = 7) -> Dict[str, Dict[str, Dict[str, float]]]:
        """Get comprehensive usage analysis for both warehouses with enhanced threshold support"""
        try:
            print(f"🔄 [Usage Calculator] Starting comprehensive usage analysis...")

            # Initialize threshold manager integration
            self.integrate_with_threshold_manager()

            # Load all required data
            feed_inventory, mix_inventory = self.load_current_inventory()
            feed_packaging, mix_packaging = self.load_packaging_info()
            usage_history = self.load_usage_history(days_history)

            # Calculate daily averages
            daily_usage = self.calculate_average_daily_usage(usage_history)

            # Calculate remaining days using enhanced threshold logic
            if hasattr(self, 'threshold_manager'):
                feed_remaining = self.calculate_remaining_days_with_thresholds(feed_inventory, daily_usage, "feed")
                mix_remaining = self.calculate_remaining_days_with_thresholds(mix_inventory, daily_usage, "mix")
            else:
                feed_remaining = self.calculate_remaining_days(feed_inventory, daily_usage, "feed")
                mix_remaining = self.calculate_remaining_days(mix_inventory, daily_usage, "mix")

            # Enhanced summary with more detailed statistics
            analysis_result = {
                "feed": feed_remaining,
                "mix": mix_remaining,
                "summary": {
                    "total_feed_items": len(feed_remaining),
                    "total_mix_items": len(mix_remaining),
                    "feed_critical": len([item for item in feed_remaining.values() if item["status"] == "critical"]),
                    "feed_low": len([item for item in feed_remaining.values() if item["status"] == "low"]),
                    "feed_warning": len([item for item in feed_remaining.values() if item["status"] == "warning"]),
                    "feed_good": len([item for item in feed_remaining.values() if item["status"] == "good"]),
                    "mix_critical": len([item for item in mix_remaining.values() if item["status"] == "critical"]),
                    "mix_low": len([item for item in mix_remaining.values() if item["status"] == "low"]),
                    "mix_warning": len([item for item in mix_remaining.values() if item["status"] == "warning"]),
                    "mix_good": len([item for item in mix_remaining.values() if item["status"] == "good"]),
                    "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "days_analyzed": days_history,
                    "total_ingredients_tracked": len(daily_usage),
                    "ingredients_with_usage_data": len([k for k, v in daily_usage.items() if v > 0])
                }
            }

            # Enhanced logging
            summary = analysis_result["summary"]
            print(f"📊 [Usage Calculator] Analysis complete:")
            print(f"   Feed warehouse: {summary['total_feed_items']} items")
            print(f"     - Critical: {summary['feed_critical']}, Low: {summary['feed_low']}")
            print(f"     - Warning: {summary['feed_warning']}, Good: {summary['feed_good']}")
            print(f"   Mix warehouse: {summary['total_mix_items']} items")
            print(f"     - Critical: {summary['mix_critical']}, Low: {summary['mix_low']}")
            print(f"     - Warning: {summary['mix_warning']}, Good: {summary['mix_good']}")
            print(f"   Usage data: {summary['ingredients_with_usage_data']}/{summary['total_ingredients_tracked']} ingredients")

            return analysis_result

        except Exception as e:
            print(f"❌ [Usage Calculator] Error in comprehensive analysis: {e}")
            import traceback
            traceback.print_exc()
            return {"feed": {}, "mix": {}, "summary": {}}

    def get_ingredient_status_color(self, status: str) -> Tuple[str, str]:
        """Get background and text colors for ingredient status"""
        color_map = {
            "critical": ("#FFEBEE", "#C62828"),  # Light red background, dark red text
            "low": ("#FFF3E0", "#F57C00"),       # Light orange background, dark orange text
            "warning": ("#FFFDE7", "#F9A825"),   # Light yellow background, dark yellow text
            "good": ("#E8F5E9", "#2E7D32")       # Light green background, dark green text
        }
        return color_map.get(status, ("#F5F5F5", "#424242"))  # Default gray

    def format_remaining_days(self, days: float) -> str:
        """Format remaining days for display"""
        if days >= 999:
            return "∞"
        elif days >= 30:
            return f"{days:.0f} ngày"
        elif days >= 1:
            return f"{days:.1f} ngày"
        else:
            return f"{days*24:.1f} giờ"

    def get_critical_alerts(self, analysis_result: Dict = None) -> Dict[str, List[Dict]]:
        """Get critical and warning alerts for ingredients running low"""
        if analysis_result is None:
            analysis_result = self.get_comprehensive_usage_analysis()

        alerts = {
            "critical": [],
            "low": [],
            "warning": []
        }

        # Process feed warehouse alerts
        for ingredient, data in analysis_result.get("feed", {}).items():
            alert_item = {
                "ingredient": ingredient,
                "warehouse": "feed",
                "current_amount": data["current_amount"],
                "daily_usage": data["daily_usage"],
                "remaining_days": data["remaining_days"],
                "status": data["status"]
            }

            if data["status"] == "critical":
                alerts["critical"].append(alert_item)
            elif data["status"] == "low":
                alerts["low"].append(alert_item)
            elif data["status"] == "warning":
                alerts["warning"].append(alert_item)

        # Process mix warehouse alerts
        for ingredient, data in analysis_result.get("mix", {}).items():
            alert_item = {
                "ingredient": ingredient,
                "warehouse": "mix",
                "current_amount": data["current_amount"],
                "daily_usage": data["daily_usage"],
                "remaining_days": data["remaining_days"],
                "status": data["status"]
            }

            if data["status"] == "critical":
                alerts["critical"].append(alert_item)
            elif data["status"] == "low":
                alerts["low"].append(alert_item)
            elif data["status"] == "warning":
                alerts["warning"].append(alert_item)

        # Sort alerts by remaining days (ascending)
        for alert_type in alerts:
            alerts[alert_type].sort(key=lambda x: x["remaining_days"])

        return alerts

    def generate_usage_report(self, days_history: int = 7, save_to_file: bool = True) -> Dict:
        """Generate comprehensive usage report with alerts"""
        try:
            print(f"📋 [Usage Calculator] Generating usage report for {days_history} days...")

            # Get comprehensive analysis
            analysis = self.get_comprehensive_usage_analysis(days_history)

            # Get alerts
            alerts = self.get_critical_alerts(analysis)

            # Create report structure
            report = {
                "report_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "analysis_period_days": days_history,
                "warehouses": {
                    "feed": analysis.get("feed", {}),
                    "mix": analysis.get("mix", {})
                },
                "alerts": alerts,
                "summary": analysis.get("summary", {}),
                "recommendations": self._generate_recommendations(alerts)
            }

            if save_to_file:
                # Save report to file
                report_filename = f"usage_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                report_path = self.reports_path / report_filename

                try:
                    with open(report_path, 'w', encoding='utf-8') as f:
                        json.dump(report, f, indent=2, ensure_ascii=False, default=str)
                    print(f"💾 [Usage Calculator] Report saved to: {report_path}")
                    report["saved_to"] = str(report_path)
                except Exception as e:
                    print(f"⚠️ [Usage Calculator] Failed to save report: {e}")

            return report

        except Exception as e:
            print(f"❌ [Usage Calculator] Error generating usage report: {e}")
            import traceback
            traceback.print_exc()
            return {}

    def _generate_recommendations(self, alerts: Dict[str, List[Dict]]) -> List[str]:
        """Generate recommendations based on alerts"""
        recommendations = []

        # Critical items recommendations
        if alerts["critical"]:
            recommendations.append(f"🚨 URGENT: {len(alerts['critical'])} ingredients are critically low (≤1 day remaining)")
            for item in alerts["critical"][:3]:  # Show top 3 critical items
                recommendations.append(f"   • {item['ingredient']} ({item['warehouse']}): {item['remaining_days']:.1f} days left")

        # Low stock recommendations
        if alerts["low"]:
            recommendations.append(f"⚠️ {len(alerts['low'])} ingredients are running low (≤3 days remaining)")

        # Warning recommendations
        if alerts["warning"]:
            recommendations.append(f"📋 {len(alerts['warning'])} ingredients need attention (≤7 days remaining)")

        # General recommendations
        if not alerts["critical"] and not alerts["low"] and not alerts["warning"]:
            recommendations.append("✅ All ingredients have sufficient stock levels")
        else:
            recommendations.append("💡 Consider placing orders for low-stock ingredients")
            recommendations.append("📊 Review consumption patterns for better inventory planning")

        return recommendations

    def integrate_with_threshold_manager(self, threshold_manager=None):
        """Integrate with ThresholdManager for consistent status categorization"""
        if threshold_manager is None:
            try:
                from src.core.threshold_manager import ThresholdManager
                threshold_manager = ThresholdManager()
            except ImportError:
                print("⚠️ [Usage Calculator] ThresholdManager not available, using default thresholds")
                return

        self.threshold_manager = threshold_manager
        print("🔗 [Usage Calculator] Integrated with ThresholdManager")

    def calculate_remaining_days_with_thresholds(self, current_inventory: Dict[str, float],
                                               daily_usage: Dict[str, float],
                                               warehouse_type: str) -> Dict[str, Dict[str, float]]:
        """Calculate remaining days using ThresholdManager if available"""
        try:
            remaining_data = {}

            for ingredient, current_amount in current_inventory.items():
                usage_key = f"{warehouse_type}_{ingredient}"
                daily_consumption = daily_usage.get(usage_key, 0.0)

                # Calculate remaining days
                if daily_consumption > 0:
                    remaining_days = current_amount / daily_consumption
                else:
                    remaining_days = 999.0

                # Use ThresholdManager if available
                if hasattr(self, 'threshold_manager'):
                    status_text, color_info = self.threshold_manager.get_inventory_status(
                        remaining_days, current_amount, ingredient
                    )
                    # Map color_info to our status system
                    status_map = {"red": "critical", "yellow": "low", "orange": "warning", "green": "good"}
                    status = status_map.get(color_info, "good")
                else:
                    # Use default logic
                    if remaining_days <= 1:
                        status = "critical"
                    elif remaining_days <= 3:
                        status = "low"
                    elif remaining_days <= 7:
                        status = "warning"
                    else:
                        status = "good"

                remaining_data[ingredient] = {
                    "current_amount": current_amount,
                    "daily_usage": daily_consumption,
                    "remaining_days": remaining_days,
                    "status": status,
                    "warehouse": warehouse_type
                }

            return remaining_data

        except Exception as e:
            print(f"❌ [Usage Calculator] Error calculating remaining days for {warehouse_type}: {e}")
            return {}
