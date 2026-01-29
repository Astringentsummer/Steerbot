@echo off
echo ========================================================
echo   MINIMAL TEST - Isaac Sim Basic Functionality
echo ========================================================
echo.
echo This will test if Isaac Sim can:
echo  1. Load successfully
echo  2. Create a simple scene
echo  3. Stay open without crashing
echo.
echo If this works, the problem is in the G29+Piper integration
echo If this fails, there's an Isaac Sim installation issue
echo.

set ISAAC_PYTHON=C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64\python.bat

echo Starting minimal test...
call "%ISAAC_PYTHON%" TEST_MINIMAL.py

echo.
echo Test completed.
pause
