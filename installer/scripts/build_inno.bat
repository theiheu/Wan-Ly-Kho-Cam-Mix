@echo off
echo Building with Inno Setup...

REM Try common Inno Setup installation paths
set INNO_PATH=""

if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set INNO_PATH="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set INNO_PATH="C:\Program Files\Inno Setup 6\ISCC.exe"
) else if exist "C:\Program Files (x86)\Inno Setup 5\ISCC.exe" (
    set INNO_PATH="C:\Program Files (x86)\Inno Setup 5\ISCC.exe"
) else (
    echo ❌ Inno Setup not found in standard locations
    echo Please check your installation
    pause
    exit /b 1
)

echo ✅ Found Inno Setup: %INNO_PATH%
%INNO_PATH% installer\scripts\installer.iss

echo.
echo ✅ Build complete!
pause