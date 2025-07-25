# Kế hoạch Tái cấu trúc Ứng dụng

## Cấu trúc hiện tại

Hiện tại ứng dụng có cấu trúc như sau:

- File `main.py` rất lớn (>6000 dòng) chứa tất cả các thành phần UI và logic nghiệp vụ
- Một số module core đã được tách biệt như `FormulaManager`, `InventoryManager`
- Các công cụ phụ trợ như `visualize.py` đã được tách biệt

## Vấn đề

- Mã nguồn quá tập trung (monolithic), gây khó khăn trong việc bảo trì và phát triển
- Các chức năng UI và logic nghiệp vụ lẫn lộn trong cùng một file
- Thiếu tính module hóa cho việc mở rộng

## Kế hoạch tái cấu trúc

### 1. Cấu trúc thư mục mới

```
src/
  ├── core/                  # Logic nghiệp vụ chính
  │   ├── formula_manager.py
  │   ├── inventory_manager.py
  │   └── report_manager.py  # Mới - Quản lý báo cáo
  ├── data/                  # Không thay đổi - Dữ liệu
  ├── ui/                    # Mới - Giao diện người dùng
  │   ├── main_window.py     # Cửa sổ chính
  │   ├── widgets/           # Các widget tùy chỉnh
  │   │   ├── custom_spinbox.py
  │   │   └── custom_table.py
  │   └── tabs/              # Các tab UI
  │       ├── feed_usage_tab.py
  │       ├── inventory_tab.py
  │       ├── import_tab.py
  │       ├── formula_tab.py
  │       └── history_tab.py
  ├── utils/                 # Công cụ tiện ích
  │   ├── app_icon.py
  │   ├── default_formulas.py
  │   ├── init_data.py
  │   ├── formatting.py      # Mới - Các hàm định dạng
  │   ├── visualize.py
  │   └── constants.py       # Mới - Các hằng số
  └── services/              # Mới - Các dịch vụ ứng dụng
      ├── import_service.py
      ├── export_service.py
      └── history_service.py
```

### 2. Tách các file

#### Lớp chính `ChickenFarmApp` (main_window.py)

- Sẽ chứa `__init__`, `init_ui`, `create_menu_bar` và các phương thức chung
- Sẽ tạo các tab và điều phối chúng

#### Tách theo tab

- Mỗi tab được tách thành một file riêng trong `ui/tabs/`
- Mỗi file sẽ chứa một lớp chuyên biệt để xử lý tab đó

#### Tách widgets tùy chỉnh

- `CustomDoubleSpinBox` và các widget tùy chỉnh khác -> widgets/
- Các widget có thể tái sử dụng sẽ được tách riêng

#### Tách các dịch vụ nghiệp vụ

- Dịch vụ Import/Export -> services/
- Dịch vụ Báo cáo -> services/
- Các công cụ xử lý lịch sử -> services/

#### Tách các hàm tiện ích

- Hàm `format_number` và các hàm định dạng khác -> utils/formatting.py
- Các hằng số (`AREAS`, `SHIFTS`, `FARMS`) -> utils/constants.py

### 3. Kế hoạch triển khai

1. Tạo cấu trúc thư mục mới
2. Tách các hằng số và hàm tiện ích trước
3. Tách các widget tùy chỉnh
4. Tách từng tab riêng biệt
5. Tạo lớp main_window để điều phối
6. Cập nhật các import và tham chiếu
7. Kiểm thử từng phần đã tách

### 4. Lợi ích

- Dễ bảo trì và phát triển hơn
- Mã nguồn rõ ràng, tổ chức tốt hơn
- Dễ dàng thêm tính năng mới
- Tái sử dụng mã nguồn tốt hơn
- Hỗ trợ đồng thời làm việc bởi nhiều lập trình viên
