# Steerbot-Gripper: SAC-Based Robotic Steering Control

Deep reinforcement learning system using Soft Actor-Critic (SAC) algorithm for training a Piper robotic arm to grasp and control a Logitech G29 steering wheel in NVIDIA Isaac Sim.

## Overview

This project implements a complete hardware-in-the-loop training pipeline for robotic manipulation tasks, featuring:

- **SAC Algorithm** with inverse kinematics guidance for stable learning
- **100,000 Episode Training** with curriculum learning and domain randomization
- **Integrated High-Fidelity Digital Twin:** Real-time synchronization between physical G29 steering and simulated Piper Arm.
- **MoveIt 2 Kinematic Control:** Utilization of MoveIt 2 and OMPL for collision-free robotic steering.
- **Hardware-in-the-Loop Simulation:** Direct bridge for human-in-the-loop driving simulation.
- **SAC Algorithm Guidance:** Advanced RL pipeline for autonomous grasping tasks.

## Features

### Training System
- Soft Actor-Critic (SAC) reinforcement learning
- Inverse kinematics (IK) reward shaping
- Curriculum learning: 15° → 30° → 45° → 55° rotation
- Domain randomization for robustness
- Automatic checkpointing every 500 episodes

### Hardware Integration
- G29 steering wheel → Isaac Sim bridge
- Real-time policy deployment to Piper arm
- 30 Hz control loop
- Safety features and emergency stop

### Digital Twin & Interactive Integration
- **Kinematic Processor:** Industrial-grade signal processing and joint state mapping.
- **Physics Backend:** Integrated Isaac Sim environment with automated ROS 2 bridging.
- **Deployment Orchestration:** Cross-platform launch scripts (Windows/Linux) for unified system execution.
- **Telemetry Synthesis:** Integrated signal generation for hardware-free system verification.

## Quick Start

### Prerequisites

```
- NVIDIA Isaac Sim 4.5.0+
- PyTorch 2.0+ with CUDA
- Python 3.10+
- Logitech G29 steering wheel (optional)
- Piper robotic arm (optional)
```

### Training

**Headless Training with Dashboard:**
```powershell
cd isaac_lab
& "C:\path\to\isaac-sim\python.bat" train_dashboard_100k.py
```

Then open http://localhost:8080 in your browser to monitor progress.

**Visual Training (GUI):**
```powershell
& "C:\path\to\isaac-sim\python.bat" train_visual_100k.py
```

### Testing Trained Agent

```powershell
& "C:\path\to\isaac-sim\python.bat" test_trained_agent.py
```

### Hardware Integration

**1. Initialize Simulation Backend:**
```bash
./python.sh simulation_bridge_backend.py
```

**2. Launch Interactive Controller:**
```bash
python3 hictp_steering_controller.py
```

**3. (Optional) Run Input Simulator:**
```bash
python3 input_signals_simulator.py
```

## Project Structure

```
Steerbot-Gripper/
 isaac_lab/
    train_sac_isaac.py           # Initial 1K training
    train_extended_sac.py        # Extended 100K training
    train_dashboard_100k.py      # Training with web dashboard
    train_visual_100k.py         # Training with GUI
    sac_algorithm.py             # SAC implementation
    inverse_kinematics.py        # IK solver
    export_model.py              # Model export utility
    sac_adapter.py               # Integration adapter
    g29_isaac_bridge.py          # G29 hardware bridge
    deploy_to_piper.py           # Piper deployment
    test_trained_agent.py        # Model evaluation
 docs/
    HARDWARE_IN_LOOP_GUIDE.md    # Complete workflow guide
    TEAMMATE_INTEGRATION.md      # Integration documentation
    INTEGRATION_SPEC.md          # API specification
    TRAINING_QUICKSTART.md       # Quick start guide
 README.md
```

## Documentation

- [Hardware-in-Loop Guide](isaac_lab/HARDWARE_IN_LOOP_GUIDE.md) - Complete training and deployment workflow
- [Teammate Integration](isaac_lab/TEAMMATE_INTEGRATION.md) - How to integrate trained policies
- [Integration Spec](isaac_lab/INTEGRATION_SPEC.md) - API documentation
- [Training Quickstart](isaac_lab/TRAINING_QUICKSTART.md) - Fast setup guide

## Training Configuration

### Curriculum Learning
| Stage | Episodes | Target Angle | Difficulty |
|-------|----------|--------------|------------|
| 1 | 0-10K | 15° | Easy |
| 2 | 10K-30K | 30° | Medium |
| 3 | 30K-60K | 45° | Hard |
| 4 | 60K-100K | 55° | Expert |

### Domain Randomization
- Position: ±0.1m
- Friction: 0.3-0.9
- Mass: 0.8-1.2x nominal

### Hyperparameters
- Algorithm: SAC
- Replay Buffer: 2M transitions
- Batch Size: 256
- Learning Rate: 3e-4
- Discount Factor: 0.99
- Target Update: τ=0.005

## Performance

### Expected Results (100K Episodes)
- Success Rate: 80-95%
- Grasp Success: 90%+
- Average Reward: ~125
- Final Angle Accuracy: ±5°

### Training Time
- Headless: ~100 hours (4 days)
- With GUI: ~200 hours (8 days)
- Hardware: NVIDIA RTX 5080 Laptop GPU

## Integration with Existing Systems

For teams with existing virtual hardware interfaces:

```python
from isaac_lab.sac_adapter import SACPolicyAdapter

# Load trained policy
policy = SACPolicyAdapter('piper_sac_policy.pt')

# In your control loop
state = your_system.get_state()
action = policy.get_action(state)
your_system.send_action(action)
```

See [INTEGRATION_SPEC.md](isaac_lab/INTEGRATION_SPEC.md) for details.

## Requirements

### Software
```
torch>=2.0.0
numpy>=1.24.0
scipy>=1.10.0
matplotlib>=3.7.0
pyyaml>=6.0
inputs>=0.5  # For G29 hardware
```

### Hardware
- NVIDIA GPU with CUDA support (RTX 3060+ recommended)
- 16GB+ RAM
- Logitech G29 steering wheel (for hardware integration)
- Piper robotic arm (for deployment)

## Status

- Training Framework: Complete
- Hardware Integration: Complete
- Documentation: Complete
- Model Training: In Progress (30K/100K episodes)

## Contributing

This project is part of ongoing research in robotic manipulation and reinforcement learning. Contributions and feedback are welcome.

## License

[Specify your license here]

## Citation

If you use this work in your research, please cite:

```bibtex
@misc{steerbot-gripper,
  title={SAC-Based Robotic Steering Control with Hardware-in-the-Loop Training},
  author={[Your Name]},
  year={2026},
  publisher={GitHub},
  url={https://github.com/[your-username]/Steerbot-Gripper}
}
```

## Acknowledgments

- NVIDIA Isaac Sim team for the simulation platform
- OpenAI for the SAC algorithm
- [Add other acknowledgments]

## Contact

For questions or collaboration:
- GitHub Issues: [Astringentsummer/Steerbot](https://github.com/Astringentsummer/Steerbot/issues)
- Email: rohit15parmar15@gmail.com

---

**Note:** This repository follows a strict MLOps separation of concerns. The `training_pipeline/` generates model artifacts, which are then versioned and consumed by the `inference_interface.py` in the operational system.

