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

    # Import persistent path manager after setting up paths
    try:
        from src.utils.persistent_paths import persistent_path_manager

        # Ensure data directories exist using persistent path manager
        os.makedirs(str(persistent_path_manager.config_path), exist_ok=True)
        os.makedirs(str(persistent_path_manager.data_path / "presets" / "feed"), exist_ok=True)
        os.makedirs(str(persistent_path_manager.data_path / "presets" / "mix"), exist_ok=True)
        os.makedirs(str(persistent_path_manager.reports_path), exist_ok=True)
    except ImportError:
        # Fallback to hardcoded paths if import fails
        os.makedirs("src/data/config", exist_ok=True)
        os.makedirs("src/data/presets/feed", exist_ok=True)
        os.makedirs("src/data/presets/mix", exist_ok=True)
        os.makedirs("src/data/reports", exist_ok=True)

def initialize_data():
    """Khởi tạo dữ liệu nếu chưa tồn tại"""
    try:
        from src.utils.persistent_paths import get_config_file_path

        # Check if config files exist using persistent path manager
        feed_config = get_config_file_path("feed_formula.json")
        mix_config = get_config_file_path("mix_formula.json")
        inventory_config = get_config_file_path("inventory.json")

        if not feed_config.exists() or not mix_config.exists() or not inventory_config.exists():
            print("Khởi tạo dữ liệu ban đầu...")
            from src.utils.init_data import init_data
            init_data()
    except ImportError:
        # Fallback to hardcoded paths if import fails
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
    from src.main import Quan_Ly_Kho_Cam_Mix_App
    from src.utils.app_icon import create_app_icon
    from src.main import DEFAULT_FONT

    print("Starting Chicken Farm Application...")
    app = QApplication(sys.argv)
    app.setWindowIcon(create_app_icon())

    # Thiết lập font mặc định cho toàn bộ ứng dụng
    app.setFont(DEFAULT_FONT)

    print("Creating main window...")
    window = Quan_Ly_Kho_Cam_Mix_App()
    print("Showing main window...")
    window.show()
    print("Entering application event loop...")
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()