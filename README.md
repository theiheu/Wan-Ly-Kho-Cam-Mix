# 🐔 Quản Lý Kho Cám & Mix - Chicken Farm Manager

Hệ thống quản lý kho cám và thức ăn gia súc chuyên nghiệp cho trang trại gà.

## 🚀 Tính Năng Chính

### 📦 Quản Lý Kho
- **Quản lý tồn kho**: Theo dõi số lượng cám, mix và nguyên liệu
- **Cảnh báo tồn kho thấp**: Thông báo khi nguyên liệu sắp hết
- **Nhập/Xuất kho**: Ghi nhận các giao dịch nhập xuất
- **Báo cáo tồn kho**: Báo cáo chi tiết theo thời gian

### 🧮 Quản Lý Công Thức
- **Công thức cám**: Tạo và quản lý công thức sản xuất cám
- **Công thức mix**: Quản lý công thức thức ăn hỗn hợp
- **Tính toán nguyên liệu**: Tự động tính toán nguyên liệu cần thiết
- **Preset công thức**: Lưu trữ các công thức thường dùng

### 👥 Quản Lý Nhân Sự
- **Quản lý nhân viên**: Thông tin nhân viên và chức vụ
- **Chấm công**: Theo dõi giờ làm việc và nghỉ phép
- **Tính lương**: Tự động tính lương theo công và thưởng
- **Báo cáo nhân sự**: Báo cáo chi tiết về nhân sự

### 📊 Báo Cáo & Thống Kê
- **Báo cáo hàng ngày**: Tình hình sử dụng cám theo ngày
- **Báo cáo tổng hợp**: Xuất Excel với nhiều định dạng
- **Thống kê tiêu thụ**: Phân tích xu hướng sử dụng
- **Dự báo nhu cầu**: Dự đoán nhu cầu nguyên liệu

## 🛠️ Cài Đặt & Sử Dụng

### 📥 Tải Về & Cài Đặt

#### 🎯 KHUYẾN NGHỊ: Ứng Dụng Tự Cài Đặt (Professional)

```bash
# Từ thư mục installer/build
cd installer\build
python builder.py
```

**Kết quả:** `installer\output\Quan_Ly_Kho_Cam_&_Mix.exe`

**Tính năng:**
- ✅ **Tự động cài đặt**: Tự cài vào Program Files khi chạy lần đầu
- ✅ **Lưu trữ dữ liệu bền vững**: Dữ liệu được lưu trong AppData
- ✅ **Tạo shortcut**: Tự động tạo shortcut trên Desktop
- ✅ **Copy dữ liệu JSON**: Tự động copy các file cấu hình cần thiết
- ✅ **Trải nghiệm chuyên nghiệp**: Hoạt động như phần mềm thương mại

#### 🔄 Quy Trình Build Hoàn Chỉnh

```bash
# Từ thư mục installer/build
cd installer\build
python build_workflow.py
```

### 🏃‍♂️ Chạy Ứng Dụng

#### Từ Source Code
```bash
# Cài đặt dependencies
pip install -r requirements.txt

# Chạy ứng dụng
python run.py
```

#### Từ Executable
- Chạy file `Quan_Ly_Kho_Cam_&_Mix.exe` đã build
- Hoặc sử dụng installer đã tạo

### 📋 Yêu Cầu Hệ Thống

#### Môi Trường Phát Triển
- Windows 10/11 (64-bit)
- Python 3.8+
- PyQt5
- Pandas, NumPy, Matplotlib
- OpenPyXL (cho xuất Excel)

#### Hệ Thống Đích
- Windows 10 (64-bit) trở lên
- 4GB RAM tối thiểu
- 200MB dung lượng trống
- Quyền Administrator (cho cài đặt)

## 📁 Cấu Trúc Dự Án

```text
Wan_Ly_Kho_Cam_Mix/
├── src/                           # Mã nguồn chính
│   ├── main.py                   # Entry point
│   ├── ui/                       # Giao diện người dùng
│   ├── core/                     # Logic nghiệp vụ
│   ├── services/                 # Dịch vụ và xử lý
│   ├── utils/                    # Tiện ích
│   └── data/                     # Dữ liệu và cấu hình
│       ├── config/               # File cấu hình JSON
│       ├── business/             # Dữ liệu nghiệp vụ
│       ├── reports/              # Báo cáo đã tạo
│       └── exports/              # File xuất Excel
├── installer/                    # Hệ thống installer
│   ├── build/                    # Scripts build
│   │   ├── builder.py           # Build chính (có copy JSON)
│   │   ├── build_workflow.py    # Quy trình build hoàn chỉnh
│   │   └── test_copy_json.py    # Test chức năng copy JSON
│   ├── scripts/                  # Scripts installer
│   ├── resources/                # Tài nguyên installer
│   └── output/                   # Kết quả build
├── requirements.txt              # Dependencies Python
└── run.py                       # Script chạy ứng dụng
```

## 🔧 Tính Năng Mới

### 📋 Copy Dữ Liệu JSON Tự Động
Khi build ứng dụng, hệ thống sẽ tự động copy các file JSON cần thiết:

**File Config được copy:**
- `bonus_rates.json` - Tỷ lệ thưởng
- `feed_formula.json` - Công thức cám
- `mix_formula.json` - Công thức mix
- `inventory.json` - Dữ liệu tồn kho
- `packaging_info.json` - Thông tin đóng gói
- `salary_rates.json` - Bảng lương
- `thresholds.json` - Ngưỡng cảnh báo
- `user_preferences.json` - Cài đặt người dùng
- Và nhiều file khác...

### 🧪 Test Chức Năng Copy JSON
```bash
# Test chức năng copy JSON
cd installer\build
python test_copy_json.py
```

## 🎯 Hướng Dẫn Sử Dụng

### 1. Quản Lý Kho
- Mở tab "Quản Lý Kho"
- Nhập/cập nhật số lượng tồn kho
- Thiết lập ngưỡng cảnh báo
- Xem báo cáo tồn kho

### 2. Tạo Công Thức
- Mở tab "Công Thức"
- Chọn loại công thức (Cám/Mix)
- Nhập tỷ lệ nguyên liệu
- Lưu preset cho lần sau

### 3. Quản Lý Nhân Sự
- Mở tab "Nhân Sự"
- Thêm/sửa thông tin nhân viên
- Chấm công hàng ngày
- Tính lương theo tháng

### 4. Xuất Báo Cáo
- Chọn loại báo cáo cần xuất
- Thiết lập khoảng thời gian
- Chọn thư mục lưu file
- Xuất ra Excel

## 🐛 Khắc Phục Sự Cố

### Lỗi Build
```bash
# Lỗi PyInstaller không tìm thấy
pip install pyinstaller>=5.0.0

# Lỗi thiếu dependencies
pip install -r requirements.txt

# Lỗi quyền truy cập
# Chạy Command Prompt với quyền Administrator
```

### Lỗi Chạy Ứng Dụng
- Kiểm tra file cấu hình JSON có tồn tại
- Đảm bảo thư mục data có quyền ghi
- Kiểm tra log file để xem lỗi chi tiết

## 📄 Giấy Phép

© 2025 Minh-Tan_Phat. Tất cả quyền được bảo lưu.

---

**Được xây dựng với ❤️ cho quản lý trang trại chuyên nghiệp**
