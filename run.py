#!/usr/bin/env python3
"""
Phần mềm Quản lý Cám - Trại Gà
==============================

Script khởi động chính cho ứng dụng.
"""

import os
import sys

def setup_environment():
    """Thiết lập môi trường chạy"""
    # Đảm bảo thư mục hiện tại là thư mục gốc của dự án
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)

    # Thêm thư mục gốc vào đường dẫn tìm kiếm module
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    # Đảm bảo các thư mục dữ liệu tồn tại
    os.makedirs("src/data/config", exist_ok=True)
    os.makedirs("src/data/presets/feed", exist_ok=True)
    os.makedirs("src/data/presets/mix", exist_ok=True)
    os.makedirs("src/data/reports", exist_ok=True)

def initialize_data():
    """Khởi tạo dữ liệu nếu chưa tồn tại"""
    if not os.path.exists("src/data/config/feed_formula.json") or \
       not os.path.exists("src/data/config/mix_formula.json") or \
       not os.path.exists("src/data/config/inventory.json"):
        print("Khởi tạo dữ liệu ban đầu...")
        from src.utils.init_data import init_data
        init_data()

def main():
    """Hàm chính để chạy ứng dụng"""
    setup_environment()
    initialize_data()

    # Import và chạy ứng dụng chính
    from src.main import main as run_app
    run_app()

if __name__ == "__main__":
    main()