@echo off
echo ============================================
echo Starting X Server for Isaac Sim
echo ============================================
echo.
echo This will launch VcXsrv X Server to display
echo Isaac Sim GUI from WSL2.
echo.
echo Make sure to:
echo 1. Allow VcXsrv through Windows Firewall
echo 2. Keep this window open while using Isaac Sim
echo.
echo ============================================
echo.

start "" "C:\Program Files\VcXsrv\vcxsrv.exe" :0 -multiwindow -clipboard -wgl -ac

echo X Server is now running!
echo.
echo You can now run Isaac Sim in WSL2 with:
echo   wsl
echo   /root/launch_isaac_gui.sh
echo.
echo Press any key to stop the X Server...
pause > nul
