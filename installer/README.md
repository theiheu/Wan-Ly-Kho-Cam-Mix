# Professional Windows Installer System

## Quan*Ly_Kho_Cam*&\_Mix - Complete Installation Package

This directory contains a comprehensive, professional-grade Windows installer system for the Quan*Ly_Kho_Cam*&\_Mix application. The installer meets commercial software standards with modern UI, complete Windows integration, and enterprise-level features.

## 🚀 Quick Start (PROFESSIONAL SOLUTIONS)

### 🎯 RECOMMENDED: Enhanced Build System with JSON Data Copy

**Status: ✅ WORKING** - Complete Windows application with automatic installation, data persistence, and JSON configuration files

```bash
# From installer/build directory
cd installer\build
python builder.py
```

**Output:** `installer\output\Quan_Ly_Kho_Cam_&_Mix.exe`

**NEW FEATURES:**

- ✅ **Automatic JSON Data Copy**: Essential configuration files automatically copied to output
- ✅ **Enhanced Data Persistence**: All JSON config files included in distribution
- ✅ **Professional Build Management**: Improved build process with better error handling
- ✅ **Configuration Preservation**: User settings and business data properly packaged

**Core Features:**

- ✅ **Automatic Installation**: Self-installs to Program Files on first run
- ✅ **Persistent Data Storage**: Saves data in AppData and Documents folders
- ✅ **Desktop Shortcut**: Creates desktop shortcut automatically
- ✅ **Professional Experience**: Behaves like commercial Windows software
- ✅ **Data Persistence**: User data survives application restarts and system reboots
- ✅ **No Setup Required**: Single .exe file handles everything automatically

### 🧪 NEW: JSON Copy Testing

**Status: ✅ WORKING** - Test the JSON file copying functionality

```bash
# From installer/build directory
cd installer\build
python test_copy_json.py
```

**Features:**

- ✅ Tests copying of all essential JSON configuration files
- ✅ Validates file integrity and structure
- ✅ Creates test output directory for verification
- ✅ Comprehensive reporting of copy operations

### ✅ ALTERNATIVE: Standalone .exe (Basic)

**Status: ✅ WORKING** - Simple standalone executable with JSON data

```bash
# From installer/build directory
cd installer\build
python builder.py
```

**Output:** `installer\output\Quan_Ly_Kho_Cam_&_Mix.exe`

- ✅ True standalone executable - no Python installation required
- ✅ **NEW**: Essential JSON configuration files included
- ✅ Double-click to run - enhanced user experience
- ✅ **Improved Data Persistence**: Configuration data properly preserved

### ✅ ALTERNATIVE: Portable Application

**Status: ✅ WORKING** - Professional distribution for developers/power users

```bash
# From installer/build directory
cd installer\build
python portable_build.py
```

**Output:** `installer\output\Quan_Ly_Kho_Cam_&_Mix_Portable.zip` (164 KB)

- ✅ Small download size with automatic dependency installation
- ✅ Complete source code included for customization
- ✅ Works on any Windows system with Python
- ✅ Extract and run with batch file launcher
- ✅ Ideal for development and technical users

### 🔄 COMPREHENSIVE: Complete Build Workflow

**Status: ✅ WORKING** - Builds both .exe and portable versions

```bash
# From installer/build directory
cd installer\build
python build_workflow.py
```

**Features:**

- Creates both standalone .exe and portable application
- Comprehensive validation and testing
- Professional build reporting
- Multiple distribution options

## 🎯 Features

### 🆕 Enhanced JSON Data Management

- **Automatic JSON Copy**: Essential configuration files automatically copied during build
- **Configuration Preservation**: All user settings and business data properly packaged
- **Data Integrity**: JSON files validated and tested during copy process
- **Structured Organization**: Config and business data organized in separate directories
- **Test Validation**: Comprehensive testing system for JSON copy functionality

**JSON Files Included:**

- `bonus_rates.json` - Employee bonus calculation rates
- `feed_formula.json` - Feed production formulas
- `mix_formula.json` - Mix production formulas
- `inventory.json` - Inventory management data
- `packaging_info.json` - Product packaging information
- `salary_rates.json` - Employee salary structures
- `thresholds.json` - Alert and warning thresholds
- `user_preferences.json` - User interface preferences
- `threshold_config.json` - Advanced threshold configurations
- And more essential configuration files...

### Professional Installation Experience

- **Modern Wizard UI**: Multi-screen installation wizard with professional graphics
- **Complete Windows Integration**: Program Files installation, Start Menu entries, Add/Remove Programs registration
- **UAC Handling**: Proper User Account Control elevation and security
- **Multiple Installation Options**: Interactive, silent, portable, and custom directory installation
- **Professional Uninstaller**: Complete removal with user data options and rollback capabilities

### Advanced Installer Features

- **Error Handling & Rollback**: Comprehensive error detection with automatic rollback on failure
- **Registry Management**: Proper Windows registry integration and cleanup
- **Code Signing Ready**: Prepared for digital certificate signing
- **Validation System**: Automated testing and quality assurance
- **Multi-format Support**: NSIS, Inno Setup, and Batch installers

### Commercial-Grade Quality

- **Professional Assets**: Custom installer images, icons, and documentation
- **Comprehensive Documentation**: User guides, license agreements, and technical documentation
- **Validation & Testing**: Automated installer testing and verification
- **Distribution Ready**: Complete distribution packages with all necessary files

## 📁 Directory Structure

```text
installer/
├── build/                          # Enhanced build system with JSON support
│   ├── builder.py                 # 🆕 PRIMARY: Enhanced builder with JSON copy
│   ├── test_copy_json.py          # 🆕 JSON copy functionality testing
│   ├── portable_build.py          # Alternative portable application builder
│   ├── build_workflow.py          # Complete build workflow
│   ├── cx_freeze_build.py         # Alternative executable builder
│   ├── version_info.py            # Windows version information
│   ├── cleanup.py                 # Build cleanup utility
│   ├── qt_plugin_copy.py          # Qt plugin management utility
│   └── test_dependencies.py       # Dependency testing utility
├── scripts/                       # Installer scripts and tools
│   ├── installer.nsi              # NSIS installer script
│   ├── installer.iss              # Inno Setup installer script
│   ├── validate_installer.py      # Installer validation system
│   └── sign_installer.py          # Code signing manager
├── resources/                     # Installer assets and resources
│   ├── app_icon.ico              # Application icon
│   ├── welcome_image.bmp         # Installer welcome image
│   ├── header_image.bmp          # Installer header image
│   ├── license.txt               # Software license agreement
│   └── readme.txt                # Installation instructions
├── output/                       # Generated distribution packages
│   ├── Quan_Ly_Kho_Cam_&_Mix.exe # 🆕 Enhanced executable with JSON data
│   ├── data/                     # 🆕 Copied JSON configuration files
│   │   ├── config/               # 🆕 Application configuration files
│   │   └── business/             # 🆕 Business logic configuration
│   └── test_output/              # 🆕 Test output for JSON copy validation
└── test_output/                  # 🆕 JSON copy test results
    └── data/                     # 🆕 Test copied JSON files
```

## 🚀 Build Instructions

### 🎯 PRIMARY: Enhanced Build Method with JSON Data Copy

1. **Navigate to Build Directory**:

   ```bash
   cd installer\build
   ```

2. **Create Enhanced Executable with JSON Data**:

   ```bash
   python builder.py
   ```

3. **Find Your Distribution**:
   - Enhanced executable: `installer/output/Quan_Ly_Kho_Cam_&_Mix.exe`
   - JSON configuration files: `installer/output/data/`
   - Config files: `installer/output/data/config/`
   - Business data: `installer/output/data/business/`

### 🧪 Test JSON Copy Functionality

```bash
# Test JSON file copying before building
python test_copy_json.py

# Verify test results in installer/test_output/
```

### 🔄 Complete Build Workflow

```bash
# Run complete build process with validation
python build_workflow.py
```

### Alternative Build Methods

#### Portable Application

```bash
# Create portable application
python portable_build.py
```

#### cx_Freeze Alternative

```bash
# Alternative executable creation
python cx_freeze_build.py

# Test dependencies (optional)
python test_dependencies.py

# Clean build artifacts (if needed)
python cleanup.py
```

### Validation and Testing

```bash
# Validate distribution packages
python installer/scripts/validate_installer.py

# Sign packages (requires certificate)
python installer/scripts/sign_installer.py
```

## 🔧 Installation Options

### For End Users

1. **Professional Installer** (Recommended):

   - Run `Quan_Ly_Kho_Cam_&_Mix_Setup.exe`
   - Follow the installation wizard
   - Complete Windows integration

2. **Batch Installer** (Advanced):

   - Run `install.bat` as Administrator
   - Choose installation type
   - Supports silent installation with `/S` flag

3. **Portable Installation**:
   - Extract and run `Quan_Ly_Kho_Cam_&_Mix.exe` directly
   - No installation required

### Silent Installation

```cmd
# Silent installation to Program Files
install.bat /S

# Silent installation with NSIS installer
Quan_Ly_Kho_Cam_&_Mix_Setup.exe /S
```

## 🔐 Code Signing

### Setup Code Signing

1. **Create Configuration**:

   ```bash
   python installer/scripts/sign_installer.py config
   ```

2. **Edit Configuration**:

   - Update `installer/scripts/signing_config.json`
   - Add your certificate path and password

3. **Sign Installers**:

   ```bash
   python installer/scripts/sign_installer.py sign
   ```

4. **Verify Signatures**:
   ```bash
   python installer/scripts/sign_installer.py verify
   ```

## 🔍 Quality Assurance

### Automated Validation

The installer system includes comprehensive validation:

```bash
python installer/scripts/validate_installer.py
```

**Tests Include**:

- File integrity verification
- Executable functionality testing
- Installer execution testing
- Registry integration validation
- Shortcut creation testing
- Uninstaller functionality
- Silent installation capability

### Manual Testing Checklist

- [ ] Install on clean Windows 10/11 system
- [ ] Verify all shortcuts are created
- [ ] Test application launches correctly
- [ ] Verify Add/Remove Programs entry
- [ ] Test uninstaller removes everything
- [ ] Test silent installation
- [ ] Verify UAC prompts work correctly

## 🛠️ Customization

### Modifying Installer Appearance

1. **Update Images**:

   - Replace `installer/resources/welcome_image.bmp` (164x314)
   - Replace `installer/resources/header_image.bmp` (55x58)
   - Update `installer/resources/app_icon.ico`

2. **Update Text**:

   - Modify `installer/resources/license.txt`
   - Update `installer/resources/readme.txt`
   - Edit installer scripts for custom messages

3. **Rebuild**:

   ```bash
   python installer/build/portable_build.py
   ```

### Adding New Features

1. **Modify Scripts**:

   - Update `installer/scripts/installer.nsi` for NSIS features
   - Update `installer/scripts/installer.iss` for Inno Setup features
   - Enhance `installer/build/portable_build.py` for portable distribution

2. **Test Changes**:

   ```bash
   python installer/scripts/validate_installer.py
   ```

## 📋 System Requirements

### Build Environment

- Windows 10/11 (64-bit)
- Python 3.8+
- Administrator privileges
- 2GB free disk space

### Optional Tools

- **NSIS 3.0+**: For NSIS installer creation
- **Inno Setup 6.0+**: For Inno Setup installer creation
- **Windows SDK**: For code signing with SignTool
- **Code Signing Certificate**: For production releases

### Target Systems

- Windows 10 (64-bit) or newer
- 4GB RAM minimum
- 200MB free disk space
- Administrator privileges for installation

## 🐛 Troubleshooting

### Common Issues

**Build Fails with "PyInstaller not found"**:

```bash
pip install pyinstaller>=5.0.0
```

**"Permission denied" errors**:

- Run Command Prompt as Administrator
- Check antivirus software isn't blocking files

**Installer validation fails**:

- Ensure all source files are present
- Check that executable was built successfully
- Verify installer scripts are not corrupted

**Code signing fails**:

- Verify certificate file exists and is valid
- Check certificate password is correct
- Ensure SignTool is installed (Windows SDK)

### Getting Help

1. **Check Logs**: Build process provides detailed logging
2. **Run Validation**: Use the validation system to identify issues
3. **GitHub Issues**: Report bugs on the project repository
4. **Documentation**: Review this README and inline comments

## 📄 License

This installer system is part of the Quan*Ly_Kho_Cam*&\_Mix project.
© 2025 Minh-Tan_Phat. All rights reserved.

See `installer/resources/license.txt` for complete license terms.

---

**Built with ❤️ for professional Windows software distribution**
