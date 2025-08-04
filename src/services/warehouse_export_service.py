#!/usr/bin/env python3
"""
Warehouse Export Service - Dịch vụ xuất báo cáo kho hàng
Phiên bản mới được thiết kế đơn giản, đáng tin cậy và dễ bảo trì
"""

import os
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class WarehouseExportService:
    """Dịch vụ xuất báo cáo kho hàng"""
    
    def __init__(self):
        """Khởi tạo dịch vụ xuất báo cáo"""
        self.data_dir = Path("src/data")
        self.config_dir = self.data_dir / "config"
        self.exports_dir = self.data_dir / "exports"
        
        # Đảm bảo thư mục tồn tại
        self.exports_dir.mkdir(parents=True, exist_ok=True)
        
        # Kiểm tra và tạo dữ liệu mẫu nếu cần
        self._ensure_sample_data()
    
    def _ensure_sample_data(self):
        """Đảm bảo có dữ liệu mẫu để xuất"""
        # Dữ liệu mẫu cho tồn kho cám
        feed_inventory_file = self.config_dir / "feed_inventory.json"
        if not feed_inventory_file.exists() or self._is_file_empty(feed_inventory_file):
            sample_feed = {
                "Bắp nghiền": 1500.0,
                "Cám gạo": 800.0,
                "Đậu nành": 1200.0,
                "Dầu đậu nành": 150.0,
                "Cám lúa mì": 600.0
            }
            self._save_json(feed_inventory_file, sample_feed)
        
        # Dữ liệu mẫu cho tồn kho mix
        mix_inventory_file = self.config_dir / "mix_inventory.json"
        if not mix_inventory_file.exists() or self._is_file_empty(mix_inventory_file):
            sample_mix = {
                "Lysine": 75.0,
                "Methionine": 45.0,
                "Choline": 60.0,
                "Đá vôi": 300.0,
                "Vitamin premix": 25.0
            }
            self._save_json(mix_inventory_file, sample_mix)
        
        # Dữ liệu mẫu cho công thức cám
        feed_formula_file = self.config_dir / "feed_formula.json"
        if not feed_formula_file.exists() or self._is_file_empty(feed_formula_file):
            sample_feed_formula = {
                "Bắp nghiền": 45.0,
                "Cám gạo": 20.0,
                "Đậu nành": 25.0,
                "Dầu đậu nành": 5.0,
                "Nguyên liệu tổ hợp": 5.0
            }
            self._save_json(feed_formula_file, sample_feed_formula)
        
        # Dữ liệu mẫu cho công thức mix
        mix_formula_file = self.config_dir / "mix_formula.json"
        if not mix_formula_file.exists() or self._is_file_empty(mix_formula_file):
            sample_mix_formula = {
                "Lysine": 40.0,
                "Methionine": 25.0,
                "Choline": 20.0,
                "Đá vôi": 15.0
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
            print(f"Lỗi lưu file {file_path}: {e}")
    
    def _load_json(self, file_path: Path) -> Dict:
        """Tải dữ liệu JSON"""
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Lỗi đọc file {file_path}: {e}")
        return {}
    
    def _get_stock_status(self, quantity: float) -> str:
        """Xác định trạng thái tồn kho"""
        if quantity <= 0:
            return "Hết hàng"
        elif quantity < 100:
            return "Sắp hết"
        elif quantity < 500:
            return "Ít"
        else:
            return "Đủ"
    
    def _generate_filename(self, report_type: str) -> str:
        """Tạo tên file với timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{report_type}_{timestamp}.xlsx"
    
    def export_inventory_report(self, include_feed: bool = True, include_mix: bool = True) -> Tuple[bool, str]:
        """Xuất báo cáo tồn kho"""
        try:
            if not include_feed and not include_mix:
                return False, "Vui lòng chọn ít nhất một loại kho để xuất"
            
            export_data = []
            
            # Xuất dữ liệu kho cám
            if include_feed:
                feed_data = self._load_json(self.config_dir / "feed_inventory.json")
                for item_name, quantity in feed_data.items():
                    export_data.append({
                        'Loại Kho': 'Kho Cám',
                        'Tên Nguyên Liệu': item_name,
                        'Số Lượng (kg)': quantity,
                        'Trạng Thái': self._get_stock_status(quantity),
                        'Ngày Cập Nhật': datetime.now().strftime("%d/%m/%Y %H:%M")
                    })
            
            # Xuất dữ liệu kho mix
            if include_mix:
                mix_data = self._load_json(self.config_dir / "mix_inventory.json")
                for item_name, quantity in mix_data.items():
                    export_data.append({
                        'Loại Kho': 'Kho Mix',
                        'Tên Nguyên Liệu': item_name,
                        'Số Lượng (kg)': quantity,
                        'Trạng Thái': self._get_stock_status(quantity),
                        'Ngày Cập Nhật': datetime.now().strftime("%d/%m/%Y %H:%M")
                    })
            
            if not export_data:
                return False, "Không có dữ liệu tồn kho để xuất"
            
            # Tạo DataFrame và xuất Excel
            df = pd.DataFrame(export_data)
            filename = self._generate_filename("bao_cao_ton_kho")
            file_path = self.exports_dir / filename
            
            # Xuất với định dạng cơ bản
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Báo Cáo Tồn Kho', index=False)
                
                # Định dạng header
                worksheet = writer.sheets['Báo Cáo Tồn Kho']
                for cell in worksheet[1]:
                    cell.font = cell.font.copy(bold=True)
                
                # Tự động điều chỉnh độ rộng cột
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            return True, f"Xuất báo cáo tồn kho thành công!\nFile: {filename}\nVị trí: {file_path}\nSố mục: {len(export_data)}"
            
        except Exception as e:
            return False, f"Lỗi xuất báo cáo tồn kho: {str(e)}"
    
    def export_formula_report(self, include_feed: bool = True, include_mix: bool = True) -> Tuple[bool, str]:
        """Xuất báo cáo công thức"""
        try:
            if not include_feed and not include_mix:
                return False, "Vui lòng chọn ít nhất một loại công thức để xuất"
            
            export_data = []
            
            # Xuất công thức cám
            if include_feed:
                feed_formula = self._load_json(self.config_dir / "feed_formula.json")
                for ingredient, percentage in feed_formula.items():
                    export_data.append({
                        'Loại Công Thức': 'Công Thức Cám',
                        'Nguyên Liệu': ingredient,
                        'Tỷ Lệ (%)': percentage,
                        'Khối Lượng/1000kg': round((percentage / 100) * 1000, 2),
                        'Ghi Chú': 'Nguyên liệu chính' if percentage >= 20 else 'Nguyên liệu phụ'
                    })
            
            # Xuất công thức mix
            if include_mix:
                mix_formula = self._load_json(self.config_dir / "mix_formula.json")
                for ingredient, percentage in mix_formula.items():
                    export_data.append({
                        'Loại Công Thức': 'Công Thức Mix',
                        'Nguyên Liệu': ingredient,
                        'Tỷ Lệ (%)': percentage,
                        'Khối Lượng/1000kg': round((percentage / 100) * 1000, 2),
                        'Ghi Chú': 'Nguyên liệu chính' if percentage >= 20 else 'Nguyên liệu phụ'
                    })
            
            if not export_data:
                return False, "Không có dữ liệu công thức để xuất"
            
            # Tạo DataFrame và xuất Excel
            df = pd.DataFrame(export_data)
            filename = self._generate_filename("bao_cao_cong_thuc")
            file_path = self.exports_dir / filename
            
            # Xuất với định dạng cơ bản
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Báo Cáo Công Thức', index=False)
                
                # Định dạng header
                worksheet = writer.sheets['Báo Cáo Công Thức']
                for cell in worksheet[1]:
                    cell.font = cell.font.copy(bold=True)
                
                # Tự động điều chỉnh độ rộng cột
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            return True, f"Xuất báo cáo công thức thành công!\nFile: {filename}\nVị trí: {file_path}\nSố mục: {len(export_data)}"
            
        except Exception as e:
            return False, f"Lỗi xuất báo cáo công thức: {str(e)}"
    
    def export_summary_report(self) -> Tuple[bool, str]:
        """Xuất báo cáo tổng hợp"""
        try:
            # Tải dữ liệu
            feed_inventory = self._load_json(self.config_dir / "feed_inventory.json")
            mix_inventory = self._load_json(self.config_dir / "mix_inventory.json")
            feed_formula = self._load_json(self.config_dir / "feed_formula.json")
            mix_formula = self._load_json(self.config_dir / "mix_formula.json")
            
            # Tạo báo cáo tổng hợp
            summary_data = []
            
            # Thống kê tồn kho
            total_feed_items = len(feed_inventory)
            total_feed_quantity = sum(feed_inventory.values())
            total_mix_items = len(mix_inventory)
            total_mix_quantity = sum(mix_inventory.values())
            
            summary_data.extend([
                {'Loại Thống Kê': 'Tồn Kho Cám', 'Số Mục': total_feed_items, 'Tổng Khối Lượng (kg)': total_feed_quantity, 'Ghi Chú': 'Nguyên liệu thô'},
                {'Loại Thống Kê': 'Tồn Kho Mix', 'Số Mục': total_mix_items, 'Tổng Khối Lượng (kg)': total_mix_quantity, 'Ghi Chú': 'Phụ gia dinh dưỡng'},
                {'Loại Thống Kê': 'Công Thức Cám', 'Số Mục': len(feed_formula), 'Tổng Khối Lượng (kg)': sum(feed_formula.values()), 'Ghi Chú': 'Tỷ lệ phần trăm'},
                {'Loại Thống Kê': 'Công Thức Mix', 'Số Mục': len(mix_formula), 'Tổng Khối Lượng (kg)': sum(mix_formula.values()), 'Ghi Chú': 'Tỷ lệ phần trăm'}
            ])
            
            # Tạo DataFrame và xuất Excel
            df = pd.DataFrame(summary_data)
            filename = self._generate_filename("bao_cao_tong_hop")
            file_path = self.exports_dir / filename
            
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Báo Cáo Tổng Hợp', index=False)
                
                # Định dạng header
                worksheet = writer.sheets['Báo Cáo Tổng Hợp']
                for cell in worksheet[1]:
                    cell.font = cell.font.copy(bold=True)
                
                # Tự động điều chỉnh độ rộng cột
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            return True, f"Xuất báo cáo tổng hợp thành công!\nFile: {filename}\nVị trí: {file_path}"
            
        except Exception as e:
            return False, f"Lỗi xuất báo cáo tổng hợp: {str(e)}"
    
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
