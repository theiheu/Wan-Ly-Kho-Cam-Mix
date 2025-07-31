@echo off
chcp 65001 >nul
echo ========================================
echo   Quick Build - Chicken Farm Management
echo   Build nhanh file thực thi Windows
echo ========================================
echo.

echo 🚀 Bắt đầu build...
python build_windows.py

if %errorLevel% neq 0 (
    echo ❌ Build thất bại!
    pause
    exit /b 1
)

echo.
echo 🎉 Build thành công!
echo 📁 Kiểm tra thư mục dist/ để xem kết quả
echo.

echo 🔍 Mở thư mục dist?
choice /C YN /M "Mở thư mục dist (Y/N)"
if %errorLevel% == 1 (
    explorer dist
)

echo.
echo ✅ Hoàn tất!
pause
