#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phần mềm Quản lý Cám - Trại Gà
==============================

Script khởi động chính cho ứng dụng.
"""

import os
import sys

# Fix console encoding for Windows (safe for executable)
if sys.platform == "win32":
    try:
        import codecs
        if hasattr(sys.stdout, 'buffer') and sys.stdout.buffer is not None:
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        if hasattr(sys.stderr, 'buffer') and sys.stderr.buffer is not None:
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    except (AttributeError, TypeError):
        # In executable environment, stdout/stderr might not have buffer
        pass


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
    import sys
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtGui import QFont
    from src.main import ChickenFarmApp
    from src.utils.app_icon import create_app_icon
    from src.main import DEFAULT_FONT

    print("Starting Chicken Farm Application...")
    app = QApplication(sys.argv)
    app.setWindowIcon(create_app_icon())

    # Thiết lập font mặc định cho toàn bộ ứng dụng
    app.setFont(DEFAULT_FONT)

    print("Creating main window...")
    window = ChickenFarmApp()
    print("Showing main window...")
    window.show()
    print("Entering application event loop...")
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()