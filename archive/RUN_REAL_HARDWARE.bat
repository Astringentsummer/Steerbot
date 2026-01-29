@echo off
echo ========================================================
echo   G29 + PIPER REAL HARDWARE TEST
echo ========================================================
echo.
echo Launching in WSL2...
echo.

wsl bash -c "cd /mnt/c/Users/rohit/Downloads/Steerbot-Gripper/Steerbot-Gripper && chmod +x RUN_REAL_HARDWARE.sh && ./RUN_REAL_HARDWARE.sh"

echo.
echo Test complete.
pause
