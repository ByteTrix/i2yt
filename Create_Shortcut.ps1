# PowerShell script to create a Windows shortcut
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$PSScriptRoot\Instagram Reel Scraper.lnk")
$Shortcut.TargetPath = "powershell.exe"
$Shortcut.Arguments = "-NoExit -ExecutionPolicy Bypass -File `"$PSScriptRoot\run_scraper.ps1`""
$Shortcut.WorkingDirectory = $PSScriptRoot
$Shortcut.IconLocation = "powershell.exe,0"
$Shortcut.Description = "Launch Instagram Reel Scraper"
$Shortcut.WindowStyle = 1
$Shortcut.Save()

Write-Host "Desktop shortcut created successfully!" -ForegroundColor Green
Write-Host "Location: $PSScriptRoot\Instagram Reel Scraper.lnk" -ForegroundColor Cyan
Write-Host ""
Write-Host "You can now double-click the shortcut to launch the scraper." -ForegroundColor Yellow
