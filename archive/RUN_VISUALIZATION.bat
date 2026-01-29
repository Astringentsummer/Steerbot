@echo off
echo ========================================================
echo   PIPER CONTROLS G29 - WITH RVIZ VISUALIZATION
echo ========================================================
echo.
echo Launching in WSL2...
echo.

wsl bash -c "cd /mnt/c/Users/rohit/Downloads/Steerbot-Gripper/Steerbot-Gripper && chmod +x RUN_WITH_VISUALIZATION.sh && ./RUN_WITH_VISUALIZATION.sh"

echo.
pause
