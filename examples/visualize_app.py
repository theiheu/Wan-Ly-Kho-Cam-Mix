#!/usr/bin/env python3
"""
Công cụ trực quan hóa dữ liệu lượng cám
=========================================

Script khởi động công cụ trực quan hóa.
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

    # Đảm bảo thư mục báo cáo tồn tại
    os.makedirs("src/data/reports", exist_ok=True)

def main():
    """Hàm chính để chạy công cụ trực quan hóa"""
    setup_environment()

    # Import và chạy công cụ trực quan hóa
    from src.utils.visualize import main as run_visualize
    run_visualize()

if __name__ == "__main__":
    main()