#!/usr/bin/env python3
"""
Test script for Import Tracking functionality
"""

import os
import json
import sys
from datetime import datetime

def test_data_loading():
    """Test 1: Kiểm tra hiển thị dữ liệu"""
    print("=== TEST 1: KIỂM TRA HIỂN THỊ DỮ LIỆU ===")
    
    # Check imports directory
    imports_dir = "src/data/imports"
    if not os.path.exists(imports_dir):
        print("❌ Thư mục imports không tồn tại")
        return False
    
    import_files = [f for f in os.listdir(imports_dir) if f.startswith('import_') and f.endswith('.json')]
    print(f"✅ Tìm thấy {len(import_files)} file import: {import_files}")
    
    # Check data structure
    total_entries = 0
    material_types = {}
    
    for filename in import_files:
        file_path = os.path.join(imports_dir, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                entries = json.load(f)
            
            print(f"📁 {filename}: {len(entries)} entries")
            total_entries += len(entries)
            
            for entry in entries:
                ingredient = entry.get('ingredient', '')
                material_type = categorize_material(ingredient)
                material_types[material_type] = material_types.get(material_type, 0) + 1
                
        except Exception as e:
            print(f"❌ Lỗi đọc file {filename}: {str(e)}")
    
    print(f"📊 Tổng số entries: {total_entries}")
    print("📊 Phân loại nguyên liệu:")
    for material, count in material_types.items():
        print(f"   - {material}: {count} entries")
    
    return True

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

def test_participation_data():
    """Test 2: Kiểm tra dữ liệu tham gia"""
    print("\n=== TEST 2: KIỂM TRA DỮ LIỆU THAM GIA ===")
    
    participation_file = "src/data/import_participation.json"
    if not os.path.exists(participation_file):
        print("❌ File import_participation.json không tồn tại")
        return False
    
    try:
        with open(participation_file, 'r', encoding='utf-8') as f:
            participation_data = json.load(f)
        
        print(f"✅ Tìm thấy {len(participation_data)} bản ghi tham gia")
        
        for import_key, data in participation_data.items():
            participants = data.get('participants', [])
            print(f"📝 {import_key[:50]}...")
            print(f"   - Ngày: {data.get('date')}")
            print(f"   - Nguyên liệu: {data.get('material_type')} ({data.get('ingredient')})")
            print(f"   - Số lượng: {data.get('amount')} kg")
            print(f"   - Nhân viên: {len(participants)} người")
            for p in participants:
                print(f"     + {p.get('name')} ({p.get('position')})")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi đọc file participation: {str(e)}")
        return False

def test_employee_data():
    """Test 3: Kiểm tra dữ liệu nhân viên"""
    print("\n=== TEST 3: KIỂM TRA DỮ LIỆU NHÂN VIÊN ===")
    
    employees_file = "src/data/employees.json"
    if not os.path.exists(employees_file):
        print("❌ File employees.json không tồn tại")
        return False
    
    try:
        with open(employees_file, 'r', encoding='utf-8') as f:
            employees_data = json.load(f)
        
        print(f"✅ Tìm thấy {len(employees_data)} nhân viên")
        
        for emp in employees_data:
            print(f"👤 ID: {emp.get('id')} - {emp.get('name')} ({emp.get('position')})")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi đọc file employees: {str(e)}")
        return False

def test_attendance_data():
    """Test 4: Kiểm tra dữ liệu nghỉ phép"""
    print("\n=== TEST 4: KIỂM TRA DỮ LIỆU NGHỈ PHÉP ===")
    
    attendance_file = "src/data/attendance.json"
    if not os.path.exists(attendance_file):
        print("⚠️ File attendance.json không tồn tại (có thể chưa có dữ liệu nghỉ phép)")
        return True
    
    try:
        with open(attendance_file, 'r', encoding='utf-8') as f:
            attendance_data = json.load(f)
        
        print(f"✅ Tìm thấy dữ liệu nghỉ phép cho {len(attendance_data)} nhân viên")
        
        for emp_id, dates in attendance_data.items():
            print(f"👤 Nhân viên ID {emp_id}: {len(dates)} ngày nghỉ")
            for date, info in dates.items():
                print(f"   - {date}: {info.get('type')} - {info.get('note', 'Không có ghi chú')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi đọc file attendance: {str(e)}")
        return False

def test_integration():
    """Test 5: Kiểm tra tích hợp"""
    print("\n=== TEST 5: KIỂM TRA TÍCH HỢP ===")
    
    # Test available employees logic
    test_date = "2025-07-25"
    print(f"🔍 Kiểm tra nhân viên có mặt ngày {test_date}")
    
    # Load employees
    try:
        with open("src/data/employees.json", 'r', encoding='utf-8') as f:
            employees = json.load(f)
    except:
        print("❌ Không thể load dữ liệu nhân viên")
        return False
    
    # Load attendance
    try:
        with open("src/data/attendance.json", 'r', encoding='utf-8') as f:
            attendance = json.load(f)
    except:
        attendance = {}
        print("⚠️ Không có dữ liệu nghỉ phép")
    
    available_employees = []
    for emp in employees:
        emp_id = str(emp.get('id'))
        is_absent = False
        
        if emp_id in attendance and test_date in attendance[emp_id]:
            absence_type = attendance[emp_id][test_date].get('type', '')
            if absence_type == 'Nghỉ ốm':
                is_absent = True
        
        if not is_absent:
            available_employees.append(emp)
    
    print(f"✅ Nhân viên có mặt ngày {test_date}: {len(available_employees)}/{len(employees)}")
    for emp in available_employees:
        print(f"   - {emp.get('name')} ({emp.get('position')})")
    
    return True

def main():
    """Main test function"""
    print("🧪 KIỂM TRA TÍNH NĂNG THEO DÕI NHẬP KHO")
    print("=" * 50)
    
    tests = [
        test_data_loading,
        test_participation_data,
        test_employee_data,
        test_attendance_data,
        test_integration
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
        print("🎉 TẤT CẢ TESTS ĐỀU THÀNH CÔNG!")
    else:
        print("⚠️ CÓ MỘT SỐ TESTS THẤT BẠI")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
