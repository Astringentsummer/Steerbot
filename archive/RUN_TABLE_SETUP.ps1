# G29 + Piper Arm - Table Setup Launcher (PowerShell)

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  G29 + PIPER ARM - TABLE SETUP" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This simulates a person at a table with:" -ForegroundColor Yellow
Write-Host " - G29 steering wheel (fixed to table)" -ForegroundColor Yellow
Write-Host " - Piper arm (reaching toward wheel)" -ForegroundColor Yellow
Write-Host ""

$ISAAC_PYTHON = "C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64\python.bat"

Write-Host "[1/2] Starting G29 Bridge (Port 5006)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python g29_bridge_5006.py"

Start-Sleep -Seconds 2

Write-Host "[2/2] Launching Table Setup..." -ForegroundColor Green
Write-Host ""

& $ISAAC_PYTHON G29_PIPER_TABLE_SETUP.py

Write-Host ""
Write-Host "Integration closed." -ForegroundColor Yellow
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
