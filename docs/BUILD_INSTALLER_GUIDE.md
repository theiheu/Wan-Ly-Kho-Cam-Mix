# 🚀 Windows Installer Build Guide

Hướng dẫn chi tiết để build và tạo Windows installer cho **Phần mềm Quản lý Cám - Trại Gà**.

## 📋 Tổng quan

Hệ thống build mới cung cấp:
- ✅ **Professional Windows Installer** (.exe) với NSIS/Inno Setup
- ✅ **Advanced Batch Installer** với GUI đẹp
- ✅ **Desktop & Start Menu Shortcuts** tự động
- ✅ **Proper Uninstaller** với registry cleanup
- ✅ **Application Icon** (.ico) tự động tạo
- ✅ **Enhanced PyInstaller** configuration
- ✅ **Multiple Installation Options**

## 🔧 Yêu cầu hệ thống

### Bắt buộc
- **Windows 10/11** (64-bit)
- **Python 3.6+**
- **PyQt5 >= 5.15.0**
- **PyInstaller >= 5.0.0**

### Tùy chọn (cho Professional Installer)
- **NSIS** (Nullsoft Scriptable Install System)
- **Inno Setup** (khuyến nghị)

## 🚀 Quick Start

### 1. Setup môi trường (lần đầu)
```bash
python setup_build_environment.py
```

### 2. Build nhanh (chỉ executable)
```bash
quick_build.bat
# hoặc
python tools/build_windows.py
```

### 3. Build đầy đủ (executable + installer)
```bash
full_build.bat
# hoặc
python build_complete.py
```

## 📁 Cấu trúc file sau build

```
📦 Project Root
├── 📁 dist/
│   └── 📁 ChickenFarmManager/
│       └── 📄 ChickenFarmManager.exe        # Executable chính
├── 📄 ChickenFarmManager_v2.0.0_Setup.exe   # Professional Installer
├── 📄 install_advanced.bat                  # Advanced Batch Installer
├── 📄 install.bat                          # Basic Batch Installer
├── 📄 LICENSE.txt                          # License file
├── 📄 README_DISTRIBUTION.txt              # Hướng dẫn phân phối
└── 📁 packages/                            # Distribution packages
    ├── 📄 ChickenFarmManager_v2.0.0_Portable.zip
    └── 📄 ChickenFarmManager_v2.0.0_Installer.zip
```

## 🎯 Các loại installer

### 1. Professional Windows Installer (.exe)
**File**: `ChickenFarmManager_v2.0.0_Setup.exe`

**Tính năng**:
- ✅ Modern UI với wizard
- ✅ License agreement
- ✅ Component selection
- ✅ Custom install directory
- ✅ Desktop & Start Menu shortcuts
- ✅ Registry integration
- ✅ Proper uninstaller
- ✅ Automatic upgrade detection

**Yêu cầu**: NSIS hoặc Inno Setup

### 2. Advanced Batch Installer (.bat)
**File**: `install_advanced.bat`

**Tính năng**:
- ✅ Colorful console UI
- ✅ Administrator check
- ✅ Multiple install locations
- ✅ Optional shortcuts
- ✅ Uninstaller creation
- ✅ Launch option

**Yêu cầu**: Chỉ Windows

### 3. Basic Batch Installer (.bat)
**File**: `install.bat`

**Tính năng**:
- ✅ Simple installation
- ✅ Fixed install location
- ✅ Basic shortcuts

## 🔧 Cài đặt công cụ tạo installer

### NSIS (Khuyến nghị cho file nhỏ)
1. Tải từ: https://nsis.sourceforge.io/
2. Cài đặt với default settings
3. Thêm vào PATH nếu cần

### Inno Setup (Khuyến nghị cho UI đẹp)
1. Tải từ: https://jrsoftware.org/isinfo.php
2. Cài đặt với default settings
3. Không cần thêm vào PATH

## 📋 Build Scripts chi tiết

### setup_build_environment.py
**Mục đích**: Thiết lập môi trường build lần đầu
```bash
python setup_build_environment.py
```

**Chức năng**:
- Kiểm tra Python version
- Cài đặt required packages
- Kiểm tra installer tools
- Tạo build scripts
- Test môi trường

### build_complete.py
**Mục đích**: Build hoàn chỉnh từ đầu đến cuối
```bash
python build_complete.py
```

**Quy trình**:
1. Kiểm tra requirements
2. Dọn dẹp build cũ
3. Build executable
4. Tạo installers
5. Tạo packages

### tools/build_windows.py
**Mục đích**: Build executable với PyInstaller
```bash
python tools/build_windows.py
```

**Tính năng**:
- Enhanced PyInstaller config
- Auto icon generation
- Version info creation
- NSIS script generation

### tools/create_windows_installer.py
**Mục đích**: Tạo các loại installer
```bash
python tools/create_windows_installer.py
```

**Tính năng**:
- Professional installer (NSIS/Inno)
- Advanced batch installer
- License file creation

## 🎨 Icon System

Hệ thống tự động tạo icon từ `src/utils/app_icon.py`:

```
📁 src/data/icons/
├── 📄 app_icon.ico           # Windows icon
├── 📄 app_icon_16x16.png     # Small icon
├── 📄 app_icon_32x32.png     # Medium icon
├── 📄 app_icon_64x64.png     # Large icon
├── 📄 app_icon_128x128.png   # Extra large
└── 📄 app_icon_256x256.png   # High DPI
```

## 🔍 Troubleshooting

### Build thất bại
```bash
# 1. Dọn dẹp và thử lại
python clean.py
python build_complete.py

# 2. Kiểm tra dependencies
pip install -r requirements-build.txt

# 3. Test từng bước
python tools/build_windows.py
python tools/create_windows_installer.py
```

### Installer không tạo được
```bash
# Kiểm tra NSIS/Inno Setup
makensis /VERSION
# hoặc kiểm tra Inno Setup trong Program Files

# Fallback: sử dụng batch installer
python tools/create_windows_installer.py
```

### Icon không hiển thị
```bash
# Tạo lại icon
python -c "from tools.build_windows import create_app_icon; create_app_icon()"
```

## 📦 Distribution

### Portable Version
- Copy thư mục `dist/ChickenFarmManager/`
- Chạy trực tiếp `ChickenFarmManager.exe`
- Không cần cài đặt

### Installer Version
- Chạy `ChickenFarmManager_v2.0.0_Setup.exe`
- Hoặc `install_advanced.bat`
- Tự động tạo shortcuts và uninstaller

## 🎊 Kết luận

Hệ thống build mới cung cấp:
- **3 loại installer** phù hợp mọi nhu cầu
- **Tự động hóa hoàn toàn** quy trình build
- **Professional appearance** cho end users
- **Easy maintenance** cho developers

Chọn installer phù hợp:
- **Professional**: Cho phân phối chính thức
- **Advanced Batch**: Cho internal deployment
- **Portable**: Cho testing và demo
