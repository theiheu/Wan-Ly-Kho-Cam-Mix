# Cấu Trúc Thư Mục Data

## 📁 Tổ Chức Mới (Ngày 2025-08-04)

```
src/data/
├── business/           # 📊 File nghiệp vụ chính
│   ├── employees.json
│   ├── attendance.json
│   ├── import_participation.json
│   ├── bonus_calculation.json
│   └── ...
├── daily/              # 📅 Dữ liệu theo ngày/tháng
│   ├── reports_202507/
│   ├── reports_202508/
│   └── imports/
├── config/             # ⚙️ Cấu hình hệ thống
├── temp/               # 🗂️ File tạm thời
│   ├── cache/
│   └── logs/
├── backups/            # 💾 File backup
├── assets/             # 🎨 Tài nguyên
│   └── icons/
├── exports/            # 📤 File xuất
└── presets/            # 📋 Mẫu có sẵn
```

## 🎯 Lợi Ích

- ✅ **Gọn gàng**: File được nhóm theo chức năng
- ✅ **Dễ tìm**: Biết file ở đâu theo logic
- ✅ **Dễ backup**: Chỉ cần backup folder business/
- ✅ **Performance**: Ít file ở root level

## 📝 Lưu Ý

- File nghiệp vụ chính trong `business/`
- Reports được nhóm theo tháng trong `daily/`
- File tạm thời trong `temp/` có thể xóa an toàn
- Backup được lưu tự động trước khi sắp xếp
