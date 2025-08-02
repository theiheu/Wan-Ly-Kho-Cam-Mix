# 🐔 Chicken Farm Management System

A comprehensive management system for chicken farms with feed tracking, inventory management, and analytics.

## ✨ Features

- 📊 **Daily Feed Management** - Track feed consumption and costs
- 📦 **Inventory System** - Complete inventory CRUD operations  
- 🧪 **Formula Management** - Create and manage feed formulas
- 📈 **Reports & Analytics** - Generate insights and reports
- 🔔 **Smart Alerts** - Inventory threshold notifications
- 📱 **Modern UI** - Responsive PyQt5 interface

## 🚀 Quick Start

### Option 1: Use Pre-built Installer (Recommended)
```bash
# Download and run the installer
build\install.bat
```

### Option 2: Run Portable
```bash
# Run directly without installation
dist\ChickenFarmManager.exe
```

### Option 3: Build from Source
```bash
# Build the application
python build\build.py

# Then use the installer
build\install.bat
```

## 📋 Requirements

- **OS**: Windows 10/11 (64-bit)
- **RAM**: 4GB minimum
- **Storage**: 200MB free space
- **Python**: 3.6+ (for building from source)

## 🔧 Building

### Simple Build
```bash
python build\build.py
```

This creates:
- `dist\ChickenFarmManager.exe` - Standalone executable
- `build\install.bat` - Windows installer

### Build Dependencies
```bash
pip install -r requirements-build.txt
```

## 📁 Project Structure

```
📦 chicken-farm-management/
├── 📁 src/                 # Application source code
├── 📁 build/               # Build tools & installer
│   ├── 🔧 build.py         # Main build script  
│   ├── 📦 install.bat      # Windows installer
│   └── 📁 tools/           # Build utilities
├── 📁 dist/                # Built executable (generated)
├── 📁 docs/                # Documentation
├── 📁 examples/            # Demo code
├── 📁 tests/               # Test files
├── 🐍 run.py               # Development launcher
├── 📄 requirements.txt     # Runtime dependencies
└── 📄 requirements-build.txt # Build dependencies
```

## 💡 Usage

1. **Launch**: Run executable or use desktop shortcut
2. **Feed Tracking**: Monitor daily feed consumption
3. **Inventory**: Manage stock levels and alerts  
4. **Formulas**: Create custom feed recipes
5. **Reports**: Generate analytics and insights

## 📚 Documentation

- 📖 [Build Guide](docs/BUILD_INSTALLER_GUIDE.md)
- 🎯 [Build Solution](docs/FINAL_BUILD_SOLUTION.md)  
- ✅ [Success Summary](docs/BUILD_SUCCESS_SUMMARY.md)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

## 📄 License

© 2024 Minh-Tan_Phat. All rights reserved.
