@echo off
chcp 65001 >nul
echo ========================================
echo   Clean Build - Chicken Farm Management
echo   Dọn dẹp TOÀN BỘ file build (Bao gồm dist/)
echo ========================================
echo.

echo ⚠️  CẢNH BÁO: Script này sẽ XÓA TOÀN BỘ:
echo   • Thư mục build/
echo   • Thư mục dist/ (executable)
echo   • Thư mục packages/
echo   • File *.zip
echo   • File *.spec, version_info.txt
echo   • Tất cả __pycache__/
echo.

choice /C YN /M "Tiếp tục xóa TOÀN BỘ (Y/N)"
if %errorLevel% == 2 (
    echo Hủy dọn dẹp. Sử dụng smart_clean.bat để dọn dẹp an toàn.
    pause
    exit /b 0
)

echo.
echo 🧹 Dọn dẹp thư mục build...

if exist build (
    rmdir /s /q build
    echo ✅ Đã xóa thư mục build
)

if exist dist (
    rmdir /s /q dist
    echo ✅ Đã xóa thư mục dist
)

if exist packages (
    rmdir /s /q packages
    echo ✅ Đã xóa thư mục packages
)

if exist __pycache__ (
    rmdir /s /q __pycache__
    echo ✅ Đã xóa __pycache__
)

for /r . %%d in (__pycache__) do (
    if exist "%%d" (
        rmdir /s /q "%%d"
        echo ✅ Đã xóa %%d
    )
)

for %%f in (*.spec) do (
    if exist "%%f" (
        del "%%f"
        echo ✅ Đã xóa %%f
    )
)

for %%f in (*.zip) do (
    if exist "%%f" (
        del "%%f"
        echo ✅ Đã xóa %%f
    )
)

if exist version_info.txt (
    del version_info.txt
    echo ✅ Đã xóa version_info.txt
)

if exist install.bat (
    del install.bat
    echo ✅ Đã xóa install.bat
)

if exist README_DISTRIBUTION.txt (
    del README_DISTRIBUTION.txt
    echo ✅ Đã xóa README_DISTRIBUTION.txt
)

echo.
echo 🎉 Dọn dẹp TOÀN BỘ hoàn tất!
echo 💡 Bây giờ bạn có thể chạy build mới từ đầu
echo.
pause
