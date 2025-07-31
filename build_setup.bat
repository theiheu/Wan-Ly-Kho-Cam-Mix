@echo off
chcp 65001 >nul
echo ========================================
echo   Chicken Farm Management - Build Setup
echo   Thiết lập môi trường build Windows
echo ========================================
echo.

echo 🔍 Kiểm tra Python...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ Python chưa được cài đặt hoặc không có trong PATH
    echo 💡 Vui lòng cài đặt Python 3.6+ từ https://python.org
    pause
    exit /b 1
)

python --version
echo ✅ Python đã sẵn sàng

echo.
echo 📦 Cài đặt dependencies cho build...
pip install -r requirements-build.txt

if %errorLevel% neq 0 (
    echo ❌ Không thể cài đặt dependencies
    echo 💡 Thử chạy với quyền Administrator
    pause
    exit /b 1
)

echo.
echo ✅ Thiết lập hoàn tất!
echo 🚀 Bây giờ bạn có thể chạy: python build_windows.py
echo.
pause
