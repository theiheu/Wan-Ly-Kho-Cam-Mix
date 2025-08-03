# Professional Windows Installer System

## Chicken Farm Manager - Complete Installation Package

This directory contains a comprehensive, professional-grade Windows installer system for the Chicken Farm Manager application. The installer meets commercial software standards with modern UI, complete Windows integration, and enterprise-level features.

## 🚀 Quick Start (WORKING SOLUTIONS)

### ✅ RECOMMENDED: Portable Application

**Status: ✅ WORKING** - No PyQt5/PyInstaller issues

```bash
# From installer/build directory
cd installer\build
python portable_build.py
```

**Output:** `installer\output\ChickenFarmManager_Portable.zip`

- ✅ No Qt plugin errors
- ✅ Professional distribution package
- ✅ Automatic dependency installation
- ✅ Works on any Windows system with Python

### ⚠️ PyInstaller Build (Known Issues)

**Status: ❌ FAILING** - PyQt5 plugin directory issues

```bash
# From installer/build directory
python build_installer.py
```

**Issue:** PyQt5 plugin directory not found due to Unicode path characters.
**Recommendation:** Use the Portable Application instead.

## 🎯 Features

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

```
installer/
├── build/                          # Build system and tools
│   ├── build_installer.py         # Main build orchestrator
│   ├── create_executable.py       # PyInstaller executable builder
│   ├── package_installer.py       # Installer package creator
│   ├── version_info.py            # Windows version information
│   └── ChickenFarmManager.spec    # PyInstaller specification
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
└── output/                       # Generated installer files
    ├── ChickenFarmManager.exe    # Main application executable
    ├── ChickenFarmManager_Setup.exe # Professional installer
    ├── install.bat               # Advanced batch installer
    └── [Distribution Package].zip # Complete distribution package
```

## 🚀 Quick Start

### Building the Complete Installer

1. **Install Dependencies**:

   ```bash
   pip install -r requirements-build.txt
   ```

2. **Build Everything**:

   ```bash
   python installer\build\build_installer.py
   ```

3. **Find Your Installers**:
   - Professional installer: `installer/output/ChickenFarmManager_Setup.exe`
   - Batch installer: `installer/output/install.bat`
   - Distribution package: `installer/output/ChickenFarmManager_v2.0.0_Professional_Distribution.zip`

### Individual Build Steps

```bash
# Build just the executable
python installer/build/create_executable.py

# Create installer packages
python installer/build/package_installer.py

# Validate installers
python installer/scripts/validate_installer.py

# Sign installers (requires certificate)
python installer/scripts/sign_installer.py
```

## 🔧 Installation Options

### For End Users

1. **Professional Installer** (Recommended):

   - Run `ChickenFarmManager_Setup.exe`
   - Follow the installation wizard
   - Complete Windows integration

2. **Batch Installer** (Advanced):

   - Run `install.bat` as Administrator
   - Choose installation type
   - Supports silent installation with `/S` flag

3. **Portable Installation**:
   - Extract and run `ChickenFarmManager.exe` directly
   - No installation required

### Silent Installation

```cmd
# Silent installation to Program Files
install.bat /S

# Silent installation with NSIS installer
ChickenFarmManager_Setup.exe /S
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
   python installer/build/build_installer.py
   ```

### Adding New Features

1. **Modify Scripts**:

   - Update `installer/scripts/installer.nsi` for NSIS features
   - Update `installer/scripts/installer.iss` for Inno Setup features
   - Enhance `installer/build/package_installer.py` for batch installer

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

This installer system is part of the Chicken Farm Manager project.
© 2025 Minh-Tan_Phat. All rights reserved.

See `installer/resources/license.txt` for complete license terms.

---

**Built with ❤️ for professional Windows software distribution**
