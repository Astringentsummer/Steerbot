#!/usr/bin/env python3
"""
Export Trained SAC Model for Integration with Teammates' System
Converts PyTorch model to portable TorchScript format
"""
import torch
import os
import sys

# Add isaac_lab to path
sys.path.append(os.path.dirname(__file__))
from sac_algorithm import SAC


def export_model(model_path, output_path='piper_sac_policy.pt'):
    """Export trained SAC model as TorchScript"""
    
    print("=" * 80)
    print("EXPORTING SAC MODEL FOR TEAMMATE INTEGRATION")
    print("=" * 80)
    print(f"Input: {model_path}")
    print(f"Output: {output_path}")
    print("=" * 80 + "\n")
    
    # Check if model exists
    if not os.path.exists(model_path):
        print(f" ERROR: Model not found: {model_path}")
        print("\nAvailable models:")
        for root, dirs, files in os.walk('logs'):
            for file in files:
                if file.endswith('.pt'):
                    print(f"  - {os.path.join(root, file)}")
        return False
    
    # Load trained model
    print("Loading trained model...")
    agent = SAC(state_dim=15, action_dim=8, device='cpu')
    agent.load(model_path)
    print(" Model loaded\n")
    
    # Export actor network as TorchScript
    print("Exporting actor network...")
    agent.actor.eval()
    
    # Create example input
    example_input = torch.randn(1, 15)
    
    # Trace the model
    traced_actor = torch.jit.trace(agent.actor, example_input)
    
    # Save traced model
    traced_actor.save(output_path)
    print(f" Model exported: {output_path}\n")
    
    # Test exported model
    print("Testing exported model...")
    loaded_model = torch.jit.load(output_path)
    test_input = torch.randn(1, 15)
    
    with torch.no_grad():
        original_output, _ = agent.actor(test_input)
        exported_output, _ = loaded_model(test_input)
        
        diff = torch.abs(original_output - exported_output).max().item()
        print(f" Max difference: {diff:.2e} (should be ~0)")
    
    # Print model info
    file_size = os.path.getsize(output_path) / (1024 * 1024)
    print(f"\n{'='*80}")
    print("EXPORT COMPLETE")
    print(f"{'='*80}")
    print(f"File: {output_path}")
    print(f"Size: {file_size:.2f} MB")
    print(f"Format: TorchScript (portable)")
    print(f"\nShare this file with your teammates!")
    print(f"{'='*80}")
    
    return True


if __name__ == "__main__":
    # Export latest model
    model_paths = [
        "logs/extended_sac/sac_final_10k.pt",  # Extended training
        "logs/sac_20260131_211747/sac_final.pt",  # Initial training
    ]
    
    # Find first existing model
    model_path = None
    for path in model_paths:
        if os.path.exists(path):
            model_path = path
            break
    
    if model_path is None:
        print(" No trained model found!")
        print("Train a model first using train_sac_isaac.py or train_extended_sac.py")
    else:
        export_model(model_path, output_path='piper_sac_policy.pt')
