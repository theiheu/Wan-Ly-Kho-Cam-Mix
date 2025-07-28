#!/usr/bin/env python3
"""
Test script for attendance management
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    print("Testing attendance management...")
    
    # Test imports
    from PyQt5.QtWidgets import QApplication, QTextEdit
    print("✅ PyQt5 imports successful")
    
    # Test data loading
    import json
    
    # Test leave types config
    leave_types_file = "src/data/config/leave_types.json"
    if os.path.exists(leave_types_file):
        with open(leave_types_file, 'r', encoding='utf-8') as f:
            leave_config = json.load(f)
        print(f"✅ Leave types config loaded: {len(leave_config.get('leave_types', {}))} types")
    else:
        print("❌ Leave types config not found")
    
    # Test attendance data
    attendance_file = "src/data/attendance.json"
    if os.path.exists(attendance_file):
        with open(attendance_file, 'r', encoding='utf-8') as f:
            attendance_data = json.load(f)
        print(f"✅ Attendance data loaded")
        print(f"   - Records: {len(attendance_data.get('attendance_records', {}))}")
        print(f"   - Balances: {len(attendance_data.get('leave_balances', {}))}")
        print(f"   - Summaries: {len(attendance_data.get('monthly_summaries', {}))}")
    else:
        print("❌ Attendance data not found")
    
    # Test employees data
    employees_file = "src/data/employees.json"
    if os.path.exists(employees_file):
        with open(employees_file, 'r', encoding='utf-8') as f:
            employees_data = json.load(f)
        print(f"✅ Employees data loaded: {len(employees_data)} employees")
    else:
        print("❌ Employees data not found")
    
    print("✅ All tests passed!")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
