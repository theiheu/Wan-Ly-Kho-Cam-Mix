#!/usr/bin/env python3
"""
Complete Rebuild Script for Chicken Farm Management Software
Script tổng hợp: Dọn dẹp → Build → Package
"""

import os
import sys
import subprocess
import time

def run_script(script_name, description):
    """Chạy script và kiểm tra kết quả"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")

    try:
        if script_name.endswith('.py'):
            result = subprocess.run([sys.executable, script_name],
                                  capture_output=False, text=True)
        else:
            result = subprocess.run([script_name],
                                  capture_output=False, text=True, shell=True)

        if result.returncode == 0:
            print(f"✅ {description} - THÀNH CÔNG!")
            return True
        else:
            print(f"❌ {description} - THẤT BẠI!")
            return False

    except Exception as e:
        print(f"❌ Lỗi khi chạy {script_name}: {e}")
        return False

def main():
    """Hàm chính"""
    print("🔄 REBUILD ALL - Chicken Farm Management")
    print("=" * 60)
    print("🎯 Quy trình: Dọn dẹp → Build → Package")
    print()

    # Kiểm tra các script cần thiết
    required_scripts = [
        'tools/smart_cleanup.py',
        'tools/build_windows.py',
        'tools/create_package.py'
    ]

    missing_scripts = []
    for script in required_scripts:
        if not os.path.exists(script):
            missing_scripts.append(script)

    if missing_scripts:
        print("❌ Thiếu các script cần thiết:")
        for script in missing_scripts:
            print(f"   • {script}")
        return 1

    print("✅ Tất cả script cần thiết đã có sẵn")
    print()

    # Xác nhận từ người dùng
    print("⚠️  QUY TRÌNH SẼ THỰC HIỆN:")
    print("   1. Dọn dẹp file tạm thời (giữ lại dist/)")
    print("   2. Build executable mới")
    print("   3. Tạo packages (Portable + Installer)")
    print("   4. Tạo file ZIP phân phối")
    print()

    try:
        choice = input("Tiếp tục? (Y/N): ").strip().upper()
        if choice != 'Y':
            print("Hủy rebuild.")
            return 0
    except KeyboardInterrupt:
        print("\nHủy rebuild.")
        return 0

    start_time = time.time()

    # Bước 1: Dọn dẹp thông minh
    if not run_script('tools/smart_cleanup.py', 'BƯỚC 1: Dọn dẹp thông minh'):
        print("\n❌ Dọn dẹp thất bại. Dừng quy trình.")
        return 1

    # Bước 2: Build executable
    if not run_script('tools/build_windows.py', 'BƯỚC 2: Build executable'):
        print("\n❌ Build thất bại. Dừng quy trình.")
        return 1

    # Bước 3: Tạo packages
    if not run_script('tools/create_package.py', 'BƯỚC 3: Tạo packages'):
        print("\n❌ Tạo package thất bại. Dừng quy trình.")
        return 1

    # Thống kê kết quả
    end_time = time.time()
    duration = end_time - start_time

    print(f"\n{'='*60}")
    print("🎉 REBUILD ALL HOÀN TẤT!")
    print(f"{'='*60}")
    print(f"⏱️  Thời gian: {duration:.1f} giây")
    print()

    # Kiểm tra kết quả
    print("📊 KẾT QUẢ:")

    if os.path.exists("dist/ChickenFarmManager/ChickenFarmManager.exe"):
        size = os.path.getsize("dist/ChickenFarmManager/ChickenFarmManager.exe")
        print(f"✅ Executable: dist/ChickenFarmManager/ChickenFarmManager.exe ({size//1024//1024} MB)")
    else:
        print("❌ Executable: Không tìm thấy")

    if os.path.exists("packages"):
        packages = [d for d in os.listdir("packages") if os.path.isdir(f"packages/{d}")]
        print(f"✅ Packages: {len(packages)} package(s)")
        for pkg in packages:
            print(f"   📁 {pkg}")
    else:
        print("❌ Packages: Không tìm thấy")

    zip_files = [f for f in os.listdir(".") if f.endswith(".zip")]
    if zip_files:
        print(f"✅ ZIP files: {len(zip_files)} file(s)")
        for zip_file in zip_files:
            size = os.path.getsize(zip_file)
            print(f"   📄 {zip_file} ({size//1024//1024} MB)")
    else:
        print("❌ ZIP files: Không tìm thấy")

    print()
    print("💡 BƯỚC TIẾP THEO:")
    print("   • Test executable trong dist/")
    print("   • Test installer trong packages/")
    print("   • Phân phối file .zip")
    print()

    return 0

if __name__ == "__main__":
    exit_code = main()
    input("\nNhấn Enter để thoát...")
    sys.exit(exit_code)
