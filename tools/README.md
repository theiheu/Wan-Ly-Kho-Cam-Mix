# 🔧 Build và Development Tools

Thư mục này chứa các công cụ build và development cho dự án Chicken Farm Management.

## 📋 Danh sách Tools

### 🏗️ build_windows.py
**Mục đích**: Build executable cho Windows với PyInstaller

**Tính năng**:
- Tạo file .spec tự động
- Tạo version info cho Windows
- Build executable với tất cả dependencies
- Tạo installer script
- Tạo README phân phối

**Sử dụng**:
```bash
python tools/build_windows.py
# Hoặc từ root
python build.py
```

### 📦 create_package.py
**Mục đích**: Tạo packages phân phối

**Tính năng**:
- Tạo package portable (không cần cài đặt)
- Tạo package installer (với script cài đặt)
- Tự động tạo file ZIP
- Tự động xóa packages cũ

**Sử dụng**:
```bash
python tools/create_package.py
# Hoặc từ root
python package.py
```

### 🧹 smart_cleanup.py
**Mục đích**: Dọn dẹp thông minh file build

**Tính năng**:
- Xóa file tạm thời và build artifacts
- Giữ lại kết quả build (dist/, packages/, *.zip)
- Tùy chọn xóa packages cũ
- Hiển thị thống kê file được giữ lại

**Sử dụng**:
```bash
python tools/smart_cleanup.py
# Hoặc từ root
python clean.py
```

### 🔄 rebuild_all.py
**Mục đích**: Rebuild hoàn chỉnh từ đầu đến cuối

**Tính năng**:
- Quy trình tự động: Cleanup → Build → Package
- Kiểm tra dependencies
- Báo cáo kết quả chi tiết
- Thống kê thời gian build

**Sử dụng**:
```bash
python tools/rebuild_all.py
# Hoặc từ root
python rebuild.py
```

## 🚀 Quy trình Build

### Build đơn lẻ
```bash
# 1. Dọn dẹp
python clean.py

# 2. Build
python build.py

# 3. Package
python package.py
```

### Build hoàn chỉnh
```bash
# Tất cả trong một lệnh
python rebuild.py
```

## 📁 Kết quả Build

### Sau khi build
- `dist/ChickenFarmManager/` - Executable và dependencies
- `ChickenFarmManager.spec` - PyInstaller spec file
- `version_info.txt` - Windows version info
- `install.bat` - Script cài đặt đơn giản
- `README_DISTRIBUTION.txt` - Hướng dẫn phân phối

### Sau khi package
- `packages/ChickenFarmManager_v2.0.0_Portable/` - Package portable
- `packages/ChickenFarmManager_v2.0.0_Installer/` - Package installer
- `ChickenFarmManager_v2.0.0_Portable.zip` - ZIP portable
- `ChickenFarmManager_v2.0.0_Installer.zip` - ZIP installer

## ⚙️ Cấu hình

### Thông tin ứng dụng
Các thông tin này được định nghĩa trong từng script:
```python
APP_NAME = "ChickenFarmManager"
APP_DISPLAY_NAME = "Phần mềm Quản lý Cám - Trại Gà"
APP_VERSION = "2.0.0"
APP_AUTHOR = "Minh-Tan_Phat"
```

### Dependencies
- PyInstaller >= 5.0.0
- setuptools >= 60.0.0
- wheel >= 0.37.0

## 🐛 Troubleshooting

### Build thất bại
1. Kiểm tra dependencies: `pip install -r requirements-build.txt`
2. Dọn dẹp và thử lại: `python clean.py && python build.py`
3. Chạy rebuild hoàn chỉnh: `python rebuild.py`

### Package thất bại
1. Đảm bảo đã build trước: `python build.py`
2. Kiểm tra thư mục dist/ tồn tại
3. Chạy lại: `python package.py`

### Lỗi "file already exists"
- Đã được sửa: Scripts tự động xóa file cũ
- Nếu vẫn lỗi: Chạy `python clean.py` trước

## 📝 Notes

- Tất cả scripts đều có wrapper trong thư mục root
- Scripts tự động tạo thư mục cần thiết
- Kết quả build được giữ lại sau cleanup thông minh
- Hỗ trợ tiếng Việt hoàn toàn
