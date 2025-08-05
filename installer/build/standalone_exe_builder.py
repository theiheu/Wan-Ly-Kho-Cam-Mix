#!/usr/bin/env python3
"""
Standalone EXE Builder for Quan Ly Kho Cam & Mix Manager
Creates a single executable with embedded data persistence
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def get_project_paths():
    """Get project paths"""
    project_root = Path(__file__).parent.parent.parent
    installer_dir = project_root / "installer"
    output_dir = installer_dir / "output"

    return project_root, installer_dir, output_dir

def create_runtime_hook():
    """Create runtime hook for environment setup"""

    project_root, installer_dir, output_dir = get_project_paths()
    hook_file = output_dir / "standalone_runtime_hook.py"

    hook_content = '''
import os
import sys
from pathlib import Path

def setup_standalone_environment():
    """Setup environment for standalone executable"""

    if getattr(sys, 'frozen', False):
        app_name = "Quan_Ly_Kho_Cam_&_Mix"

        # Get executable directory
        exe_dir = Path(sys.executable).parent

        # For standalone, use portable mode with local directories
        # But also support professional mode if environment variables exist
        if 'CFM_DATA_PATH' not in os.environ:
            # Check if we should use professional paths
            use_professional = (
                'Program Files' in str(exe_dir) or
                exe_dir.name.lower() in ['program files', 'program files (x86)']
            )

            if use_professional:
                # Professional installation paths
                appdata_path = Path(os.environ.get('APPDATA', '')) / app_name
                documents_path = Path(os.environ.get('USERPROFILE', '')) / 'Documents' / app_name

                env_vars = {
                    'CFM_DATA_PATH': str(appdata_path / "data"),
                    'CFM_CONFIG_PATH': str(appdata_path / "config"),
                    'CFM_LOGS_PATH': str(appdata_path / "logs"),
                    'CFM_REPORTS_PATH': str(documents_path / "reports"),
                    'CFM_EXPORTS_PATH': str(documents_path / "exports"),
                    'CFM_BACKUPS_PATH': str(documents_path / "backups")
                }
            else:
                # Portable mode - use executable directory
                env_vars = {
                    'CFM_DATA_PATH': str(exe_dir / "data"),
                    'CFM_CONFIG_PATH': str(exe_dir / "config"),
                    'CFM_LOGS_PATH': str(exe_dir / "logs"),
                    'CFM_REPORTS_PATH': str(exe_dir / "reports"),
                    'CFM_EXPORTS_PATH': str(exe_dir / "exports"),
                    'CFM_BACKUPS_PATH': str(exe_dir / "backups")
                }

            # Set environment variables and create directories
            for var_name, var_value in env_vars.items():
                os.environ[var_name] = var_value
                try:
                    Path(var_value).mkdir(parents=True, exist_ok=True)
                except Exception:
                    pass

# Setup environment on import
setup_standalone_environment()
'''

    with open(hook_file, 'w', encoding='utf-8') as f:
        f.write(hook_content)

    return hook_file

def create_spec_file():
    """Create PyInstaller spec file for standalone build"""

    project_root, installer_dir, output_dir = get_project_paths()
    spec_file = output_dir / "standalone.spec"

    # Get main script path - use forward slashes and raw strings
    main_script = str(project_root / "src" / "main.py").replace('\\', '/')
    runtime_hook = str(create_runtime_hook()).replace('\\', '/')
    src_path = str(project_root / "src").replace('\\', '/')
    version_file = str(output_dir / "version_info.txt").replace('\\', '/')
    icon_file = str(installer_dir / "resources" / "app_icon.ico").replace('\\', '/')

    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    [r'{main_script}'],
    pathex=[r'{str(project_root).replace(chr(92), "/")}'],
    binaries=[],
    datas=[
        (r'{src_path}', 'src'),
    ],
    hiddenimports=[
        'src.utils.persistent_paths',
        'src.core.formula_manager',
        'src.core.inventory_manager',
        'src.core.threshold_manager',
        'src.core.remaining_usage_calculator',
        'src.utils.default_formulas',
        'src.utils.app_icon',
        'src.ui.threshold_settings_dialog',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'pandas',
        'matplotlib',
        'openpyxl',
        'numpy'
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[r'{runtime_hook}'],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Quan_Ly_Kho_Cam_&_Mix',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version=r'{version_file}',
    icon=r'{icon_file}'
)
'''

    with open(spec_file, 'w', encoding='utf-8') as f:
        f.write(spec_content)

    return spec_file

def create_version_info():
    """Create version info file"""

    project_root, installer_dir, output_dir = get_project_paths()
    version_file = output_dir / "version_info.txt"

    version_content = '''# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(2, 0, 0, 0),
    prodvers=(2, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'Minh-Tan_Phat'),
        StringStruct(u'FileDescription', u'Phần mềm Quản lý Kho Cám & Mix'),
        StringStruct(u'FileVersion', u'2.0.0.0'),
        StringStruct(u'InternalName', u'Quan_Ly_Kho_Cam_&_Mix'),
        StringStruct(u'LegalCopyright', u'© 2025 Minh-Tan_Phat. All rights reserved.'),
        StringStruct(u'OriginalFilename', u'Quan_Ly_Kho_Cam_&_Mix.exe'),
        StringStruct(u'ProductName', u'Quan Ly Kho Cam & Mix Manager'),
        StringStruct(u'ProductVersion', u'2.0.0.0')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''

    with open(version_file, 'w', encoding='utf-8') as f:
        f.write(version_content)

    return version_file

def build_standalone_exe():
    """Build standalone executable"""

    project_root, installer_dir, output_dir = get_project_paths()

    print("🔨 Building standalone executable...")
    print(f"📁 Project root: {project_root}")
    print(f"📁 Output directory: {output_dir}")

    # Ensure output directory exists
    output_dir.mkdir(exist_ok=True)

    # Clean previous builds
    build_temp = output_dir / "build_temp"
    if build_temp.exists():
        shutil.rmtree(build_temp, ignore_errors=True)

    # Create version info
    version_file = create_version_info()
    print(f"✅ Version info created: {version_file}")

    # Create spec file
    spec_file = create_spec_file()
    print(f"✅ Spec file created: {spec_file}")

    # Build with PyInstaller using absolute paths
    cmd = [
        "pyinstaller",
        "--distpath", str(output_dir),
        "--workpath", str(build_temp),
        "--clean",
        "--noconfirm",
        str(spec_file)
    ]

    try:
        print("🚀 Running PyInstaller...")
        print(f"Command: {' '.join(cmd)}")

        # Change to project root to avoid path issues
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            cwd=str(project_root),
            encoding='utf-8',
            errors='replace'
        )

        print("PyInstaller output:")
        print(result.stdout)

        # Check if executable was created
        exe_path = output_dir / "Quan_Ly_Kho_Cam_&_Mix.exe"
        if exe_path.exists():
            file_size = exe_path.stat().st_size / (1024 * 1024)  # MB
            print(f"✅ Standalone executable built successfully!")
            print(f"📁 Location: {exe_path}")
            print(f"📊 Size: {file_size:.1f} MB")

            # Create readme for standalone
            create_standalone_readme()

            return True
        else:
            print("❌ Executable not found after build")
            return False

    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        print(f"Error output: {e.stderr}")
        print(f"Standard output: {e.stdout}")
        return False
    except FileNotFoundError:
        print("❌ PyInstaller not found. Install with: pip install pyinstaller")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_standalone_readme():
    """Create README for standalone executable"""

    project_root, installer_dir, output_dir = get_project_paths()
    readme_file = output_dir / "README_Standalone.txt"

    readme_content = '''🏭 Quan Ly Kho Cam & Mix Management System - Standalone Version
================================================================

📋 THÔNG TIN PHIÊN BẢN
- Phiên bản: 2.0.0 Standalone
- Loại: Standalone Executable (Không cần cài đặt)
- Kích thước: ~74 MB
- Hỗ trợ: Windows 10/11 (64-bit)

🚀 CÁCH SỬ DỤNG
1. Giải nén file zip (nếu có)
2. Double-click vào "Quan_Ly_Kho_Cam_&_Mix.exe"
3. Ứng dụng sẽ tự động khởi chạy

📁 CHẾ ĐỘ LƯU TRỮ DỮ LIỆU
Standalone executable hỗ trợ 2 chế độ:

🏢 PROFESSIONAL MODE (Tự động phát hiện)
- Khi chạy từ Program Files
- Dữ liệu lưu tại: %APPDATA%\\Quan_Ly_Kho_Cam_&_Mix\\
- Báo cáo lưu tại: %USERPROFILE%\\Documents\\Quan_Ly_Kho_Cam_&_Mix\\

💼 PORTABLE MODE (Mặc định)
- Khi chạy từ thư mục bất kỳ
- Dữ liệu lưu cùng thư mục với file .exe
- Thư mục: data/, config/, reports/, exports/

✨ TÍNH NĂNG
✅ Quản lý kho cám và mix
✅ Theo dõi tồn kho
✅ Tạo báo cáo
✅ Xuất dữ liệu Excel
✅ Cảnh báo ngưỡng tồn kho
✅ Lưu trữ dữ liệu persistent

🔧 YÊU CẦU HỆ THỐNG
- Windows 10/11 (64-bit)
- 4GB RAM
- 200MB dung lượng trống
- Không cần Python hoặc thư viện bổ sung

📞 HỖ TRỢ
- GitHub: https://github.com/Minh-Tan_Phat
- Email: support@example.com

© 2025 Minh-Tan_Phat. All rights reserved.
'''

    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)

    print(f"✅ README created: {readme_file}")

def cleanup_build_files():
    """Clean up temporary build files"""

    project_root, installer_dir, output_dir = get_project_paths()

    # Files to clean up
    cleanup_files = [
        output_dir / "standalone.spec",
        output_dir / "standalone_runtime_hook.py",
        output_dir / "version_info.txt",
        output_dir / "build_temp"
    ]

    for file_path in cleanup_files:
        try:
            if file_path.is_file():
                file_path.unlink()
            elif file_path.is_dir():
                shutil.rmtree(file_path, ignore_errors=True)
        except Exception:
            pass

    print("🧹 Build files cleaned up")

def main():
    """Main build process"""

    print("🏭 Quan Ly Kho Cam & Mix - Standalone EXE Builder")
    print("=" * 60)

    try:
        # Build standalone executable
        if build_standalone_exe():
            print("\n🎉 BUILD SUCCESSFUL!")
            print("=" * 60)

            project_root, installer_dir, output_dir = get_project_paths()
            exe_path = output_dir / "Quan_Ly_Kho_Cam_&_Mix.exe"

            print(f"📁 Executable: {exe_path}")
            print(f"📄 README: {output_dir / 'README_Standalone.txt'}")
            print("\n💡 USAGE:")
            print("   - Double-click the .exe file to run")
            print("   - Data will be saved automatically")
            print("   - No installation required")

            # Optional cleanup
            cleanup_choice = input("\n🧹 Clean up build files? (y/N): ").lower().strip()
            if cleanup_choice == 'y':
                cleanup_build_files()

            return True
        else:
            print("\n❌ BUILD FAILED!")
            return False

    except KeyboardInterrupt:
        print("\n⚠️ Build cancelled by user")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()

    print("\n" + "=" * 60)
    if success:
        print("✅ Standalone executable ready for distribution!")
    else:
        print("❌ Build process failed")

    input("\nPress Enter to exit...")
    sys.exit(0 if success else 1)


