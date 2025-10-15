# Build-Installer.ps1
# PowerShell script để build Inno Setup installer

# Chuyển về thư mục gốc của dự án
Set-Location (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent)

param(
    [string]$OutputDir = "installer\output",
    [string]$OutputName = "",
    [switch]$Quiet = $false,
    [string]$Version = ""
)

Write-Host "Building Inno Setup Installer" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

# Tìm ISCC.exe
$IsccPaths = @(
    "C:\Program Files\Inno Setup 6\ISCC.exe",
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    "C:\Program Files (x86)\Inno Setup 5\ISCC.exe"
)

$IsccPath = $null
foreach ($path in $IsccPaths) {
    if (Test-Path $path) {
        $IsccPath = $path
        Write-Host "Found ISCC at: $path" -ForegroundColor Green
        break
    }
}

if (-not $IsccPath) {
    Write-Host "ISCC.exe not found!" -ForegroundColor Red
    Write-Host "Please install Inno Setup from: https://jrsoftware.org/isinfo.php"
    exit 1
}

# Xây dựng câu lệnh
$ScriptPath = "installer\scripts\installer.iss"
$Arguments = @()

if ($OutputDir) {
    $Arguments += "/O`"$OutputDir`""
}

if ($OutputName) {
    $Arguments += "/F`"$OutputName`""
}

if ($Quiet) {
    $Arguments += "/Q"
}

if ($Version) {
    $Arguments += "/DAppVersion=$Version"
}

$Arguments += "`"$ScriptPath`""

# Chạy build
Write-Host "Building installer..." -ForegroundColor Yellow
Write-Host "Command: $IsccPath $($Arguments -join ' ')" -ForegroundColor Gray

$Process = Start-Process -FilePath $IsccPath -ArgumentList $Arguments -Wait -PassThru -NoNewWindow

if ($Process.ExitCode -eq 0) {
    Write-Host "Build completed successfully!" -ForegroundColor Green
    Write-Host "Output directory: $OutputDir" -ForegroundColor Cyan

    # Hiển thị file đã tạo
    $OutputFiles = Get-ChildItem -Path $OutputDir -Filter "*.exe" | Sort-Object LastWriteTime -Descending
    if ($OutputFiles) {
        Write-Host "Created files:" -ForegroundColor Cyan
        foreach ($file in $OutputFiles) {
            $size = [math]::Round($file.Length / 1MB, 2)
            Write-Host "   - $($file.Name) ($size MB)" -ForegroundColor White
        }
    }
} else {
    Write-Host "Build failed with exit code: $($Process.ExitCode)" -ForegroundColor Red
    exit $Process.ExitCode
}