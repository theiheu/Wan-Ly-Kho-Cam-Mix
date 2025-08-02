# 🐔 Phần mềm Quản lý Cám - Trại Gà

Hệ thống quản lý toàn diện cho trại gà với giao diện PyQt5 hiện đại và các tính năng chuyên nghiệp.

## 🎯 Tính năng chính

### 📊 Quản lý lượng cám hàng ngày
- Nhập liệu lượng cám cho từng chuồng
- Tính toán tự động tổng lượng cám
- Lưu trữ lịch sử sử dụng cám với báo cáo chi tiết

### 📦 Hệ thống CRUD tồn kho hoàn chỉnh
- **Create**: Thêm mới nguyên liệu vào kho
- **Read**: Xem danh sách tồn kho với thông tin chi tiết
- **Update**: Cập nhật số lượng, giá cả nguyên liệu
- **Delete**: Xóa nguyên liệu không còn sử dụng

### 🧪 Quản lý công thức dinh dưỡng
- Tạo và chỉnh sửa công thức cám
- Tính toán tỷ lệ dinh dưỡng
- Quản lý công thức trộn cám với preset

### 📈 Báo cáo và phân tích
- Báo cáo sử dụng cám theo ngày/tuần/tháng
- Phân tích xu hướng tiêu thụ
- Xuất báo cáo Excel với charts

### 📋 Thao tác hàng loạt
- Import/Export dữ liệu Excel
- Backup và restore dữ liệu
- Cập nhật hàng loạt với validation

## 🚀 Quick Start

### Chạy ứng dụng
```bash
python run.py
```

### Build và Package
```bash
# Build executable
python build.py

# Tạo packages phân phối
python package.py

# Dọn dẹp file tạm
python clean.py

# Rebuild hoàn chỉnh
python rebuild.py
```

## 📁 Cấu trúc dự án

```
Wan_Ly_Kho_Cam_Mix-3.3/
├── 📁 src/                    # 🎯 Source code chính
│   ├── main.py               # Entry point của ứng dụng
│   ├── config/               # Configuration và settings
│   ├── controllers/          # Business logic controllers
│   ├── core/                 # Core functionality
│   ├── data/                 # Data files, presets, reports
│   ├── models/               # Data models và schemas
│   ├── services/             # Service layer
│   ├── ui/                   # User interface components
│   └── utils/                # Utility functions
├── 📁 tools/                  # 🔧 Build và development tools
│   ├── build_windows.py      # Build executable cho Windows
│   ├── create_package.py     # Tạo packages phân phối
│   ├── smart_cleanup.py      # Dọn dẹp thông minh
│   └── rebuild_all.py        # Rebuild hoàn chỉnh
├── 📁 scripts/                # 🤖 Automation scripts
│   ├── build_complete.bat    # Build script hoàn chỉnh
│   ├── clean_build.bat       # Dọn dẹp toàn bộ
│   ├── smart_clean.bat       # Dọn dẹp thông minh
│   └── *.bat                 # Các batch scripts khác
├── 📁 examples/               # 🧪 Demo và examples
│   ├── demo_responsive_dialog.py  # Demo responsive UI
│   └── visualize_app.py      # Tool trực quan hóa
├── 📁 docs/                   # 📖 Documentation
│   ├── CLEANUP_GUIDE.md      # Hướng dẫn dọn dẹp
│   └── README_DISTRIBUTION.txt # Hướng dẫn phân phối
├── 📁 tests/                  # 🧪 Test files
├── 📁 temp/                   # 🗂️ Temporary files
├── 📁 dist/                   # 📦 Built executables
├── 📁 packages/               # 📦 Distribution packages
├── 🐍 run.py                  # Main entry point
├── 🐍 build.py               # Build wrapper
├── 🐍 package.py             # Package wrapper
├── 🐍 clean.py               # Cleanup wrapper
├── 🐍 rebuild.py             # Rebuild wrapper
├── 📄 requirements.txt       # Runtime dependencies
├── 📄 requirements-build.txt # Build dependencies
└── 📄 README.md              # This file
```

## 🛠️ Development Tools

### Build Tools (tools/)
- **build_windows.py**: Build executable cho Windows với PyInstaller
- **create_package.py**: Tạo packages portable và installer
- **smart_cleanup.py**: Dọn dẹp thông minh, giữ lại kết quả build
- **rebuild_all.py**: Script tổng hợp rebuild từ đầu đến cuối

### Automation Scripts (scripts/)
- **build_complete.bat**: Build hoàn chỉnh với batch script
- **clean_build.bat**: Dọn dẹp toàn bộ (nguy hiểm)
- **smart_clean.bat**: Wrapper cho smart cleanup
- **quick_build.bat**: Build nhanh

### Examples (examples/)
- **demo_responsive_dialog.py**: Demo tính năng responsive UI
- **visualize_app.py**: Tool trực quan hóa dữ liệu

## 🔧 Yêu cầu hệ thống

### Runtime
- Python 3.6+
- PyQt5 >= 5.15.0
- pandas >= 1.0.0
- matplotlib >= 3.3.0
- openpyxl >= 3.0.0

### Build
- pyinstaller >= 5.0.0
- setuptools >= 60.0.0
- wheel >= 0.37.0

### Cài đặt
```bash
# Runtime dependencies
pip install -r requirements.txt

# Build dependencies
pip install -r requirements-build.txt
```

## 📖 Documentation

- **docs/CLEANUP_GUIDE.md**: Hướng dẫn chi tiết về dọn dẹp build files
- **docs/README_DISTRIBUTION.txt**: Hướng dẫn phân phối phần mềm

## 🧪 Testing

```bash
# Chạy tests (nếu có)
python -m pytest tests/

# Test build
python build.py

# Test package
python package.py
```

## 📦 Distribution

### Tạo packages
```bash
# Tạo cả portable và installer
python package.py

# Hoặc sử dụng tools trực tiếp
python tools/create_package.py
```

### Kết quả
- **Portable**: Giải nén và chạy trực tiếp
- **Installer**: Chạy install.bat với quyền Admin
- **ZIP files**: Sẵn sàng phân phối

## 🤝 Contributing

1. Fork dự án
2. Tạo feature branch
3. Commit changes
4. Push to branch
5. Tạo Pull Request

## 📝 License

© 2024 Minh-Tan_Phat. All rights reserved.

## 🆘 Support

- **Issues**: Tạo issue trên GitHub
- **Documentation**: Xem thư mục docs/
- **Examples**: Xem thư mục examples/
