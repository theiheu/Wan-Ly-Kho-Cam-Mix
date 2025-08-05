import json
import os
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta
try:
    from src.utils.persistent_paths import get_data_file_path, get_config_file_path
except ImportError:
    from utils.persistent_paths import get_data_file_path, get_config_file_path

class InventoryManager:
    """Class to manage inventory of feed and mix ingredients with separate warehouses"""

    def __init__(self, warehouse_type=None):
        """
        Initialize inventory manager for specific warehouse type or both

        Args:
            warehouse_type (str): 'feed', 'mix', or None for both warehouses
        """
        self.warehouse_type = warehouse_type

        # File paths for separate warehouses
        self.feed_inventory_file = str(get_config_file_path("feed_inventory.json"))
        self.mix_inventory_file = str(get_config_file_path("mix_inventory.json"))
        self.legacy_inventory_file = str(get_config_file_path("inventory.json"))

        # Packaging info files (separate for each warehouse)
        self.feed_packaging_file = str(get_config_file_path("feed_packaging_info.json"))
        self.mix_packaging_file = str(get_config_file_path("mix_packaging_info.json"))
        self.legacy_packaging_file = str(get_config_file_path("packaging_info.json"))

        # Load inventory and packaging data
        self.feed_inventory = self.load_warehouse_inventory("feed")
        self.mix_inventory = self.load_warehouse_inventory("mix")
        self.feed_packaging_info = self.load_warehouse_packaging_info("feed")
        self.mix_packaging_info = self.load_warehouse_packaging_info("mix")

        # For backward compatibility, provide unified view
        self.inventory = self.get_unified_inventory()
        self.packaging_info = self.get_unified_packaging_info()

    def load_warehouse_inventory(self, warehouse_type: str) -> Dict[str, float]:
        """Load inventory from warehouse-specific JSON file"""
        try:
            if warehouse_type == "feed":
                file_path = self.feed_inventory_file
            elif warehouse_type == "mix":
                file_path = self.mix_inventory_file
            else:
                raise ValueError(f"Invalid warehouse type: {warehouse_type}")

            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Try to migrate from legacy file if warehouse files don't exist
                return self.migrate_from_legacy_inventory(warehouse_type)
        except Exception as e:
            print(f"Error loading {warehouse_type} inventory: {e}")
            return {}

    def load_inventory(self) -> Dict[str, float]:
        """Legacy method - load unified inventory for backward compatibility"""
        return self.get_unified_inventory()

    def save_warehouse_inventory(self, warehouse_type: str) -> bool:
        """Save inventory to warehouse-specific JSON file"""
        try:
            if warehouse_type == "feed":
                file_path = self.feed_inventory_file
                inventory_data = self.feed_inventory
            elif warehouse_type == "mix":
                file_path = self.mix_inventory_file
                inventory_data = self.mix_inventory
            else:
                raise ValueError(f"Invalid warehouse type: {warehouse_type}")

            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(inventory_data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Error saving {warehouse_type} inventory: {e}")
            return False

    def save_inventory(self) -> bool:
        """Legacy method - save both warehouses for backward compatibility"""
        feed_success = self.save_warehouse_inventory("feed")
        mix_success = self.save_warehouse_inventory("mix")
        return feed_success and mix_success

    def load_warehouse_packaging_info(self, warehouse_type: str) -> Dict[str, int]:
        """Load packaging information from warehouse-specific JSON file"""
        try:
            if warehouse_type == "feed":
                file_path = self.feed_packaging_file
            elif warehouse_type == "mix":
                file_path = self.mix_packaging_file
            else:
                raise ValueError(f"Invalid warehouse type: {warehouse_type}")

            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Try to migrate from legacy file if warehouse files don't exist
                return self.migrate_packaging_from_legacy(warehouse_type)
        except Exception as e:
            print(f"Error loading {warehouse_type} packaging info: {e}")
            return {}

    def load_packaging_info(self) -> Dict[str, int]:
        """Legacy method - load unified packaging info for backward compatibility"""
        return self.get_unified_packaging_info()

    def get_unified_inventory(self) -> Dict[str, float]:
        """Get unified view of both warehouses for backward compatibility"""
        unified = {}
        unified.update(self.feed_inventory)
        unified.update(self.mix_inventory)
        return unified

    def get_unified_packaging_info(self) -> Dict[str, int]:
        """Get unified view of both warehouse packaging info for backward compatibility"""
        unified = {}
        unified.update(self.feed_packaging_info)
        unified.update(self.mix_packaging_info)
        return unified

    def migrate_from_legacy_inventory(self, warehouse_type: str) -> Dict[str, float]:
        """Migrate inventory data from legacy inventory.json file"""
        try:
            if not os.path.exists(self.legacy_inventory_file):
                return {}

            # Load categorization analysis
            categorization_file = "inventory_categorization_analysis.json"
            if os.path.exists(categorization_file):
                with open(categorization_file, 'r', encoding='utf-8') as f:
                    categorization = json.load(f)

                if warehouse_type == "feed":
                    return categorization.get("feed_warehouse", {})
                elif warehouse_type == "mix":
                    return categorization.get("mix_warehouse", {})

            # Fallback: load legacy file and return empty (will be populated by migration script)
            return {}

        except Exception as e:
            print(f"Error migrating from legacy inventory for {warehouse_type}: {e}")
            return {}

    def migrate_packaging_from_legacy(self, warehouse_type: str) -> Dict[str, int]:
        """Migrate packaging data from legacy packaging_info.json file"""
        try:
            if not os.path.exists(self.legacy_packaging_file):
                return self.get_default_packaging_info()

            with open(self.legacy_packaging_file, 'r', encoding='utf-8') as f:
                legacy_packaging = json.load(f)

            # Filter packaging info based on warehouse inventory
            warehouse_inventory = getattr(self, f"{warehouse_type}_inventory", {})
            warehouse_packaging = {}

            for ingredient in warehouse_inventory.keys():
                if ingredient in legacy_packaging:
                    warehouse_packaging[ingredient] = legacy_packaging[ingredient]
                else:
                    # Default bag size is now 0 (optional)
                    warehouse_packaging[ingredient] = 0

            return warehouse_packaging

        except Exception as e:
            print(f"Error migrating packaging from legacy: {e}")
            return {}  # Return an empty dictionary if migration fails

    def get_default_packaging_info(self) -> Dict[str, int]:
        """Get default packaging info"""
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

    def determine_warehouse_type(self, ingredient_name: str) -> str:
        """Determine which warehouse an ingredient belongs to based on formulas and patterns"""
        try:
            # Load formulas to check ingredient usage
            feed_formula_file = str(get_config_file_path("feed_formula.json"))
            mix_formula_file = str(get_config_file_path("mix_formula.json"))

            feed_formula = {}
            mix_formula = {}

            if os.path.exists(feed_formula_file):
                with open(feed_formula_file, 'r', encoding='utf-8') as f:
                    feed_formula = json.load(f)

            if os.path.exists(mix_formula_file):
                with open(mix_formula_file, 'r', encoding='utf-8') as f:
                    mix_formula = json.load(f)

            # Check if ingredient is in formulas
            in_feed_formula = ingredient_name in feed_formula
            in_mix_formula = ingredient_name in mix_formula

            # If in both, use categorization rules
            if in_feed_formula and in_mix_formula:
                # These are typically feed ingredients even if used in mix
                feed_priority_ingredients = ["DCP", "Đá hạt", "Đá bột mịn"]
                if ingredient_name in feed_priority_ingredients:
                    return "feed"
                else:
                    return "mix"  # Default to mix for shared additives

            # If only in one formula, use that
            if in_feed_formula:
                return "feed"
            if in_mix_formula:
                return "mix"

            # If not in any formula, categorize based on name patterns
            ingredient_lower = ingredient_name.lower()

            # Feed ingredients patterns
            feed_patterns = ['cám', 'bắp', 'nành', 'dầu', 'gạo', 'nguyên liệu']
            if any(pattern in ingredient_lower for pattern in feed_patterns):
                return "feed"

            # Mix ingredients patterns (additives, supplements, etc.)
            mix_patterns = ['performix', 'premix', 'enzyme', 'lysine', 'methionine', 'choline',
                           'phytast', 'miamix', 'carophy', 'zym', 'tetracylin', 'tiamulin',
                           'amox', 'immune', 'lysoforte', 'nutriprotect', 'defitox', 'ecobiol',
                           'lactic', 'sodium', 'bicarbonate']
            if any(pattern in ingredient_lower for pattern in mix_patterns):
                return "mix"

            # Default to mix for unknown ingredients (typically additives)
            return "mix"

        except Exception as e:
            print(f"Error determining warehouse type for {ingredient_name}: {e}")
            return "mix"  # Default to mix

    def save_warehouse_packaging_info(self, warehouse_type: str) -> bool:
        """Save packaging info to warehouse-specific JSON file"""
        try:
            if warehouse_type == "feed":
                file_path = self.feed_packaging_file
                packaging_data = self.feed_packaging_info
            elif warehouse_type == "mix":
                file_path = self.mix_packaging_file
                packaging_data = self.mix_packaging_info
            else:
                raise ValueError(f"Invalid warehouse type: {warehouse_type}")

            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(packaging_data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Error saving {warehouse_type} packaging info: {e}")
            return False
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
        """Update the inventory for a specific ingredient in appropriate warehouse"""
        try:
            # Find which warehouse contains this ingredient
            if ingredient in self.feed_inventory:
                self.feed_inventory[ingredient] = amount
                warehouse_type = "feed"
            elif ingredient in self.mix_inventory:
                self.mix_inventory[ingredient] = amount
                warehouse_type = "mix"
            else:
                # If ingredient doesn't exist, determine warehouse and add it
                warehouse_type = self.determine_warehouse_type(ingredient)
                if warehouse_type == "feed":
                    self.feed_inventory[ingredient] = amount
                else:
                    self.mix_inventory[ingredient] = amount

            # Update unified view
            self.inventory = self.get_unified_inventory()

            # Save appropriate warehouse
            return self.save_warehouse_inventory(warehouse_type)

        except Exception as e:
            print(f"Error updating inventory for {ingredient}: {e}")
            return False

    def update_multiple(self, updates: Dict[str, float]) -> bool:
        """Update multiple inventory items at once"""
        for ingredient, amount in updates.items():
            self.inventory[ingredient] = amount
        return self.save_inventory()

    def add_new_item(self, item_name: str, initial_quantity: float = 0, bag_size: int = 0, warehouse_type: str = None) -> bool:
        """Add a new inventory item - bag_size defaults to 0 (optional)"""
        try:
            # Determine warehouse type if not specified
            if warehouse_type is None:
                warehouse_type = self.determine_warehouse_type(item_name)

            # Check if item already exists in any warehouse
            if item_name in self.feed_inventory or item_name in self.mix_inventory:
                print(f"Item '{item_name}' already exists in inventory")
                return False

            # Add to appropriate warehouse
            if warehouse_type == "feed":
                self.feed_inventory[item_name] = initial_quantity
                self.feed_packaging_info[item_name] = bag_size
            elif warehouse_type == "mix":
                self.mix_inventory[item_name] = initial_quantity
                self.mix_packaging_info[item_name] = bag_size
            else:
                print(f"Invalid warehouse type: {warehouse_type}")
                return False

            # Update unified views
            self.inventory = self.get_unified_inventory()
            self.packaging_info = self.get_unified_packaging_info()

            # Save warehouse files
            inventory_saved = self.save_warehouse_inventory(warehouse_type)
            packaging_saved = self.save_warehouse_packaging_info(warehouse_type)

            if inventory_saved and packaging_saved:
                print(f"Successfully added new item: {item_name} with {initial_quantity} units to {warehouse_type} warehouse")
                return True
            else:
                print(f"Error saving data for new item: {item_name}")
                return False

        except Exception as e:
            print(f"Error adding new item '{item_name}': {e}")
            return False

    def remove_item(self, item_name: str) -> bool:
        """Remove an item from inventory and packaging info from appropriate warehouse"""
        try:
            removed_from_inventory = False
            removed_from_packaging = False
            warehouse_type = None

            # Remove from feed warehouse
            if item_name in self.feed_inventory:
                del self.feed_inventory[item_name]
                removed_from_inventory = True
                warehouse_type = "feed"
                print(f"Removed '{item_name}' from feed inventory")

            # Remove from mix warehouse
            if item_name in self.mix_inventory:
                del self.mix_inventory[item_name]
                removed_from_inventory = True
                warehouse_type = "mix"
                print(f"Removed '{item_name}' from mix inventory")

            # Remove from feed packaging info
            if item_name in self.feed_packaging_info:
                del self.feed_packaging_info[item_name]
                removed_from_packaging = True
                print(f"Removed '{item_name}' from feed packaging_info")

            # Remove from mix packaging info
            if item_name in self.mix_packaging_info:
                del self.mix_packaging_info[item_name]
                removed_from_packaging = True
                print(f"Removed '{item_name}' from mix packaging_info")

            # Update unified views
            self.inventory = self.get_unified_inventory()
            self.packaging_info = self.get_unified_packaging_info()

            # Save warehouse files
            success = True
            if warehouse_type:
                inventory_success = self.save_warehouse_inventory(warehouse_type)
                packaging_success = self.save_warehouse_packaging_info(warehouse_type)
                success = inventory_success and packaging_success

                if success:
                    print(f"Successfully saved {warehouse_type} warehouse data after removing '{item_name}'")

            # Return True if item was found and removed from at least one location
            return success and (removed_from_inventory or removed_from_packaging)

        except Exception as e:
            print(f"Error removing item '{item_name}': {e}")
            import traceback
            traceback.print_exc()
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
        if bag_size < 0:
            return False, "Kích thước bao phải >= 0"

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
        """Get detailed information about an inventory item - handle zero bag size"""
        try:
            if item_name not in self.inventory:
                return {}

            quantity = self.inventory[item_name]
            bag_size = self.packaging_info.get(item_name, 0)  # Default to 0 instead of 25
            num_bags = quantity / bag_size if bag_size > 0 else 0  # Handle zero bag size

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
        """Validate bag size value - allow 0 and make optional"""
        if bag_size < 0:
            return False, "Kích thước bao phải >= 0"

        if bag_size > 1000:
            return False, "Kích thước bao không được vượt quá 1,000 kg"

        return True, ""

    def validate_item_data_comprehensive(self, name: str, quantity: float, bag_size: int, exclude_name: str = None) -> Tuple[bool, List[str]]:
        """Comprehensive validation for item data - bag size is optional"""
        errors = []

        # Validate name
        name_valid, name_error = self.validate_item_name(name, exclude_name)
        if not name_valid:
            errors.append(name_error)

        # Validate quantity
        qty_valid, qty_error = self.validate_quantity(quantity)
        if not qty_valid:
            errors.append(qty_error)

        # Validate bag size - now allows 0
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
            feed_formula_file = "config/feed_formula.json"
            if os.path.exists(feed_formula_file):
                with open(feed_formula_file, 'r', encoding='utf-8') as f:
                    feed_formula = json.load(f)
                    if item_name in feed_formula:
                        dependencies['feed_formulas'].append("Công thức cám hiện tại")

            # Check mix formulas
            mix_formula_file = "config/mix_formula.json"
            if os.path.exists(mix_formula_file):
                with open(mix_formula_file, 'r', encoding='utf-8') as f:
                    mix_formula = json.load(f)
                    if item_name in mix_formula:
                        dependencies['mix_formulas'].append("Công thức mix hiện tại")

            # Check preset formulas
            presets_dir = "presets"
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
        warehouses_to_save = set()

        for ingredient, amount in ingredients_added.items():
            # Find which warehouse contains this ingredient
            if ingredient in self.feed_inventory:
                current = self.feed_inventory.get(ingredient, 0)
                self.feed_inventory[ingredient] = current + amount
                warehouses_to_save.add("feed")
            elif ingredient in self.mix_inventory:
                current = self.mix_inventory.get(ingredient, 0)
                self.mix_inventory[ingredient] = current + amount
                warehouses_to_save.add("mix")
            else:
                # If ingredient doesn't exist, determine warehouse and add it
                warehouse_type = self.determine_warehouse_type(ingredient)
                if warehouse_type == "feed":
                    current = self.feed_inventory.get(ingredient, 0)
                    self.feed_inventory[ingredient] = current + amount
                    warehouses_to_save.add("feed")
                else:
                    current = self.mix_inventory.get(ingredient, 0)
                    self.mix_inventory[ingredient] = current + amount
                    warehouses_to_save.add("mix")

        # Update unified view
        self.inventory = self.get_unified_inventory()

        # Save affected warehouses
        for warehouse_type in warehouses_to_save:
            self.save_warehouse_inventory(warehouse_type)

        return self.inventory

    def get_packaging_info(self) -> Dict[str, int]:
        """Get packaging information for all ingredients"""
        return self.packaging_info

    def get_warehouse_inventory(self, warehouse_type: str) -> Dict[str, float]:
        """Get inventory for specific warehouse"""
        if warehouse_type == "feed":
            return self.feed_inventory.copy()
        elif warehouse_type == "mix":
            return self.mix_inventory.copy()
        else:
            raise ValueError(f"Invalid warehouse type: {warehouse_type}")

    def get_warehouse_packaging_info(self, warehouse_type: str) -> Dict[str, int]:
        """Get packaging info for specific warehouse"""
        if warehouse_type == "feed":
            return self.feed_packaging_info.copy()
        elif warehouse_type == "mix":
            return self.mix_packaging_info.copy()
        else:
            raise ValueError(f"Invalid warehouse type: {warehouse_type}")

    def get_bag_size(self, ingredient: str) -> int:
        """Get bag size for a specific ingredient"""
        return self.packaging_info.get(ingredient, 0)

    def check_file_permissions(self) -> bool:
        """Check if we have write permissions to all necessary files"""
        try:
            files_to_check = [
                self.feed_inventory_file,
                self.mix_inventory_file,
                self.feed_packaging_file,
                self.mix_packaging_file
            ]

            for file_path in files_to_check:
                # Check if directory exists and is writable
                directory = os.path.dirname(file_path)
                if not os.path.exists(directory):
                    try:
                        os.makedirs(directory, exist_ok=True)
                    except PermissionError:
                        print(f"❌ [InventoryManager] No permission to create directory: {directory}")
                        return False

                # Check if file is writable (if it exists)
                if os.path.exists(file_path):
                    if not os.access(file_path, os.W_OK):
                        print(f"❌ [InventoryManager] No write permission to file: {file_path}")
                        return False
                else:
                    # Check if we can create the file
                    try:
                        with open(file_path, 'a'):
                            pass
                        # Remove the test file if it was created
                        if os.path.getsize(file_path) == 0:
                            os.remove(file_path)
                    except PermissionError:
                        print(f"❌ [InventoryManager] No permission to create file: {file_path}")
                        return False

            print("✅ [InventoryManager] All file permissions OK")
            return True

        except Exception as e:
            print(f"❌ [InventoryManager] Error checking file permissions: {e}")
            return False

    def reload_all_data(self):
        """Force reload all data from files to ensure consistency"""
        try:
            print("🔄 [InventoryManager] Force reloading all data from files...")

            # Check file permissions first
            if not self.check_file_permissions():
                print("❌ [InventoryManager] File permission check failed")
                return False

            # Reload warehouse inventories from files
            self.feed_inventory = self.load_warehouse_inventory("feed")
            self.mix_inventory = self.load_warehouse_inventory("mix")

            # Reload packaging info from files
            self.feed_packaging_info = self.load_warehouse_packaging_info("feed")
            self.mix_packaging_info = self.load_warehouse_packaging_info("mix")

            # Rebuild unified data structures
            self.inventory = self.get_unified_inventory()
            self.packaging_info = self.get_unified_packaging_info()

            print("✅ [InventoryManager] All data reloaded successfully")
            return True

        except Exception as e:
            print(f"❌ [InventoryManager] Error reloading data: {e}")
            import traceback
            traceback.print_exc()
            return False

    def check_ingredient_availability(self, ingredient: str, required_amount: float, warehouse_type: str = None) -> bool:
        """Check if ingredient is available in sufficient quantity in specified warehouse"""
        if warehouse_type is None:
            # Check in unified inventory
            available = self.inventory.get(ingredient, 0)
        elif warehouse_type == "feed":
            available = self.feed_inventory.get(ingredient, 0)
        elif warehouse_type == "mix":
            available = self.mix_inventory.get(ingredient, 0)
        else:
            raise ValueError(f"Invalid warehouse type: {warehouse_type}")

        return available >= required_amount

    def get_ingredient_warehouse(self, ingredient: str) -> str:
        """Determine which warehouse contains the ingredient"""
        if ingredient in self.feed_inventory:
            return "feed"
        elif ingredient in self.mix_inventory:
            return "mix"
        else:
            # If not found, determine based on patterns
            return self.determine_warehouse_type(ingredient)

    def validate_formula_ingredients(self, formula: Dict[str, float], formula_type: str) -> Dict[str, Any]:
        """Validate that all formula ingredients are available in appropriate warehouse"""
        validation_result = {
            "valid": True,
            "missing_ingredients": [],
            "insufficient_ingredients": [],
            "wrong_warehouse_ingredients": [],
            "details": {}
        }

        expected_warehouse = "feed" if formula_type == "feed" else "mix"

        for ingredient, required_amount in formula.items():
            ingredient_warehouse = self.get_ingredient_warehouse(ingredient)
            available_amount = self.inventory.get(ingredient, 0)

            # Check if ingredient exists
            if available_amount == 0 and ingredient not in self.inventory:
                validation_result["missing_ingredients"].append(ingredient)
                validation_result["valid"] = False

            # Check if sufficient quantity available
            elif available_amount < required_amount:
                validation_result["insufficient_ingredients"].append({
                    "ingredient": ingredient,
                    "required": required_amount,
                    "available": available_amount
                })
                validation_result["valid"] = False

            # Check if ingredient is in expected warehouse
            elif ingredient_warehouse != expected_warehouse:
                validation_result["wrong_warehouse_ingredients"].append({
                    "ingredient": ingredient,
                    "expected_warehouse": expected_warehouse,
                    "actual_warehouse": ingredient_warehouse
                })
                # This is a warning, not an error - formulas can use ingredients from other warehouses

            validation_result["details"][ingredient] = {
                "required": required_amount,
                "available": available_amount,
                "warehouse": ingredient_warehouse,
                "sufficient": available_amount >= required_amount
            }

        return validation_result

    def calculate_bags(self, ingredient: str, amount: float) -> float:
        """Calculate number of bags - handle zero bag size"""
        bag_size = self.get_bag_size(ingredient)
        if bag_size <= 0:
            return 0  # Return 0 bags if bag size is 0 or invalid
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
        reports_dir = "reports"
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

