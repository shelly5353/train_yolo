#!/usr/bin/env python3
"""
Batch YOLO Detection
Runs your trained model on all images and saves initial labels
Expects dataset structure: dataset_folder/images/ and dataset_folder/labels/
"""

import os
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utilities.dataset_utils import (
    select_dataset_directory,
    validate_dataset_structure,
    prepare_labels_for_dataset,
    show_structure_error_dialog
)

def batch_detect(dataset_dir, model_path=None, confidence=0.25):
    """
    Run YOLO model detection on all images in dataset

    Args:
        dataset_dir: Path to dataset folder (must contain images/ and labels/ subfolders)
        model_path: Path to YOLO model (auto-detects if None)
        confidence: Detection confidence threshold
    """
    print("="*60)
    print("BATCH YOLO DETECTION")
    print("="*60)

    # Validate dataset structure
    try:
        images_dir, labels_dir = validate_dataset_structure(dataset_dir)
        print(f"✅ Valid dataset structure")
        print(f"   Images: {images_dir}")
        print(f"   Labels: {labels_dir}\n")
    except ValueError as e:
        print(f"\n{e}")
        show_structure_error_dialog(str(e))
        return

    # Run YOLO detection on all images (generates labels for missing ones)
    try:
        prepare_labels_for_dataset(images_dir, labels_dir,
                                  model_path=model_path,
                                  confidence=confidence,
                                  verbose=True)
    except Exception as e:
        print(f"❌ Error during detection: {e}")
        return

    print("\n" + "="*60)
    print("BATCH DETECTION COMPLETE")
    print("="*60)
    print(f"Labels saved to: {labels_dir}")
    print(f"\nYou can now review and edit labels with:")
    print(f"  python labeling_tools/simple_edit_tool.py --dir {dataset_dir}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Batch YOLO detection on all images",
        epilog='Dataset must have structure: dataset_folder/images/ and dataset_folder/labels/'
    )
    parser.add_argument(
        "--dir",
        type=str,
        help="Path to dataset folder (must contain images/ and labels/ subfolders). If not provided, dialog will appear."
    )
    parser.add_argument(
        "--model",
        type=str,
        help="Model file path (optional, defaults to models/best.pt)"
    )
    parser.add_argument(
        "--confidence", "-c",
        type=float,
        default=0.25,
        help="Detection confidence threshold (default: 0.25)"
    )

    args = parser.parse_args()

    # Get directory from user if not provided
    if args.dir is None:
        dataset_dir = select_dataset_directory()
        if not dataset_dir:
            print("No directory selected. Exiting.")
            exit(1)
    else:
        dataset_dir = args.dir

    # Check directory exists
    if not os.path.exists(dataset_dir):
        print(f"Error: Directory '{dataset_dir}' not found!")
        exit(1)

    batch_detect(dataset_dir, args.model, args.confidence)