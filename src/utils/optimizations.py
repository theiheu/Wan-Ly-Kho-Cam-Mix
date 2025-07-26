"""
Optimization utilities for the Chicken Farm App.
This module provides functions to optimize application performance and usability.
"""

import os
import json
import shutil
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional

# Try to import PyQt5 but don't fail if it's not available
try:
    from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QMessageBox
    from PyQt5.QtCore import Qt
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

# Try to import logger but don't fail if it's not available
try:
    from src.utils.error_handler import logger
except ImportError:
    # Create a simple logger
    import logging
    logger = logging.getLogger("ChickenFarmApp")
    if not logger.handlers:
        handler = logging.StreamHandler()
        logger.addHandler(handler)


def optimize_table_rendering(table) -> None:
    """
    Optimize table rendering performance.

    Args:
        table: The table widget to optimize
    """
    if not PYQT_AVAILABLE or not isinstance(table, QTableWidget):
        return

    try:
        # Disable sorting temporarily during updates
        table.setSortingEnabled(False)

        # Disable screen updates
        table.setUpdatesEnabled(False)

        # Set row count at once instead of incrementally
        table.setRowCount(0)

        # Enable after updates
        table.setUpdatesEnabled(True)
    except Exception as e:
        logger.error(f"Error optimizing table rendering: {e}")


def batch_update_inventory(inventory_manager, updates: Dict[str, float]) -> bool:
    """
    Update multiple inventory items in a single batch operation.

    Args:
        inventory_manager: The inventory manager instance
        updates: Dictionary mapping ingredient names to new amounts

    Returns:
        bool: True if update was successful
    """
    try:
        return inventory_manager.update_multiple(updates)
    except Exception as e:
        logger.error(f"Error in batch update inventory: {e}")
        # Try individual updates as fallback
        try:
            success = True
            for ingredient, amount in updates.items():
                if not inventory_manager.update_inventory(ingredient, amount):
                    success = False
            return success
        except Exception as e2:
            logger.error(f"Error in fallback inventory update: {e2}")
            return False


def export_data_to_excel(data: Dict[str, Any], filename: str) -> bool:
    """
    Export data to Excel with optimized performance.

    Args:
        data: Dictionary containing data to export
        filename: Path to save Excel file

    Returns:
        bool: True if export was successful
    """
    try:
        # Try to import pandas
        import pandas as pd

        # Create Excel writer with optimized settings
        writer = pd.ExcelWriter(filename, engine='xlsxwriter')

        # Export inventory data
        if "inventory" in data:
            inventory_df = pd.DataFrame(list(data["inventory"].items()), columns=["Ingredient", "Amount"])
            inventory_df.to_excel(writer, sheet_name="Inventory", index=False)

        # Export formula data
        if "formulas" in data:
            if "feed" in data["formulas"]:
                feed_df = pd.DataFrame(list(data["formulas"]["feed"].items()), columns=["Ingredient", "Ratio"])
                feed_df.to_excel(writer, sheet_name="Feed Formula", index=False)

            if "mix" in data["formulas"]:
                mix_df = pd.DataFrame(list(data["formulas"]["mix"].items()), columns=["Ingredient", "Ratio"])
                mix_df.to_excel(writer, sheet_name="Mix Formula", index=False)

        # Export usage data
        if "usage" in data:
            usage_df = pd.DataFrame(list(data["usage"].items()), columns=["Area", "Amount"])
            usage_df.to_excel(writer, sheet_name="Usage", index=False)

        # Save and close
        writer.close()
        return True
    except ImportError:
        logger.warning("Pandas not available, falling back to JSON export")
        try:
            # Fallback to JSON export if pandas is not available
            json_filename = filename.replace('.xlsx', '.json')
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Data exported to JSON: {json_filename}")
            return True
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
            return False
    except Exception as e:
        logger.error(f"Error exporting to Excel: {e}")
        return False


def compress_history_data(history_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compress history data to reduce storage size.

    Args:
        history_data: Dictionary containing history data

    Returns:
        Dict[str, Any]: Compressed history data
    """
    try:
        compressed = {}

        # Only store non-zero values
        for key, value in history_data.items():
            if isinstance(value, dict):
                compressed[key] = compress_history_data(value)
            elif value != 0:
                compressed[key] = value

        return compressed
    except Exception as e:
        logger.error(f"Error compressing history data: {e}")
        return history_data  # Return original data on error


def validate_input_data(data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate input data to ensure it meets requirements.

    Args:
        data: Dictionary containing input data

    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    try:
        # Check required fields
        required_fields = ["date", "feed_usage"]
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"

        # Validate date format
        try:
            datetime.strptime(data["date"], "%Y-%m-%d")
        except ValueError:
            return False, "Invalid date format. Expected YYYY-MM-DD"

        return True, ""
    except Exception as e:
        logger.error(f"Error validating input data: {e}")
        return False, f"Validation error: {str(e)}"


def optimize_report_storage(report_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Optimize report data storage by removing redundant or zero values.

    Args:
        report_data: Dictionary containing report data

    Returns:
        Dict[str, Any]: Optimized report data
    """
    try:
        optimized = {}

        # Copy essential fields
        essential_fields = ["date", "default_formula"]
        for field in essential_fields:
            if field in report_data:
                optimized[field] = report_data[field]

        # Optimize feed_usage data
        if "feed_usage" in report_data:
            optimized["feed_usage"] = {}
            for khu, farms in report_data["feed_usage"].items():
                optimized["feed_usage"][khu] = {}
                for farm, shifts in farms.items():
                    optimized["feed_usage"][khu][farm] = {}
                    for shift, value in shifts.items():
                        if value > 0:  # Only store non-zero values
                            optimized["feed_usage"][khu][farm][shift] = value

        # Optimize formula_usage data
        if "formula_usage" in report_data:
            optimized["formula_usage"] = {}
            for khu, farms in report_data["formula_usage"].items():
                optimized["formula_usage"][khu] = {}
                for farm, shifts in farms.items():
                    optimized["formula_usage"][khu][farm] = {}
                    for shift, formula in shifts.items():
                        if formula:  # Only store non-empty formulas
                            optimized["formula_usage"][khu][farm][shift] = formula

        # Optimize feed_ingredients data
        if "feed_ingredients" in report_data:
            optimized["feed_ingredients"] = {}
            for ingredient, amount in report_data["feed_ingredients"].items():
                if amount > 0:  # Only store non-zero amounts
                    optimized["feed_ingredients"][ingredient] = amount

        # Optimize mix_ingredients data
        if "mix_ingredients" in report_data:
            optimized["mix_ingredients"] = {}
            for ingredient, amount in report_data["mix_ingredients"].items():
                if amount > 0:  # Only store non-zero amounts
                    optimized["mix_ingredients"][ingredient] = amount

        # Copy other fields
        for key, value in report_data.items():
            if key not in optimized and key not in ["feed_usage", "formula_usage", "feed_ingredients", "mix_ingredients"]:
                optimized[key] = value

        return optimized
    except Exception as e:
        logger.error(f"Error optimizing report storage: {e}")
        return report_data  # Return original data on error


def backup_data_files(backup_dir: str = "backups") -> bool:
    """
    Create backups of important data files.

    Args:
        backup_dir: Directory to store backups

    Returns:
        bool: True if backup was successful
    """
    try:
        # Create backup directory if it doesn't exist
        os.makedirs(backup_dir, exist_ok=True)

        # Create timestamp for backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Define files to backup
        data_files = [
            "src/data/config/inventory.json",
            "src/data/config/feed_formula.json",
            "src/data/config/mix_formula.json",
            "src/data/config/formula_links.json",
            "src/data/config/default_formula.json",
            "src/data/config/column_mix_formulas.json"
        ]

        # Copy each file to backup directory
        for file_path in data_files:
            if os.path.exists(file_path):
                filename = os.path.basename(file_path)
                backup_path = os.path.join(backup_dir, f"{filename}_{timestamp}")
                shutil.copy2(file_path, backup_path)

        return True
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        return False


def show_low_stock_warning(inventory_manager, daily_usage: Dict[str, float], threshold_days: int = 7) -> None:
    """
    Show warning for ingredients with low stock.

    Args:
        inventory_manager: The inventory manager instance
        daily_usage: Dictionary mapping ingredient names to daily usage amounts
        threshold_days: Number of days to consider as low stock threshold
    """
    try:
        # Get inventory
        inventory = inventory_manager.get_inventory()

        # Calculate days remaining for each ingredient
        low_stock = []
        for ingredient, daily_amount in daily_usage.items():
            if daily_amount > 0:
                current = inventory.get(ingredient, 0)
                days_remaining = current / daily_amount if daily_amount > 0 else float('inf')

                if days_remaining < threshold_days:
                    low_stock.append((ingredient, current, days_remaining))

        # Sort by days remaining (ascending)
        low_stock.sort(key=lambda x: x[2])

        # Show warning if there are low stock items
        if low_stock:
            warning_message = "Cảnh báo: Các thành phần sau sắp hết:\n\n"

            for ingredient, current, days in low_stock:
                warning_message += f"- {ingredient}: {current:.2f} kg (còn {days:.1f} ngày)\n"

            if PYQT_AVAILABLE:
                QMessageBox.warning(None, "Cảnh báo tồn kho thấp", warning_message)
            else:
                print(warning_message)
    except Exception as e:
        logger.error(f"Error showing low stock warning: {e}")
        print(f"Error checking low stock: {e}")