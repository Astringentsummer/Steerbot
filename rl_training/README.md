# RL Training - Quick Start (Updated for Isaac Sim)

## ⚠️ IMPORTANT: Use Isaac Sim's Python

The RL training scripts **must** be run with Isaac Sim's Python interpreter, not your system Python.

## Installation

**Option 1: Use the launcher scripts (Recommended)**

Just run the appropriate `.bat` file from the main directory:

```cmd
cd C:\Users\rohit\Downloads\Steerbot-Gripper\Steerbot-Gripper

# Train SAC (recommended)
.\TRAIN_SAC.bat

# Train PPO
.\TRAIN_PPO.bat

# Train TD3
.\TRAIN_TD3.bat
```

**Option 2: Manual installation**

```cmd
set ISAAC_PYTHON=C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64\python.bat
%ISAAC_PYTHON% -m pip install stable-baselines3[extra] gymnasium torch tensorboard
```

## Training

### SAC (Recommended - Sample Efficient)
```cmd
.\TRAIN_SAC.bat
```
- **Time:** ~2 hours on RTX 5080
- **Timesteps:** 500,000
- **Best for:** Deployment

### PPO (Stable Baseline)
```cmd
.\TRAIN_PPO.bat
```
- **Time:** ~4 hours on RTX 5080
- **Timesteps:** 1,000,000
- **Best for:** Initial prototyping

### TD3 (Deterministic Control)
```cmd
.\TRAIN_TD3.bat
```
- **Time:** ~2 hours on RTX 5080
- **Timesteps:** 500,000
- **Best for:** Precise control

## Monitor Training

While training is running, open a new terminal:

```cmd
set ISAAC_PYTHON=C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64\python.bat
%ISAAC_PYTHON% -m tensorboard.main --logdir logs
```

Then open: http://localhost:6006

## Trained Models

Models will be saved to:
- `trained_models/sac/best_model.zip`
- `trained_models/ppo/best_model.zip`
- `trained_models/td3/best_model.zip`

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'isaacsim.simulation_app'"

**Cause:** Using system Python instead of Isaac Sim's Python

**Solution:** Use the `.bat` launcher scripts or manually set `ISAAC_PYTHON` path

### Error: "IndexError: list index out of range"

**Cause:** Isaac Sim Python path issue

**Solution:** Verify Isaac Sim is installed at:
```
C:\Users\rohit\Downloads\isaac-sim-standalone-4.5.0-windows-x86_64
```

### Training too slow?

- Ensure GPU is being used (check CUDA availability)
- Reduce `--timesteps` for faster testing
- Use `headless=True` in environment

### Out of memory?

- Reduce `buffer_size` in training scripts
- Close other applications
- Use `headless=True` mode
