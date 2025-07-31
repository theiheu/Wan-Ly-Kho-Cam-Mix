#!/usr/bin/env python3
"""
Build Wrapper Script
Wrapper script để chạy build tools từ thư mục gốc
"""

import os
import sys
import subprocess

def main():
    """Chạy build script từ tools/"""
    tools_dir = os.path.join(os.path.dirname(__file__), 'tools')
    build_script = os.path.join(tools_dir, 'build_windows.py')
    
    if not os.path.exists(build_script):
        print("❌ Không tìm thấy build script trong tools/")
        return 1
    
    # Chạy script build
    try:
        result = subprocess.run([sys.executable, build_script], cwd=os.getcwd())
        return result.returncode
    except Exception as e:
        print(f"❌ Lỗi khi chạy build: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
