import json
import os
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta

class InventoryManager:
    """Class to manage inventory of feed and mix ingredients"""

    def __init__(self):
        self.inventory_file = "src/data/config/inventory.json"
        self.inventory = self.load_inventory()

        # Packaging information for inventory
        self.packaging_info = {
            "DCP": 25,  # 1 bag = 25kg
            "Đá hạt": 50,  # 1 bag = 50kg
            "Đá bột mịn": 50,  # 1 bag = 50kg
            "Cám gạo": 40,  # 1 bag = 40kg
            "L-Lysine": 25,
            "DL-Methionine": 25,
            "Bio-Choline": 25,
            "Phytast": 25,
            "Performix 0.25% layer": 25,
            "Miamix": 25,
            "Premix 0.25% layer": 25,
            "Compound Enzyme FE808E": 25,
            "Carophy Red": 25,
            "P-Zym": 25,
            "Immunewall": 25,
            "Lysoforte Dry": 25,
            "Defitox L1": 25,
            "Men Ecobiol": 25,
            "Lactic LD": 25,
            "Sodium bicarbonate": 25,
            "Bột đá mịn": 50,
            "Muối": 50
        }

    def load_inventory(self) -> Dict[str, float]:
        """Load inventory from JSON file"""
        try:
            if os.path.exists(self.inventory_file):
                with open(self.inventory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading inventory: {e}")
            return {}

    def save_inventory(self) -> bool:
        """Save inventory to JSON file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.inventory_file), exist_ok=True)

            with open(self.inventory_file, 'w', encoding='utf-8') as f:
                json.dump(self.inventory, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Error saving inventory: {e}")
            return False

    def get_inventory(self) -> Dict[str, float]:
        """Get the current inventory"""
        return self.inventory

    def update_inventory(self, ingredient: str, amount: float) -> bool:
        """Update the inventory for a specific ingredient"""
        self.inventory[ingredient] = amount
        return self.save_inventory()

    def update_multiple(self, updates: Dict[str, float]) -> bool:
        """Update multiple inventory items at once"""
        for ingredient, amount in updates.items():
            self.inventory[ingredient] = amount
        return self.save_inventory()

    def use_ingredients(self, ingredients_used: Dict[str, float]) -> Dict[str, float]:
        """Subtract used ingredients from inventory and return updated inventory"""
        for ingredient, amount in ingredients_used.items():
            current = self.inventory.get(ingredient, 0)
            self.inventory[ingredient] = max(0, current - amount)

        self.save_inventory()
        return self.inventory

    def add_ingredients(self, ingredients_added: Dict[str, float]) -> Dict[str, float]:
        """Add ingredients to inventory and return updated inventory"""
        for ingredient, amount in ingredients_added.items():
            current = self.inventory.get(ingredient, 0)
            self.inventory[ingredient] = current + amount

        self.save_inventory()
        return self.inventory

    def get_packaging_info(self) -> Dict[str, int]:
        """Get packaging information for all ingredients"""
        return self.packaging_info

    def get_bag_size(self, ingredient: str) -> int:
        """Get bag size for a specific ingredient"""
        return self.packaging_info.get(ingredient, 0)

    def calculate_bags(self, ingredient: str, amount: float) -> float:
        """Calculate number of bags for a given amount of ingredient"""
        bag_size = self.get_bag_size(ingredient)
        if bag_size <= 0:
            return 0
        return amount / bag_size

    def get_low_stock_items(self, threshold_days: int = 7, daily_usage: Dict[str, float] = None) -> List[Tuple[str, float, float]]:
        """
        Get items with low stock based on daily usage
        Returns list of (ingredient, current_amount, days_remaining)
        """
        if daily_usage is None:
            return []

        low_stock = []
        for ingredient, daily_amount in daily_usage.items():
            if daily_amount > 0:
                current = self.inventory.get(ingredient, 0)
                days_remaining = current / daily_amount if daily_amount > 0 else float('inf')

                if days_remaining < threshold_days:
                    low_stock.append((ingredient, current, days_remaining))

        # Sort by days remaining (ascending)
        low_stock.sort(key=lambda x: x[2])
        return low_stock

    def analyze_consumption_patterns(self, days: int = 7) -> Dict[str, float]:
        """
        Analyze consumption patterns from recent reports
        Returns dict with ingredient -> average daily usage
        """
        reports_dir = "src/data/reports"
        end_date = datetime.now()

        daily_usage = {}
        valid_days = 0

        # Get report files for the last N days
        for i in range(days):
            date = end_date - timedelta(days=i)
            date_str = date.strftime("%Y%m%d")
            report_file = os.path.join(reports_dir, f"report_{date_str}.json")

            if os.path.exists(report_file):
                try:
                    with open(report_file, 'r', encoding='utf-8') as f:
                        report_data = json.load(f)

                    # Extract feed and mix ingredients
                    feed_ingredients = report_data.get('feed_ingredients', {})
                    mix_ingredients = report_data.get('mix_ingredients', {})

                    # Combine all ingredients for this day
                    all_ingredients = {**feed_ingredients, **mix_ingredients}

                    # Add to daily usage tracking
                    for ingredient, amount in all_ingredients.items():
                        if isinstance(amount, (int, float)) and amount > 0:
                            if ingredient not in daily_usage:
                                daily_usage[ingredient] = []
                            daily_usage[ingredient].append(amount)

                    valid_days += 1

                except Exception as e:
                    print(f"Error reading report {report_file}: {e}")

        # Calculate average daily usage for each ingredient
        avg_daily_usage = {}
        for ingredient, usage_list in daily_usage.items():
            if usage_list:
                avg_daily_usage[ingredient] = sum(usage_list) / len(usage_list)

        print(f"[DEBUG] Analyzed {valid_days} days of reports, found usage for {len(avg_daily_usage)} ingredients")
        return avg_daily_usage

    def calculate_days_until_empty(self, avg_daily_usage: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate days until empty for each ingredient
        Returns dict with ingredient -> days remaining
        """
        days_remaining = {}

        for ingredient, current_stock in self.inventory.items():
            if ingredient in avg_daily_usage and avg_daily_usage[ingredient] > 0:
                days = current_stock / avg_daily_usage[ingredient]
                days_remaining[ingredient] = days
            else:
                # No usage data or zero usage - set to infinity
                days_remaining[ingredient] = float('inf')

        return days_remaining

