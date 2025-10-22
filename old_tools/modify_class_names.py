#!/usr/bin/env python3
"""
Script to modify class names in a YOLO model file.
Changes class names while preserving all other model parameters and weights.
"""

import torch
import yaml
import tempfile
import os
from pathlib import Path

def load_yolo_model(model_path):
    """Load YOLO model and extract class information."""
    print(f"Loading YOLO model from: {model_path}")

    # Load the model checkpoint (with weights_only=False for YOLO models)
    checkpoint = torch.load(model_path, map_location='cpu', weights_only=False)

    print("Model checkpoint keys:", list(checkpoint.keys()))

    # Extract model info
    if 'model' in checkpoint:
        model = checkpoint['model']
        print("Model architecture keys:", list(model.__dict__.keys()) if hasattr(model, '__dict__') else "No __dict__")

    # Look for class names in various possible locations
    class_names = None

    # Check if there's a 'names' key in the checkpoint
    if 'names' in checkpoint:
        class_names = checkpoint['names']
        print("Found class names in checkpoint['names']:", class_names)

    # Check if there's class info in the model
    if hasattr(checkpoint.get('model', {}), 'names'):
        class_names = checkpoint['model'].names
        print("Found class names in model.names:", class_names)

    # Check if there's a yaml config
    if 'yaml' in checkpoint:
        yaml_config = checkpoint['yaml']
        if isinstance(yaml_config, str):
            try:
                config = yaml.safe_load(yaml_config)
                if 'names' in config:
                    class_names = config['names']
                    print("Found class names in yaml config:", class_names)
            except:
                pass

    return checkpoint, class_names

def update_class_names(checkpoint, old_names, new_names_mapping):
    """Update class names in the model checkpoint."""
    print(f"Updating class names...")
    print(f"Current names: {old_names}")
    print(f"Mapping: {new_names_mapping}")

    # Create new names list/dict
    if isinstance(old_names, dict):
        new_names = {}
        for idx, old_name in old_names.items():
            if old_name in new_names_mapping:
                new_names[idx] = new_names_mapping[old_name]
            else:
                new_names[idx] = old_name
    elif isinstance(old_names, list):
        new_names = []
        for old_name in old_names:
            if old_name in new_names_mapping:
                new_names.append(new_names_mapping[old_name])
            else:
                new_names.append(old_name)
    else:
        print(f"Unexpected class names format: {type(old_names)}")
        return checkpoint

    print(f"New names: {new_names}")

    # Update names in all possible locations
    if 'names' in checkpoint:
        checkpoint['names'] = new_names
        print("Updated checkpoint['names']")

    if 'model' in checkpoint and hasattr(checkpoint['model'], 'names'):
        checkpoint['model'].names = new_names
        print("Updated model.names")

    # Update yaml config if it exists
    if 'yaml' in checkpoint:
        yaml_config = checkpoint['yaml']
        if isinstance(yaml_config, str):
            try:
                config = yaml.safe_load(yaml_config)
                if 'names' in config:
                    config['names'] = new_names
                    checkpoint['yaml'] = yaml.dump(config)
                    print("Updated yaml config")
            except Exception as e:
                print(f"Warning: Could not update yaml config: {e}")

    return checkpoint

def save_modified_model(checkpoint, output_path):
    """Save the modified model checkpoint."""
    print(f"Saving modified model to: {output_path}")
    torch.save(checkpoint, output_path)
    print("Model saved successfully!")

def verify_changes(model_path, expected_names):
    """Verify that the changes were applied correctly."""
    print(f"Verifying changes in: {model_path}")

    checkpoint, class_names = load_yolo_model(model_path)

    print(f"Verification - Class names: {class_names}")

    # Convert to comparable format
    if isinstance(class_names, dict):
        actual_names = list(class_names.values())
    else:
        actual_names = class_names

    if isinstance(expected_names, dict):
        expected_names_list = list(expected_names.values())
    else:
        expected_names_list = expected_names

    if actual_names == expected_names_list:
        print("✅ Verification successful! Class names updated correctly.")
        return True
    else:
        print("❌ Verification failed! Class names don't match expected values.")
        print(f"Expected: {expected_names_list}")
        print(f"Actual: {actual_names}")
        return False

def main():
    # Configuration
    model_path = "best copy.pt"
    output_path = "best copy.pt"  # Overwrite the original

    # Class name mapping: old_name -> new_name
    name_mapping = {
        "straight": "shape_000",
        "L-shape": "104",
        "U-shape": "200",
        "complex": "complex"  # No change
    }

    try:
        # Load and examine the model
        checkpoint, current_names = load_yolo_model(model_path)

        if current_names is None:
            print("❌ Could not find class names in the model file!")
            return False

        # Update class names
        modified_checkpoint = update_class_names(checkpoint, current_names, name_mapping)

        # Save the modified model
        save_modified_model(modified_checkpoint, output_path)

        # Verify the changes
        expected_names = ["shape_000", "104", "200", "complex"]
        success = verify_changes(output_path, expected_names)

        return success

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Class names updated successfully!")
    else:
        print("\n💥 Failed to update class names.")