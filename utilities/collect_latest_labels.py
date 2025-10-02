#!/usr/bin/env python3
"""
Collect Latest Labeled Images
Finds the most recent version of each labeled image across all directories
"""

import os
import shutil
from pathlib import Path
from collections import defaultdict

# Directories to search for labeled data
SEARCH_DIRS = [
    "labeled_new_dataset",
    "labeld_data",
    "pdf_labeling_data",
    "yolo_training_dataset"
]

OUTPUT_DIR = "final_labeled_dataset"

def collect_latest_labels():
    """Collect the latest version of each labeled image"""

    # Track latest version of each image
    latest_files = {}  # image_name -> (image_path, label_path, mtime)

    print("🔍 Searching for labeled images...\n")

    for search_dir in SEARCH_DIRS:
        if not os.path.exists(search_dir):
            print(f"⊘ Skipping {search_dir} (doesn't exist)")
            continue

        print(f"📂 Checking {search_dir}...")

        # Find all images
        for img_file in Path(search_dir).glob("*.png"):
            img_name = img_file.stem
            label_file = img_file.with_suffix('.txt')

            # Skip if no label file exists
            if not label_file.exists():
                continue

            # Get modification time
            mtime = os.path.getmtime(label_file)

            # Check if this is the latest version
            if img_name not in latest_files or mtime > latest_files[img_name][2]:
                latest_files[img_name] = (str(img_file), str(label_file), mtime)

    print(f"\n✅ Found {len(latest_files)} unique labeled images\n")

    # Create output directory
    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(exist_ok=True)

    # Copy latest versions
    print(f"📋 Copying latest versions to {OUTPUT_DIR}...\n")

    stats = defaultdict(int)

    for img_name, (img_path, label_path, mtime) in latest_files.items():
        # Copy image and label
        shutil.copy2(img_path, output_path / Path(img_path).name)
        shutil.copy2(label_path, output_path / Path(label_path).name)

        # Count labels per image
        with open(label_path) as f:
            num_labels = len([l for l in f.readlines() if l.strip()])
            stats['total_annotations'] += num_labels
            if num_labels > 0:
                stats['images_with_labels'] += 1

        stats['total_images'] += 1

        source_dir = Path(img_path).parent.name
        print(f"  ✓ {img_name} (from {source_dir})")

    print(f"\n{'='*60}")
    print(f"📊 COLLECTION SUMMARY")
    print(f"{'='*60}")
    print(f"Total images collected:     {stats['total_images']}")
    print(f"Images with annotations:    {stats['images_with_labels']}")
    print(f"Total annotations:          {stats['total_annotations']}")
    print(f"Average per image:          {stats['total_annotations']/stats['total_images']:.1f}")
    print(f"Output directory:           {OUTPUT_DIR}/")
    print(f"{'='*60}\n")

    return output_path

if __name__ == "__main__":
    collect_latest_labels()
    print("✅ Ready for augmentation!")
    print(f"   Next: python augment_dataset.py --input_dir {OUTPUT_DIR}")
