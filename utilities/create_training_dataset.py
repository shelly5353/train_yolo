#!/usr/bin/env python3
"""
Create Augmented Training Dataset
Takes the latest labeled images and creates augmented versions for YOLO training
"""

import cv2
import numpy as np
import os
from pathlib import Path
import shutil
import argparse

def flip_horizontal(image, bboxes):
    """Flip image horizontally and adjust bboxes"""
    flipped_image = cv2.flip(image, 1)
    flipped_bboxes = []
    for bbox in bboxes:
        x_center, y_center, width, height = bbox
        new_x_center = 1.0 - x_center
        flipped_bboxes.append([new_x_center, y_center, width, height])
    return flipped_image, flipped_bboxes

def adjust_brightness(image, factor=1.2):
    """Adjust image brightness"""
    bright_image = image.astype(np.float32) * factor
    bright_image = np.clip(bright_image, 0, 255).astype(np.uint8)
    return bright_image

def load_yolo_annotations(label_file):
    """Load YOLO format annotations"""
    annotations = []
    class_labels = []
    if not os.path.exists(label_file):
        return annotations, class_labels

    with open(label_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                parts = line.split()
                class_id = int(parts[0])
                x_center, y_center, width, height = map(float, parts[1:5])
                annotations.append([x_center, y_center, width, height])
                class_labels.append(class_id)
    return annotations, class_labels

def save_yolo_annotations(annotations, class_labels, output_file):
    """Save YOLO format annotations"""
    with open(output_file, 'w') as f:
        for bbox, class_id in zip(annotations, class_labels):
            x_center, y_center, width, height = bbox
            f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")

def augment_dataset(input_dir, output_dir):
    """Create augmented training dataset"""

    input_path = Path(input_dir)
    output_path = Path(output_dir)

    # Create output directories
    images_dir = output_path / "images"
    labels_dir = output_path / "labels"
    images_dir.mkdir(parents=True, exist_ok=True)
    labels_dir.mkdir(parents=True, exist_ok=True)

    print(f"🚀 Creating Augmented Training Dataset")
    print(f"📂 Input:  {input_dir}")
    print(f"📂 Output: {output_dir}\n")

    # Find all image files
    image_files = list(input_path.glob("*.png"))
    valid_pairs = []

    for image_file in image_files:
        label_file = input_path / f"{image_file.stem}.txt"
        if label_file.exists():
            valid_pairs.append((image_file, label_file))

    print(f"Found {len(valid_pairs)} image-label pairs\n")

    stats = {
        'original': 0,
        'hflip': 0,
        'bright': 0,
        'dark': 0,
        'total_annotations': 0
    }

    for idx, (image_path, label_path) in enumerate(valid_pairs, 1):
        # Load image and annotations
        image = cv2.imread(str(image_path))
        if image is None:
            print(f"⚠️  Skipping {image_path.name} (failed to load)")
            continue

        annotations, class_labels = load_yolo_annotations(str(label_path))
        original_name = image_path.stem

        # Count annotations
        stats['total_annotations'] += len(annotations)

        # 1. Copy original
        shutil.copy2(image_path, images_dir / f"{original_name}.png")
        shutil.copy2(label_path, labels_dir / f"{original_name}.txt")
        stats['original'] += 1

        # 2. Horizontal flip
        flip_img, flip_bbox = flip_horizontal(image, annotations)
        cv2.imwrite(str(images_dir / f"{original_name}_hflip.png"), flip_img)
        save_yolo_annotations(flip_bbox, class_labels, labels_dir / f"{original_name}_hflip.txt")
        stats['hflip'] += 1

        # 3. Brightness increase
        bright_img = adjust_brightness(image, 1.3)
        cv2.imwrite(str(images_dir / f"{original_name}_bright.png"), bright_img)
        save_yolo_annotations(annotations, class_labels, labels_dir / f"{original_name}_bright.txt")
        stats['bright'] += 1

        # 4. Brightness decrease
        dark_img = adjust_brightness(image, 0.7)
        cv2.imwrite(str(images_dir / f"{original_name}_dark.png"), dark_img)
        save_yolo_annotations(annotations, class_labels, labels_dir / f"{original_name}_dark.txt")
        stats['dark'] += 1

        if idx % 50 == 0:
            print(f"  Processed {idx}/{len(valid_pairs)} images...")

    total_images = stats['original'] + stats['hflip'] + stats['bright'] + stats['dark']

    print(f"\n{'='*60}")
    print(f"📊 AUGMENTATION SUMMARY")
    print(f"{'='*60}")
    print(f"Original images:        {stats['original']}")
    print(f"Horizontal flips:       {stats['hflip']}")
    print(f"Brightness augments:    {stats['bright'] + stats['dark']}")
    print(f"Total training images:  {total_images}")
    print(f"Total annotations:      {stats['total_annotations']}")
    print(f"Output directory:       {output_dir}/")
    print(f"{'='*60}\n")

    print("✅ Augmented dataset created successfully!")
    print(f"\n📁 Training structure:")
    print(f"   {output_dir}/images/  - {total_images} training images")
    print(f"   {output_dir}/labels/  - {total_images} label files")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create augmented YOLO training dataset")
    parser.add_argument("--input_dir", default="final_labeled_dataset",
                       help="Directory with latest labeled images")
    parser.add_argument("--output_dir", default="training_dataset_final",
                       help="Output directory for augmented dataset")

    args = parser.parse_args()
    augment_dataset(args.input_dir, args.output_dir)
