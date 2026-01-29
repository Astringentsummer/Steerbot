@echo off
echo ========================================================
echo   ISAAC SIM DIAGNOSTIC TOOL
echo ========================================================
echo.
echo This will diagnose why Isaac Sim won't start
echo.

set ISAAC_SIM_PATH=C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64
set ISAAC_PYTHON=%ISAAC_SIM_PATH%\python.bat

echo [1/6] Checking Isaac Sim installation...
if exist "%ISAAC_SIM_PATH%" (
    echo   [OK] Isaac Sim directory found
) else (
    echo   [ERROR] Isaac Sim not found at: %ISAAC_SIM_PATH%
    echo   Please verify installation path
    pause
    exit /b 1
)

echo.
echo [2/6] Checking Python executable...
if exist "%ISAAC_PYTHON%" (
    echo   [OK] Python.bat found
) else (
    echo   [ERROR] Python.bat not found
    pause
    exit /b 1
)

echo.
echo [3/6] Testing Python import...
call "%ISAAC_PYTHON%" -c "print('Python works!')" 2>nul
if %ERRORLEVEL% EQU 0 (
    echo   [OK] Python executable works
) else (
    echo   [ERROR] Python executable failed
    pause
    exit /b 1
)

echo.
echo [4/6] Checking NumPy version...
call "%ISAAC_PYTHON%" -c "import numpy; print(f'  NumPy: {numpy.__version__}')"
if %ERRORLEVEL% NEQ 0 (
    echo   [ERROR] NumPy import failed
    echo   Run: .\FIX_ISAAC_SIM.bat
    pause
    exit /b 1
)

echo.
echo [5/6] Testing SimulationApp import...
call "%ISAAC_PYTHON%" -c "from isaacsim import SimulationApp; print('  [OK] SimulationApp can be imported')" 2>temp_error.txt
if %ERRORLEVEL% NEQ 0 (
    echo   [ERROR] SimulationApp import failed
    echo.
    echo   Error details:
    type temp_error.txt
    del temp_error.txt
    echo.
    echo   This is the main issue preventing Isaac Sim from starting.
    pause
    exit /b 1
) else (
    del temp_error.txt 2>nul
)

echo.
echo [6/6] Testing minimal Isaac Sim startup...
echo   Creating test script...

echo from isaacsim import SimulationApp > test_isaac.py
echo config = {"headless": True} >> test_isaac.py
echo print("Creating SimulationApp...") >> test_isaac.py
echo app = SimulationApp(config) >> test_isaac.py
echo print("SUCCESS: Isaac Sim started!") >> test_isaac.py
echo app.close() >> test_isaac.py

echo   Running test...
call "%ISAAC_PYTHON%" test_isaac.py
set TEST_RESULT=%ERRORLEVEL%

del test_isaac.py 2>nul

if %TEST_RESULT% EQU 0 (
    echo.
    echo ========================================================
    echo   [SUCCESS] Isaac Sim CAN start!
    echo ========================================================
    echo.
    echo   The issue may be with your specific script.
    echo   Try running: .\RUN_SIMPLE_DEMO.bat
    echo.
) else (
    echo.
    echo ========================================================
    echo   [FAILED] Isaac Sim cannot start
    echo ========================================================
    echo.
    echo   Possible solutions:
    echo   1. Reinstall Isaac Sim
    echo   2. Check GPU drivers
    echo   3. Run as Administrator
    echo   4. Check Windows Event Viewer for crashes
    echo.
)

pause
