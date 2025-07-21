# Phần mềm Quản lý Cám - Trại Gà

Phần mềm quản lý cám cho trại gà, giúp theo dõi lượng cám sử dụng hàng ngày và quản lý tồn kho.

## Cấu trúc thư mục

```
.
├── run.py                  # Script chạy ứng dụng chính
├── visualize_app.py        # Script chạy công cụ trực quan hóa
├── requirements.txt        # Các thư viện cần thiết
├── src/                    # Thư mục mã nguồn
│   ├── main.py             # Điểm khởi đầu của ứng dụng
│   ├── core/               # Các module lõi
│   │   ├── formula_manager.py    # Quản lý công thức cám và mix
│   │   └── inventory_manager.py  # Quản lý tồn kho
│   ├── utils/              # Các tiện ích
│   │   ├── app_icon.py           # Tạo biểu tượng ứng dụng
│   │   ├── default_formulas.py   # Công thức mặc định
│   │   ├── init_data.py          # Khởi tạo dữ liệu
│   │   └── visualize.py          # Trực quan hóa dữ liệu
│   └── data/               # Dữ liệu ứng dụng
│       ├── config/         # Cấu hình
│       │   ├── feed_formula.json      # Công thức cám hiện tại
│       │   ├── mix_formula.json       # Công thức mix hiện tại
│       │   ├── formula_links.json     # Liên kết giữa công thức cám và mix
│       │   └── inventory.json         # Dữ liệu tồn kho
│       ├── presets/        # Công thức đã lưu
│       │   ├── feed/       # Công thức cám đã lưu
│       │   └── mix/        # Công thức mix đã lưu
│       └── reports/        # Báo cáo và hình ảnh trực quan hóa
```

## Cài đặt

1. Cài đặt Python 3.6 trở lên
2. Cài đặt các thư viện cần thiết:

```bash
pip install -r requirements.txt
```

## Chạy ứng dụng

### Chạy ứng dụng chính

```bash
python run.py
```

### Chạy công cụ trực quan hóa

```bash
python visualize_app.py
```

## Tính năng

- Quản lý công thức cám và mix
- Theo dõi lượng cám sử dụng hàng ngày theo khu và trại
- Quản lý tồn kho nguyên liệu
- Tính toán lượng cám và mix cần sử dụng
- Lưu và tải các công thức đã lưu
- Gắn công thức mix vào công thức cám
- Trực quan hóa dữ liệu lượng cám
- Xuất báo cáo ra Excel

## Hướng dẫn sử dụng

### Tab Tổng quan

1. Nhập lượng cám sử dụng cho từng trại theo buổi (sáng/chiều)
2. Nhấn "Tính Toán" để xem kết quả
3. Nhấn "Lưu Báo Cáo" để lưu kết quả
4. Nhấn "Xuất Excel" để xuất báo cáo ra file Excel

### Tab Tồn Kho

1. Xem tồn kho hiện tại của các nguyên liệu
2. Nhấn "Cập nhật tồn kho" để cập nhật số lượng

### Tab Công Thức

1. Chọn công thức có sẵn để tải
2. Nhấn "Cập nhật" để cập nhật công thức đang chọn
3. Nhấn "Lưu thành" để lưu công thức hiện tại thành công thức mới
4. Nhấn "Xóa" để xóa công thức đang chọn
5. Chọn công thức mix cho Nguyên liệu tổ hợp và nhấn "Gắn công thức"

### Tab Lịch Sử

1. Chọn ngày để xem dữ liệu lịch sử
2. Chọn ngày để so sánh và nhấn "So Sánh"
3. Nhấn "Hiển Thị Biểu Đồ" để xem biểu đồ trực quan
4. Nhấn "Xuất Excel" để xuất dữ liệu lịch sử ra file Excel

## Tác giả

© 2023 Minh-Tan_Phat
