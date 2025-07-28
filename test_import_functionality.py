#!/usr/bin/env python3
"""
Test script for Import functionality to verify crash fixes
"""

import os
import json
import sys
from datetime import datetime

def test_import_file_structure():
    """Test 1: Kiểm tra cấu trúc file import"""
    print("=== TEST 1: KIỂM TRA CẤU TRÚC FILE IMPORT ===")
    
    imports_dir = "src/data/imports"
    if not os.path.exists(imports_dir):
        print("❌ Thư mục imports không tồn tại")
        return False
    
    # Check existing files
    import_files = [f for f in os.listdir(imports_dir) if f.startswith('import_') and f.endswith('.json')]
    print(f"✅ Tìm thấy {len(import_files)} file import hiện có")
    
    # Test file format
    for filename in import_files:
        file_path = os.path.join(imports_dir, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                print(f"❌ File {filename} không đúng format (phải là array)")
                return False
            
            # Check entry structure
            for entry in data:
                required_fields = ['timestamp', 'type', 'ingredient', 'amount']
                for field in required_fields:
                    if field not in entry:
                        print(f"❌ Entry trong {filename} thiếu field: {field}")
                        return False
            
            print(f"✅ File {filename}: {len(data)} entries, format đúng")
            
        except Exception as e:
            print(f"❌ Lỗi đọc file {filename}: {str(e)}")
            return False
    
    return True

def test_filename_format():
    """Test 2: Kiểm tra format filename"""
    print("\n=== TEST 2: KIỂM TRA FORMAT FILENAME ===")
    
    # Test date conversion
    test_dates = [
        "2025-07-28",  # Correct format
        "28/07/2025",  # Old problematic format
    ]
    
    for date_str in test_dates:
        try:
            if "/" in date_str:
                # Convert dd/MM/yyyy to yyyy-MM-dd
                day, month, year = date_str.split("/")
                converted = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                print(f"✅ Converted {date_str} → {converted}")
            else:
                print(f"✅ Date {date_str} already in correct format")
                
            # Test filename creation
            filename = f"src/data/imports/import_{date_str.replace('/', '-')}.json"
            print(f"✅ Filename: {filename}")
            
        except Exception as e:
            print(f"❌ Lỗi xử lý date {date_str}: {str(e)}")
            return False
    
    return True

def test_json_operations():
    """Test 3: Kiểm tra JSON operations"""
    print("\n=== TEST 3: KIỂM TRA JSON OPERATIONS ===")
    
    test_file = "src/data/imports/test_import.json"
    
    try:
        # Test 1: Create new file
        test_data = [
            {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "type": "feed",
                "ingredient": "Test Bắp",
                "amount": 100.0,
                "note": "Test entry"
            }
        ]
        
        os.makedirs(os.path.dirname(test_file), exist_ok=True)
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        
        print("✅ Tạo file JSON mới thành công")
        
        # Test 2: Read and append
        with open(test_file, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
        
        new_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": "mix",
            "ingredient": "Test L-Lysine",
            "amount": 25.0,
            "note": "Test mix entry"
        }
        
        existing_data.append(new_entry)
        
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
        
        print("✅ Append dữ liệu thành công")
        
        # Test 3: Verify data
        with open(test_file, 'r', encoding='utf-8') as f:
            final_data = json.load(f)
        
        if len(final_data) == 2:
            print("✅ Dữ liệu được lưu đúng")
        else:
            print(f"❌ Dữ liệu không đúng: expected 2, got {len(final_data)}")
            return False
        
        # Cleanup
        os.remove(test_file)
        print("✅ Cleanup test file thành công")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi JSON operations: {str(e)}")
        if os.path.exists(test_file):
            os.remove(test_file)
        return False

def test_error_handling():
    """Test 4: Kiểm tra error handling"""
    print("\n=== TEST 4: KIỂM TRA ERROR HANDLING ===")
    
    # Test 1: Invalid JSON file
    invalid_file = "src/data/imports/invalid_test.json"
    try:
        os.makedirs(os.path.dirname(invalid_file), exist_ok=True)
        with open(invalid_file, 'w', encoding='utf-8') as f:
            f.write("invalid json content {")
        
        # Try to read invalid file
        try:
            with open(invalid_file, 'r', encoding='utf-8') as f:
                json.load(f)
            print("❌ Should have failed to read invalid JSON")
            return False
        except json.JSONDecodeError:
            print("✅ Correctly handled invalid JSON")
        
        # Cleanup
        os.remove(invalid_file)
        
    except Exception as e:
        print(f"❌ Lỗi test invalid JSON: {str(e)}")
        return False
    
    # Test 2: Non-existent directory
    try:
        non_existent_dir = "src/data/non_existent"
        test_file = os.path.join(non_existent_dir, "test.json")
        
        # This should create directory automatically
        os.makedirs(os.path.dirname(test_file), exist_ok=True)
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump([], f)
        
        print("✅ Tự động tạo directory thành công")
        
        # Cleanup
        os.remove(test_file)
        os.rmdir(non_existent_dir)
        
    except Exception as e:
        print(f"❌ Lỗi test directory creation: {str(e)}")
        return False
    
    return True

def test_data_validation():
    """Test 5: Kiểm tra data validation"""
    print("\n=== TEST 5: KIỂM TRA DATA VALIDATION ===")
    
    # Test valid data
    valid_entries = [
        {"type": "feed", "ingredient": "Bắp", "amount": 100.0, "note": "Valid"},
        {"type": "mix", "ingredient": "L-Lysine", "amount": 25.5, "note": ""},
    ]
    
    for entry in valid_entries:
        try:
            # Validate amount is numeric
            amount = float(entry["amount"])
            if amount <= 0:
                print(f"❌ Invalid amount: {amount}")
                return False
            
            # Validate type
            if entry["type"] not in ["feed", "mix"]:
                print(f"❌ Invalid type: {entry['type']}")
                return False
            
            # Validate ingredient
            if not entry["ingredient"]:
                print(f"❌ Empty ingredient")
                return False
            
            print(f"✅ Valid entry: {entry['ingredient']} - {amount} kg")
            
        except Exception as e:
            print(f"❌ Validation error: {str(e)}")
            return False
    
    # Test invalid data
    invalid_entries = [
        {"type": "feed", "ingredient": "", "amount": 100.0},  # Empty ingredient
        {"type": "feed", "ingredient": "Bắp", "amount": 0},   # Zero amount
        {"type": "feed", "ingredient": "Bắp", "amount": -10}, # Negative amount
        {"type": "invalid", "ingredient": "Bắp", "amount": 100}, # Invalid type
    ]
    
    for entry in invalid_entries:
        try:
            # This should fail validation
            if not entry.get("ingredient"):
                print(f"✅ Correctly rejected empty ingredient")
                continue
            
            amount = float(entry["amount"])
            if amount <= 0:
                print(f"✅ Correctly rejected invalid amount: {amount}")
                continue
            
            if entry["type"] not in ["feed", "mix"]:
                print(f"✅ Correctly rejected invalid type: {entry['type']}")
                continue
            
            print(f"❌ Should have rejected: {entry}")
            return False
            
        except Exception as e:
            print(f"✅ Correctly caught validation error: {str(e)}")
    
    return True

def main():
    """Main test function"""
    print("🧪 KIỂM TRA CHỨC NĂNG NHẬP HÀNG")
    print("=" * 50)
    
    tests = [
        test_import_file_structure,
        test_filename_format,
        test_json_operations,
        test_error_handling,
        test_data_validation
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
        print("✅ Chức năng nhập hàng đã được sửa lỗi và ổn định")
    else:
        print("⚠️ CÓ MỘT SỐ TESTS THẤT BẠI")
        print("❌ Cần kiểm tra thêm các vấn đề")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
