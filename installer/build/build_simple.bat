@echo off
echo 🧹 Clean Build Process
echo ========================

REM Kill any running processes
echo 🔄 Stopping processes...
taskkill /F /IM ChickenFarmManager.exe 2>nul
timeout /t 2 /nobreak >nul

REM Clean output directory
echo 🧹 Cleaning output...
if exist "..\..\installer\output\ChickenFarmManager.exe" (
    del /F /Q "..\..\installer\output\ChickenFarmManager.exe"
)

REM Clean build directories
if exist "..\..\dist" rmdir /S /Q "..\..\dist"
if exist "..\..\build" rmdir /S /Q "..\..\build"

REM Create output directory
if not exist "..\..\installer\output" mkdir "..\..\installer\output"

REM Build executable
echo 🔨 Building executable...
cd ..\..
pyinstaller --onefile --windowed --name=ChickenFarmManager --distpath=installer\output --clean --noconfirm --add-data=src;src main.py

REM Check result
if exist "installer\output\ChickenFarmManager.exe" (
    echo ✅ Build successful!
    echo 📦 File: installer\output\ChickenFarmManager.exe
) else (
    echo ❌ Build failed!
)

pause