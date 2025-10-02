#!/usr/bin/env python3
import os
from pathlib import Path

def count_annotations_by_class(labels_dir):
    class_counts = {0: 0, 1: 0, 2: 0, 3: 0}
    total_annotations = 0
    
    for label_file in Path(labels_dir).glob("*.txt"):
        with open(label_file, 'r') as f:
            for line in f:
                if line.strip():
                    class_id = int(line.split()[0])
                    class_counts[class_id] += 1
                    total_annotations += 1
    
    return class_counts, total_annotations

def main():
    class_names = {0: 'straight', 1: 'L-shape', 2: 'U-shape', 3: 'complex'}
    
    print("📊 YOLO Dataset Statistics Summary")
    print("=" * 50)
    
    # Original dataset
    print("\n🔸 Original Dataset:")
    orig_counts, orig_total = count_annotations_by_class("labeld_data")
    orig_images = len(list(Path("labeld_data").glob("*.txt")))
    print(f"  Images: {orig_images}")
    print(f"  Total annotations: {orig_total}")
    for class_id, count in orig_counts.items():
        percentage = (count / orig_total * 100) if orig_total > 0 else 0
        print(f"    {class_names[class_id]}: {count} ({percentage:.1f}%)")
    
    # Augmented dataset
    print("\n🔸 Augmented Dataset:")
    aug_counts, aug_total = count_annotations_by_class("augmented_dataset/labels")
    aug_images = len(list(Path("augmented_dataset/images").glob("*.png")))
    print(f"  Images: {aug_images}")
    print(f"  Total annotations: {aug_total}")
    for class_id, count in aug_counts.items():
        percentage = (count / aug_total * 100) if aug_total > 0 else 0
        print(f"    {class_names[class_id]}: {count} ({percentage:.1f}%)")
    
    # Summary
    print(f"\n🎯 Summary:")
    print(f"  Dataset size multiplier: {aug_images / orig_images:.1f}x")
    print(f"  Annotation multiplier: {aug_total / orig_total:.1f}x")
    print(f"  Ready for YOLO training!")

if __name__ == "__main__":
    main()
