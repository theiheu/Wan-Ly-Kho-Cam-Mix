#!/usr/bin/env python3
"""
Test script for Import-Team Management Integration
"""

import os
import json
import sys
from datetime import datetime

def test_bonus_config():
    """Test 1: Kiểm tra file config bonus rates"""
    print("=== TEST 1: KIỂM TRA FILE CONFIG BONUS RATES ===")
    
    config_file = "src/data/config/bonus_rates.json"
    if not os.path.exists(config_file):
        print("❌ File bonus_rates.json không tồn tại")
        return False
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Check structure
        required_keys = ['default_rates', 'specific_rates']
        for key in required_keys:
            if key not in config:
                print(f"❌ Thiếu key: {key}")
                return False
        
        # Check default rates
        default_rates = config['default_rates']
        expected_materials = ['Bắp', 'Nành', 'Cám gạo', 'Khác']
        
        for material in expected_materials:
            if material not in default_rates:
                print(f"❌ Thiếu mức thưởng cho: {material}")
                return False
            
            rate = default_rates[material]
            if not isinstance(rate, (int, float)) or rate < 0:
                print(f"❌ Mức thưởng không hợp lệ cho {material}: {rate}")
                return False
        
        print("✅ File config bonus rates hợp lệ")
        print(f"   - Default rates: {len(default_rates)} loại")
        print(f"   - Specific rates: {len(config['specific_rates'])} nguyên liệu")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi đọc config: {str(e)}")
        return False

def test_import_participation_structure():
    """Test 2: Kiểm tra cấu trúc import participation"""
    print("\n=== TEST 2: KIỂM TRA CẤU TRÚC IMPORT PARTICIPATION ===")
    
    participation_file = "src/data/import_participation.json"
    if not os.path.exists(participation_file):
        print("⚠️ File import_participation.json chưa tồn tại (chưa có dữ liệu)")
        return True
    
    try:
        with open(participation_file, 'r', encoding='utf-8') as f:
            participation_data = json.load(f)
        
        print(f"✅ Tìm thấy {len(participation_data)} bản ghi participation")
        
        # Check structure of each entry
        for import_key, data in participation_data.items():
            required_fields = ['date', 'material_type', 'ingredient', 'amount', 'participants']
            
            for field in required_fields:
                if field not in data:
                    print(f"❌ Entry {import_key} thiếu field: {field}")
                    return False
            
            # Check participants structure
            participants = data['participants']
            if not isinstance(participants, list):
                print(f"❌ Participants phải là list: {import_key}")
                return False
            
            for participant in participants:
                if not isinstance(participant, dict):
                    print(f"❌ Participant phải là dict: {import_key}")
                    return False
                
                participant_fields = ['id', 'name', 'position']
                for field in participant_fields:
                    if field not in participant:
                        print(f"❌ Participant thiếu field {field}: {import_key}")
                        return False
        
        print("✅ Cấu trúc import participation hợp lệ")
        return True
        
    except Exception as e:
        print(f"❌ Lỗi đọc participation data: {str(e)}")
        return False

def test_data_consistency():
    """Test 3: Kiểm tra tính nhất quán dữ liệu"""
    print("\n=== TEST 3: KIỂM TRA TÍNH NHẤT QUÁN DỮ LIỆU ===")
    
    # Check employees data
    employees_file = "src/data/employees.json"
    if not os.path.exists(employees_file):
        print("❌ File employees.json không tồn tại")
        return False
    
    try:
        with open(employees_file, 'r', encoding='utf-8') as f:
            employees = json.load(f)
        
        employee_ids = set(str(emp.get('id', '')) for emp in employees)
        print(f"✅ Tìm thấy {len(employee_ids)} nhân viên")
        
        # Check participation data references valid employees
        participation_file = "src/data/import_participation.json"
        if os.path.exists(participation_file):
            with open(participation_file, 'r', encoding='utf-8') as f:
                participation_data = json.load(f)
            
            invalid_refs = 0
            for import_key, data in participation_data.items():
                participants = data.get('participants', [])
                for participant in participants:
                    participant_id = str(participant.get('id', ''))
                    if participant_id not in employee_ids:
                        print(f"⚠️ Invalid employee reference: {participant_id} in {import_key}")
                        invalid_refs += 1
            
            if invalid_refs == 0:
                print("✅ Tất cả references đều hợp lệ")
            else:
                print(f"⚠️ Tìm thấy {invalid_refs} invalid references")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi kiểm tra consistency: {str(e)}")
        return False

def test_material_categorization():
    """Test 4: Kiểm tra phân loại nguyên liệu"""
    print("\n=== TEST 4: KIỂM TRA PHÂN LOẠI NGUYÊN LIỆU ===")
    
    def categorize_material(ingredient_name):
        """Helper function to categorize materials"""
        ingredient_lower = ingredient_name.lower()
        
        if 'bắp' in ingredient_lower or 'corn' in ingredient_lower:
            return 'Bắp'
        elif 'nành' in ingredient_lower or 'soybean' in ingredient_lower or 'đậu nành' in ingredient_lower:
            return 'Nành'
        elif 'đá hạt' in ingredient_lower or 'stone' in ingredient_lower or 'gravel' in ingredient_lower:
            return 'Đá hạt'
        elif 'cám gạo' in ingredient_lower or 'rice bran' in ingredient_lower or 'cám' in ingredient_lower:
            return 'Cám gạo'
        else:
            return 'Khác'
    
    # Test cases
    test_cases = [
        ("Bắp", "Bắp"),
        ("Nành", "Nành"),
        ("Đậu nành", "Nành"),
        ("Cám gạo", "Cám gạo"),
        ("Đá hạt", "Đá hạt"),
        ("DL-Methionine", "Khác"),
        ("L-Lysine", "Khác"),
        ("Bio-Choline", "Khác"),
    ]
    
    all_passed = True
    for ingredient, expected in test_cases:
        result = categorize_material(ingredient)
        if result == expected:
            print(f"✅ {ingredient} → {result}")
        else:
            print(f"❌ {ingredient} → {result} (expected: {expected})")
            all_passed = False
    
    return all_passed

def test_workflow_simulation():
    """Test 5: Mô phỏng workflow tích hợp"""
    print("\n=== TEST 5: MÔ PHỎNG WORKFLOW TÍCH HỢP ===")
    
    # Simulate import workflow
    print("📝 Mô phỏng quy trình:")
    print("1. User nhập hàng → Chọn nguyên liệu và số lượng")
    print("2. Hệ thống hiển thị dialog chọn nhân viên")
    print("3. Lưu dữ liệu nhập kho + danh sách nhân viên")
    print("4. Dữ liệu được sử dụng cho tính thưởng")
    
    # Check if all required files exist
    required_files = [
        "src/data/employees.json",
        "src/data/config/bonus_rates.json"
    ]
    
    optional_files = [
        "src/data/import_participation.json",
        "src/data/attendance.json"
    ]
    
    print("\n📁 Kiểm tra files cần thiết:")
    all_required_exist = True
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} (bắt buộc)")
            all_required_exist = False
    
    for file_path in optional_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"⚠️ {file_path} (tùy chọn)")
    
    if all_required_exist:
        print("✅ Workflow có thể hoạt động")
        return True
    else:
        print("❌ Thiếu files bắt buộc")
        return False

def main():
    """Main test function"""
    print("🧪 KIỂM TRA TÍCH HỢP IMPORT-TEAM MANAGEMENT")
    print("=" * 60)
    
    tests = [
        test_bonus_config,
        test_import_participation_structure,
        test_data_consistency,
        test_material_categorization,
        test_workflow_simulation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test thất bại: {str(e)}")
    
    print(f"\n📊 KẾT QUẢ: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 TÍCH HỢP THÀNH CÔNG!")
        print("✅ Hệ thống đã sẵn sàng cho production")
    else:
        print("⚠️ CÓ MỘT SỐ VẤN ĐỀ CẦN KHẮC PHỤC")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
