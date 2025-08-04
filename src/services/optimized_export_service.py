#!/usr/bin/env python3
"""
Optimized Export Service - Dịch vụ xuất báo cáo được tối ưu hóa
Cải thiện hiệu suất, chất lượng Excel và trải nghiệm người dùng
"""

import os
import json
import pandas as pd
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from concurrent.futures import ThreadPoolExecutor
import threading

# Excel formatting imports
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment, NamedStyle
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.drawing.image import Image


class ExcelStyleManager:
    """Quản lý styles cho Excel với hiệu suất cao"""

    def __init__(self):
        self._styles_cache = {}
        self._create_predefined_styles()

    def _create_predefined_styles(self):
        """Tạo sẵn các style thường dùng"""
        # Header style
        self.header_style = NamedStyle(name="header_style")
        self.header_style.font = Font(name='Arial', size=12, bold=True, color='FFFFFF')
        self.header_style.fill = PatternFill(start_color='366092', end_color='366092', fill_type='solid')
        self.header_style.border = Border(
            left=Side(style='thin'), right=Side(style='thin'),
            top=Side(style='thin'), bottom=Side(style='thin')
        )
        self.header_style.alignment = Alignment(horizontal='center', vertical='center')

        # Data styles
        self.data_style = NamedStyle(name="data_style")
        self.data_style.font = Font(name='Arial', size=10)
        self.data_style.border = Border(
            left=Side(style='thin'), right=Side(style='thin'),
            top=Side(style='thin'), bottom=Side(style='thin')
        )
        self.data_style.alignment = Alignment(horizontal='left', vertical='center')

        # Number style
        self.number_style = NamedStyle(name="number_style")
        self.number_style.font = Font(name='Arial', size=10)
        self.number_style.number_format = '#,##0.00'
        self.number_style.alignment = Alignment(horizontal='right', vertical='center')

        # Status styles
        self.status_styles = {
            'Đủ': PatternFill(start_color='C6EFCE', end_color='C6EFCE', fill_type='solid'),
            'Ít': PatternFill(start_color='FFEB9C', end_color='FFEB9C', fill_type='solid'),
            'Sắp hết': PatternFill(start_color='FFC7CE', end_color='FFC7CE', fill_type='solid'),
            'Hết hàng': PatternFill(start_color='FF6B6B', end_color='FF6B6B', fill_type='solid')
        }

    def get_status_fill(self, status: str) -> PatternFill:
        """Lấy fill color cho status"""
        return self.status_styles.get(status, PatternFill())


class OptimizedExportService:
    """Dịch vụ xuất báo cáo được tối ưu hóa"""

    def __init__(self, inventory_manager=None, formula_manager=None, threshold_manager=None, remaining_usage_calculator=None):
        """Khởi tạo dịch vụ với data managers từ ứng dụng chính"""
        self.data_dir = Path("src/data")
        self.config_dir = self.data_dir / "config"
        self.exports_dir = self.data_dir / "exports"
        self.daily_consumption_dir = self.data_dir / "daily_consumption"

        # Performance optimizations
        self._data_cache = {}
        self._cache_lock = threading.Lock()
        self._cache_timeout = 300  # 5 minutes

        # Style manager
        self.style_manager = ExcelStyleManager()

        # Ensure directories exist
        self.exports_dir.mkdir(parents=True, exist_ok=True)
        self.daily_consumption_dir.mkdir(parents=True, exist_ok=True)

        # Data managers from main application
        self.inventory_manager = inventory_manager
        self.formula_manager = formula_manager
        self.threshold_manager = threshold_manager
        self.remaining_usage_calculator = remaining_usage_calculator

        # Initialize data managers if not provided (fallback to sample data)
        if not self.inventory_manager or not self.formula_manager:
            print("⚠️ Warning: Data managers not provided, falling back to sample data")
            self._ensure_sample_data()

        # Ensure daily consumption data exists
        self._ensure_daily_consumption_data()

    def get_real_time_inventory_summary(self) -> Dict:
        """Lấy tóm tắt tồn kho real-time từ inventory manager"""
        try:
            if not self.inventory_manager:
                return {}

            summary = {
                'total_items': 0,
                'total_value': 0,
                'low_stock_items': 0,
                'out_of_stock_items': 0,
                'warehouses': {}
            }

            # Get data for each warehouse type
            for warehouse_type in ['feed', 'mix']:
                warehouse_data = self._get_real_inventory_data(warehouse_type)
                warehouse_summary = self._analyze_warehouse_data(warehouse_data, warehouse_type)
                summary['warehouses'][warehouse_type] = warehouse_summary

                # Add to totals
                summary['total_items'] += warehouse_summary.get('item_count', 0)
                summary['total_value'] += warehouse_summary.get('total_value', 0)
                summary['low_stock_items'] += warehouse_summary.get('low_stock_count', 0)
                summary['out_of_stock_items'] += warehouse_summary.get('out_of_stock_count', 0)

            return summary

        except Exception as e:
            print(f"Error getting real-time inventory summary: {e}")
            return {}

    def get_real_time_production_capacity(self) -> Dict:
        """Lấy khả năng sản xuất real-time từ formula và inventory managers"""
        try:
            if not self.formula_manager or not self.inventory_manager:
                return {}

            capacity = {
                'feed_capacity': {},
                'mix_capacity': {},
                'bottleneck_ingredients': []
            }

            # Analyze feed production capacity
            feed_formula = self._get_real_formula_data("feed")
            feed_inventory = self._get_real_inventory_data("feed")
            capacity['feed_capacity'] = self._calculate_production_capacity(feed_formula, feed_inventory)

            # Analyze mix production capacity
            mix_formula = self._get_real_formula_data("mix")
            mix_inventory = self._get_real_inventory_data("mix")
            capacity['mix_capacity'] = self._calculate_production_capacity(mix_formula, mix_inventory)

            # Identify bottleneck ingredients
            capacity['bottleneck_ingredients'] = self._identify_bottlenecks(
                [capacity['feed_capacity'], capacity['mix_capacity']]
            )

            return capacity

        except Exception as e:
            print(f"Error getting real-time production capacity: {e}")
            return {}

    def get_real_time_usage_trends(self, days: int = 30) -> Dict:
        """Lấy xu hướng sử dụng real-time"""
        try:
            if not self.remaining_usage_calculator:
                return {}

            trends = {
                'consumption_trends': {},
                'prediction_accuracy': {},
                'recommended_orders': []
            }

            # Get consumption trends
            trends['consumption_trends'] = self.remaining_usage_calculator.get_consumption_trends(days)

            # Get prediction accuracy
            trends['prediction_accuracy'] = self.remaining_usage_calculator.get_prediction_accuracy()

            # Get recommended orders
            trends['recommended_orders'] = self.remaining_usage_calculator.get_recommended_orders()

            return trends

        except Exception as e:
            print(f"Error getting real-time usage trends: {e}")
            return {}

    def _analyze_warehouse_data(self, warehouse_data: Dict, warehouse_type: str) -> Dict:
        """Phân tích dữ liệu kho"""
        try:
            analysis = {
                'item_count': 0,
                'total_quantity': 0,
                'total_value': 0,
                'low_stock_count': 0,
                'out_of_stock_count': 0,
                'categories': {}
            }

            unit_price = 15000 if warehouse_type == 'feed' else 25000

            if isinstance(warehouse_data, dict):
                if 'items' in warehouse_data:
                    items = warehouse_data['items']
                elif 'inventory' in warehouse_data:
                    items = [{'name': k, 'quantity': v} for k, v in warehouse_data['inventory'].items()]
                else:
                    items = [{'name': k, 'quantity': v} for k, v in warehouse_data.items()]

                for item in items:
                    if isinstance(item, dict):
                        quantity = float(item.get('quantity', 0))
                        analysis['item_count'] += 1
                        analysis['total_quantity'] += quantity
                        analysis['total_value'] += quantity * unit_price

                        # Check stock status
                        if quantity == 0:
                            analysis['out_of_stock_count'] += 1
                        elif quantity < 100:  # Low stock threshold
                            analysis['low_stock_count'] += 1

            return analysis

        except Exception as e:
            print(f"Error analyzing warehouse data: {e}")
            return {}

    def _calculate_production_capacity(self, formula_data: Dict, inventory_data: Dict) -> Dict:
        """Tính toán khả năng sản xuất"""
        try:
            capacity = {
                'max_batches': 0,
                'limiting_ingredients': [],
                'ingredient_usage': {}
            }

            if not formula_data or not inventory_data:
                return capacity

            min_batches = float('inf')

            # Process formula data
            if isinstance(formula_data, dict):
                if 'ingredients' in formula_data:
                    ingredients = formula_data['ingredients']
                elif 'formula' in formula_data:
                    ingredients = [{'name': k, 'percentage': v} for k, v in formula_data['formula'].items()]
                else:
                    ingredients = [{'name': k, 'percentage': v} for k, v in formula_data.items()]

                for ingredient in ingredients:
                    if isinstance(ingredient, dict):
                        name = ingredient.get('name', '')
                        percentage = float(ingredient.get('percentage', 0))

                        if percentage > 0:
                            current_stock = self._get_ingredient_stock(name, inventory_data)
                            usage_per_batch = (percentage / 100) * 1000  # For 1000kg batch
                            possible_batches = int(current_stock / usage_per_batch) if usage_per_batch > 0 else 0

                            capacity['ingredient_usage'][name] = {
                                'stock': current_stock,
                                'usage_per_batch': usage_per_batch,
                                'possible_batches': possible_batches
                            }

                            if possible_batches < min_batches:
                                min_batches = possible_batches
                                capacity['limiting_ingredients'] = [name]
                            elif possible_batches == min_batches:
                                capacity['limiting_ingredients'].append(name)

            capacity['max_batches'] = min_batches if min_batches != float('inf') else 0
            return capacity

        except Exception as e:
            print(f"Error calculating production capacity: {e}")
            return {}

    def _identify_bottlenecks(self, capacity_data: List[Dict]) -> List[Dict]:
        """Xác định các nguyên liệu cổ chai"""
        try:
            bottlenecks = []

            for capacity in capacity_data:
                for ingredient, usage_data in capacity.get('ingredient_usage', {}).items():
                    possible_batches = usage_data.get('possible_batches', 0)
                    if possible_batches < 10:  # Less than 10 batches possible
                        bottlenecks.append({
                            'ingredient': ingredient,
                            'current_stock': usage_data.get('stock', 0),
                            'possible_batches': possible_batches,
                            'urgency': 'high' if possible_batches < 5 else 'medium'
                        })

            # Sort by urgency and possible batches
            bottlenecks.sort(key=lambda x: (x['urgency'] == 'high', -x['possible_batches']))

            return bottlenecks

        except Exception as e:
            print(f"Error identifying bottlenecks: {e}")
            return []

    def _get_real_inventory_data(self, warehouse_type: str = None) -> Dict:
        """Lấy dữ liệu tồn kho thực từ inventory_manager"""
        try:
            if not self.inventory_manager:
                print("⚠️ No inventory_manager available, using sample data")
                return self._load_json_cached(self.config_dir / f"{warehouse_type}_inventory.json" if warehouse_type else self.config_dir / "feed_inventory.json")

            if warehouse_type:
                # Get specific warehouse inventory
                return self.inventory_manager.get_warehouse_inventory(warehouse_type)
            else:
                # Get all inventory
                return self.inventory_manager.get_inventory()

        except Exception as e:
            print(f"Error getting real inventory data: {e}")
            # Fallback to sample data
            return self._load_json_cached(self.config_dir / f"{warehouse_type}_inventory.json" if warehouse_type else self.config_dir / "feed_inventory.json")

    def _get_real_formula_data(self, formula_type: str) -> Dict:
        """Lấy dữ liệu công thức thực từ formula_manager"""
        try:
            if not self.formula_manager:
                print("⚠️ No formula_manager available, using sample data")
                return self._load_json_cached(self.config_dir / f"{formula_type}_formula.json")

            if formula_type == "feed":
                return self.formula_manager.get_feed_formula()
            elif formula_type == "mix":
                return self.formula_manager.get_mix_formula()
            else:
                return {}

        except Exception as e:
            print(f"Error getting real formula data: {e}")
            # Fallback to sample data
            return self._load_json_cached(self.config_dir / f"{formula_type}_formula.json")

    def _get_real_packaging_info(self) -> Dict:
        """Lấy thông tin đóng gói thực từ inventory_manager"""
        try:
            if not self.inventory_manager:
                return {}

            return self.inventory_manager.get_packaging_info()

        except Exception as e:
            print(f"Error getting real packaging info: {e}")
            return {}

    def _get_real_usage_analysis(self) -> Dict:
        """Lấy phân tích sử dụng thực từ remaining_usage_calculator"""
        try:
            if not self.remaining_usage_calculator:
                return {}

            # Get usage analysis for both feed and mix
            return self.remaining_usage_calculator.analyze_usage_patterns()

        except Exception as e:
            print(f"Error getting real usage analysis: {e}")
            return {}

    def _process_inventory_data(self, export_data: List[Dict], inventory_data: Dict, warehouse_type: str, unit_price: float):
        """Xử lý dữ liệu tồn kho từ inventory manager"""
        try:
            if isinstance(inventory_data, dict):
                # Handle different data structures from inventory manager
                if 'items' in inventory_data:
                    # Structure: {'items': [{'name': ..., 'quantity': ..., 'unit': ...}, ...]}
                    for item in inventory_data.get('items', []):
                        self._add_inventory_item(export_data, item, warehouse_type, unit_price)
                elif 'inventory' in inventory_data:
                    # Structure: {'inventory': {'item_name': quantity, ...}}
                    for item_name, quantity in inventory_data.get('inventory', {}).items():
                        item_data = {'name': item_name, 'quantity': quantity}
                        self._add_inventory_item(export_data, item_data, warehouse_type, unit_price)
                else:
                    # Simple structure: {'item_name': quantity, ...}
                    for item_name, quantity in inventory_data.items():
                        item_data = {'name': item_name, 'quantity': quantity}
                        self._add_inventory_item(export_data, item_data, warehouse_type, unit_price)
            elif isinstance(inventory_data, list):
                # Handle list of items
                for item in inventory_data:
                    self._add_inventory_item(export_data, item, warehouse_type, unit_price)

        except Exception as e:
            print(f"Error processing inventory data: {e}")

    def _add_inventory_item(self, export_data: List[Dict], item_data: Dict, warehouse_type: str, unit_price: float):
        """Thêm một item tồn kho vào export data"""
        try:
            # Extract item information with fallbacks
            item_name = item_data.get('name', item_data.get('item_name', 'Unknown'))
            quantity = float(item_data.get('quantity', item_data.get('amount', 0)))
            unit = item_data.get('unit', 'kg')

            # Get additional info if available
            supplier = item_data.get('supplier', item_data.get('nha_cung_cap', ''))
            batch_number = item_data.get('batch_number', item_data.get('so_lo', ''))
            expiry_date = item_data.get('expiry_date', item_data.get('han_su_dung', ''))

            # Get stock status
            status = self._get_stock_status_from_item(item_data, quantity)

            # Calculate estimated value
            estimated_value = quantity * unit_price

            export_data.append({
                'Loại Kho': warehouse_type,
                'Tên Nguyên Liệu': item_name,
                'Số Lượng': quantity,
                'Đơn Vị': unit,
                'Trạng Thái': status,
                'Nhà Cung Cấp': supplier,
                'Số Lô': batch_number,
                'Hạn Sử Dụng': expiry_date,
                'Giá Trị Ước Tính': estimated_value,
                'Ngày Cập Nhật': datetime.now().strftime("%d/%m/%Y %H:%M")
            })

        except Exception as e:
            print(f"Error adding inventory item: {e}")

    def _get_stock_status_from_item(self, item_data: Dict, quantity: float) -> str:
        """Lấy trạng thái tồn kho từ item data hoặc tính toán"""
        try:
            # Check if status is already provided
            if 'status' in item_data:
                return item_data['status']
            if 'trang_thai' in item_data:
                return item_data['trang_thai']

            # Use threshold manager if available
            if self.threshold_manager:
                item_name = item_data.get('name', item_data.get('item_name', ''))
                return self.threshold_manager.get_stock_status(item_name, quantity)

            # Fallback to simple quantity-based status
            return self._get_stock_status(quantity)

        except Exception as e:
            print(f"Error getting stock status: {e}")
            return self._get_stock_status(quantity)

    def _process_formula_data(self, export_data: List[Dict], formula_data: Dict, inventory_data: Dict, formula_type: str):
        """Xử lý dữ liệu công thức từ formula manager"""
        try:
            if isinstance(formula_data, dict):
                # Handle different formula data structures
                if 'ingredients' in formula_data:
                    # Structure: {'ingredients': [{'name': ..., 'percentage': ...}, ...]}
                    for ingredient in formula_data.get('ingredients', []):
                        self._add_formula_ingredient(export_data, ingredient, inventory_data, formula_type)
                elif 'formula' in formula_data:
                    # Structure: {'formula': {'ingredient_name': percentage, ...}}
                    for ingredient_name, percentage in formula_data.get('formula', {}).items():
                        ingredient_data = {'name': ingredient_name, 'percentage': percentage}
                        self._add_formula_ingredient(export_data, ingredient_data, inventory_data, formula_type)
                else:
                    # Simple structure: {'ingredient_name': percentage, ...}
                    for ingredient_name, percentage in formula_data.items():
                        ingredient_data = {'name': ingredient_name, 'percentage': percentage}
                        self._add_formula_ingredient(export_data, ingredient_data, inventory_data, formula_type)
            elif isinstance(formula_data, list):
                # Handle list of ingredients
                for ingredient in formula_data:
                    self._add_formula_ingredient(export_data, ingredient, inventory_data, formula_type)

        except Exception as e:
            print(f"Error processing formula data: {e}")

    def _add_formula_ingredient(self, export_data: List[Dict], ingredient_data: Dict, inventory_data: Dict, formula_type: str):
        """Thêm một ingredient công thức vào export data"""
        try:
            # Extract ingredient information
            ingredient_name = ingredient_data.get('name', ingredient_data.get('ingredient_name', 'Unknown'))
            percentage = float(ingredient_data.get('percentage', ingredient_data.get('ratio', 0)))

            # Get current stock from inventory
            current_stock = self._get_ingredient_stock(ingredient_name, inventory_data)

            # Calculate usage and production capacity
            usage_per_batch = (percentage / 100) * 1000  # For 1000kg batch
            possible_batches = int(current_stock / usage_per_batch) if usage_per_batch > 0 else 0

            # Get additional info if available
            nutritional_value = ingredient_data.get('nutritional_value', ingredient_data.get('gia_tri_dinh_duong', ''))
            function = ingredient_data.get('function', ingredient_data.get('chuc_nang', ''))

            # Determine ingredient category
            category = self._categorize_ingredient(ingredient_name, percentage)

            export_data.append({
                'Loại Công Thức': formula_type,
                'Nguyên Liệu': ingredient_name,
                'Tỷ Lệ (%)': percentage,
                'Khối Lượng/1000kg': round(usage_per_batch, 2),
                'Tồn Kho Hiện Tại (kg)': current_stock,
                'Số Lô Có Thể Sản Xuất': possible_batches,
                'Trạng Thái Nguyên Liệu': self._get_stock_status(current_stock),
                'Giá Trị Dinh Dưỡng': nutritional_value,
                'Chức Năng': function,
                'Ghi Chú': category
            })

        except Exception as e:
            print(f"Error adding formula ingredient: {e}")

    def _get_ingredient_stock(self, ingredient_name: str, inventory_data: Dict) -> float:
        """Lấy số lượng tồn kho của nguyên liệu"""
        try:
            if isinstance(inventory_data, dict):
                # Handle different inventory structures
                if 'items' in inventory_data:
                    for item in inventory_data.get('items', []):
                        if item.get('name', '') == ingredient_name:
                            return float(item.get('quantity', 0))
                elif 'inventory' in inventory_data:
                    return float(inventory_data.get('inventory', {}).get(ingredient_name, 0))
                else:
                    return float(inventory_data.get(ingredient_name, 0))
            return 0.0
        except Exception as e:
            print(f"Error getting ingredient stock: {e}")
            return 0.0

    def _categorize_ingredient(self, ingredient_name: str, percentage: float) -> str:
        """Phân loại nguyên liệu dựa trên tên và tỷ lệ"""
        try:
            ingredient_lower = ingredient_name.lower()

            if percentage >= 20:
                return 'Nguyên liệu chính'
            elif 'vitamin' in ingredient_lower or 'khoang' in ingredient_lower:
                return 'Vitamin/Khoáng chất'
            elif 'enzyme' in ingredient_lower or 'men' in ingredient_lower:
                return 'Enzyme/Men vi sinh'
            elif percentage < 1:
                return 'Vi lượng'
            else:
                return 'Nguyên liệu phụ'

        except Exception as e:
            print(f"Error categorizing ingredient: {e}")
            return 'Nguyên liệu phụ'

    def _load_json_cached(self, file_path: Path) -> Dict:
        """Tải JSON với caching để tăng hiệu suất"""
        cache_key = str(file_path)
        current_time = time.time()

        with self._cache_lock:
            # Check cache
            if cache_key in self._data_cache:
                cached_data, cache_time = self._data_cache[cache_key]
                if current_time - cache_time < self._cache_timeout:
                    return cached_data

            # Load from file
            try:
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        self._data_cache[cache_key] = (data, current_time)
                        return data
            except Exception as e:
                print(f"Error loading {file_path}: {e}")

            return {}

    def _clear_cache(self):
        """Xóa cache khi cần"""
        with self._cache_lock:
            self._data_cache.clear()

    def _ensure_sample_data(self):
        """Tạo dữ liệu mẫu với nhiều items hơn để test performance"""
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Enhanced sample data for performance testing
        feed_inventory_file = self.config_dir / "feed_inventory.json"
        if not feed_inventory_file.exists() or self._is_file_empty(feed_inventory_file):
            sample_feed = {
                "Bắp nghiền": 1500.0, "Cám gạo": 800.0, "Đậu nành": 1200.0,
                "Dầu đậu nành": 150.0, "Cám lúa mì": 600.0, "Khô dừa": 300.0,
                "Bột cá": 250.0, "Tấm gạo": 400.0, "Rỉ mật": 180.0,
                "Bột xương": 120.0, "Cám mì": 350.0, "Ngô vàng": 900.0,
                "Đậu xanh": 200.0, "Lúa mì": 750.0, "Yến mạch": 180.0
            }
            self._save_json(feed_inventory_file, sample_feed)

        mix_inventory_file = self.config_dir / "mix_inventory.json"
        if not mix_inventory_file.exists() or self._is_file_empty(mix_inventory_file):
            sample_mix = {
                "Lysine": 75.0, "Methionine": 45.0, "Choline": 60.0,
                "Đá vôi": 300.0, "Vitamin premix": 25.0, "Mineral premix": 35.0,
                "Threonine": 20.0, "Tryptophan": 15.0, "Valine": 18.0,
                "Phytase": 12.0, "Xylanase": 8.0, "Protease": 10.0,
                "Antioxidant": 5.0, "Acidifier": 22.0, "Probiotic": 30.0
            }
            self._save_json(mix_inventory_file, sample_mix)

        # Enhanced formulas
        feed_formula_file = self.config_dir / "feed_formula.json"
        if not feed_formula_file.exists():
            sample_feed_formula = {
                "Bắp nghiền": 35.0, "Cám gạo": 15.0, "Đậu nành": 20.0,
                "Dầu đậu nành": 3.0, "Cám lúa mì": 12.0, "Khô dừa": 5.0,
                "Bột cá": 4.0, "Tấm gạo": 3.0, "Nguyên liệu tổ hợp": 3.0
            }
            self._save_json(feed_formula_file, sample_feed_formula)

        mix_formula_file = self.config_dir / "mix_formula.json"
        if not mix_formula_file.exists():
            sample_mix_formula = {
                "Lysine": 25.0, "Methionine": 15.0, "Choline": 12.0,
                "Đá vôi": 20.0, "Vitamin premix": 10.0, "Mineral premix": 8.0,
                "Threonine": 5.0, "Tryptophan": 3.0, "Phytase": 2.0
            }
            self._save_json(mix_formula_file, sample_mix_formula)

    def _is_file_empty(self, file_path: Path) -> bool:
        """Kiểm tra file có rỗng không"""
        try:
            if file_path.stat().st_size == 0:
                return True
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return not data or len(data) == 0
        except:
            return True

    def _save_json(self, file_path: Path, data: Dict):
        """Lưu dữ liệu JSON"""
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error saving {file_path}: {e}")

    def _get_stock_status(self, quantity: float) -> str:
        """Xác định trạng thái tồn kho với logic cải tiến"""
        if quantity <= 0:
            return "Hết hàng"
        elif quantity < 50:
            return "Sắp hết"
        elif quantity < 200:
            return "Ít"
        else:
            return "Đủ"

    def _generate_filename(self, report_type: str, options: Dict = None) -> str:
        """Tạo tên file với thông tin chi tiết hơn"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if options:
            suffix_parts = []
            if options.get('include_feed', False):
                suffix_parts.append('cam')
            if options.get('include_mix', False):
                suffix_parts.append('mix')

            if suffix_parts:
                suffix = '_' + '_'.join(suffix_parts)
            else:
                suffix = ''
        else:
            suffix = ''

        return f"{report_type}_{timestamp}{suffix}.xlsx"

    def _apply_advanced_formatting(self, worksheet, data_range: str, report_type: str):
        """Áp dụng formatting nâng cao cho worksheet"""
        # Apply header style
        for cell in worksheet[1]:
            cell.style = self.style_manager.header_style

        # Apply data styles with conditional formatting
        for row in worksheet.iter_rows(min_row=2, max_row=worksheet.max_row):
            for cell in row:
                if cell.column == worksheet.max_column and report_type == "inventory":
                    # Status column - apply conditional formatting
                    status = str(cell.value)
                    cell.fill = self.style_manager.get_status_fill(status)

                # Apply appropriate style based on data type
                if isinstance(cell.value, (int, float)):
                    cell.style = self.style_manager.number_style
                else:
                    cell.style = self.style_manager.data_style

        # Auto-adjust column widths (optimized)
        self._optimize_column_widths(worksheet)

        # Add alternating row colors
        self._add_alternating_rows(worksheet)

    def _optimize_column_widths(self, worksheet):
        """Tối ưu hóa độ rộng cột với algorithm hiệu quả hơn"""
        column_widths = {}

        # Calculate optimal widths in one pass
        for row in worksheet.iter_rows():
            for cell in row:
                column_letter = cell.column_letter
                if column_letter not in column_widths:
                    column_widths[column_letter] = 0

                try:
                    cell_length = len(str(cell.value))
                    if cell_length > column_widths[column_letter]:
                        column_widths[column_letter] = cell_length
                except:
                    pass

        # Apply widths
        for column_letter, width in column_widths.items():
            adjusted_width = min(max(width + 2, 10), 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width

    def _add_alternating_rows(self, worksheet):
        """Thêm màu xen kẽ cho các hàng"""
        light_fill = PatternFill(start_color='F2F2F2', end_color='F2F2F2', fill_type='solid')

        for row_num in range(3, worksheet.max_row + 1, 2):  # Start from row 3, every other row
            for cell in worksheet[row_num]:
                if not cell.fill.start_color.rgb or cell.fill.start_color.rgb == '00000000':
                    cell.fill = light_fill

    def _add_summary_section(self, worksheet, data: List[Dict], report_type: str):
        """Thêm phần tóm tắt vào worksheet"""
        # Add summary after data
        summary_start_row = worksheet.max_row + 3

        # Summary header
        summary_cell = worksheet.cell(row=summary_start_row, column=1, value="TỔNG KẾT")
        summary_cell.font = Font(name='Arial', size=14, bold=True, color='366092')

        if report_type == "inventory":
            # Inventory summary
            total_items = len(data)
            total_quantity = sum(item.get('Số Lượng (kg)', 0) for item in data)

            status_counts = {}
            for item in data:
                status = item.get('Trạng Thái', 'Unknown')
                status_counts[status] = status_counts.get(status, 0) + 1

            # Add summary data
            worksheet.cell(row=summary_start_row + 1, column=1, value=f"Tổng số mục: {total_items}")
            worksheet.cell(row=summary_start_row + 2, column=1, value=f"Tổng khối lượng: {total_quantity:,.2f} kg")

            row_offset = 3
            for status, count in status_counts.items():
                worksheet.cell(row=summary_start_row + row_offset, column=1, value=f"{status}: {count} mục")
                row_offset += 1

        elif report_type == "formula":
            # Formula summary
            total_ingredients = len(data)
            total_percentage = sum(item.get('Tỷ Lệ (%)', 0) for item in data)

            worksheet.cell(row=summary_start_row + 1, column=1, value=f"Tổng số nguyên liệu: {total_ingredients}")
            worksheet.cell(row=summary_start_row + 2, column=1, value=f"Tổng tỷ lệ: {total_percentage:.1f}%")

    def export_inventory_report_optimized(self, include_feed: bool = True, include_mix: bool = True,
                                        progress_callback=None) -> Tuple[bool, str]:
        """Xuất báo cáo tồn kho được tối ưu hóa"""
        try:
            start_time = time.time()

            if not include_feed and not include_mix:
                return False, "Vui lòng chọn ít nhất một loại kho để xuất"

            if progress_callback:
                progress_callback(10, "Đang tải dữ liệu...")

            # Load real data from data managers
            feed_data = {}
            mix_data = {}

            if include_feed:
                feed_data = self._get_real_inventory_data("feed")

            if include_mix:
                mix_data = self._get_real_inventory_data("mix")

            if progress_callback:
                progress_callback(30, "Đang xử lý dữ liệu...")

            # Process data efficiently
            export_data = []

            # Process feed data from real inventory manager
            if include_feed and feed_data:
                self._process_inventory_data(export_data, feed_data, 'Kho Cám', 15000)

            # Process mix data from real inventory manager
            if include_mix and mix_data:
                self._process_inventory_data(export_data, mix_data, 'Kho Mix', 25000)

            if not export_data:
                return False, "Không có dữ liệu tồn kho để xuất"

            if progress_callback:
                progress_callback(50, "Đang tạo file Excel...")

            # Generate filename with options
            options = {'include_feed': include_feed, 'include_mix': include_mix}
            filename = self._generate_filename("bao_cao_ton_kho_toi_uu", options)
            file_path = self.exports_dir / filename

            # Create Excel with advanced formatting
            workbook = Workbook()
            worksheet = workbook.active
            worksheet.title = "Báo Cáo Tồn Kho"

            # Add data to worksheet
            df = pd.DataFrame(export_data)
            for r in dataframe_to_rows(df, index=False, header=True):
                worksheet.append(r)

            if progress_callback:
                progress_callback(70, "Đang định dạng Excel...")

            # Apply advanced formatting
            self._apply_advanced_formatting(worksheet, f"A1:F{len(export_data)+1}", "inventory")

            # Add summary section
            self._add_summary_section(worksheet, export_data, "inventory")

            if progress_callback:
                progress_callback(90, "Đang lưu file...")

            # Save workbook
            workbook.save(file_path)

            end_time = time.time()
            processing_time = round(end_time - start_time, 2)

            return True, f"Xuất báo cáo tồn kho tối ưu thành công!\nFile: {filename}\nVị trí: {file_path}\nSố mục: {len(export_data)}\nThời gian xử lý: {processing_time}s"

        except Exception as e:
            return False, f"Lỗi xuất báo cáo tồn kho: {str(e)}"

    def export_formula_report_optimized(self, include_feed: bool = True, include_mix: bool = True,
                                      progress_callback=None) -> Tuple[bool, str]:
        """Xuất báo cáo công thức được tối ưu hóa"""
        try:
            start_time = time.time()

            if not include_feed and not include_mix:
                return False, "Vui lòng chọn ít nhất một loại công thức để xuất"

            if progress_callback:
                progress_callback(10, "Đang tải công thức...")

            # Load real formula data from formula manager
            feed_formula = {}
            mix_formula = {}

            if include_feed:
                feed_formula = self._get_real_formula_data("feed")

            if include_mix:
                mix_formula = self._get_real_formula_data("mix")

            if progress_callback:
                progress_callback(30, "Đang tải dữ liệu tồn kho...")

            # Load real inventory data for availability check
            feed_inventory = self._get_real_inventory_data("feed") if include_feed else {}
            mix_inventory = self._get_real_inventory_data("mix") if include_mix else {}

            if progress_callback:
                progress_callback(50, "Đang xử lý dữ liệu công thức...")

            export_data = []

            # Process feed formula
            if include_feed and feed_formula:
                for ingredient, percentage in feed_formula.items():
                    current_stock = feed_inventory.get(ingredient, 0)
                    usage_per_batch = (percentage / 100) * 1000  # For 1000kg batch
                    possible_batches = int(current_stock / usage_per_batch) if usage_per_batch > 0 else 0

                    export_data.append({
                        'Loại Công Thức': 'Công Thức Cám',
                        'Nguyên Liệu': ingredient,
                        'Tỷ Lệ (%)': percentage,
                        'Khối Lượng/1000kg': round(usage_per_batch, 2),
                        'Tồn Kho Hiện Tại (kg)': current_stock,
                        'Số Lô Có Thể Sản Xuất': possible_batches,
                        'Trạng Thái Nguyên Liệu': self._get_stock_status(current_stock),
                        'Ghi Chú': 'Nguyên liệu chính' if percentage >= 20 else 'Nguyên liệu phụ'
                    })

            # Process mix formula
            if include_mix and mix_formula:
                for ingredient, percentage in mix_formula.items():
                    current_stock = mix_inventory.get(ingredient, 0)
                    usage_per_batch = (percentage / 100) * 1000
                    possible_batches = int(current_stock / usage_per_batch) if usage_per_batch > 0 else 0

                    export_data.append({
                        'Loại Công Thức': 'Công Thức Mix',
                        'Nguyên Liệu': ingredient,
                        'Tỷ Lệ (%)': percentage,
                        'Khối Lượng/1000kg': round(usage_per_batch, 2),
                        'Tồn Kho Hiện Tại (kg)': current_stock,
                        'Số Lô Có Thể Sản Xuất': possible_batches,
                        'Trạng Thái Nguyên Liệu': self._get_stock_status(current_stock),
                        'Ghi Chú': 'Nguyên liệu chính' if percentage >= 20 else 'Nguyên liệu phụ'
                    })

            if not export_data:
                return False, "Không có dữ liệu công thức để xuất"

            if progress_callback:
                progress_callback(70, "Đang tạo file Excel...")

            # Generate filename
            options = {'include_feed': include_feed, 'include_mix': include_mix}
            filename = self._generate_filename("bao_cao_cong_thuc_toi_uu", options)
            file_path = self.exports_dir / filename

            # Create Excel with advanced formatting
            workbook = Workbook()
            worksheet = workbook.active
            worksheet.title = "Báo Cáo Công Thức"

            # Add data
            df = pd.DataFrame(export_data)
            for r in dataframe_to_rows(df, index=False, header=True):
                worksheet.append(r)

            if progress_callback:
                progress_callback(85, "Đang định dạng Excel...")

            # Apply advanced formatting
            self._apply_advanced_formatting(worksheet, f"A1:H{len(export_data)+1}", "formula")

            # Add summary section
            self._add_summary_section(worksheet, export_data, "formula")

            # Add production capacity analysis
            self._add_production_analysis(worksheet, export_data)

            if progress_callback:
                progress_callback(95, "Đang lưu file...")

            workbook.save(file_path)

            end_time = time.time()
            processing_time = round(end_time - start_time, 2)

            return True, f"Xuất báo cáo công thức tối ưu thành công!\nFile: {filename}\nVị trí: {file_path}\nSố mục: {len(export_data)}\nThời gian xử lý: {processing_time}s"

        except Exception as e:
            return False, f"Lỗi xuất báo cáo công thức: {str(e)}"

    def _add_production_analysis(self, worksheet, data: List[Dict]):
        """Thêm phân tích khả năng sản xuất"""
        analysis_start_row = worksheet.max_row + 2

        # Analysis header
        analysis_cell = worksheet.cell(row=analysis_start_row, column=1, value="PHÂN TÍCH KHẢ NĂNG SẢN XUẤT")
        analysis_cell.font = Font(name='Arial', size=12, bold=True, color='D35400')

        # Calculate minimum production capacity
        min_batches = float('inf')
        limiting_ingredient = ""

        for item in data:
            batches = item.get('Số Lô Có Thể Sản Xuất', 0)
            if batches < min_batches:
                min_batches = batches
                limiting_ingredient = item.get('Nguyên Liệu', '')

        if min_batches == float('inf'):
            min_batches = 0

        worksheet.cell(row=analysis_start_row + 1, column=1,
                      value=f"Số lô tối đa có thể sản xuất: {min_batches}")
        worksheet.cell(row=analysis_start_row + 2, column=1,
                      value=f"Nguyên liệu hạn chế: {limiting_ingredient}")
        worksheet.cell(row=analysis_start_row + 3, column=1,
                      value=f"Khối lượng tối đa: {min_batches * 1000:,.0f} kg")

    def export_summary_report_optimized(self, progress_callback=None) -> Tuple[bool, str]:
        """Xuất báo cáo tổng hợp được tối ưu hóa"""
        try:
            start_time = time.time()

            if progress_callback:
                progress_callback(10, "Đang tải tất cả dữ liệu...")

            # Load all data concurrently
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = {
                    'feed_inventory': executor.submit(self._load_json_cached, self.config_dir / "feed_inventory.json"),
                    'mix_inventory': executor.submit(self._load_json_cached, self.config_dir / "mix_inventory.json"),
                    'feed_formula': executor.submit(self._load_json_cached, self.config_dir / "feed_formula.json"),
                    'mix_formula': executor.submit(self._load_json_cached, self.config_dir / "mix_formula.json")
                }

                # Collect results
                results = {key: future.result() for key, future in futures.items()}

            if progress_callback:
                progress_callback(40, "Đang tính toán thống kê...")

            # Calculate comprehensive statistics
            summary_data = []

            # Inventory statistics
            feed_items = len(results['feed_inventory'])
            feed_quantity = sum(results['feed_inventory'].values())
            feed_value = feed_quantity * 15000

            mix_items = len(results['mix_inventory'])
            mix_quantity = sum(results['mix_inventory'].values())
            mix_value = mix_quantity * 25000

            # Status distribution
            feed_status_dist = self._calculate_status_distribution(results['feed_inventory'])
            mix_status_dist = self._calculate_status_distribution(results['mix_inventory'])

            # Add comprehensive summary data
            summary_data.extend([
                {'Loại Thống Kê': 'Tồn Kho Cám', 'Số Mục': feed_items, 'Tổng Khối Lượng (kg)': feed_quantity,
                 'Giá Trị Ước Tính (VND)': feed_value, 'Ghi Chú': 'Nguyên liệu thô'},
                {'Loại Thống Kê': 'Tồn Kho Mix', 'Số Mục': mix_items, 'Tổng Khối Lượng (kg)': mix_quantity,
                 'Giá Trị Ước Tính (VND)': mix_value, 'Ghi Chú': 'Phụ gia dinh dưỡng'},
                {'Loại Thống Kê': 'Công Thức Cám', 'Số Mục': len(results['feed_formula']),
                 'Tổng Khối Lượng (kg)': sum(results['feed_formula'].values()), 'Giá Trị Ước Tính (VND)': 0,
                 'Ghi Chú': 'Tỷ lệ phần trăm'},
                {'Loại Thống Kê': 'Công Thức Mix', 'Số Mục': len(results['mix_formula']),
                 'Tổng Khối Lượng (kg)': sum(results['mix_formula'].values()), 'Giá Trị Ước Tính (VND)': 0,
                 'Ghi Chú': 'Tỷ lệ phần trăm'}
            ])

            if progress_callback:
                progress_callback(70, "Đang tạo file Excel...")

            filename = self._generate_filename("bao_cao_tong_hop_toi_uu")
            file_path = self.exports_dir / filename

            # Create comprehensive Excel report
            workbook = Workbook()

            # Main summary sheet
            summary_sheet = workbook.active
            summary_sheet.title = "Tổng Quan"

            df = pd.DataFrame(summary_data)
            for r in dataframe_to_rows(df, index=False, header=True):
                summary_sheet.append(r)

            self._apply_advanced_formatting(summary_sheet, f"A1:E{len(summary_data)+1}", "summary")

            # Add detailed status analysis
            self._add_detailed_status_analysis(workbook, feed_status_dist, mix_status_dist)

            if progress_callback:
                progress_callback(90, "Đang hoàn tất...")

            workbook.save(file_path)

            end_time = time.time()
            processing_time = round(end_time - start_time, 2)

            return True, f"Xuất báo cáo tổng hợp tối ưu thành công!\nFile: {filename}\nVị trí: {file_path}\nThời gian xử lý: {processing_time}s"

        except Exception as e:
            return False, f"Lỗi xuất báo cáo tổng hợp: {str(e)}"

    def _calculate_status_distribution(self, inventory_data: Dict) -> Dict:
        """Tính phân bố trạng thái tồn kho"""
        status_dist = {'Đủ': 0, 'Ít': 0, 'Sắp hết': 0, 'Hết hàng': 0}

        for quantity in inventory_data.values():
            status = self._get_stock_status(quantity)
            status_dist[status] += 1

        return status_dist

    def _add_detailed_status_analysis(self, workbook, feed_status: Dict, mix_status: Dict):
        """Thêm sheet phân tích trạng thái chi tiết"""
        status_sheet = workbook.create_sheet("Phân Tích Trạng Thái")

        # Headers
        status_sheet.append(['Loại Kho', 'Trạng Thái', 'Số Lượng Mục', 'Tỷ Lệ (%)'])

        # Feed status data
        total_feed = sum(feed_status.values())
        for status, count in feed_status.items():
            percentage = (count / total_feed * 100) if total_feed > 0 else 0
            status_sheet.append(['Kho Cám', status, count, round(percentage, 1)])

        # Mix status data
        total_mix = sum(mix_status.values())
        for status, count in mix_status.items():
            percentage = (count / total_mix * 100) if total_mix > 0 else 0
            status_sheet.append(['Kho Mix', status, count, round(percentage, 1)])

        # Apply formatting
        self._apply_advanced_formatting(status_sheet, f"A1:D{status_sheet.max_row}", "status")

    def get_export_directory(self) -> str:
        """Lấy đường dẫn thư mục xuất"""
        return str(self.exports_dir.absolute())

    def list_exported_files(self) -> List[str]:
        """Liệt kê các file đã xuất"""
        try:
            excel_files = list(self.exports_dir.glob("*.xlsx"))
            return [f.name for f in sorted(excel_files, key=lambda x: x.stat().st_mtime, reverse=True)]
        except:
            return []

    def clear_cache(self):
        """Xóa cache để refresh dữ liệu"""
        self._clear_cache()

    def _ensure_daily_consumption_data(self):
        """Đảm bảo có dữ liệu tiêu thụ hàng ngày"""
        try:
            # Kiểm tra xem có file dữ liệu nào không
            daily_files = list(self.daily_consumption_dir.glob("daily_consumption_*.json"))

            if not daily_files:
                # Tạo dữ liệu mẫu nếu chưa có
                from src.data.daily_consumption_data import DailyConsumptionDataGenerator
                generator = DailyConsumptionDataGenerator()
                generator.save_sample_data(30)
                print("Đã tạo dữ liệu tiêu thụ hàng ngày mẫu")
        except Exception as e:
            print(f"Lỗi tạo dữ liệu tiêu thụ hàng ngày: {e}")

    def _load_daily_consumption_data(self, start_date: datetime, end_date: datetime) -> Dict:
        """Tải dữ liệu tiêu thụ hàng ngày trong khoảng thời gian"""
        daily_data = {}

        # Tạo danh sách các tháng cần tải
        current_date = start_date.replace(day=1)  # Đầu tháng
        end_month = end_date.replace(day=1)

        while current_date <= end_month:
            month_key = current_date.strftime("%Y-%m")
            file_path = self.daily_consumption_dir / f"daily_consumption_{month_key}.json"

            if file_path.exists():
                try:
                    month_data = self._load_json_cached(file_path)

                    # Lọc dữ liệu theo khoảng thời gian
                    for date_str, day_data in month_data.items():
                        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                        if start_date <= date_obj <= end_date:
                            daily_data[date_str] = day_data

                except Exception as e:
                    print(f"Lỗi tải dữ liệu tháng {month_key}: {e}")

            # Chuyển sang tháng tiếp theo
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)

        return daily_data

    def export_daily_regional_report(self, start_date: datetime, end_date: datetime,
                                   selected_regions: List[str] = None,
                                   include_feed: bool = True, include_mix: bool = True,
                                   progress_callback=None) -> Tuple[bool, str]:
        """Xuất báo cáo tiêu thụ hàng ngày theo khu vực"""
        try:
            start_time = time.time()

            if progress_callback:
                progress_callback(10, "Đang tải dữ liệu tiêu thụ hàng ngày...")

            # Tải dữ liệu tiêu thụ
            daily_data = self._load_daily_consumption_data(start_date, end_date)

            if not daily_data:
                return False, "Không có dữ liệu tiêu thụ trong khoảng thời gian đã chọn"

            if progress_callback:
                progress_callback(30, "Đang xử lý dữ liệu theo khu vực...")

            # Xử lý dữ liệu theo khu vực
            processed_data = self._process_regional_data(daily_data, selected_regions, include_feed, include_mix)

            if progress_callback:
                progress_callback(50, "Đang tạo file Excel...")

            # Tạo filename
            date_range = f"{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}"
            regions_suffix = "_".join(selected_regions) if selected_regions else "all_regions"
            filename = f"bao_cao_hang_ngay_{date_range}_{regions_suffix}.xlsx"
            file_path = self.exports_dir / filename

            # Tạo Excel với multiple sheets
            workbook = Workbook()

            # Sheet tổng quan
            self._create_daily_overview_sheet(workbook, processed_data, start_date, end_date)

            if progress_callback:
                progress_callback(70, "Đang tạo sheet chi tiết...")

            # Sheet chi tiết theo khu vực
            if selected_regions:
                for region_id in selected_regions:
                    if region_id in processed_data['regions']:
                        self._create_regional_detail_sheet(workbook, region_id, processed_data['regions'][region_id])

            # Sheet phân tích xu hướng
            self._create_trend_analysis_sheet(workbook, processed_data)

            if progress_callback:
                progress_callback(90, "Đang lưu file...")

            workbook.save(file_path)

            end_time = time.time()
            processing_time = round(end_time - start_time, 2)

            return True, f"Xuất báo cáo hàng ngày thành công!\nFile: {filename}\nVị trí: {file_path}\nSố ngày: {len(daily_data)}\nThời gian xử lý: {processing_time}s"

        except Exception as e:
            return False, f"Lỗi xuất báo cáo hàng ngày: {str(e)}"

    def export_feed_component_report(self, start_date: datetime, end_date: datetime,
                                   selected_regions: List[str] = None,
                                   progress_callback=None) -> Tuple[bool, str]:
        """Xuất báo cáo chi tiết thành phần cám"""
        try:
            start_time = time.time()

            if progress_callback:
                progress_callback(10, "Đang tải dữ liệu thành phần cám...")

            daily_data = self._load_daily_consumption_data(start_date, end_date)

            if not daily_data:
                return False, "Không có dữ liệu thành phần cám trong khoảng thời gian đã chọn"

            if progress_callback:
                progress_callback(40, "Đang phân tích thành phần cám...")

            # Xử lý dữ liệu thành phần cám
            feed_analysis = self._analyze_feed_components(daily_data, selected_regions)

            if progress_callback:
                progress_callback(60, "Đang tạo báo cáo Excel...")

            # Tạo filename
            date_range = f"{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}"
            regions_suffix = "_".join(selected_regions) if selected_regions else "all_regions"
            filename = f"bao_cao_thanh_phan_cam_{date_range}_{regions_suffix}.xlsx"
            file_path = self.exports_dir / filename

            # Tạo Excel với phân tích chi tiết
            workbook = Workbook()

            # Sheet tổng quan thành phần
            self._create_feed_component_overview_sheet(workbook, feed_analysis)

            # Sheet xu hướng tiêu thụ
            self._create_feed_consumption_trend_sheet(workbook, feed_analysis)

            # Sheet so sánh với công thức chuẩn
            self._create_feed_formula_comparison_sheet(workbook, feed_analysis)

            if progress_callback:
                progress_callback(90, "Đang lưu file...")

            workbook.save(file_path)

            end_time = time.time()
            processing_time = round(end_time - start_time, 2)

            return True, f"Xuất báo cáo thành phần cám thành công!\nFile: {filename}\nVị trí: {file_path}\nThời gian xử lý: {processing_time}s"

        except Exception as e:
            return False, f"Lỗi xuất báo cáo thành phần cám: {str(e)}"

    def export_mix_component_report(self, start_date: datetime, end_date: datetime,
                                  selected_regions: List[str] = None,
                                  progress_callback=None) -> Tuple[bool, str]:
        """Xuất báo cáo chi tiết thành phần mix"""
        try:
            start_time = time.time()

            if progress_callback:
                progress_callback(10, "Đang tải dữ liệu thành phần mix...")

            daily_data = self._load_daily_consumption_data(start_date, end_date)

            if not daily_data:
                return False, "Không có dữ liệu thành phần mix trong khoảng thời gian đã chọn"

            if progress_callback:
                progress_callback(40, "Đang phân tích thành phần mix...")

            # Xử lý dữ liệu thành phần mix
            mix_analysis = self._analyze_mix_components(daily_data, selected_regions)

            if progress_callback:
                progress_callback(60, "Đang tạo báo cáo Excel...")

            # Tạo filename
            date_range = f"{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}"
            regions_suffix = "_".join(selected_regions) if selected_regions else "all_regions"
            filename = f"bao_cao_thanh_phan_mix_{date_range}_{regions_suffix}.xlsx"
            file_path = self.exports_dir / filename

            # Tạo Excel với phân tích chi tiết
            workbook = Workbook()

            # Sheet tổng quan thành phần
            self._create_mix_component_overview_sheet(workbook, mix_analysis)

            # Sheet xu hướng tiêu thụ
            self._create_mix_consumption_trend_sheet(workbook, mix_analysis)

            # Sheet phân tích hiệu quả
            self._create_mix_efficiency_analysis_sheet(workbook, mix_analysis)

            if progress_callback:
                progress_callback(90, "Đang lưu file...")

            workbook.save(file_path)

            end_time = time.time()
            processing_time = round(end_time - start_time, 2)

            return True, f"Xuất báo cáo thành phần mix thành công!\nFile: {filename}\nVị trí: {file_path}\nThời gian xử lý: {processing_time}s"

        except Exception as e:
            return False, f"Lỗi xuất báo cáo thành phần mix: {str(e)}"

    def _process_regional_data(self, daily_data: Dict, selected_regions: List[str],
                             include_feed: bool, include_mix: bool) -> Dict:
        """Xử lý dữ liệu theo khu vực"""
        processed_data = {
            'summary': {
                'total_days': len(daily_data),
                'date_range': {
                    'start': min(daily_data.keys()),
                    'end': max(daily_data.keys())
                },
                'total_production': 0,
                'total_feed_consumption': {},
                'total_mix_consumption': {}
            },
            'regions': {},
            'daily_totals': {}
        }

        # Import region definitions
        try:
            from src.data.daily_consumption_data import REGIONS
        except ImportError:
            REGIONS = {
                "mien_bac": {"name": "Miền Bắc"},
                "mien_trung": {"name": "Miền Trung"},
                "mien_nam": {"name": "Miền Nam"}
            }

        # Xử lý từng ngày
        for date_str, day_data in daily_data.items():
            daily_total = {
                'date': date_str,
                'total_production': 0,
                'regions_production': {}
            }

            # Xử lý từng khu vực
            for region_id, region_data in day_data.get('regions', {}).items():
                if selected_regions and region_id not in selected_regions:
                    continue

                # Khởi tạo dữ liệu khu vực nếu chưa có
                if region_id not in processed_data['regions']:
                    processed_data['regions'][region_id] = {
                        'region_name': region_data.get('region_name', REGIONS.get(region_id, {}).get('name', region_id)),
                        'total_production': 0,
                        'daily_production': {},
                        'feed_consumption': {},
                        'mix_consumption': {},
                        'animal_distribution': {}
                    }

                region_production = region_data.get('total_production', 0)
                processed_data['regions'][region_id]['total_production'] += region_production
                processed_data['regions'][region_id]['daily_production'][date_str] = region_production

                daily_total['total_production'] += region_production
                daily_total['regions_production'][region_id] = region_production

                # Xử lý tiêu thụ cám
                if include_feed:
                    feed_consumption = region_data.get('feed_consumption', {})
                    for component, amount in feed_consumption.items():
                        if component not in processed_data['regions'][region_id]['feed_consumption']:
                            processed_data['regions'][region_id]['feed_consumption'][component] = 0
                        processed_data['regions'][region_id]['feed_consumption'][component] += amount

                        if component not in processed_data['summary']['total_feed_consumption']:
                            processed_data['summary']['total_feed_consumption'][component] = 0
                        processed_data['summary']['total_feed_consumption'][component] += amount

                # Xử lý tiêu thụ mix
                if include_mix:
                    mix_consumption = region_data.get('mix_consumption', {})
                    for component, amount in mix_consumption.items():
                        if component not in processed_data['regions'][region_id]['mix_consumption']:
                            processed_data['regions'][region_id]['mix_consumption'][component] = 0
                        processed_data['regions'][region_id]['mix_consumption'][component] += amount

                        if component not in processed_data['summary']['total_mix_consumption']:
                            processed_data['summary']['total_mix_consumption'][component] = 0
                        processed_data['summary']['total_mix_consumption'][component] += amount

            processed_data['daily_totals'][date_str] = daily_total
            processed_data['summary']['total_production'] += daily_total['total_production']

        return processed_data

    def _analyze_feed_components(self, daily_data: Dict, selected_regions: List[str]) -> Dict:
        """Phân tích chi tiết thành phần cám"""
        try:
            from src.data.daily_consumption_data import FEED_COMPONENTS, ANIMAL_TYPES
        except ImportError:
            FEED_COMPONENTS = {}
            ANIMAL_TYPES = {}

        analysis = {
            'components_summary': {},
            'daily_consumption': {},
            'regional_breakdown': {},
            'formula_comparison': {},
            'cost_analysis': {}
        }

        # Phân tích từng thành phần
        for date_str, day_data in daily_data.items():
            analysis['daily_consumption'][date_str] = {}

            for region_id, region_data in day_data.get('regions', {}).items():
                if selected_regions and region_id not in selected_regions:
                    continue

                feed_consumption = region_data.get('feed_consumption', {})

                for component, amount in feed_consumption.items():
                    # Tổng hợp theo thành phần
                    if component not in analysis['components_summary']:
                        analysis['components_summary'][component] = {
                            'total_consumption': 0,
                            'average_daily': 0,
                            'max_daily': 0,
                            'min_daily': float('inf'),
                            'component_info': FEED_COMPONENTS.get(component, {})
                        }

                    analysis['components_summary'][component]['total_consumption'] += amount

                    # Theo ngày
                    if component not in analysis['daily_consumption'][date_str]:
                        analysis['daily_consumption'][date_str][component] = 0
                    analysis['daily_consumption'][date_str][component] += amount

                    # Theo khu vực
                    if region_id not in analysis['regional_breakdown']:
                        analysis['regional_breakdown'][region_id] = {}
                    if component not in analysis['regional_breakdown'][region_id]:
                        analysis['regional_breakdown'][region_id][component] = 0
                    analysis['regional_breakdown'][region_id][component] += amount

        # Tính toán thống kê
        total_days = len(daily_data)
        for component, data in analysis['components_summary'].items():
            data['average_daily'] = data['total_consumption'] / total_days if total_days > 0 else 0

            # Tìm min/max daily
            daily_amounts = []
            for day_consumption in analysis['daily_consumption'].values():
                daily_amounts.append(day_consumption.get(component, 0))

            if daily_amounts:
                data['max_daily'] = max(daily_amounts)
                data['min_daily'] = min(daily_amounts)

            # Tính chi phí
            price_per_kg = data['component_info'].get('price_per_kg', 0)
            data['total_cost'] = data['total_consumption'] * price_per_kg
            data['average_daily_cost'] = data['average_daily'] * price_per_kg

        return analysis

    def _analyze_mix_components(self, daily_data: Dict, selected_regions: List[str]) -> Dict:
        """Phân tích chi tiết thành phần mix"""
        try:
            from src.data.daily_consumption_data import MIX_COMPONENTS
        except ImportError:
            MIX_COMPONENTS = {}

        analysis = {
            'components_summary': {},
            'daily_consumption': {},
            'regional_breakdown': {},
            'efficiency_analysis': {},
            'cost_analysis': {}
        }

        # Phân tích tương tự như feed components
        for date_str, day_data in daily_data.items():
            analysis['daily_consumption'][date_str] = {}

            for region_id, region_data in day_data.get('regions', {}).items():
                if selected_regions and region_id not in selected_regions:
                    continue

                mix_consumption = region_data.get('mix_consumption', {})

                for component, amount in mix_consumption.items():
                    # Tổng hợp theo thành phần
                    if component not in analysis['components_summary']:
                        analysis['components_summary'][component] = {
                            'total_consumption': 0,
                            'average_daily': 0,
                            'max_daily': 0,
                            'min_daily': float('inf'),
                            'component_info': MIX_COMPONENTS.get(component, {})
                        }

                    analysis['components_summary'][component]['total_consumption'] += amount

                    # Theo ngày
                    if component not in analysis['daily_consumption'][date_str]:
                        analysis['daily_consumption'][date_str][component] = 0
                    analysis['daily_consumption'][date_str][component] += amount

                    # Theo khu vực
                    if region_id not in analysis['regional_breakdown']:
                        analysis['regional_breakdown'][region_id] = {}
                    if component not in analysis['regional_breakdown'][region_id]:
                        analysis['regional_breakdown'][region_id][component] = 0
                    analysis['regional_breakdown'][region_id][component] += amount

        # Tính toán thống kê và hiệu quả
        total_days = len(daily_data)
        for component, data in analysis['components_summary'].items():
            data['average_daily'] = data['total_consumption'] / total_days if total_days > 0 else 0

            # Tìm min/max daily
            daily_amounts = []
            for day_consumption in analysis['daily_consumption'].values():
                daily_amounts.append(day_consumption.get(component, 0))

            if daily_amounts:
                data['max_daily'] = max(daily_amounts)
                data['min_daily'] = min(daily_amounts)

            # Tính chi phí
            price_per_kg = data['component_info'].get('price_per_kg', 0)
            data['total_cost'] = data['total_consumption'] * price_per_kg
            data['average_daily_cost'] = data['average_daily'] * price_per_kg

            # Phân tích hiệu quả (so với dosage range)
            dosage_range = data['component_info'].get('dosage_range', '')
            if dosage_range and '-' in dosage_range:
                try:
                    min_dosage, max_dosage = dosage_range.replace('%', '').split('-')
                    min_dosage = float(min_dosage)
                    max_dosage = float(max_dosage)

                    # Tính tỷ lệ sử dụng trung bình (giả định)
                    avg_usage_rate = (data['average_daily'] / 1000) * 100  # Giả định 1000kg/ngày

                    if avg_usage_rate < min_dosage:
                        data['efficiency_status'] = 'Dưới mức khuyến nghị'
                    elif avg_usage_rate > max_dosage:
                        data['efficiency_status'] = 'Vượt mức khuyến nghị'
                    else:
                        data['efficiency_status'] = 'Trong khoảng khuyến nghị'

                    data['usage_rate'] = round(avg_usage_rate, 3)
                except:
                    data['efficiency_status'] = 'Không xác định'

        return analysis

    def _create_daily_overview_sheet(self, workbook: Workbook, processed_data: Dict,
                                   start_date: datetime, end_date: datetime):
        """Tạo sheet tổng quan báo cáo hàng ngày"""
        # Remove default sheet and create overview
        if 'Sheet' in [ws.title for ws in workbook.worksheets]:
            workbook.remove(workbook['Sheet'])

        overview_sheet = workbook.create_sheet("Tổng Quan Hàng Ngày")

        # Header thông tin
        overview_sheet.append(['BÁO CÁO TIÊU THỤ HÀNG NGÀY'])
        overview_sheet.append([f'Từ ngày: {start_date.strftime("%d/%m/%Y")} - Đến ngày: {end_date.strftime("%d/%m/%Y")}'])
        overview_sheet.append([f'Tổng số ngày: {processed_data["summary"]["total_days"]}'])
        overview_sheet.append([])  # Empty row

        # Thống kê tổng quan
        overview_sheet.append(['THỐNG KÊ TỔNG QUAN'])
        overview_sheet.append(['Chỉ số', 'Giá trị', 'Đơn vị'])
        overview_sheet.append(['Tổng sản lượng', processed_data['summary']['total_production'], 'kg'])
        overview_sheet.append(['Sản lượng trung bình/ngày',
                              round(processed_data['summary']['total_production'] / processed_data['summary']['total_days'], 2), 'kg'])
        overview_sheet.append([])  # Empty row

        # Thống kê theo khu vực
        overview_sheet.append(['THỐNG KÊ THEO KHU VỰC'])
        overview_sheet.append(['Khu vực', 'Tổng sản lượng (kg)', 'Tỷ lệ (%)', 'Trung bình/ngày (kg)'])

        total_production = processed_data['summary']['total_production']
        for region_id, region_data in processed_data['regions'].items():
            region_production = region_data['total_production']
            percentage = (region_production / total_production * 100) if total_production > 0 else 0
            avg_daily = region_production / processed_data['summary']['total_days']

            overview_sheet.append([
                region_data['region_name'],
                round(region_production, 2),
                round(percentage, 1),
                round(avg_daily, 2)
            ])

        overview_sheet.append([])  # Empty row

        # Top 10 thành phần cám tiêu thụ nhiều nhất
        if processed_data['summary']['total_feed_consumption']:
            overview_sheet.append(['TOP 10 THÀNH PHẦN CÁM TIÊU THỤ NHIỀU NHẤT'])
            overview_sheet.append(['Thành phần', 'Tổng tiêu thụ (kg)', 'Trung bình/ngày (kg)'])

            sorted_feed = sorted(processed_data['summary']['total_feed_consumption'].items(),
                               key=lambda x: x[1], reverse=True)[:10]

            for component, total_amount in sorted_feed:
                avg_daily = total_amount / processed_data['summary']['total_days']
                overview_sheet.append([component, round(total_amount, 2), round(avg_daily, 2)])

        # Apply formatting
        self._apply_advanced_formatting(overview_sheet, f"A1:C{overview_sheet.max_row}", "daily_overview")

    def _create_regional_detail_sheet(self, workbook: Workbook, region_id: str, region_data: Dict):
        """Tạo sheet chi tiết cho một khu vực"""
        sheet_name = f"Chi Tiết {region_data['region_name']}"
        detail_sheet = workbook.create_sheet(sheet_name)

        # Header
        detail_sheet.append([f'CHI TIẾT KHU VỰC: {region_data["region_name"].upper()}'])
        detail_sheet.append([])

        # Thông tin tổng quan khu vực
        detail_sheet.append(['THÔNG TIN TỔNG QUAN'])
        detail_sheet.append(['Tổng sản lượng:', f'{region_data["total_production"]:,.2f} kg'])
        detail_sheet.append(['Số ngày có dữ liệu:', len(region_data['daily_production'])])
        detail_sheet.append([])

        # Sản lượng theo ngày
        detail_sheet.append(['SẢN LƯỢNG THEO NGÀY'])
        detail_sheet.append(['Ngày', 'Sản lượng (kg)', 'Ghi chú'])

        for date_str, production in sorted(region_data['daily_production'].items()):
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            weekday = date_obj.strftime("%A")
            detail_sheet.append([
                date_obj.strftime("%d/%m/%Y"),
                round(production, 2),
                f'Thứ {weekday}'
            ])

        detail_sheet.append([])

        # Tiêu thụ thành phần cám
        if region_data['feed_consumption']:
            detail_sheet.append(['TIÊU THỤ THÀNH PHẦN CÁM'])
            detail_sheet.append(['Thành phần', 'Tổng tiêu thụ (kg)', 'Trung bình/ngày (kg)', 'Tỷ lệ (%)'])

            total_feed = sum(region_data['feed_consumption'].values())
            days_count = len(region_data['daily_production'])

            for component, amount in sorted(region_data['feed_consumption'].items(), key=lambda x: x[1], reverse=True):
                avg_daily = amount / days_count if days_count > 0 else 0
                percentage = (amount / total_feed * 100) if total_feed > 0 else 0

                detail_sheet.append([
                    component,
                    round(amount, 2),
                    round(avg_daily, 2),
                    round(percentage, 1)
                ])

        detail_sheet.append([])

        # Tiêu thụ thành phần mix
        if region_data['mix_consumption']:
            detail_sheet.append(['TIÊU THỤ THÀNH PHẦN MIX'])
            detail_sheet.append(['Thành phần', 'Tổng tiêu thụ (kg)', 'Trung bình/ngày (kg)', 'Tỷ lệ (%)'])

            total_mix = sum(region_data['mix_consumption'].values())
            days_count = len(region_data['daily_production'])

            for component, amount in sorted(region_data['mix_consumption'].items(), key=lambda x: x[1], reverse=True):
                avg_daily = amount / days_count if days_count > 0 else 0
                percentage = (amount / total_mix * 100) if total_mix > 0 else 0

                detail_sheet.append([
                    component,
                    round(amount, 2),
                    round(avg_daily, 2),
                    round(percentage, 1)
                ])

        # Apply formatting
        self._apply_advanced_formatting(detail_sheet, f"A1:D{detail_sheet.max_row}", "regional_detail")

    def _create_trend_analysis_sheet(self, workbook: Workbook, processed_data: Dict):
        """Tạo sheet phân tích xu hướng"""
        trend_sheet = workbook.create_sheet("Phân Tích Xu Hướng")

        # Header
        trend_sheet.append(['PHÂN TÍCH XU HƯỚNG TIÊU THỤ'])
        trend_sheet.append([])

        # Xu hướng sản lượng theo ngày
        trend_sheet.append(['XU HƯỚNG SẢN LƯỢNG THEO NGÀY'])
        trend_sheet.append(['Ngày', 'Tổng sản lượng (kg)'] + [region_data['region_name'] for region_data in processed_data['regions'].values()])

        for date_str, daily_total in sorted(processed_data['daily_totals'].items()):
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            row = [date_obj.strftime("%d/%m/%Y"), round(daily_total['total_production'], 2)]

            # Thêm sản lượng từng khu vực
            for region_id in processed_data['regions'].keys():
                region_production = daily_total['regions_production'].get(region_id, 0)
                row.append(round(region_production, 2))

            trend_sheet.append(row)

        trend_sheet.append([])

        # Phân tích theo ngày trong tuần
        trend_sheet.append(['PHÂN TÍCH THEO NGÀY TRONG TUẦN'])
        trend_sheet.append(['Thứ', 'Sản lượng trung bình (kg)', 'Số ngày', 'Tỷ lệ (%)'])

        weekday_stats = {}
        total_production = processed_data['summary']['total_production']

        for date_str, daily_total in processed_data['daily_totals'].items():
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            weekday = date_obj.strftime("%A")

            if weekday not in weekday_stats:
                weekday_stats[weekday] = {'total': 0, 'count': 0}

            weekday_stats[weekday]['total'] += daily_total['total_production']
            weekday_stats[weekday]['count'] += 1

        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekday_names = ['Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7', 'Chủ nhật']

        for i, weekday in enumerate(weekday_order):
            if weekday in weekday_stats:
                stats = weekday_stats[weekday]
                avg_production = stats['total'] / stats['count']
                percentage = (stats['total'] / total_production * 100) if total_production > 0 else 0

                trend_sheet.append([
                    weekday_names[i],
                    round(avg_production, 2),
                    stats['count'],
                    round(percentage, 1)
                ])

        # Apply formatting
        self._apply_advanced_formatting(trend_sheet, f"A1:E{trend_sheet.max_row}", "trend_analysis")

    def _create_feed_component_overview_sheet(self, workbook: Workbook, feed_analysis: Dict):
        """Tạo sheet tổng quan thành phần cám"""
        if 'Sheet' in [ws.title for ws in workbook.worksheets]:
            workbook.remove(workbook['Sheet'])

        overview_sheet = workbook.create_sheet("Tổng Quan Thành Phần Cám")

        # Header
        overview_sheet.append(['BÁO CÁO CHI TIẾT THÀNH PHẦN CÁM'])
        overview_sheet.append([])

        # Thống kê tổng quan
        overview_sheet.append(['THỐNG KÊ TỔNG QUAN THÀNH PHẦN'])
        overview_sheet.append(['Thành phần', 'Tổng tiêu thụ (kg)', 'TB/ngày (kg)', 'Max/ngày (kg)',
                              'Min/ngày (kg)', 'Giá/kg (VND)', 'Tổng chi phí (VND)'])

        for component, data in sorted(feed_analysis['components_summary'].items(),
                                    key=lambda x: x[1]['total_consumption'], reverse=True):
            overview_sheet.append([
                component,
                round(data['total_consumption'], 2),
                round(data['average_daily'], 2),
                round(data['max_daily'], 2),
                round(data['min_daily'], 2) if data['min_daily'] != float('inf') else 0,
                data['component_info'].get('price_per_kg', 0),
                round(data.get('total_cost', 0), 0)
            ])

        overview_sheet.append([])

        # Thông tin dinh dưỡng
        overview_sheet.append(['THÔNG TIN DINH DƯỠNG THÀNH PHẦN'])
        overview_sheet.append(['Thành phần', 'Protein (%)', 'Năng lượng (kcal/kg)', 'Chất xơ (%)', 'Nhà cung cấp'])

        for component, data in feed_analysis['components_summary'].items():
            component_info = data['component_info']
            overview_sheet.append([
                component,
                component_info.get('protein', 'N/A'),
                component_info.get('energy', 'N/A'),
                component_info.get('fiber', 'N/A'),
                component_info.get('supplier', 'N/A')
            ])

        # Apply formatting
        self._apply_advanced_formatting(overview_sheet, f"A1:G{overview_sheet.max_row}", "feed_overview")

    def _create_feed_consumption_trend_sheet(self, workbook: Workbook, feed_analysis: Dict):
        """Tạo sheet xu hướng tiêu thụ cám"""
        trend_sheet = workbook.create_sheet("Xu Hướng Tiêu Thụ Cám")

        # Header
        trend_sheet.append(['XU HƯỚNG TIÊU THỤ THÀNH PHẦN CÁM THEO NGÀY'])
        trend_sheet.append([])

        # Tạo bảng dữ liệu theo ngày
        components = list(feed_analysis['components_summary'].keys())
        header = ['Ngày'] + components
        trend_sheet.append(header)

        for date_str in sorted(feed_analysis['daily_consumption'].keys()):
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            row = [date_obj.strftime("%d/%m/%Y")]

            daily_data = feed_analysis['daily_consumption'][date_str]
            for component in components:
                amount = daily_data.get(component, 0)
                row.append(round(amount, 2))

            trend_sheet.append(row)

        trend_sheet.append([])

        # Phân tích biến động
        trend_sheet.append(['PHÂN TÍCH BIẾN ĐỘNG'])
        trend_sheet.append(['Thành phần', 'Độ lệch chuẩn', 'Hệ số biến động (%)', 'Xu hướng'])

        for component in components:
            daily_amounts = []
            for daily_data in feed_analysis['daily_consumption'].values():
                daily_amounts.append(daily_data.get(component, 0))

            if daily_amounts:
                import statistics
                mean_amount = statistics.mean(daily_amounts)
                std_dev = statistics.stdev(daily_amounts) if len(daily_amounts) > 1 else 0
                cv = (std_dev / mean_amount * 100) if mean_amount > 0 else 0

                # Đánh giá xu hướng đơn giản
                if len(daily_amounts) >= 3:
                    first_half = daily_amounts[:len(daily_amounts)//2]
                    second_half = daily_amounts[len(daily_amounts)//2:]

                    avg_first = statistics.mean(first_half)
                    avg_second = statistics.mean(second_half)

                    if avg_second > avg_first * 1.1:
                        trend = "Tăng"
                    elif avg_second < avg_first * 0.9:
                        trend = "Giảm"
                    else:
                        trend = "Ổn định"
                else:
                    trend = "Không đủ dữ liệu"

                trend_sheet.append([
                    component,
                    round(std_dev, 2),
                    round(cv, 1),
                    trend
                ])

        # Apply formatting
        self._apply_advanced_formatting(trend_sheet, f"A1:D{trend_sheet.max_row}", "feed_trend")

    def _create_feed_formula_comparison_sheet(self, workbook: Workbook, feed_analysis: Dict):
        """Tạo sheet so sánh với công thức chuẩn"""
        comparison_sheet = workbook.create_sheet("So Sánh Công Thức Chuẩn")

        # Header
        comparison_sheet.append(['SO SÁNH VỚI CÔNG THỨC CHUẨN'])
        comparison_sheet.append([])

        try:
            from src.data.daily_consumption_data import ANIMAL_TYPES

            # So sánh với từng loại động vật
            for animal_type, animal_info in ANIMAL_TYPES.items():
                comparison_sheet.append([f'CÔNG THỨC {animal_info["name"].upper()}'])
                comparison_sheet.append(['Thành phần', 'Công thức chuẩn (%)', 'Tiêu thụ thực tế (kg)',
                                       'Tỷ lệ thực tế (%)', 'Chênh lệch (%)'])

                feed_formula = animal_info['feed_formula']
                total_actual = sum(feed_analysis['components_summary'].get(comp, {}).get('total_consumption', 0)
                                 for comp in feed_formula.keys())

                for component, standard_percentage in feed_formula.items():
                    actual_consumption = feed_analysis['components_summary'].get(component, {}).get('total_consumption', 0)
                    actual_percentage = (actual_consumption / total_actual * 100) if total_actual > 0 else 0
                    difference = actual_percentage - standard_percentage

                    comparison_sheet.append([
                        component,
                        standard_percentage,
                        round(actual_consumption, 2),
                        round(actual_percentage, 1),
                        round(difference, 1)
                    ])

                comparison_sheet.append([])  # Empty row between animal types

        except ImportError:
            comparison_sheet.append(['Không thể tải dữ liệu công thức chuẩn'])

        # Apply formatting
        self._apply_advanced_formatting(comparison_sheet, f"A1:E{comparison_sheet.max_row}", "formula_comparison")

    def _create_mix_component_overview_sheet(self, workbook: Workbook, mix_analysis: Dict):
        """Tạo sheet tổng quan thành phần mix"""
        if 'Sheet' in [ws.title for ws in workbook.worksheets]:
            workbook.remove(workbook['Sheet'])

        overview_sheet = workbook.create_sheet("Tổng Quan Thành Phần Mix")

        # Header
        overview_sheet.append(['BÁO CÁO CHI TIẾT THÀNH PHẦN MIX'])
        overview_sheet.append([])

        # Thống kê tổng quan
        overview_sheet.append(['THỐNG KÊ TỔNG QUAN THÀNH PHẦN'])
        overview_sheet.append(['Thành phần', 'Tổng tiêu thụ (kg)', 'TB/ngày (kg)', 'Max/ngày (kg)',
                              'Min/ngày (kg)', 'Giá/kg (VND)', 'Tổng chi phí (VND)'])

        for component, data in sorted(mix_analysis['components_summary'].items(),
                                    key=lambda x: x[1]['total_consumption'], reverse=True):
            overview_sheet.append([
                component,
                round(data['total_consumption'], 2),
                round(data['average_daily'], 2),
                round(data['max_daily'], 2),
                round(data['min_daily'], 2) if data['min_daily'] != float('inf') else 0,
                data['component_info'].get('price_per_kg', 0),
                round(data.get('total_cost', 0), 0)
            ])

        overview_sheet.append([])

        # Thông tin chức năng
        overview_sheet.append(['THÔNG TIN CHỨC NĂNG THÀNH PHẦN'])
        overview_sheet.append(['Thành phần', 'Chức năng', 'Liều lượng khuyến nghị', 'Nhà cung cấp'])

        for component, data in mix_analysis['components_summary'].items():
            component_info = data['component_info']
            overview_sheet.append([
                component,
                component_info.get('function', 'N/A'),
                component_info.get('dosage_range', 'N/A'),
                component_info.get('supplier', 'N/A')
            ])

        # Apply formatting
        self._apply_advanced_formatting(overview_sheet, f"A1:G{overview_sheet.max_row}", "mix_overview")

    def _create_mix_consumption_trend_sheet(self, workbook: Workbook, mix_analysis: Dict):
        """Tạo sheet xu hướng tiêu thụ mix"""
        trend_sheet = workbook.create_sheet("Xu Hướng Tiêu Thụ Mix")

        # Header
        trend_sheet.append(['XU HƯỚNG TIÊU THỤ THÀNH PHẦN MIX THEO NGÀY'])
        trend_sheet.append([])

        # Tạo bảng dữ liệu theo ngày
        components = list(mix_analysis['components_summary'].keys())
        header = ['Ngày'] + components
        trend_sheet.append(header)

        for date_str in sorted(mix_analysis['daily_consumption'].keys()):
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            row = [date_obj.strftime("%d/%m/%Y")]

            daily_data = mix_analysis['daily_consumption'][date_str]
            for component in components:
                amount = daily_data.get(component, 0)
                row.append(round(amount, 2))

            trend_sheet.append(row)

        # Apply formatting
        self._apply_advanced_formatting(trend_sheet, f"A1:F{trend_sheet.max_row}", "mix_trend")

    def _create_mix_efficiency_analysis_sheet(self, workbook: Workbook, mix_analysis: Dict):
        """Tạo sheet phân tích hiệu quả mix"""
        efficiency_sheet = workbook.create_sheet("Phân Tích Hiệu Quả Mix")

        # Header
        efficiency_sheet.append(['PHÂN TÍCH HIỆU QUẢ SỬ DỤNG THÀNH PHẦN MIX'])
        efficiency_sheet.append([])

        # Bảng phân tích hiệu quả
        efficiency_sheet.append(['Thành phần', 'Tỷ lệ sử dụng (%)', 'Khoảng khuyến nghị',
                                'Trạng thái', 'Ghi chú'])

        for component, data in mix_analysis['components_summary'].items():
            usage_rate = data.get('usage_rate', 'N/A')
            dosage_range = data['component_info'].get('dosage_range', 'N/A')
            efficiency_status = data.get('efficiency_status', 'Không xác định')

            # Ghi chú dựa trên trạng thái
            if efficiency_status == 'Dưới mức khuyến nghị':
                note = 'Cần tăng liều lượng'
            elif efficiency_status == 'Vượt mức khuyến nghị':
                note = 'Cần giảm liều lượng'
            elif efficiency_status == 'Trong khoảng khuyến nghị':
                note = 'Liều lượng phù hợp'
            else:
                note = 'Cần kiểm tra thêm'

            efficiency_sheet.append([
                component,
                usage_rate if usage_rate != 'N/A' else 'N/A',
                dosage_range,
                efficiency_status,
                note
            ])

        efficiency_sheet.append([])

        # Khuyến nghị tối ưu hóa
        efficiency_sheet.append(['KHUYẾN NGHỊ TỐI ƯU HÓA'])
        efficiency_sheet.append(['Thành phần', 'Khuyến nghị', 'Lý do'])

        for component, data in mix_analysis['components_summary'].items():
            efficiency_status = data.get('efficiency_status', 'Không xác định')

            if efficiency_status == 'Dưới mức khuyến nghị':
                recommendation = 'Tăng liều lượng'
                reason = 'Hiệu quả chưa tối ưu'
            elif efficiency_status == 'Vượt mức khuyến nghị':
                recommendation = 'Giảm liều lượng'
                reason = 'Tránh lãng phí và tác dụng phụ'
            elif efficiency_status == 'Trong khoảng khuyến nghị':
                recommendation = 'Duy trì hiện tại'
                reason = 'Liều lượng phù hợp'
            else:
                recommendation = 'Cần đánh giá thêm'
                reason = 'Thiếu thông tin tham chiếu'

            efficiency_sheet.append([component, recommendation, reason])

        # Apply formatting
        self._apply_advanced_formatting(efficiency_sheet, f"A1:E{efficiency_sheet.max_row}", "mix_efficiency")
