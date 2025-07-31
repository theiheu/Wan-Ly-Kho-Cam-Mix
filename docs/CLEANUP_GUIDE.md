# 🧹 Hướng dẫn Dọn dẹp Build Files

## Tổng quan

Dự án có 3 script dọn dẹp khác nhau để phục vụ các mục đích khác nhau:

## 📋 Các Script Dọn dẹp

### 1. 🎯 `smart_cleanup.py` / `smart_clean.bat` (KHUYẾN NGHỊ)

**Mục đích**: Dọn dẹp thông minh, GIỮ LẠI kết quả build

**Sẽ XÓA:**

- ✅ Thư mục `build/` (file tạm PyInstaller)
- ✅ File `*.spec` (tự động tạo)
- ✅ File `version_info.txt`
- ✅ Tất cả thư mục `__pycache__/` và file `*.pyc`
- ✅ File log, temp (_.log, _.tmp, \*.temp)

**Sẽ GIỮ LẠI:**

- 📦 Thư mục `dist/` (executable)
- 📦 Thư mục `packages/` (package phân phối)
- 📦 File `*.zip` (package nén)
- 📦 File `install.bat`, `README_DISTRIBUTION.txt`

**Cách sử dụng:**

```bash
# Chạy Python script
python smart_cleanup.py

# Hoặc chạy batch file
smart_clean.bat
```

### 2. 🗑️ `clean_build.bat` (NGUY HIỂM)

**Mục đích**: Dọn dẹp TOÀN BỘ, bao gồm cả kết quả build

**Sẽ XÓA TOÀN BỘ:**

- ❌ Thư mục `build/`
- ❌ Thư mục `dist/` (executable)
- ❌ Thư mục `packages/`
- ❌ File `*.zip`
- ❌ File `*.spec`, `version_info.txt`
- ❌ Tất cả `__pycache__/`

**Cách sử dụng:**

```bash
clean_build.bat
```

### 3. 📁 `cleanup.py` (CŨ)

**Mục đích**: Script cũ, chỉ dọn dẹp file development

## 🚀 Quy trình Build & Cleanup

### Quy trình thông thường:

1. **Phát triển code** → Tạo nhiều `__pycache__/`
2. **Dọn dẹp thông minh**: `python smart_cleanup.py`
3. **Build mới**: `python build_windows.py`
4. **Tạo package**: `python create_package.py`
5. **Phân phối**: Sử dụng file `.zip`

### Khi cần build từ đầu:

1. **Dọn dẹp toàn bộ**: `clean_build.bat`
2. **Build hoàn chỉnh**: `python build_windows.py`
3. **Tạo package**: `python create_package.py`

## 📊 So sánh Script

| Script             | Xóa build/ | Xóa dist/ | Xóa packages/ | Xóa \*.zip | Xóa **pycache** | An toàn |
| ------------------ | ---------- | --------- | ------------- | ---------- | --------------- | ------- |
| `smart_cleanup.py` | ✅         | ❌        | ❌            | ❌         | ✅              | 🟢 Cao  |
| `clean_build.bat`  | ✅         | ✅        | ✅            | ✅         | ✅              | 🔴 Thấp |
| `cleanup.py`       | ❌         | ❌        | ❌            | ❌         | ✅              | 🟢 Cao  |

## 💡 Khuyến nghị

### Sử dụng hàng ngày:

```bash
python smart_cleanup.py
```

### Khi gặp lỗi build:

```bash
clean_build.bat
python build_windows.py
python create_package.py
```

### Trước khi commit code:

```bash
python smart_cleanup.py
```

## 🔍 Kiểm tra kết quả

Sau khi dọn dẹp, kiểm tra:

- Thư mục `dist/` có còn không?
- File `.zip` có còn không?
- Thư mục `__pycache__/` đã biến mất?

## ⚠️ Lưu ý quan trọng

1. **Backup trước khi dọn dẹp**: Nếu không chắc chắn
2. **Sử dụng `smart_cleanup.py`**: Cho hầu hết trường hợp
3. **Chỉ dùng `clean_build.bat`**: Khi thực sự cần build từ đầu
4. **Kiểm tra kết quả**: Sau mỗi lần dọn dẹp

## 🚀 Script Tổng hợp

### `rebuild_all.py` (MỚI)

**Mục đích**: Rebuild hoàn chỉnh từ đầu đến cuối

**Quy trình tự động:**

1. Dọn dẹp thông minh
2. Build executable
3. Tạo packages
4. Báo cáo kết quả

**Cách sử dụng:**

```bash
python rebuild_all.py
```

## 🛠️ Troubleshooting

### Lỗi "Cannot create a file when that file already exists":

**Nguyên nhân**: Package/ZIP đã tồn tại từ build trước
**Giải pháp**: ✅ ĐÃ SỬA - Script tự động xóa file cũ

### Lỗi "Permission denied":

- Đóng tất cả file explorer đang mở thư mục dự án
- Đóng IDE/editor
- Chạy lại script

### Script không chạy:

- Kiểm tra Python đã cài đặt
- Chạy từ thư mục gốc dự án
- Kiểm tra quyền file

### File không bị xóa:

- Kiểm tra file có đang được sử dụng không
- Restart và thử lại
- Xóa thủ công nếu cần

### Build thất bại:

- Chạy `python rebuild_all.py` để rebuild từ đầu
- Kiểm tra dependencies: `pip install -r requirements-build.txt`
