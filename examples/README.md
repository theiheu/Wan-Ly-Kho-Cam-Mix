# 🧪 Examples và Demo

Thư mục này chứa các file demo, examples và tools hỗ trợ development.

## 📋 Danh sách Examples

### 🎨 demo_responsive_dialog.py
**Mục đích**: Demo tính năng responsive dialog

**Tính năng**:
- Hiển thị dialog responsive với PyQt5
- Demo layout tự động điều chỉnh
- Test tính năng UI components
- Ví dụ về best practices UI

**Sử dụng**:
```bash
cd examples
python demo_responsive_dialog.py
```

**Học được gì**:
- Cách tạo dialog responsive
- Layout management trong PyQt5
- Event handling
- UI design patterns

### 📊 visualize_app.py
**Mục đích**: Tool trực quan hóa dữ liệu ứng dụng

**Tính năng**:
- Trực quan hóa cấu trúc dữ liệu
- Hiển thị charts và graphs
- Tool phân tích performance
- Debug UI components

**Sử dụng**:
```bash
cd examples
python visualize_app.py
```

**Học được gì**:
- Data visualization với matplotlib
- Integration PyQt5 + matplotlib
- Performance monitoring
- Debug techniques

## 🎯 Mục đích Examples

### 📚 Learning
- Hiểu cách implement các tính năng
- Best practices trong PyQt5
- Code patterns và architecture
- Testing và debugging

### 🔧 Development
- Prototype tính năng mới
- Test UI components
- Performance benchmarking
- Code experimentation

### 📖 Documentation
- Ví dụ sử dụng API
- Tutorial code
- Reference implementation
- Code samples

## 🚀 Cách sử dụng

### Chạy examples
```bash
# Từ thư mục gốc
python examples/demo_responsive_dialog.py
python examples/visualize_app.py

# Từ thư mục examples
cd examples
python demo_responsive_dialog.py
python visualize_app.py
```

### Modify và experiment
1. Copy example file
2. Modify theo nhu cầu
3. Test và experiment
4. Apply vào main project

## 📁 Cấu trúc

```
examples/
├── demo_responsive_dialog.py    # UI demo
├── visualize_app.py            # Data visualization
├── README.md                   # This file
└── (future examples)           # Các examples khác
```

## 🛠️ Dependencies

### Cho demo_responsive_dialog.py
- PyQt5 >= 5.15.0
- sys, os (built-in)

### Cho visualize_app.py
- PyQt5 >= 5.15.0
- matplotlib >= 3.3.0
- pandas >= 1.0.0 (nếu cần)

### Cài đặt
```bash
pip install -r ../requirements.txt
```

## 💡 Tips

### Development workflow
1. Chạy examples để hiểu tính năng
2. Modify examples để test ý tưởng
3. Integrate vào main project
4. Tạo examples mới cho tính năng mới

### Best practices
- Giữ examples đơn giản và focused
- Comment code rõ ràng
- Include error handling
- Test trên nhiều môi trường

### Debugging
- Sử dụng examples để isolate issues
- Test components riêng biệt
- Profile performance
- Validate UI behavior

## 🧪 Testing

### Manual testing
```bash
# Test từng example
python examples/demo_responsive_dialog.py
python examples/visualize_app.py
```

### Automated testing
```bash
# Nếu có test framework
python -m pytest examples/
```

## 📝 Contributing

### Thêm example mới
1. Tạo file .py trong examples/
2. Follow naming convention: `demo_*.py` hoặc `example_*.py`
3. Include docstring và comments
4. Update README.md này
5. Test thoroughly

### Guidelines
- **Focused**: Mỗi example demo một tính năng cụ thể
- **Simple**: Dễ hiểu và follow
- **Complete**: Có thể chạy standalone
- **Documented**: Comments và docstrings đầy đủ

## 🔗 Related

- **Main app**: `../src/` - Source code chính
- **Tools**: `../tools/` - Build và development tools
- **Docs**: `../docs/` - Documentation
- **Tests**: `../tests/` - Test files

## 📞 Support

- Tạo issue nếu example không chạy
- Suggest examples mới
- Report bugs trong examples
- Contribute improvements
