@echo off
chcp 65001 >nul
title Build Complete - Chicken Farm Management

echo ========================================
echo   BUILD HOÀN CHỈNH
echo   Chicken Farm Management Software
echo ========================================
echo.

echo 🚀 Bắt đầu quy trình build hoàn chỉnh...
echo.

echo ⏱️  Bước 1/4: Dọn dẹp build cũ...
call clean_build.bat

echo.
echo ⏱️  Bước 2/4: Build executable...
python build_windows.py

if %errorLevel% neq 0 (
    echo ❌ Build executable thất bại!
    pause
    exit /b 1
)

echo.
echo ⏱️  Bước 3/4: Tạo packages...
python create_package.py

if %errorLevel% neq 0 (
    echo ❌ Tạo package thất bại!
    pause
    exit /b 1
)

echo.
echo ⏱️  Bước 4/4: Kiểm tra kết quả...

echo.
echo 📊 Thống kê build:
echo ========================================

if exist "dist\ChickenFarmManager\ChickenFarmManager.exe" (
    echo ✅ Executable: dist\ChickenFarmManager\ChickenFarmManager.exe
    for %%I in ("dist\ChickenFarmManager\ChickenFarmManager.exe") do echo    Kích thước: %%~zI bytes
) else (
    echo ❌ Executable: Không tìm thấy
)

if exist "packages" (
    echo ✅ Packages folder: packages\
    for /d %%D in ("packages\*") do (
        echo    📁 %%~nxD
    )
) else (
    echo ❌ Packages: Không tìm thấy
)

echo.
echo 📦 ZIP files:
for %%F in ("*.zip") do (
    echo ✅ %%~nxF
    echo    Kích thước: %%~zF bytes
)

echo.
echo ========================================
echo 🎉 BUILD HOÀN CHỈNH THÀNH CÔNG!
echo ========================================
echo.
echo 📁 Kết quả build:
echo    • dist\ChickenFarmManager\ - File thực thi
echo    • packages\ - Các package phân phối
echo    • *.zip - File nén sẵn sàng phân phối
echo.
echo 💡 Bước tiếp theo:
echo    1. Test file .exe trong dist\
echo    2. Test installer trong packages\
echo    3. Phân phối file .zip
echo.

choice /C YN /M "Mở thư mục kết quả (Y/N)"
if %errorLevel% == 1 (
    explorer .
)

echo.
echo ✅ Hoàn tất!
pause
