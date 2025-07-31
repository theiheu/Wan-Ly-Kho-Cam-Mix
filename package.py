#!/usr/bin/env python3
"""
Package Wrapper Script
Wrapper script để chạy package tools từ thư mục gốc
"""

import os
import sys
import subprocess

def main():
    """Chạy package script từ tools/"""
    tools_dir = os.path.join(os.path.dirname(__file__), 'tools')
    package_script = os.path.join(tools_dir, 'create_package.py')
    
    if not os.path.exists(package_script):
        print("❌ Không tìm thấy package script trong tools/")
        return 1
    
    # Chạy script package
    try:
        result = subprocess.run([sys.executable, package_script], cwd=os.getcwd())
        return result.returncode
    except Exception as e:
        print(f"❌ Lỗi khi chạy package: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
