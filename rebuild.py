#!/usr/bin/env python3
"""
Rebuild Wrapper Script
Wrapper script để chạy rebuild tools từ thư mục gốc
"""

import os
import sys
import subprocess

def main():
    """Chạy rebuild script từ tools/"""
    tools_dir = os.path.join(os.path.dirname(__file__), 'tools')
    rebuild_script = os.path.join(tools_dir, 'rebuild_all.py')
    
    if not os.path.exists(rebuild_script):
        print("❌ Không tìm thấy rebuild script trong tools/")
        return 1
    
    # Chạy script rebuild
    try:
        result = subprocess.run([sys.executable, rebuild_script], cwd=os.getcwd())
        return result.returncode
    except Exception as e:
        print(f"❌ Lỗi khi chạy rebuild: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
