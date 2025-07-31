#!/usr/bin/env python3
"""
Smart Cleanup Script for Chicken Farm Management Software
Dọn dẹp thông minh các file build tạm thời
"""

import os
import shutil
import glob
import sys
from pathlib import Path

def clean_build_artifacts():
    """Xóa các file artifacts từ quá trình build"""
    print("🧹 Dọn dẹp build artifacts...")

    # Thư mục build tạm thời
    build_dirs = ['build']
    for build_dir in build_dirs:
        if os.path.exists(build_dir):
            try:
                shutil.rmtree(build_dir)
                print(f"✅ Đã xóa thư mục: {build_dir}/")
            except Exception as e:
                print(f"❌ Lỗi khi xóa {build_dir}: {e}")

    # File .spec tự động tạo
    spec_files = glob.glob('*.spec')
    for spec_file in spec_files:
        try:
            os.remove(spec_file)
            print(f"✅ Đã xóa file spec: {spec_file}")
        except Exception as e:
            print(f"❌ Lỗi khi xóa {spec_file}: {e}")

    # File version info
    version_files = ['version_info.txt']
    for version_file in version_files:
        if os.path.exists(version_file):
            try:
                os.remove(version_file)
                print(f"✅ Đã xóa: {version_file}")
            except Exception as e:
                print(f"❌ Lỗi khi xóa {version_file}: {e}")

def clean_pycache():
    """Xóa tất cả __pycache__ folders"""
    print("🧹 Dọn dẹp __pycache__ folders...")

    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(pycache_path)
                print(f"✅ Đã xóa: {pycache_path}")
            except Exception as e:
                print(f"❌ Lỗi khi xóa {pycache_path}: {e}")

def clean_pyc_files():
    """Xóa tất cả .pyc files"""
    print("🧹 Dọn dẹp .pyc files...")

    pyc_files = glob.glob('**/*.pyc', recursive=True)
    for pyc_file in pyc_files:
        try:
            os.remove(pyc_file)
            print(f"✅ Đã xóa: {pyc_file}")
        except Exception as e:
            print(f"❌ Lỗi khi xóa {pyc_file}: {e}")

def clean_temp_files():
    """Xóa các file tạm thời khác"""
    print("🧹 Dọn dẹp file tạm thời...")

    # File log và temp
    temp_patterns = [
        '*.log',
        '*.tmp',
        '*.temp',
        '.DS_Store',
        'Thumbs.db'
    ]

    for pattern in temp_patterns:
        temp_files = glob.glob(pattern, recursive=False)
        for temp_file in temp_files:
            try:
                os.remove(temp_file)
                print(f"✅ Đã xóa file tạm: {temp_file}")
            except Exception as e:
                print(f"❌ Lỗi khi xóa {temp_file}: {e}")

def clean_old_packages():
    """Tùy chọn xóa packages và ZIP cũ"""
    print("🤔 Tìm thấy packages và ZIP files từ build trước:")

    # Kiểm tra packages
    packages_exist = os.path.exists("packages") and os.listdir("packages")
    zip_files = glob.glob("*.zip")

    if packages_exist or zip_files:
        if packages_exist:
            print("  📁 Thư mục packages/ tồn tại")
        for zip_file in zip_files:
            size = get_size_info(zip_file)
            print(f"  📄 {zip_file} {size}")

        print("\n❓ Bạn có muốn xóa packages và ZIP cũ không?")
        print("   Y = Xóa (để tạo package mới)")
        print("   N = Giữ lại (khuyến nghị)")

        try:
            choice = input("Chọn (Y/N): ").strip().upper()
            if choice == 'Y':
                if packages_exist:
                    shutil.rmtree("packages")
                    print("✅ Đã xóa thư mục packages/")

                for zip_file in zip_files:
                    os.remove(zip_file)
                    print(f"✅ Đã xóa {zip_file}")

                print("💡 Bây giờ bạn có thể chạy create_package.py để tạo mới")
            else:
                print("📦 Đã giữ lại packages và ZIP files")
        except KeyboardInterrupt:
            print("\n📦 Đã giữ lại packages và ZIP files")

def show_preserved_items():
    """Hiển thị các item được giữ lại"""
    print("📦 Các file/thư mục được GIỮ LẠI:")

    preserved_items = [
        'dist/',
        'packages/',
        '*.zip',
        'install.bat',
        'README_DISTRIBUTION.txt'
    ]

    for item in preserved_items:
        if '*' in item:
            # Pattern matching
            matches = glob.glob(item)
            for match in matches:
                if os.path.exists(match):
                    size = get_size_info(match)
                    print(f"  ✅ {match} {size}")
        else:
            if os.path.exists(item):
                size = get_size_info(item)
                print(f"  ✅ {item} {size}")

def get_size_info(path):
    """Lấy thông tin kích thước file/folder"""
    try:
        if os.path.isfile(path):
            size = os.path.getsize(path)
            return f"({size / (1024*1024):.1f} MB)"
        elif os.path.isdir(path):
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                    except:
                        pass
            return f"({total_size / (1024*1024):.1f} MB)"
    except:
        pass
    return ""

def main():
    """Hàm chính"""
    print("🧹 Smart Cleanup Script - Chicken Farm Management")
    print("=" * 60)
    print("🎯 Mục tiêu: Dọn dẹp file tạm thời, GIỮ LẠI kết quả build")
    print()

    try:
        # Thực hiện dọn dẹp
        clean_build_artifacts()
        print()
        clean_pycache()
        print()
        clean_pyc_files()
        print()
        clean_temp_files()
        print()

        # Tùy chọn xóa packages cũ
        clean_old_packages()
        print()

        # Hiển thị những gì được giữ lại
        show_preserved_items()

        print("\n" + "=" * 60)
        print("🎉 DỌN DẸP HOÀN TẤT!")
        print("=" * 60)
        print("✅ Đã xóa: File tạm thời, build artifacts, __pycache__")
        print("📦 Đã giữ: dist/, packages/, *.zip, install.bat")
        print("💡 Bây giờ bạn có thể chạy build mới hoặc phân phối package")

        return 0

    except Exception as e:
        print(f"\n❌ Lỗi trong quá trình dọn dẹp: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    input("\nNhấn Enter để thoát...")
    sys.exit(exit_code)
