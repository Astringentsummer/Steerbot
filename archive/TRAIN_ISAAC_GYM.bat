@echo off
echo ========================================================
echo   ISAAC GYM RL TRAINING - G29 + PIPER ARM
echo ========================================================
echo.
echo Training with Isaac Sim's built-in RL framework
echo - 512 parallel GPU environments
echo - Expected time: ~30 minutes for 10M steps
echo - 100x faster than single-threaded training
echo.

set ISAAC_PYTHON=C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64\python.bat

echo [1/2] Checking Isaac Gym installation...
call "%ISAAC_PYTHON%" -c "import omni.isaac.gym; print('Isaac Gym found!')"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Isaac Gym not found!
    echo Please ensure Isaac Sim is properly installed.
    pause
    exit /b 1
)

echo.
echo [2/2] Starting RL training...
echo.
echo Training configuration:
echo   - Task: G29Piper
echo   - Algorithm: PPO
echo   - Environments: 512 (parallel on GPU)
echo   - Max iterations: 10000
echo.

cd isaac_rl

call "%ISAAC_PYTHON%" -m omni.isaac.gym.scripts.rlgames_train ^
    task=G29Piper ^
    train=G29PiperPPO ^
    headless=True ^
    num_envs=512

echo.
echo Training complete!
echo.
echo Trained model saved to: isaac_rl/runs/G29Piper/nn/
echo TensorBoard logs: isaac_rl/runs/G29Piper/summaries/
echo.
echo To view training progress:
echo   tensorboard --logdir=isaac_rl/runs
echo.
pause
