@echo off
echo ========================================================
echo   ISAAC SIM - COMPLETE FIX (NumPy + SciPy)
echo ========================================================
echo.
echo Installing ALL required dependencies for Isaac Sim
echo.

set ISAAC_PYTHON=C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64\python.bat

echo [Step 1/5] Checking current versions...
call "%ISAAC_PYTHON%" -c "try:\n    import numpy\n    print(f'NumPy: {numpy.__version__}')\nexcept: print('NumPy: NOT INSTALLED')"
call "%ISAAC_PYTHON%" -c "try:\n    import scipy\n    print(f'SciPy: {scipy.__version__}')\nexcept: print('SciPy: NOT INSTALLED')"

echo.
echo [Step 2/5] Uninstalling incompatible versions...
call "%ISAAC_PYTHON%" -m pip uninstall -y numpy scipy 2>nul

echo.
echo [Step 3/5] Installing compatible NumPy...
call "%ISAAC_PYTHON%" -m pip install numpy==1.23.5

echo.
echo [Step 4/5] Installing compatible SciPy...
call "%ISAAC_PYTHON%" -m pip install scipy==1.10.1

echo.
echo [Step 5/5] Verifying installation...
call "%ISAAC_PYTHON%" -c "import numpy; import scipy; print(f'SUCCESS! NumPy {numpy.__version__}, SciPy {scipy.__version__}')"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================================
    echo   FIX COMPLETE!
    echo ========================================================
    echo.
    echo   NumPy: 1.23.5 (compatible)
    echo   SciPy: 1.10.1 (compatible)
    echo.
    echo   Isaac Sim should now start properly.
    echo.
    echo   Next step: Run .\RUN_SIMPLE_DEMO.bat
    echo.
) else (
    echo.
    echo ========================================================
    echo   FIX FAILED!
    echo ========================================================
    echo.
    echo   Please check the error messages above.
    echo.
)

pause
