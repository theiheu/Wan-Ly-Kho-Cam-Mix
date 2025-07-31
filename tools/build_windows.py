#!/usr/bin/env python3
"""
Windows Build Script for Chicken Farm Management Software
Tạo file thực thi Windows (.exe) với PyInstaller
"""

import os
import sys
import shutil
import subprocess
import json
from pathlib import Path

# Thông tin ứng dụng
APP_NAME = "ChickenFarmManager"
APP_DISPLAY_NAME = "Phần mềm Quản lý Cám - Trại Gà"
APP_VERSION = "2.0.0"
APP_AUTHOR = "Minh-Tan_Phat"
APP_DESCRIPTION = "Hệ thống quản lý toàn diện cho trại gà"

def check_requirements():
    """Kiểm tra các yêu cầu cần thiết"""
    print("🔍 Kiểm tra yêu cầu hệ thống...")
    
    # Kiểm tra Python version
    if sys.version_info < (3, 6):
        print("❌ Cần Python 3.6 trở lên")
        return False
    
    # Kiểm tra PyInstaller
    try:
        import PyInstaller
        print(f"✅ PyInstaller {PyInstaller.__version__} đã cài đặt")
    except ImportError:
        print("❌ PyInstaller chưa được cài đặt")
        print("💡 Chạy: pip install pyinstaller")
        return False
    
    # Kiểm tra các thư viện cần thiết
    required_packages = ['PyQt5', 'pandas', 'matplotlib', 'openpyxl']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} đã cài đặt")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} chưa được cài đặt")
    
    if missing_packages:
        print(f"💡 Chạy: pip install {' '.join(missing_packages)}")
        return False
    
    return True

def clean_build_dirs():
    """Dọn dẹp thư mục build cũ"""
    print("🧹 Dọn dẹp thư mục build...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"🗑️  Đã xóa: {dir_name}")
    
    # Xóa file .spec cũ
    spec_files = [f for f in os.listdir('.') if f.endswith('.spec')]
    for spec_file in spec_files:
        os.remove(spec_file)
        print(f"🗑️  Đã xóa: {spec_file}")

def generate_version_info():
    """Tạo file thông tin version cho Windows"""
    print("📝 Tạo file thông tin version...")
    
    version_info = f"""# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({APP_VERSION.replace('.', ',')},0),
    prodvers=({APP_VERSION.replace('.', ',')},0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'{APP_AUTHOR}'),
        StringStruct(u'FileDescription', u'{APP_DESCRIPTION}'),
        StringStruct(u'FileVersion', u'{APP_VERSION}'),
        StringStruct(u'InternalName', u'{APP_NAME}'),
        StringStruct(u'LegalCopyright', u'© 2024 {APP_AUTHOR}. All rights reserved.'),
        StringStruct(u'OriginalFilename', u'{APP_NAME}.exe'),
        StringStruct(u'ProductName', u'{APP_DISPLAY_NAME}'),
        StringStruct(u'ProductVersion', u'{APP_VERSION}')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)"""
    
    with open('version_info.txt', 'w', encoding='utf-8') as f:
        f.write(version_info)
    
    print("✅ Đã tạo version_info.txt")

def create_pyinstaller_spec():
    """Tạo file .spec cho PyInstaller"""
    print("📋 Tạo file PyInstaller spec...")
    
    # Tìm đường dẫn icon
    icon_path = None
    possible_icons = [
        'src/data/icons/app_icon.ico',
        'src/data/icons/app_icon_64x64.png'
    ]
    
    for icon in possible_icons:
        if os.path.exists(icon):
            icon_path = os.path.abspath(icon)
            break
    
    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Dữ liệu cần thiết
added_files = [
    ('src/data', 'src/data'),
    ('src/utils', 'src/utils'),
    ('src/core', 'src/core'),
]

# Hidden imports
hidden_imports = [
    'PyQt5.QtCore',
    'PyQt5.QtGui', 
    'PyQt5.QtWidgets',
    'pandas',
    'matplotlib',
    'matplotlib.backends.backend_qt5agg',
    'openpyxl',
    'json',
    'datetime',
    'os',
    'sys'
]

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='{APP_NAME}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='version_info.txt',
    icon='{icon_path if icon_path else ""}',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='{APP_NAME}',
)
"""
    
    with open(f'{APP_NAME}.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print(f"✅ Đã tạo {APP_NAME}.spec")

def build_executable():
    """Build file thực thi"""
    print("🔨 Bắt đầu build executable...")
    
    try:
        # Chạy PyInstaller
        cmd = [
            'pyinstaller',
            '--clean',
            '--noconfirm',
            f'{APP_NAME}.spec'
        ]
        
        print(f"🚀 Chạy lệnh: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Build thành công!")
            return True
        else:
            print("❌ Build thất bại!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Lỗi khi build: {e}")
        return False

def create_installer_script():
    """Tạo script cài đặt đơn giản"""
    print("📦 Tạo script cài đặt...")
    
    installer_script = f"""@echo off
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
echo 📁 Tạo thư mục cài đặt...
set INSTALL_DIR=C:\\Program Files\\{APP_NAME}
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

echo.
echo 📋 Sao chép files...
xcopy /E /I /Y "dist\\{APP_NAME}\\*" "%INSTALL_DIR%\\"

echo.
echo 🔗 Tạo shortcut trên Desktop...
set DESKTOP=%USERPROFILE%\\Desktop
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%DESKTOP%\\{APP_DISPLAY_NAME}.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%INSTALL_DIR%\\{APP_NAME}.exe" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "%INSTALL_DIR%" >> CreateShortcut.vbs
echo oLink.Description = "{APP_DESCRIPTION}" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs
cscript CreateShortcut.vbs
del CreateShortcut.vbs

echo.
echo 🎉 Cài đặt hoàn tất!
echo 📍 Đường dẫn: %INSTALL_DIR%
echo 🖥️  Shortcut đã được tạo trên Desktop
echo.
pause
"""
    
    with open('install.bat', 'w', encoding='utf-8') as f:
        f.write(installer_script)
    
    print("✅ Đã tạo install.bat")

def create_readme():
    """Tạo file README cho bản phân phối"""
    print("📖 Tạo README...")
    
    readme_content = f"""# {APP_DISPLAY_NAME}

## Thông tin phiên bản
- **Phiên bản**: {APP_VERSION}
- **Tác giả**: {APP_AUTHOR}
- **Ngày build**: {__import__('datetime').datetime.now().strftime('%d/%m/%Y %H:%M')}

## Cài đặt

### Cách 1: Cài đặt tự động
1. Nhấp chuột phải vào `install.bat`
2. Chọn "Run as administrator"
3. Làm theo hướng dẫn trên màn hình

### Cách 2: Chạy trực tiếp
1. Mở thư mục `dist/{APP_NAME}/`
2. Chạy file `{APP_NAME}.exe`

## Yêu cầu hệ thống
- **Hệ điều hành**: Windows 10/11 (64-bit)
- **RAM**: Tối thiểu 4GB
- **Dung lượng**: 200MB trống

## Tính năng chính
- 📊 Quản lý lượng cám hàng ngày
- 📦 Hệ thống CRUD tồn kho hoàn chỉnh
- 🧪 Quản lý công thức dinh dưỡng
- 📈 Báo cáo và phân tích
- 📋 Thao tác hàng loạt

## Hỗ trợ
- **Email**: [your-email@example.com]
- **GitHub**: [https://github.com/your-repo]

## Giấy phép
© 2024 {APP_AUTHOR}. All rights reserved.
"""
    
    with open('README_DISTRIBUTION.txt', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("✅ Đã tạo README_DISTRIBUTION.txt")

def main():
    """Hàm chính"""
    print("🐔 Windows Build Script - Chicken Farm Management")
    print("=" * 60)
    
    # Kiểm tra yêu cầu
    if not check_requirements():
        print("\n❌ Không đủ yêu cầu để build. Vui lòng cài đặt các package cần thiết.")
        return 1
    
    try:
        # Các bước build
        clean_build_dirs()
        generate_version_info()
        create_pyinstaller_spec()
        
        # Build executable
        if not build_executable():
            return 1
        
        # Tạo các file hỗ trợ
        create_installer_script()
        create_readme()
        
        # Thông báo thành công
        print("\n" + "=" * 60)
        print("🎉 BUILD THÀNH CÔNG!")
        print("=" * 60)
        print(f"📁 File executable: dist/{APP_NAME}/{APP_NAME}.exe")
        print(f"📦 Script cài đặt: install.bat")
        print(f"📖 Hướng dẫn: README_DISTRIBUTION.txt")
        print("\n💡 Để cài đặt:")
        print("   1. Chạy install.bat với quyền Administrator")
        print("   2. Hoặc copy thư mục dist/ đến máy đích")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Lỗi trong quá trình build: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    input("\nNhấn Enter để thoát...")
    sys.exit(exit_code)
