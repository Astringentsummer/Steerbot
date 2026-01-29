#!/usr/bin/env python3
"""
Train PPO (Proximal Policy Optimization) on Piper G29 Environment
"""

import os
import sys
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
from stable_baselines3.common.callbacks import CheckpointCallback, EvalCallback
from stable_baselines3.common.monitor import Monitor
import torch

# Add rl_training to path
sys.path.insert(0, os.path.dirname(__file__))
from piper_g29_env import PiperG29Environment


def train_ppo(
    total_timesteps: int = 1_000_000,
    save_path: str = "../trained_models/ppo",
    log_path: str = "../logs/ppo",
    eval_freq: int = 10_000
):
    """
    Train PPO algorithm on Piper G29 environment
    
    Args:
        total_timesteps: Total training steps
        save_path: Where to save models
        log_path: Where to save logs
        eval_freq: Evaluation frequency
    """
    
    # Create directories
    os.makedirs(save_path, exist_ok=True)
    os.makedirs(log_path, exist_ok=True)
    
    print("="*70)
    print(" Training PPO on Piper G29 Environment")
    print("="*70)
    print(f"Total timesteps: {total_timesteps:,}")
    print(f"Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")
    print()
    
    # Create environment
    print("[1/5] Creating environment...")
    env = PiperG29Environment(render_mode=None, headless=True)
    env = Monitor(env, log_path)
    env = DummyVecEnv([lambda: env])
    env = VecNormalize(env, norm_obs=True, norm_reward=True)
    print("✓ Environment created")
    
    # Create evaluation environment
    print("[2/5] Creating evaluation environment...")
    eval_env = PiperG29Environment(render_mode=None, headless=True)
    eval_env = Monitor(eval_env, log_path + "/eval")
    eval_env = DummyVecEnv([lambda: eval_env])
    eval_env = VecNormalize(eval_env, norm_obs=True, norm_reward=False)
    print("✓ Evaluation environment created")
    
    # Create PPO model
    print("[3/5] Creating PPO model...")
    model = PPO(
        policy="MlpPolicy",
        env=env,
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        ent_coef=0.01,
        vf_coef=0.5,
        max_grad_norm=0.5,
        verbose=1,
        tensorboard_log=log_path,
        device="cuda" if torch.cuda.is_available() else "cpu"
    )
    print("✓ PPO model created")
    print(f"  Policy: MlpPolicy")
    print(f"  Learning rate: 3e-4")
    print(f"  Batch size: 64")
    print(f"  Clip range: 0.2")
    
    # Create callbacks
    print("[4/5] Setting up callbacks...")
    checkpoint_callback = CheckpointCallback(
        save_freq=50_000,
        save_path=save_path,
        name_prefix="ppo_checkpoint"
    )
    
    eval_callback = EvalCallback(
        eval_env,
        best_model_save_path=save_path,
        log_path=log_path,
        eval_freq=eval_freq,
        deterministic=True,
        render=False
    )
    print("✓ Callbacks configured")
    
    # Train
    print("[5/5] Starting training...")
    print()
    print("="*70)
    print(" Training in progress...")
    print(" Monitor with: tensorboard --logdir", log_path)
    print("="*70)
    print()
    
    model.learn(
        total_timesteps=total_timesteps,
        callback=[checkpoint_callback, eval_callback],
        progress_bar=True
    )
    
    # Save final model
    final_path = os.path.join(save_path, "ppo_final")
    model.save(final_path)
    env.save(os.path.join(save_path, "vec_normalize.pkl"))
    
    print()
    print("="*70)
    print(" Training Complete!")
    print("="*70)
    print(f"Final model saved to: {final_path}")
    print(f"Best model saved to: {save_path}/best_model.zip")
    print()
    
    # Close environments
    env.close()
    eval_env.close()
    
    return model


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Train PPO on Piper G29")
    parser.add_argument("--timesteps", type=int, default=1_000_000, help="Total timesteps")
    parser.add_argument("--save-path", type=str, default="../trained_models/ppo", help="Save path")
    parser.add_argument("--log-path", type=str, default="../logs/ppo", help="Log path")
    parser.add_argument("--eval-freq", type=int, default=10_000, help="Eval frequency")
    
    args = parser.parse_args()
    
    train_ppo(
        total_timesteps=args.timesteps,
        save_path=args.save_path,
        log_path=args.log_path,
        eval_freq=args.eval_freq
    )
