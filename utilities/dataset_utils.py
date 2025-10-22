#!/usr/bin/env python3
"""
Dataset Utilities for YOLO Labeling Tools
Handles dataset structure validation and label generation
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from typing import Tuple, Optional
import cv2
from ultralytics import YOLO
from tqdm import tqdm


def select_dataset_directory() -> Optional[str]:
    """
    Show macOS file picker to select dataset folder.
    NO automatic directory opening - user must choose.

    Returns:
        Selected directory path or None if cancelled
    """
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)

    directory = filedialog.askdirectory(
        title="Select Dataset Folder (must contain 'images/' and 'labels/' subfolders)"
        # NO initialdir - user browses freely
    )

    root.destroy()
    return directory if directory else None


def validate_dataset_structure(dataset_path: str) -> Tuple[Path, Path]:
    """
    Validate that dataset folder has correct structure:
    - Must have 'images/' subfolder with PNG files
    - Must have 'labels/' subfolder (can be empty)

    Args:
        dataset_path: Path to dataset folder

    Returns:
        Tuple of (images_dir, labels_dir) as Path objects

    Raises:
        ValueError: If structure is invalid with detailed error message
    """
    dataset_path = Path(dataset_path)

    if not dataset_path.exists():
        raise ValueError(f"Dataset folder does not exist: {dataset_path}")

    images_dir = dataset_path / "images"
    labels_dir = dataset_path / "labels"

    # Check for required subfolders
    missing = []
    if not images_dir.exists():
        missing.append("images/")
    if not labels_dir.exists():
        missing.append("labels/")

    if missing:
        error_msg = (
            f"❌ Error: Invalid dataset structure\n\n"
            f"Selected folder: {dataset_path}\n\n"
            f"Missing subfolders: {', '.join(missing)}\n\n"
            f"Required structure:\n"
            f"  {dataset_path.name}/\n"
            f"  ├── images/     {'← Missing!' if 'images/' in missing else '✓'}\n"
            f"  └── labels/     {'← Missing!' if 'labels/' in missing else '✓'}\n\n"
            f"Please select a folder that contains both 'images/' and 'labels/' subfolders."
        )
        raise ValueError(error_msg)

    # Check for PNG files in images/
    image_files = list(images_dir.glob("*.png"))
    if not image_files:
        error_msg = (
            f"❌ Error: No images found\n\n"
            f"The 'images/' folder exists but contains no PNG files.\n\n"
            f"Location: {images_dir}\n\n"
            f"Please add PNG images to the 'images/' folder or select a different dataset."
        )
        raise ValueError(error_msg)

    return images_dir, labels_dir


def prepare_labels_for_dataset(images_dir: Path, labels_dir: Path,
                                model_path: Optional[str] = None,
                                confidence: float = 0.25,
                                verbose: bool = True) -> None:
    """
    Generate labels in labels/ folder for images in images/ folder.
    Only generates for images without existing label files.

    Args:
        images_dir: Path to images/ folder
        labels_dir: Path to labels/ folder
        model_path: Path to YOLO model (auto-detects if None)
        confidence: Detection confidence threshold
        verbose: Print status messages
    """
    # Get model path
    if model_path is None:
        # Default to models/best.pt
        project_root = Path(__file__).parent.parent
        model_path = project_root / "models" / "best.pt"

    if not Path(model_path).exists():
        raise FileNotFoundError(
            f"YOLO model not found: {model_path}\n\n"
            f"Please ensure the model file exists or specify a valid model path."
        )

    # Get all PNG images
    image_files = sorted(list(images_dir.glob("*.png")))

    # Check which images need labels
    unlabeled = [
        img for img in image_files
        if not (labels_dir / f"{img.stem}.txt").exists()
    ]

    if not unlabeled:
        if verbose:
            print(f"✅ All {len(image_files)} images already have labels")
        return

    if verbose:
        print(f"\n📊 Dataset Status:")
        print(f"   Total images: {len(image_files)}")
        print(f"   Already labeled: {len(image_files) - len(unlabeled)}")
        print(f"   Need labels: {len(unlabeled)}")
        print(f"\n⚠️  Labels missing for {len(unlabeled)} images")
        print(f"🔄 Running YOLO model to generate labels...")
        print(f"   Model: {model_path}")
        print(f"   Confidence threshold: {confidence}\n")

    # Load YOLO model
    model = YOLO(str(model_path))

    # Process unlabeled images
    generated_count = 0
    for img_path in tqdm(unlabeled, desc="Generating labels", disable=not verbose):
        try:
            # Read image
            image = cv2.imread(str(img_path))
            if image is None:
                if verbose:
                    print(f"⚠️  Could not read image: {img_path.name}")
                continue

            img_h, img_w = image.shape[:2]

            # Run YOLO detection
            results = model(image, conf=confidence, verbose=False)

            # Convert detections to YOLO format
            labels = []
            if results and len(results) > 0:
                detections = results[0]
                if detections.boxes is not None and len(detections.boxes) > 0:
                    boxes = detections.boxes

                    for box in boxes:
                        # Get box coordinates (xyxy format)
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        class_id = int(box.cls[0].cpu().numpy())

                        # Convert to YOLO format (normalized xywh)
                        x_center = ((x1 + x2) / 2) / img_w
                        y_center = ((y1 + y2) / 2) / img_h
                        width = (x2 - x1) / img_w
                        height = (y2 - y1) / img_h

                        labels.append(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")

            # Write label file to labels/ folder
            label_file = labels_dir / f"{img_path.stem}.txt"
            with open(label_file, 'w') as f:
                if labels:
                    f.write('\n'.join(labels) + '\n')
                # Empty file if no detections

            generated_count += 1

        except Exception as e:
            if verbose:
                print(f"⚠️  Error processing {img_path.name}: {e}")
            continue

    if verbose:
        print(f"\n✅ Generated {generated_count} label files in labels/ folder")
        print(f"📁 Dataset ready for labeling!\n")


def show_structure_error_dialog(error_message: str) -> None:
    """
    Show error dialog with dataset structure requirements

    Args:
        error_message: Error message to display
    """
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)

    messagebox.showerror("Invalid Dataset Structure", error_message)
    root.destroy()


if __name__ == "__main__":
    # Test the utilities
    print("Testing dataset utilities...")

    # Test directory selection
    dataset_dir = select_dataset_directory()
    if dataset_dir:
        print(f"Selected: {dataset_dir}")

        try:
            images_dir, labels_dir = validate_dataset_structure(dataset_dir)
            print(f"✅ Valid structure")
            print(f"   Images: {images_dir}")
            print(f"   Labels: {labels_dir}")

            # Test label generation
            prepare_labels_for_dataset(images_dir, labels_dir, verbose=True)

        except ValueError as e:
            print(f"\n{e}")
    else:
        print("No directory selected")
