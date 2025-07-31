#!/usr/bin/env python3
"""
Package Creator for Chicken Farm Management Software
Tạo package hoàn chỉnh với installer cho Windows
"""

import os
import sys
import shutil
import zipfile
import datetime
from pathlib import Path

APP_NAME = "ChickenFarmManager"
APP_DISPLAY_NAME = "Phần mềm Quản lý Cám - Trại Gà"
APP_VERSION = "2.0.0"
APP_AUTHOR = "Minh-Tan_Phat"

def create_portable_package():
    """Tạo package portable (không cần cài đặt)"""
    print("📦 Tạo package portable...")

    package_name = f"{APP_NAME}_v{APP_VERSION}_Portable"
    package_dir = f"packages/{package_name}"

    # Xóa thư mục package cũ nếu tồn tại
    if os.path.exists(package_dir):
        print(f"🗑️  Xóa package cũ: {package_dir}")
        shutil.rmtree(package_dir)

    # Tạo thư mục package
    os.makedirs(package_dir, exist_ok=True)

    # Copy executable và dependencies
    if os.path.exists(f"dist/{APP_NAME}"):
        shutil.copytree(f"dist/{APP_NAME}", f"{package_dir}/{APP_NAME}")
        print(f"✅ Đã copy executable vào {package_dir}")
    else:
        print("❌ Không tìm thấy dist folder. Vui lòng build trước.")
        return False

    # Tạo file khởi chạy
    launcher_content = f"""@echo off
cd /d "%~dp0"
cd {APP_NAME}
start "" "{APP_NAME}.exe"
"""

    with open(f"{package_dir}/Khởi chạy {APP_DISPLAY_NAME}.bat", 'w', encoding='utf-8') as f:
        f.write(launcher_content)

    # Copy documentation
    docs_to_copy = [
        'README.md',
        'ICON_DOCUMENTATION.md',
        'ICON_IMPLEMENTATION_SUMMARY.md'
    ]

    docs_dir = f"{package_dir}/Tài liệu"
    os.makedirs(docs_dir, exist_ok=True)

    for doc in docs_to_copy:
        if os.path.exists(doc):
            shutil.copy2(doc, docs_dir)
            print(f"✅ Đã copy {doc}")

    # Tạo README cho package
    package_readme = f"""# {APP_DISPLAY_NAME} - Portable Version

## Thông tin
- **Phiên bản**: {APP_VERSION}
- **Loại**: Portable (không cần cài đặt)
- **Tác giả**: {APP_AUTHOR}
- **Ngày tạo**: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}

## Cách sử dụng
1. Giải nén toàn bộ thư mục này
2. Chạy file "Khởi chạy {APP_DISPLAY_NAME}.bat"
3. Hoặc vào thư mục {APP_NAME} và chạy {APP_NAME}.exe

## Yêu cầu hệ thống
- Windows 10/11 (64-bit)
- RAM: Tối thiểu 4GB
- Dung lượng: 200MB trống

## Tính năng
- 📊 Quản lý lượng cám hàng ngày
- 📦 Hệ thống CRUD tồn kho hoàn chỉnh
- 🧪 Quản lý công thức dinh dưỡng
- 📈 Báo cáo và phân tích
- 📋 Thao tác hàng loạt

## Lưu ý
- Đây là phiên bản portable, không cần cài đặt
- Dữ liệu sẽ được lưu trong thư mục ứng dụng
- Có thể chạy từ USB hoặc thư mục bất kỳ

## Hỗ trợ
- Email: [your-email@example.com]
- GitHub: [https://github.com/your-repo]

© 2024 {APP_AUTHOR}. All rights reserved.
"""

    with open(f"{package_dir}/README.txt", 'w', encoding='utf-8') as f:
        f.write(package_readme)

    print(f"✅ Package portable đã tạo: {package_dir}")
    return package_dir

def create_installer_package():
    """Tạo package với installer"""
    print("🔧 Tạo package installer...")

    package_name = f"{APP_NAME}_v{APP_VERSION}_Installer"
    package_dir = f"packages/{package_name}"

    # Xóa thư mục package cũ nếu tồn tại
    if os.path.exists(package_dir):
        print(f"🗑️  Xóa package cũ: {package_dir}")
        shutil.rmtree(package_dir)

    # Tạo thư mục package
    os.makedirs(package_dir, exist_ok=True)

    # Copy executable
    if os.path.exists(f"dist/{APP_NAME}"):
        shutil.copytree(f"dist/{APP_NAME}", f"{package_dir}/app")
        print(f"✅ Đã copy executable")
    else:
        print("❌ Không tìm thấy dist folder")
        return False

    # Tạo installer script nâng cao
    installer_script = f"""@echo off
chcp 65001 >nul
title Cài đặt {APP_DISPLAY_NAME}

echo ========================================
echo   {APP_DISPLAY_NAME}
echo   Phiên bản {APP_VERSION}
echo   Tác giả: {APP_AUTHOR}
echo ========================================
echo.

echo 🔍 Kiểm tra quyền Administrator...
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Đã có quyền Administrator
) else (
    echo ❌ Cần quyền Administrator để cài đặt
    echo 💡 Nhấp chuột phải và chọn "Run as administrator"
    pause
    exit /b 1
)

echo.
echo 📋 Chọn thư mục cài đặt:
echo 1. C:\\Program Files\\{APP_NAME} (Khuyến nghị)
echo 2. C:\\{APP_NAME}
echo 3. Thư mục tùy chỉnh
echo.
choice /C 123 /M "Chọn tùy chọn (1-3)"

if %errorLevel% == 1 (
    set "INSTALL_DIR=C:\\Program Files\\{APP_NAME}"
) else if %errorLevel% == 2 (
    set "INSTALL_DIR=C:\\{APP_NAME}"
) else (
    set /p "INSTALL_DIR=Nhập đường dẫn cài đặt: "
)

echo.
echo 📁 Thư mục cài đặt: %INSTALL_DIR%
echo.
choice /C YN /M "Tiếp tục cài đặt (Y/N)"
if %errorLevel% == 2 (
    echo Hủy cài đặt.
    pause
    exit /b 0
)

echo.
echo 📁 Tạo thư mục cài đặt...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

echo.
echo 📋 Sao chép files...
xcopy /E /I /Y "app\\*" "%INSTALL_DIR%\\"

if %errorLevel% neq 0 (
    echo ❌ Lỗi khi sao chép files
    pause
    exit /b 1
)

echo.
echo 🔗 Tạo shortcuts...

REM Desktop shortcut
set "DESKTOP=%PUBLIC%\\Desktop"
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%DESKTOP%\\{APP_DISPLAY_NAME}.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%INSTALL_DIR%\\{APP_NAME}.exe" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "%INSTALL_DIR%" >> CreateShortcut.vbs
echo oLink.Description = "Hệ thống quản lý toàn diện cho trại gà" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs

REM Start Menu shortcut
set "STARTMENU=%PROGRAMDATA%\\Microsoft\\Windows\\Start Menu\\Programs"
echo sLinkFile = "%STARTMENU%\\{APP_DISPLAY_NAME}.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%INSTALL_DIR%\\{APP_NAME}.exe" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "%INSTALL_DIR%" >> CreateShortcut.vbs
echo oLink.Description = "Hệ thống quản lý toàn diện cho trại gà" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs

cscript //nologo CreateShortcut.vbs
del CreateShortcut.vbs

echo.
echo 📝 Tạo uninstaller...
echo @echo off > "%INSTALL_DIR%\\uninstall.bat"
echo echo Gỡ cài đặt {APP_DISPLAY_NAME}... >> "%INSTALL_DIR%\\uninstall.bat"
echo rmdir /s /q "%INSTALL_DIR%" >> "%INSTALL_DIR%\\uninstall.bat"
echo del "%PUBLIC%\\Desktop\\{APP_DISPLAY_NAME}.lnk" >> "%INSTALL_DIR%\\uninstall.bat"
echo del "%PROGRAMDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\{APP_DISPLAY_NAME}.lnk" >> "%INSTALL_DIR%\\uninstall.bat"
echo echo Đã gỡ cài đặt hoàn tất! >> "%INSTALL_DIR%\\uninstall.bat"
echo pause >> "%INSTALL_DIR%\\uninstall.bat"

echo.
echo 🎉 Cài đặt hoàn tất!
echo ========================================
echo 📍 Đường dẫn: %INSTALL_DIR%
echo 🖥️  Shortcut Desktop: ✅
echo 📋 Start Menu: ✅
echo 🗑️  Uninstaller: %INSTALL_DIR%\\uninstall.bat
echo ========================================
echo.
choice /C YN /M "Khởi chạy ứng dụng ngay (Y/N)"
if %errorLevel% == 1 (
    start "" "%INSTALL_DIR%\\{APP_NAME}.exe"
)

echo.
echo ✅ Hoàn tất!
pause
"""

    with open(f"{package_dir}/install.bat", 'w', encoding='utf-8') as f:
        f.write(installer_script)

    # Tạo README cho installer
    installer_readme = f"""# {APP_DISPLAY_NAME} - Installer Package

## Hướng dẫn cài đặt
1. Nhấp chuột phải vào "install.bat"
2. Chọn "Run as administrator"
3. Làm theo hướng dẫn trên màn hình

## Tính năng installer
- ✅ Tự động tạo shortcuts (Desktop + Start Menu)
- ✅ Cho phép chọn thư mục cài đặt
- ✅ Tạo uninstaller tự động
- ✅ Kiểm tra quyền Administrator

## Gỡ cài đặt
Chạy file "uninstall.bat" trong thư mục cài đặt

## Yêu cầu
- Windows 10/11 (64-bit)
- Quyền Administrator
- 200MB dung lượng trống

© 2024 {APP_AUTHOR}
"""

    with open(f"{package_dir}/README_INSTALLER.txt", 'w', encoding='utf-8') as f:
        f.write(installer_readme)

    print(f"✅ Package installer đã tạo: {package_dir}")
    return package_dir

def create_zip_packages():
    """Tạo file ZIP cho các packages"""
    print("🗜️ Tạo file ZIP...")

    packages_created = []

    # Tìm các package đã tạo
    if os.path.exists("packages"):
        for item in os.listdir("packages"):
            package_path = f"packages/{item}"
            if os.path.isdir(package_path):
                zip_name = f"{item}.zip"

                # Xóa file ZIP cũ nếu tồn tại
                if os.path.exists(zip_name):
                    print(f"🗑️  Xóa ZIP cũ: {zip_name}")
                    os.remove(zip_name)

                print(f"📦 Tạo {zip_name}...")

                with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, dirs, files in os.walk(package_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arc_name = os.path.relpath(file_path, package_path)
                            zipf.write(file_path, arc_name)

                packages_created.append(zip_name)
                print(f"✅ Đã tạo {zip_name}")

    return packages_created

def main():
    """Hàm chính"""
    print("📦 Package Creator - Chicken Farm Management")
    print("=" * 60)

    # Kiểm tra dist folder
    if not os.path.exists(f"dist/{APP_NAME}"):
        print("❌ Không tìm thấy dist folder.")
        print("💡 Vui lòng chạy build_windows.py trước.")
        return 1

    try:
        # Tạo thư mục packages
        os.makedirs("packages", exist_ok=True)

        # Tạo các packages
        portable_dir = create_portable_package()
        installer_dir = create_installer_package()

        # Tạo ZIP files
        zip_files = create_zip_packages()

        # Thông báo kết quả
        print("\n" + "=" * 60)
        print("🎉 TẠO PACKAGE THÀNH CÔNG!")
        print("=" * 60)

        if portable_dir:
            print(f"📦 Portable package: {portable_dir}")

        if installer_dir:
            print(f"🔧 Installer package: {installer_dir}")

        if zip_files:
            print("\n📁 File ZIP đã tạo:")
            for zip_file in zip_files:
                size = os.path.getsize(zip_file) / (1024*1024)  # MB
                print(f"   📄 {zip_file} ({size:.1f} MB)")

        print(f"\n💡 Hướng dẫn phân phối:")
        print(f"   • Portable: Giải nén và chạy trực tiếp")
        print(f"   • Installer: Chạy install.bat với quyền Admin")

        return 0

    except Exception as e:
        print(f"\n❌ Lỗi khi tạo package: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    input("\nNhấn Enter để thoát...")
    sys.exit(exit_code)
