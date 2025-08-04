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
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

class RemainingUsageCalculator:
    """Calculate remaining ingredient usage based on historical data and current inventory"""
    
    def __init__(self, data_path: str = "src/data"):
        """Initialize the calculator with data paths"""
        self.data_path = Path(data_path)
        self.config_path = self.data_path / "config"
        self.reports_path = self.data_path / "reports"
        
        # Cache for loaded data
        self._feed_inventory = None
        self._mix_inventory = None
        self._feed_packaging = None
        self._mix_packaging = None
        self._usage_history = None
        
    def load_current_inventory(self) -> Tuple[Dict[str, float], Dict[str, float]]:
        """Load current inventory from both warehouses"""
        try:
            # Load feed inventory
            feed_file = self.config_path / "feed_inventory.json"
            if feed_file.exists():
                with open(feed_file, 'r', encoding='utf-8') as f:
                    self._feed_inventory = json.load(f)
            else:
                self._feed_inventory = {}
            
            # Load mix inventory
            mix_file = self.config_path / "mix_inventory.json"
            if mix_file.exists():
                with open(mix_file, 'r', encoding='utf-8') as f:
                    self._mix_inventory = json.load(f)
            else:
                self._mix_inventory = {}
            
            print(f"📦 [Usage Calculator] Loaded inventory: {len(self._feed_inventory)} feed, {len(self._mix_inventory)} mix items")
            return self._feed_inventory, self._mix_inventory
            
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
    
    def load_usage_history(self, days: int = 7) -> Dict[str, List[float]]:
        """Load ingredient usage history from production reports"""
        try:
            usage_history = defaultdict(list)
            
            # Get the last N days of reports
            end_date = datetime.now()
            dates_to_check = []
            
            for i in range(days):
                check_date = end_date - timedelta(days=i)
                date_str = check_date.strftime("%Y%m%d")
                dates_to_check.append(date_str)
            
            print(f"🔍 [Usage Calculator] Checking {days} days of reports: {dates_to_check[0]} to {dates_to_check[-1]}")
            
            reports_found = 0
            for date_str in dates_to_check:
                report_file = self.reports_path / f"report_{date_str}.json"
                
                if report_file.exists():
                    try:
                        with open(report_file, 'r', encoding='utf-8') as f:
                            report_data = json.load(f)
                        
                        reports_found += 1
                        
                        # Extract feed ingredients usage
                        feed_ingredients = report_data.get("feed_ingredients", {})
                        for ingredient, amount in feed_ingredients.items():
                            if isinstance(amount, (int, float)) and amount > 0:
                                usage_history[f"feed_{ingredient}"].append(amount)
                        
                        # Extract mix ingredients usage
                        mix_ingredients = report_data.get("mix_ingredients", {})
                        for ingredient, amount in mix_ingredients.items():
                            if isinstance(amount, (int, float)) and amount > 0:
                                usage_history[f"mix_{ingredient}"].append(amount)
                        
                    except Exception as e:
                        print(f"⚠️ [Usage Calculator] Error reading report {date_str}: {e}")
                        continue
            
            print(f"📊 [Usage Calculator] Processed {reports_found} reports, found usage data for {len(usage_history)} ingredients")
            
            self._usage_history = dict(usage_history)
            return self._usage_history
            
        except Exception as e:
            print(f"❌ [Usage Calculator] Error loading usage history: {e}")
            return {}
    
    def calculate_average_daily_usage(self, usage_history: Dict[str, List[float]]) -> Dict[str, float]:
        """Calculate average daily usage for each ingredient"""
        try:
            daily_averages = {}
            
            for ingredient_key, usage_list in usage_history.items():
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
            
            return daily_averages
            
        except Exception as e:
            print(f"❌ [Usage Calculator] Error calculating daily averages: {e}")
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
        """Get comprehensive usage analysis for both warehouses"""
        try:
            print(f"🔄 [Usage Calculator] Starting comprehensive usage analysis...")
            
            # Load all required data
            feed_inventory, mix_inventory = self.load_current_inventory()
            feed_packaging, mix_packaging = self.load_packaging_info()
            usage_history = self.load_usage_history(days_history)
            
            # Calculate daily averages
            daily_usage = self.calculate_average_daily_usage(usage_history)
            
            # Calculate remaining days for both warehouses
            feed_remaining = self.calculate_remaining_days(feed_inventory, daily_usage, "feed")
            mix_remaining = self.calculate_remaining_days(mix_inventory, daily_usage, "mix")
            
            # Combine results
            analysis_result = {
                "feed": feed_remaining,
                "mix": mix_remaining,
                "summary": {
                    "total_feed_items": len(feed_remaining),
                    "total_mix_items": len(mix_remaining),
                    "feed_critical": len([item for item in feed_remaining.values() if item["status"] == "critical"]),
                    "feed_low": len([item for item in feed_remaining.values() if item["status"] == "low"]),
                    "mix_critical": len([item for item in mix_remaining.values() if item["status"] == "critical"]),
                    "mix_low": len([item for item in mix_remaining.values() if item["status"] == "low"]),
                    "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "days_analyzed": days_history
                }
            }
            
            # Print summary
            summary = analysis_result["summary"]
            print(f"📊 [Usage Calculator] Analysis complete:")
            print(f"   Feed warehouse: {summary['total_feed_items']} items ({summary['feed_critical']} critical, {summary['feed_low']} low)")
            print(f"   Mix warehouse: {summary['total_mix_items']} items ({summary['mix_critical']} critical, {summary['mix_low']} low)")
            
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
