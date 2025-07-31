#!/usr/bin/env python3
"""
Cleanup Wrapper Script
Wrapper script để chạy cleanup tools từ thư mục gốc
"""

import os
import sys
import subprocess

def main():
    """Chạy cleanup script từ tools/"""
    tools_dir = os.path.join(os.path.dirname(__file__), 'tools')
    cleanup_script = os.path.join(tools_dir, 'smart_cleanup.py')
    
    if not os.path.exists(cleanup_script):
        print("❌ Không tìm thấy cleanup script trong tools/")
        return 1
    
    # Chạy script cleanup
    try:
        result = subprocess.run([sys.executable, cleanup_script], cwd=os.getcwd())
        return result.returncode
    except Exception as e:
        print(f"❌ Lỗi khi chạy cleanup: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
