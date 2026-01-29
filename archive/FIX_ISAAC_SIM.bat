@echo off
echo ========================================================
echo   ISAAC SIM - NUMPY FIX SCRIPT
echo ========================================================
echo.
echo This script will fix the NumPy compatibility issue
echo that is preventing Isaac Sim extensions from loading.
echo.

set ISAAC_PYTHON=C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64\python.bat

echo [Step 1/4] Checking current NumPy version...
call "%ISAAC_PYTHON%" -c "import numpy; print(f'Current NumPy: {numpy.__version__}')"

echo.
echo [Step 2/4] Uninstalling conflicting packages...
call "%ISAAC_PYTHON%" -m pip uninstall -y numpy scipy

echo.
echo [Step 3/4] Reinstalling compatible NumPy version...
call "%ISAAC_PYTHON%" -m pip install numpy==1.23.5

echo.
echo [Step 4/4] Verifying installation...
call "%ISAAC_PYTHON%" -c "import numpy; print(f'New NumPy: {numpy.__version__}')"

echo.
echo ========================================================
echo   FIX COMPLETE!
echo ========================================================
echo.
echo NumPy has been downgraded to a compatible version.
echo.
echo Next steps:
echo   1. Run: .\RUN_TABLE_SETUP.bat
echo   2. Test G29 + Piper arm control
echo.
pause
