#!/usr/bin/env python3
"""
Quick verification script to check the class names in the modified YOLO model.
"""

import torch

def check_model_classes(model_path):
    """Load and display the class names from a YOLO model."""
    print(f"Checking model: {model_path}")

    try:
        # Load the model
        checkpoint = torch.load(model_path, map_location='cpu', weights_only=False)

        # Get class names
        if hasattr(checkpoint.get('model', {}), 'names'):
            class_names = checkpoint['model'].names
            print(f"Class names: {class_names}")

            # Display as a clean list
            if isinstance(class_names, dict):
                print("Class mapping:")
                for idx, name in class_names.items():
                    print(f"  {idx}: {name}")

            return class_names
        else:
            print("No class names found in model")
            return None

    except Exception as e:
        print(f"Error loading model: {e}")
        return None

if __name__ == "__main__":
    print("=== YOLO Model Class Verification ===\n")

    # Check original backup
    print("1. Original model (backup):")
    check_model_classes("best_copy_original_backup.pt")

    print("\n" + "="*50 + "\n")

    # Check modified model
    print("2. Modified model:")
    check_model_classes("best copy.pt")

    print("\n=== Verification Complete ===")