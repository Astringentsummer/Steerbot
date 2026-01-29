@echo off
echo ========================================================
echo   ISAAC SIM - GUI WINDOW TEST
echo ========================================================
echo.
echo This will open the Isaac Sim GUI window
echo The window should stay open for 30 seconds
echo.

set ISAAC_PYTHON=C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64\python.bat

echo Starting Isaac Sim GUI...
echo.
echo IMPORTANT: Look for a new window to open!
echo.

call "%ISAAC_PYTHON%" TEST_GUI_WINDOW.py

echo.
echo Test complete!
pause
