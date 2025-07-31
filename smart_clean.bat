@echo off
chcp 65001 >nul
title Smart Clean - Chicken Farm Management

echo ========================================
echo   SMART CLEAN - Dọn dẹp thông minh
echo   Chicken Farm Management Software
echo ========================================
echo.
echo 🎯 Mục tiêu: Dọn dẹp file tạm thời, GIỮ LẠI kết quả build
echo.

echo 📋 Sẽ XÓA:
echo   • Thư mục build/ (file tạm PyInstaller)
echo   • File *.spec (tự động tạo)
echo   • File version_info.txt
echo   • Thư mục __pycache__/ và *.pyc
echo   • File log, temp
echo.

echo 📦 Sẽ GIỮ LẠI:
echo   • Thư mục dist/ (executable)
echo   • Thư mục packages/ (package phân phối)
echo   • File *.zip (package nén)
echo   • File install.bat, README_DISTRIBUTION.txt
echo.

choice /C YN /M "Tiếp tục dọn dẹp (Y/N)"
if %errorLevel% == 2 (
    echo Hủy dọn dẹp.
    pause
    exit /b 0
)

echo.
echo 🚀 Bắt đầu dọn dẹp...
python smart_cleanup.py

if %errorLevel% neq 0 (
    echo.
    echo ❌ Có lỗi xảy ra trong quá trình dọn dẹp!
    pause
    exit /b 1
)

echo.
echo ✅ Dọn dẹp hoàn tất!
pause
