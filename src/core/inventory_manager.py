import json
import os
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta

class InventoryManager:
    """Class to manage inventory of feed and mix ingredients"""

    def __init__(self):
        self.inventory_file = "src/data/config/inventory.json"
        self.packaging_file = "src/data/config/packaging_info.json"
        self.inventory = self.load_inventory()
        self.packaging_info = self.load_packaging_info()

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

    def load_packaging_info(self) -> Dict[str, int]:
        """Load packaging information from JSON file"""
        try:
            if os.path.exists(self.packaging_file):
                with open(self.packaging_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Return default packaging info if file doesn't exist
                default_packaging = {
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
                # Save default packaging info
                self.save_packaging_info_data(default_packaging)
                return default_packaging
        except Exception as e:
            print(f"Error loading packaging info: {e}")
            return {}

    def save_packaging_info(self) -> bool:
        """Save packaging information to JSON file"""
        return self.save_packaging_info_data(self.packaging_info)

    def save_packaging_info_data(self, packaging_data: Dict[str, int]) -> bool:
        """Save packaging information data to JSON file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.packaging_file), exist_ok=True)

            with open(self.packaging_file, 'w', encoding='utf-8') as f:
                json.dump(packaging_data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Error saving packaging info: {e}")
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

    def add_new_item(self, item_name: str, initial_quantity: float = 0, bag_size: int = 25) -> bool:
        """Add a new inventory item with initial quantity and bag size"""
        try:
            # Check if item already exists
            if item_name in self.inventory:
                print(f"Item '{item_name}' already exists in inventory")
                return False

            # Add to inventory
            self.inventory[item_name] = initial_quantity

            # Add packaging information
            self.packaging_info[item_name] = bag_size

            # Save both inventory and packaging info
            success = self.save_inventory()
            if success:
                self.save_packaging_info()

            return success

        except Exception as e:
            print(f"Error adding new item '{item_name}': {e}")
            return False

    def remove_item(self, item_name: str) -> bool:
        """Remove an item from inventory and packaging info"""
        try:
            # Remove from inventory
            if item_name in self.inventory:
                del self.inventory[item_name]

            # Remove from packaging info
            if item_name in self.packaging_info:
                del self.packaging_info[item_name]

            # Save both
            success = self.save_inventory()
            if success:
                self.save_packaging_info()

            return success

        except Exception as e:
            print(f"Error removing item '{item_name}': {e}")
            return False

    def validate_item_data(self, item_name: str, quantity: float, bag_size: int) -> Tuple[bool, str]:
        """Validate new item data"""
        # Check item name
        if not item_name or not item_name.strip():
            return False, "Tên mặt hàng không được để trống"

        # Check for duplicates
        if item_name in self.inventory:
            return False, "Tên mặt hàng đã tồn tại trong kho"

        # Check quantity
        if quantity < 0:
            return False, "Số lượng phải >= 0"

        # Check bag size
        if bag_size <= 0:
            return False, "Kích thước bao phải > 0"

        return True, ""

    def update_item_details(self, old_name: str, new_name: str, new_quantity: float, new_bag_size: int) -> bool:
        """Update item details including name, quantity, and bag size"""
        try:
            # If name changed, we need to handle it carefully
            if old_name != new_name:
                # Check if new name already exists
                if new_name in self.inventory:
                    return False

                # Remove old item
                if old_name in self.inventory:
                    del self.inventory[old_name]
                if old_name in self.packaging_info:
                    del self.packaging_info[old_name]

                # Add with new name
                self.inventory[new_name] = new_quantity
                self.packaging_info[new_name] = new_bag_size
            else:
                # Just update existing item
                self.inventory[old_name] = new_quantity
                self.packaging_info[old_name] = new_bag_size

            # Save both files
            success = self.save_inventory()
            if success:
                self.save_packaging_info()

            return success

        except Exception as e:
            print(f"Error updating item details: {e}")
            return False

    def get_item_details(self, item_name: str) -> Dict[str, Any]:
        """Get detailed information about an inventory item"""
        try:
            if item_name not in self.inventory:
                return {}

            quantity = self.inventory[item_name]
            bag_size = self.packaging_info.get(item_name, 25)
            num_bags = quantity / bag_size if bag_size > 0 else 0

            return {
                'name': item_name,
                'quantity': quantity,
                'bag_size': bag_size,
                'num_bags': num_bags,
                'exists': True
            }

        except Exception as e:
            print(f"Error getting item details: {e}")
            return {}

    def get_all_items(self) -> List[Dict[str, Any]]:
        """Get list of all inventory items with their details"""
        try:
            items = []
            for item_name in self.inventory.keys():
                item_details = self.get_item_details(item_name)
                if item_details:
                    items.append(item_details)

            # Sort by name
            items.sort(key=lambda x: x['name'])
            return items

        except Exception as e:
            print(f"Error getting all items: {e}")
            return []

    def search_items(self, search_term: str) -> List[Dict[str, Any]]:
        """Search for items by name"""
        try:
            search_term = search_term.lower().strip()
            if not search_term:
                return self.get_all_items()

            matching_items = []
            for item_name in self.inventory.keys():
                if search_term in item_name.lower():
                    item_details = self.get_item_details(item_name)
                    if item_details:
                        matching_items.append(item_details)

            # Sort by name
            matching_items.sort(key=lambda x: x['name'])
            return matching_items

        except Exception as e:
            print(f"Error searching items: {e}")
            return []

    def bulk_update_quantities(self, updates: Dict[str, float]) -> Tuple[bool, List[str]]:
        """Bulk update quantities for multiple items"""
        try:
            errors = []
            successful_updates = {}

            # Validate all updates first
            for item_name, quantity in updates.items():
                if item_name not in self.inventory:
                    errors.append(f"Mặt hàng '{item_name}' không tồn tại")
                elif quantity < 0:
                    errors.append(f"Số lượng cho '{item_name}' phải >= 0")
                else:
                    successful_updates[item_name] = quantity

            # If there are errors, don't proceed
            if errors:
                return False, errors

            # Apply all updates
            for item_name, quantity in successful_updates.items():
                self.inventory[item_name] = quantity

            # Save inventory
            success = self.save_inventory()
            if not success:
                errors.append("Không thể lưu file inventory")
                return False, errors

            return True, []

        except Exception as e:
            error_msg = f"Lỗi khi cập nhật hàng loạt: {e}"
            print(error_msg)
            return False, [error_msg]

    def bulk_delete_items(self, item_names: List[str]) -> Tuple[bool, List[str]]:
        """Bulk delete multiple items"""
        try:
            errors = []
            items_to_delete = []

            # Validate all items first
            for item_name in item_names:
                if item_name not in self.inventory:
                    errors.append(f"Mặt hàng '{item_name}' không tồn tại")
                else:
                    items_to_delete.append(item_name)

            # If there are errors, don't proceed
            if errors:
                return False, errors

            # Delete all items
            for item_name in items_to_delete:
                if item_name in self.inventory:
                    del self.inventory[item_name]
                if item_name in self.packaging_info:
                    del self.packaging_info[item_name]

            # Save both files
            success = self.save_inventory()
            if success:
                self.save_packaging_info()

            if not success:
                errors.append("Không thể lưu file")
                return False, errors

            return True, []

        except Exception as e:
            error_msg = f"Lỗi khi xóa hàng loạt: {e}"
            print(error_msg)
            return False, [error_msg]

    def validate_item_name(self, name: str, exclude_name: str = None) -> Tuple[bool, str]:
        """Validate item name"""
        if not name or not name.strip():
            return False, "Tên mặt hàng không được để trống"

        name = name.strip()

        # Check length
        if len(name) < 2:
            return False, "Tên mặt hàng phải có ít nhất 2 ký tự"

        if len(name) > 100:
            return False, "Tên mặt hàng không được quá 100 ký tự"

        # Check for invalid characters
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
        for char in invalid_chars:
            if char in name:
                return False, f"Tên mặt hàng không được chứa ký tự '{char}'"

        # Check for duplicates (excluding current item if editing)
        if exclude_name != name and name in self.inventory:
            return False, "Tên mặt hàng đã tồn tại trong kho"

        return True, ""

    def validate_quantity(self, quantity: float) -> Tuple[bool, str]:
        """Validate quantity value"""
        if quantity < 0:
            return False, "Số lượng phải >= 0"

        if quantity > 999999:
            return False, "Số lượng không được vượt quá 999,999"

        return True, ""

    def validate_bag_size(self, bag_size: int) -> Tuple[bool, str]:
        """Validate bag size value"""
        if bag_size <= 0:
            return False, "Kích thước bao phải > 0"

        if bag_size > 1000:
            return False, "Kích thước bao không được vượt quá 1,000 kg"

        return True, ""

    def validate_item_data_comprehensive(self, name: str, quantity: float, bag_size: int, exclude_name: str = None) -> Tuple[bool, List[str]]:
        """Comprehensive validation for item data"""
        errors = []

        # Validate name
        name_valid, name_error = self.validate_item_name(name, exclude_name)
        if not name_valid:
            errors.append(name_error)

        # Validate quantity
        qty_valid, qty_error = self.validate_quantity(quantity)
        if not qty_valid:
            errors.append(qty_error)

        # Validate bag size
        bag_valid, bag_error = self.validate_bag_size(bag_size)
        if not bag_valid:
            errors.append(bag_error)

        return len(errors) == 0, errors

    def check_item_dependencies(self, item_name: str) -> Dict[str, List[str]]:
        """Check if item is used in formulas or has other dependencies"""
        dependencies = {
            'feed_formulas': [],
            'mix_formulas': [],
            'reports': [],
            'warnings': []
        }

        try:
            # Check feed formulas
            feed_formula_file = "src/data/config/feed_formula.json"
            if os.path.exists(feed_formula_file):
                with open(feed_formula_file, 'r', encoding='utf-8') as f:
                    feed_formula = json.load(f)
                    if item_name in feed_formula:
                        dependencies['feed_formulas'].append("Công thức cám hiện tại")

            # Check mix formulas
            mix_formula_file = "src/data/config/mix_formula.json"
            if os.path.exists(mix_formula_file):
                with open(mix_formula_file, 'r', encoding='utf-8') as f:
                    mix_formula = json.load(f)
                    if item_name in mix_formula:
                        dependencies['mix_formulas'].append("Công thức mix hiện tại")

            # Check preset formulas
            presets_dir = "src/data/presets"
            if os.path.exists(presets_dir):
                for root, dirs, files in os.walk(presets_dir):
                    for file in files:
                        if file.endswith('.json'):
                            try:
                                file_path = os.path.join(root, file)
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    preset_data = json.load(f)
                                    if item_name in preset_data:
                                        preset_name = os.path.splitext(file)[0]
                                        if 'feed' in root:
                                            dependencies['feed_formulas'].append(f"Preset cám: {preset_name}")
                                        elif 'mix' in root:
                                            dependencies['mix_formulas'].append(f"Preset mix: {preset_name}")
                            except:
                                continue

            # Add warnings based on dependencies
            if dependencies['feed_formulas'] or dependencies['mix_formulas']:
                dependencies['warnings'].append(
                    "Xóa mặt hàng này có thể ảnh hưởng đến các công thức đang sử dụng"
                )

            # Check if item has significant inventory
            current_qty = self.inventory.get(item_name, 0)
            if current_qty > 0:
                dependencies['warnings'].append(
                    f"Mặt hàng còn {current_qty:,.2f} kg trong kho"
                )

        except Exception as e:
            print(f"Error checking dependencies for {item_name}: {e}")
            dependencies['warnings'].append("Không thể kiểm tra đầy đủ các phụ thuộc")

        return dependencies

    def get_validation_summary(self, item_name: str) -> str:
        """Get a summary of validation issues and dependencies"""
        try:
            dependencies = self.check_item_dependencies(item_name)

            summary_parts = []

            if dependencies['feed_formulas']:
                summary_parts.append(f"Được sử dụng trong {len(dependencies['feed_formulas'])} công thức cám")

            if dependencies['mix_formulas']:
                summary_parts.append(f"Được sử dụng trong {len(dependencies['mix_formulas'])} công thức mix")

            if dependencies['warnings']:
                summary_parts.extend(dependencies['warnings'])

            if not summary_parts:
                return "Không có phụ thuộc đặc biệt"

            return "; ".join(summary_parts)

        except Exception as e:
            print(f"Error getting validation summary: {e}")
            return "Không thể kiểm tra phụ thuộc"

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

