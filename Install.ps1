# Universal Android Flasher Automated Installer
$ProgressPreference = 'SilentlyContinue'

# 1. Define workspace targets on the user's desktop
$TargetFolder = "$HOME\Desktop\Android_Flasher"
$ExeUrl = "https://github.com"
$ShortcutPath = "$HOME\Desktop\Universal Android Flasher.lnk"

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  Downloading Universal Android Flasher...   " -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# 2. Create the target directory if it doesn't exist
if (-not (Test-Path $TargetFolder)) {
    New-Item -ItemType Directory -Force -Path $TargetFolder | Out-Null
}

# 3. Download your compiled executable directly from GitHub
Write-Host "Downloading application binaries..." -ForegroundColor Yellow
try {
    Invoke-WebRequest -Uri $ExeUrl -OutFile "$TargetFolder\universal_flasher.exe" -TimeoutSec 60
} catch {
    Write-Host "🔴 Error: Failed to download the flasher executable. Check your internet connection." -ForegroundColor Red
    Exit
}

# 4. Create a clean Desktop Shortcut for the user
Write-Host "Creating desktop shortcut environment..." -ForegroundColor Yellow
try {
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut($ShortcutPath)
    $Shortcut.TargetPath = "$TargetFolder\universal_flasher.exe"
    $Shortcut.WorkingDirectory = $TargetFolder
    $Shortcut.Description = "Launch Universal Android Flash and Sideload Companion Tool"
    $Shortcut.Save()
} catch {
    Write-Host "⚠️ Warning: Could not create desktop shortcut icon automatically." -ForegroundColor Yellow
}

Write-Host "`n🟢 SUCCESS: Installation Complete!" -ForegroundColor Green
Write-Host "You can find your tool inside the '$TargetFolder' folder or use the shortcut on your Desktop." -ForegroundColor White
Write-Host "=============================================" -ForegroundColor Cyan

# 5. Launch the tool automatically right after download finishes
Start-Process "$TargetFolder\universal_flasher.exe"
