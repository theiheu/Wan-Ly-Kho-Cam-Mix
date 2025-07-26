# Hướng dẫn triển khai các tính năng mới

Tài liệu này cung cấp hướng dẫn chi tiết về cách triển khai và sử dụng các tính năng mới trong phần mềm Quản lý Cám - Trại Gà.

## Cài đặt

1. Đảm bảo bạn đã cài đặt tất cả các gói phụ thuộc mới:

```bash
pip install -r requirements.txt
```

2. Tạo các thư mục cần thiết (nếu chưa tồn tại):

```bash
mkdir -p src/data/cache logs metrics backups
```

## Sử dụng các tính năng mới

### 1. Hệ thống bộ nhớ đệm

#### Áp dụng bộ nhớ đệm cho hàm

```python
from src.utils.cache_manager import cached

# Áp dụng bộ nhớ đệm cho hàm tính toán công thức
@cached(ttl=300)  # Thời gian sống: 5 phút
def calculate_formula_ingredients(formula_name, batch_count):
    # Mã tính toán tốn kém
    return result

# Áp dụng bộ nhớ đệm với lưu trữ trên đĩa
@cached(ttl=3600, use_disk=True)  # Thời gian sống: 1 giờ
def load_historical_data(date_range):
    # Mã tải dữ liệu tốn kém
    return data
```

#### Sử dụng bộ nhớ đệm thủ công

```python
from src.utils.cache_manager import cache_manager

# Lưu giá trị vào bộ nhớ đệm
cache_manager.set("key_name", value, ttl=300)

# Lấy giá trị từ bộ nhớ đệm
value = cache_manager.get("key_name")

# Xóa giá trị khỏi bộ nhớ đệm
cache_manager.invalidate("key_name")

# Xóa toàn bộ bộ nhớ đệm
cache_manager.clear()
```

### 2. Xử lý lỗi và ghi nhật ký

#### Áp dụng xử lý lỗi tự động

```python
from src.utils.error_handler import try_except, logger

# Áp dụng xử lý lỗi tự động cho hàm
@try_except
def import_data_from_excel(file_path):
    # Mã có thể gây ra ngoại lệ
    pass

# Ghi nhật ký thủ công
logger.info("Thông tin: Đã nhập dữ liệu thành công")
logger.warning("Cảnh báo: Dữ liệu không đầy đủ")
logger.error("Lỗi: Không thể kết nối cơ sở dữ liệu")
```

#### Hiển thị hộp thoại thông báo

```python
from src.utils.error_handler import show_error_dialog, show_warning_dialog, show_info_dialog, confirm_dialog

# Hiển thị hộp thoại lỗi
show_error_dialog("Lỗi nhập dữ liệu", "Không thể nhập dữ liệu từ file Excel.")

# Hiển thị hộp thoại cảnh báo
show_warning_dialog("Cảnh báo tồn kho", "Một số thành phần sắp hết hàng.")

# Hiển thị hộp thoại thông tin
show_info_dialog("Thông báo", "Dữ liệu đã được lưu thành công.")

# Hiển thị hộp thoại xác nhận
if confirm_dialog("Xác nhận xóa", "Bạn có chắc chắn muốn xóa dữ liệu này không?"):
    # Người dùng đã xác nhận
    delete_data()
```

### 3. Giám sát hiệu suất

#### Đo thời gian thực thi

```python
from src.utils.performance_monitor import measure_time

# Đo thời gian thực thi của hàm
@measure_time
def calculate_feed_usage():
    # Mã cần đo thời gian
    pass
```

#### Đo sử dụng bộ nhớ

```python
from src.utils.performance_monitor import measure_memory

# Đo sử dụng bộ nhớ của hàm
@measure_memory
def process_large_dataset():
    # Mã sử dụng nhiều bộ nhớ
    pass
```

#### Sử dụng giám sát hiệu suất thủ công

```python
from src.utils.performance_monitor import performance_monitor

# Thêm chỉ số hiệu suất
performance_monitor.add_metric("custom_metric", value)

# Bắt đầu giám sát tài nguyên hệ thống
performance_monitor.start_monitoring(interval=5.0)  # Mỗi 5 giây

# Dừng giám sát
performance_monitor.stop_monitoring()

# Lưu chỉ số hiệu suất
performance_monitor.save_metrics("performance_report.json")

# Lấy tóm tắt hiệu suất
summary = performance_monitor.get_summary()
print(summary)
```

### 4. Tối ưu hóa

#### Tối ưu hóa hiển thị bảng

```python
from src.utils.optimizations import optimize_table_rendering

# Tối ưu hóa hiển thị bảng
optimize_table_rendering(self.feed_table)
# Cập nhật dữ liệu bảng
# ...
```

#### Cập nhật hàng loạt tồn kho

```python
from src.utils.optimizations import batch_update_inventory

# Cập nhật nhiều mục tồn kho cùng lúc
updates = {
    "Bắp": 1000,
    "Nành": 500,
    "DCP": 200
}
batch_update_inventory(self.inventory_manager, updates)
```

#### Nén dữ liệu báo cáo

```python
from src.utils.optimizations import optimize_report_storage

# Nén dữ liệu báo cáo
optimized_report = optimize_report_storage(report_data)
# Lưu báo cáo đã được tối ưu hóa
```

#### Sao lưu dữ liệu

```python
from src.utils.optimizations import backup_data_files

# Sao lưu dữ liệu quan trọng
backup_data_files(backup_dir="custom_backup_folder")
```

#### Hiển thị cảnh báo tồn kho thấp

```python
from src.utils.optimizations import show_low_stock_warning

# Hiển thị cảnh báo cho các mục tồn kho thấp
show_low_stock_warning(self.inventory_manager, daily_usage, threshold_days=7)
```

### 5. Khởi tạo ứng dụng

Mô-đun khởi tạo ứng dụng đã được tích hợp vào tệp `run.py`. Bạn không cần phải thay đổi gì để sử dụng nó.

Nếu bạn muốn tùy chỉnh cấu hình khởi tạo, bạn có thể chỉnh sửa tệp `src/data/config/app_config.json`:

```json
{
  "performance_monitoring": true,
  "monitoring_interval": 10.0,
  "cache_enabled": true,
  "backup_on_start": true,
  "backup_on_exit": true,
  "auto_save_interval": 300,
  "ui_theme": "default",
  "font_size": 14,
  "table_row_height": 30
}
```

## Ví dụ thực tế

### Ví dụ 1: Tối ưu hóa hàm tính toán cám

```python
from src.utils.cache_manager import cached
from src.utils.performance_monitor import measure_time
from src.utils.error_handler import try_except, logger

@cached(ttl=300)  # Bộ nhớ đệm trong 5 phút
@measure_time  # Đo thời gian thực thi
@try_except  # Xử lý lỗi tự động
def calculate_feed_usage(self):
    """Calculate feed usage based on input values"""
    logger.info("Bắt đầu tính toán lượng cám sử dụng")

    # Mã tính toán hiện tại
    # ...

    logger.info(f"Hoàn thành tính toán, tổng số mẻ: {total_batches}")
    return result
```

### Ví dụ 2: Tối ưu hóa hiển thị bảng lịch sử

```python
from src.utils.optimizations import optimize_table_rendering
from src.utils.error_handler import try_except, logger

@try_except
def update_history_table(self, report_data):
    """Update the history table with data from a report"""
    logger.info("Cập nhật bảng lịch sử")

    # Tối ưu hóa hiển thị bảng
    optimize_table_rendering(self.history_table)

    # Mã cập nhật bảng hiện tại
    # ...

    logger.info("Hoàn thành cập nhật bảng lịch sử")
```

### Ví dụ 3: Sao lưu và khôi phục dữ liệu

```python
from src.utils.optimizations import backup_data_files
from src.utils.error_handler import try_except, show_info_dialog, confirm_dialog

@try_except
def backup_data(self):
    """Backup application data"""
    # Tạo thư mục sao lưu với dấu thời gian
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"backups/manual_backup_{timestamp}"

    # Thực hiện sao lưu
    success = backup_data_files(backup_dir=backup_dir)

    if success:
        show_info_dialog("Sao lưu thành công", f"Dữ liệu đã được sao lưu vào thư mục {backup_dir}")
    else:
        show_error_dialog("Lỗi sao lưu", "Không thể sao lưu dữ liệu")
```

## Khắc phục sự cố

### Vấn đề: Ứng dụng khởi động chậm

- Kiểm tra tệp nhật ký trong thư mục `logs` để xác định điểm nghẽn
- Tắt giám sát hiệu suất bằng cách đặt `"performance_monitoring": false` trong tệp cấu hình
- Xóa bộ nhớ đệm bằng cách xóa thư mục `src/data/cache`

### Vấn đề: Lỗi không xác định

- Kiểm tra tệp nhật ký trong thư mục `logs` để biết thông tin chi tiết về lỗi
- Khởi động lại ứng dụng với cờ gỡ lỗi: `python run.py --debug`
- Khôi phục từ bản sao lưu trong thư mục `backups`

### Vấn đề: Hiệu suất kém

- Kiểm tra báo cáo hiệu suất trong thư mục `metrics`
- Tăng kích thước bộ nhớ đệm bằng cách chỉnh sửa tệp cấu hình
- Giảm tần suất giám sát bằng cách tăng giá trị `monitoring_interval` trong tệp cấu hình

## Kết luận

Các tính năng mới này giúp cải thiện đáng kể hiệu suất, độ tin cậy và khả năng bảo trì của phần mềm. Bằng cách sử dụng các công cụ này một cách hợp lý, bạn có thể tạo ra một ứng dụng nhanh hơn, ổn định hơn và dễ bảo trì hơn.
