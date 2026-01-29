#!/usr/bin/env python3
"""
Train SAC (Soft Actor-Critic) on Piper G29 Environment
"""

import os
import sys
from stable_baselines3 import SAC
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
from stable_baselines3.common.callbacks import CheckpointCallback, EvalCallback
from stable_baselines3.common.monitor import Monitor
import torch

sys.path.insert(0, os.path.dirname(__file__))
from piper_g29_env import PiperG29Environment


def train_sac(
    total_timesteps: int = 500_000,
    save_path: str = "../trained_models/sac",
    log_path: str = "../logs/sac",
    eval_freq: int = 5_000
):
    """Train SAC algorithm"""
    
    os.makedirs(save_path, exist_ok=True)
    os.makedirs(log_path, exist_ok=True)
    
    print("="*70)
    print(" Training SAC on Piper G29 Environment")
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
    
    # Create SAC model
    print("[3/5] Creating SAC model...")
    model = SAC(
        policy="MlpPolicy",
        env=env,
        learning_rate=3e-4,
        buffer_size=1_000_000,
        learning_starts=10_000,
        batch_size=256,
        tau=0.005,
        gamma=0.99,
        train_freq=1,
        gradient_steps=1,
        ent_coef="auto",
        target_update_interval=1,
        verbose=1,
        tensorboard_log=log_path,
        device="cuda" if torch.cuda.is_available() else "cpu"
    )
    print("✓ SAC model created")
    print(f"  Policy: MlpPolicy")
    print(f"  Learning rate: 3e-4")
    print(f"  Buffer size: 1,000,000")
    print(f"  Batch size: 256")
    print(f"  Entropy: auto-tuned")
    
    # Create callbacks
    print("[4/5] Setting up callbacks...")
    checkpoint_callback = CheckpointCallback(
        save_freq=25_000,
        save_path=save_path,
        name_prefix="sac_checkpoint"
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
    final_path = os.path.join(save_path, "sac_final")
    model.save(final_path)
    env.save(os.path.join(save_path, "vec_normalize.pkl"))
    
    print()
    print("="*70)
    print(" Training Complete!")
    print("="*70)
    print(f"Final model saved to: {final_path}")
    print(f"Best model saved to: {save_path}/best_model.zip")
    print()
    
    env.close()
    eval_env.close()
    
    return model


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Train SAC on Piper G29")
    parser.add_argument("--timesteps", type=int, default=500_000, help="Total timesteps")
    parser.add_argument("--save-path", type=str, default="../trained_models/sac", help="Save path")
    parser.add_argument("--log-path", type=str, default="../logs/sac", help="Log path")
    parser.add_argument("--eval-freq", type=int, default=5_000, help="Eval frequency")
    
    args = parser.parse_args()
    
    train_sac(
        total_timesteps=args.timesteps,
        save_path=args.save_path,
        log_path=args.log_path,
        eval_freq=args.eval_freq
    )
