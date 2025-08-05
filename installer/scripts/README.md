# 🛠️ Installer Scripts & Tools

This directory contains professional installer scripts, validation tools, and automation utilities for the Quan*Ly_Kho_Cam*&\_Mix application.

## 📁 Files Overview

### 🏗️ Build Scripts

#### `build_inno.bat`

**Windows Batch Script for Inno Setup Building**

```batch
# Build installer with Inno Setup
cd installer\scripts
build_inno.bat

#Build installer with Inno Setup thủ công
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" "installer\scripts\installer.iss"
```

# Build cơ bản

.\installer\scripts\Build-Installer.ps1

# Build với tham số tùy chỉnh

.\installer\scripts\Build-Installer.ps1 -OutputDir "custom_output" -OutputName "MyApp_Setup" -Quiet

# Build với version cụ thể

.\installer\scripts\Build-Installer.ps1 -Version "2.0.1"

# Build im lặng

.\installer\scripts\Build-Installer.ps1 -Quiet

**Features:**

- ✅ Auto-detects Inno Setup installation paths
- ✅ Supports Inno Setup 5 and 6
- ✅ Error handling for missing installations
- ✅ Professional build reporting

**Supported Paths:**

- `C:\Program Files (x86)\Inno Setup 6\ISCC.exe`
- `C:\Program Files\Inno Setup 6\ISCC.exe`
- `C:\Program Files (x86)\Inno Setup 5\ISCC.exe`

### 📦 Installer Definitions

#### `installer.iss`

**Professional Inno Setup Installer Script**

**Application Info:**

- **Name**: Phần mềm Quản lý Cám - Trại Gà
- **Version**: 2.0.0
- **Publisher**: Minh-Tan_Phat
- **GUID**: `{8B5F4B2A-9C3D-4E5F-8A7B-1C2D3E4F5A6B}`

**Features:**

- ✅ Modern wizard interface
- ✅ Complete Windows integration
- ✅ UAC elevation handling
- ✅ Registry management
- ✅ Start Menu entries
- ✅ Desktop shortcuts
- ✅ Add/Remove Programs registration
- ✅ Professional uninstaller

#### `installer.nsi`

**NSIS Installer Script (Alternative)**

**Features:**

- ✅ Lightweight installer creation
- ✅ Custom UI components
- ✅ Multi-language support
- ✅ Plugin system integration

### 🔐 Code Signing

#### `sign_installer.py`

**Professional Code Signing Manager**

```python
# Setup signing configuration
python sign_installer.py config

# Sign all installers
python sign_installer.py sign

# Verify signatures
python sign_installer.py verify
```

**Features:**

- ✅ **Multi-tool Support**: SignTool (Windows SDK) and osslsigncode
- ✅ **Certificate Management**: Secure certificate handling
- ✅ **Timestamp Services**: DigiCert timestamp integration
- ✅ **Batch Processing**: Sign multiple files automatically
- ✅ **Verification**: Validate signatures after signing

**Supported Tools:**

- Windows SDK SignTool
- osslsigncode (cross-platform)
- Custom certificate stores

#### `signing_config.json`

**Code Signing Configuration**

```json
{
  "certificate_path": "path/to/certificate.p12",
  "certificate_password": "your_password",
  "timestamp_url": "http://timestamp.digicert.com",
  "description": "Phần mềm Quản lý Cám - Trại Gà",
  "url": "https://github.com/Minh-Tan_Phat"
}
```

### 🔍 Validation & Testing

#### `validate_installer.py`

**Comprehensive Installer Testing System**

```python
# Run full validation suite
python validate_installer.py

# Test specific components
python validate_installer.py --test-registry
python validate_installer.py --test-shortcuts
```

**Test Categories:**

- ✅ **File Integrity**: Verify all installer files exist and are valid
- ✅ **Installation Testing**: Test installer execution and completion
- ✅ **Registry Validation**: Verify Windows registry entries
- ✅ **Shortcut Creation**: Test desktop and Start Menu shortcuts
- ✅ **Uninstaller Testing**: Validate complete removal capability
- ✅ **Silent Installation**: Test automated installation modes
- ✅ **Rollback Testing**: Verify error recovery mechanisms

**Validation Results:**

```
🔍 Installer Validation Results:
✅ File Integrity: PASSED
✅ Installer Execution: PASSED
✅ Registry Entries: PASSED
✅ Shortcuts Created: PASSED
✅ Uninstaller Works: PASSED
✅ Silent Install: PASSED
✅ Rollback Capability: PASSED
```

### 🚀 Application Utilities

#### `app_launcher.py`

**Application Launch and Environment Setup**

**Features:**

- ✅ Environment variable configuration
- ✅ Dependency checking
- ✅ Error handling and logging
- ✅ User data directory setup

#### `setup_environment.py`

**Development Environment Setup**

**Features:**

- ✅ Python environment validation
- ✅ Dependency installation
- ✅ Path configuration
- ✅ Development tools setup

#### `create_registry_entries.py`

**Windows Registry Management**

**Features:**

- ✅ Application registration
- ✅ File association setup
- ✅ Uninstall information
- ✅ User preferences storage

## 🚀 Usage Instructions

### 1. Build Professional Installer

```batch
# Using Inno Setup (Recommended)
cd installer\scripts
build_inno.bat
```

### 2. Code Signing Workflow

```python
# Step 1: Setup configuration
python sign_installer.py config

# Step 2: Edit signing_config.json with your certificate details

# Step 3: Sign installers
python sign_installer.py sign

# Step 4: Verify signatures
python sign_installer.py verify
```

### 3. Validation & Testing

```python
# Run comprehensive validation
python validate_installer.py

# Check specific components
python validate_installer.py --component registry
python validate_installer.py --component shortcuts
```

## 🔧 Configuration

### Code Signing Setup

1. **Obtain Code Signing Certificate**:

   - Purchase from trusted CA (DigiCert, Sectigo, etc.)
   - Or use self-signed for testing

2. **Configure signing_config.json**:

   ```json
   {
     "certificate_path": "C:/path/to/certificate.p12",
     "certificate_password": "your_secure_password",
     "timestamp_url": "http://timestamp.digicert.com"
   }
   ```

3. **Install Windows SDK** (for SignTool):
   - Download from Microsoft
   - Ensure SignTool is in PATH

### Inno Setup Configuration

1. **Install Inno Setup 6**:

   - Download from https://jrsoftware.org/isinfo.php
   - Install to default location

2. **Customize installer.iss**:
   - Update application information
   - Modify installation paths
   - Add custom components

## 📋 System Requirements

### Build Environment

- Windows 10/11 (64-bit)
- Inno Setup 6.0+ or NSIS 3.0+
- Python 3.8+
- Windows SDK (for code signing)

### Optional Tools

- **Code Signing Certificate**: For production releases
- **Windows SDK**: For SignTool utility
- **Git**: For version control integration

## 🐛 Troubleshooting

### Common Issues

**"Inno Setup not found"**:

- Install Inno Setup to default location
- Check PATH environment variable
- Run as Administrator

**"SignTool not found"**:

- Install Windows SDK
- Add SignTool to PATH
- Verify certificate file exists

**Validation failures**:

- Check installer file integrity
- Verify all dependencies are included
- Run as Administrator for registry tests

### Getting Help

1. **Check Logs**: All scripts provide detailed logging
2. **Run Validation**: Use validation system to identify issues
3. **Review Configuration**: Verify all config files are correct
4. **Test Environment**: Ensure all required tools are installed

## 📄 License

These installer scripts are part of the Quan*Ly_Kho_Cam*&\_Mix project.
© 2025 Minh-Tan_Phat. All rights reserved.

---

**Professional installer tools for Windows software distribution** 🚀
