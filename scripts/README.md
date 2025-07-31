# 🤖 Automation Scripts

Thư mục này chứa các batch scripts để tự động hóa quy trình build và deployment.

## 📋 Danh sách Scripts

### 🏗️ build_complete.bat
**Mục đích**: Build hoàn chỉnh với batch script

**Quy trình**:
1. Dọn dẹp build cũ (clean_build.bat)
2. Build executable (tools/build_windows.py)
3. Tạo packages (tools/create_package.py)
4. Báo cáo kết quả

**Sử dụng**:
```cmd
cd scripts
build_complete.bat
```

### 🗑️ clean_build.bat
**Mục đích**: Dọn dẹp TOÀN BỘ file build (NGUY HIỂM)

**Xóa**:
- Thư mục build/, dist/, packages/
- File *.spec, *.zip, version_info.txt
- Tất cả __pycache__/
- File install.bat, README_DISTRIBUTION.txt

**Cảnh báo**: Script này xóa cả kết quả build!

**Sử dụng**:
```cmd
cd scripts
clean_build.bat
```

### 🧹 smart_clean.bat
**Mục đích**: Wrapper cho smart cleanup Python script

**Tính năng**:
- Gọi tools/smart_cleanup.py
- Dọn dẹp thông minh, giữ lại kết quả build
- Giao diện batch thân thiện

**Sử dụng**:
```cmd
cd scripts
smart_clean.bat
```

### ⚡ quick_build.bat
**Mục đích**: Build nhanh chỉ executable

**Quy trình**:
1. Dọn dẹp thông minh
2. Build executable
3. Không tạo packages

**Sử dụng**:
```cmd
cd scripts
quick_build.bat
```

### 🔧 build_setup.bat
**Mục đích**: Setup môi trường build

**Tính năng**:
- Kiểm tra Python
- Cài đặt dependencies
- Kiểm tra tools cần thiết

**Sử dụng**:
```cmd
cd scripts
build_setup.bat
```

## 🚀 Quy trình sử dụng

### Build hoàn chỉnh
```cmd
cd scripts
build_complete.bat
```

### Build nhanh
```cmd
cd scripts
quick_build.bat
```

### Dọn dẹp an toàn
```cmd
cd scripts
smart_clean.bat
```

### Dọn dẹp toàn bộ (cẩn thận!)
```cmd
cd scripts
clean_build.bat
```

## 📊 So sánh Scripts

| Script | Dọn dẹp | Build | Package | An toàn | Tốc độ |
|--------|---------|-------|---------|---------|--------|
| build_complete.bat | ✅ | ✅ | ✅ | 🟡 | 🐌 |
| quick_build.bat | ✅ | ✅ | ❌ | 🟢 | 🚀 |
| smart_clean.bat | ✅ | ❌ | ❌ | 🟢 | ⚡ |
| clean_build.bat | ✅ | ❌ | ❌ | 🔴 | ⚡ |

## ⚙️ Cấu hình

### Encoding
Tất cả batch files sử dụng UTF-8:
```cmd
chcp 65001 >nul
```

### Error Handling
Scripts kiểm tra error code và dừng nếu có lỗi:
```cmd
if %errorLevel% neq 0 (
    echo ❌ Lỗi!
    pause
    exit /b 1
)
```

### User Confirmation
Scripts quan trọng yêu cầu xác nhận:
```cmd
choice /C YN /M "Tiếp tục (Y/N)"
```

## 🐛 Troubleshooting

### Script không chạy
1. Chạy từ thư mục scripts/
2. Kiểm tra quyền file
3. Chạy với quyền Administrator nếu cần

### Lỗi encoding
- Scripts đã cấu hình UTF-8
- Nếu vẫn lỗi: Sử dụng Python scripts thay thế

### Python script không tìm thấy
- Kiểm tra đường dẫn tương đối
- Đảm bảo chạy từ thư mục scripts/

## 💡 Tips

### Sử dụng hàng ngày
- **quick_build.bat**: Cho development
- **smart_clean.bat**: Dọn dẹp thường xuyên

### Sử dụng production
- **build_complete.bat**: Cho release
- **clean_build.bat**: Khi cần reset hoàn toàn

### Tự động hóa
```cmd
# Build tự động mỗi ngày
schtasks /create /tn "Daily Build" /tr "C:\path\to\scripts\build_complete.bat" /sc daily
```

## 📝 Notes

- Tất cả scripts hỗ trợ tiếng Việt
- Scripts tự động pause để xem kết quả
- Error handling đầy đủ
- Tương thích Windows 10/11
