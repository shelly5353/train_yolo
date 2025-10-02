#!/usr/bin/env python3
"""
Data Augmentation Script for YOLO Dataset
Applies various augmentations to labeled images while maintaining bounding box accuracy
"""

import cv2
import numpy as np
import os
import random
from pathlib import Path
import shutil

class YOLOAugmenter:
    def __init__(self, source_images_dir, source_labels_dir, output_dir):
        self.source_images_dir = Path(source_images_dir)
        self.source_labels_dir = Path(source_labels_dir)
        self.output_dir = Path(output_dir)

        # Create output directories
        self.output_images_dir = self.output_dir / "images"
        self.output_labels_dir = self.output_dir / "labels"
        self.output_images_dir.mkdir(parents=True, exist_ok=True)
        self.output_labels_dir.mkdir(parents=True, exist_ok=True)

        # Set random seed for reproducibility
        random.seed(42)
        np.random.seed(42)

    def load_yolo_annotations(self, label_file):
        """Load YOLO format annotations"""
        annotations = []
        class_labels = []

        if not label_file.exists():
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

    def save_yolo_annotations(self, annotations, class_labels, output_file):
        """Save YOLO format annotations"""
        with open(output_file, 'w') as f:
            for bbox, class_id in zip(annotations, class_labels):
                x_center, y_center, width, height = bbox
                f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")

    def flip_horizontal(self, image, bboxes):
        """Horizontal flip with bbox adjustment"""
        flipped_image = cv2.flip(image, 1)
        flipped_bboxes = []

        for bbox in bboxes:
            x_center, y_center, width, height = bbox
            # Flip x coordinate
            new_x_center = 1.0 - x_center
            flipped_bboxes.append([new_x_center, y_center, width, height])

        return flipped_image, flipped_bboxes

    def flip_vertical(self, image, bboxes):
        """Vertical flip with bbox adjustment"""
        flipped_image = cv2.flip(image, 0)
        flipped_bboxes = []

        for bbox in bboxes:
            x_center, y_center, width, height = bbox
            # Flip y coordinate
            new_y_center = 1.0 - y_center
            flipped_bboxes.append([x_center, new_y_center, width, height])

        return flipped_image, flipped_bboxes

    def adjust_brightness(self, image, factor=1.2):
        """Adjust image brightness"""
        bright_image = image.astype(np.float32) * factor
        bright_image = np.clip(bright_image, 0, 255).astype(np.uint8)
        return bright_image

    def adjust_contrast(self, image, factor=1.2):
        """Adjust image contrast"""
        contrast_image = image.astype(np.float32)
        contrast_image = (contrast_image - 127.5) * factor + 127.5
        contrast_image = np.clip(contrast_image, 0, 255).astype(np.uint8)
        return contrast_image

    def add_noise(self, image, noise_factor=25):
        """Add Gaussian noise to image"""
        noise = np.random.normal(0, noise_factor, image.shape).astype(np.float32)
        noisy_image = image.astype(np.float32) + noise
        noisy_image = np.clip(noisy_image, 0, 255).astype(np.uint8)
        return noisy_image

    def augment_image(self, image_path, label_path, num_augmentations=4):
        """Apply augmentations to a single image and its annotations"""
        # Load image
        image = cv2.imread(str(image_path))
        if image is None:
            print(f"Warning: Could not load image {image_path}")
            return

        # Load annotations
        annotations, class_labels = self.load_yolo_annotations(label_path)

        # Copy original files first
        original_name = image_path.stem
        shutil.copy2(image_path, self.output_images_dir / f"{original_name}.png")
        shutil.copy2(label_path, self.output_labels_dir / f"{original_name}.txt")

        augmentations = [
            ("hflip", lambda img, bbox: self.flip_horizontal(img, bbox)),
            ("vflip", lambda img, bbox: self.flip_vertical(img, bbox)),
            ("bright", lambda img, bbox: (self.adjust_brightness(img, 1.3), bbox)),
            ("contrast", lambda img, bbox: (self.adjust_contrast(img, 1.3), bbox)),
            ("noise", lambda img, bbox: (self.add_noise(img, 20), bbox)),
            ("dark", lambda img, bbox: (self.adjust_brightness(img, 0.7), bbox)),
        ]

        # Apply selected augmentations
        selected_augs = random.sample(augmentations, min(num_augmentations, len(augmentations)))

        for aug_name, aug_func in selected_augs:
            try:
                aug_image, aug_bboxes = aug_func(image, annotations)

                # Save augmented image
                aug_image_name = f"{original_name}_aug_{aug_name}.png"
                cv2.imwrite(str(self.output_images_dir / aug_image_name), aug_image)

                # Save augmented annotations
                aug_label_name = f"{original_name}_aug_{aug_name}.txt"
                self.save_yolo_annotations(aug_bboxes, class_labels,
                                         self.output_labels_dir / aug_label_name)

            except Exception as e:
                print(f"Warning: Failed to apply {aug_name} to {image_path}: {e}")
                continue

    def augment_dataset(self, num_augmentations=4):
        """Augment the entire dataset"""
        # Find all images with corresponding labels
        image_files = []
        for ext in ['*.png', '*.jpg', '*.jpeg']:
            image_files.extend(list(self.source_images_dir.glob(ext)))

        # Filter to only images that have corresponding label files
        valid_pairs = []
        for image_file in image_files:
            label_file = self.source_labels_dir / f"{image_file.stem}.txt"
            if label_file.exists():
                valid_pairs.append((image_file, label_file))

        print(f"Found {len(valid_pairs)} image-label pairs to augment")
        print(f"Generating up to {num_augmentations} augmentations per image")
        print(f"Estimated dataset size: {len(valid_pairs) * (1 + num_augmentations)} images")

        # Process each image
        count = 0
        for image_path, label_path in valid_pairs:
            self.augment_image(image_path, label_path, num_augmentations)
            count += 1
            if count % 50 == 0:
                print(f"Processed {count}/{len(valid_pairs)} images...")

        # Generate statistics
        self.generate_stats()

    def generate_stats(self):
        """Generate statistics about the augmented dataset"""
        image_count = len(list(self.output_images_dir.glob("*.png")))
        label_count = len(list(self.output_labels_dir.glob("*.txt")))

        # Count annotations by class
        class_counts = {0: 0, 1: 0, 2: 0, 3: 0}  # straight, L-shape, U-shape, complex
        total_annotations = 0

        for label_file in self.output_labels_dir.glob("*.txt"):
            with open(label_file, 'r') as f:
                for line in f:
                    if line.strip():
                        class_id = int(line.split()[0])
                        class_counts[class_id] += 1
                        total_annotations += 1

        print(f"\n📊 Augmented Dataset Statistics:")
        print(f"  Total images: {image_count}")
        print(f"  Total label files: {label_count}")
        print(f"  Total annotations: {total_annotations}")
        print(f"  Class distribution:")
        class_names = {0: 'straight', 1: 'L-shape', 2: 'U-shape', 3: 'complex'}
        for class_id, count in class_counts.items():
            percentage = (count / total_annotations * 100) if total_annotations > 0 else 0
            print(f"    {class_names[class_id]}: {count} ({percentage:.1f}%)")

def main():
    # Configuration
    source_images_dir = "data"
    source_labels_dir = "labeld_data"
    output_dir = "augmented_dataset"
    num_augmentations = 4  # Generate up to 4 augmented versions per original image

    print("🚀 Starting YOLO Dataset Augmentation")
    print(f"Source images: {source_images_dir}")
    print(f"Source labels: {source_labels_dir}")
    print(f"Output directory: {output_dir}")

    # Create augmenter
    augmenter = YOLOAugmenter(source_images_dir, source_labels_dir, output_dir)

    # Run augmentation
    augmenter.augment_dataset(num_augmentations)

    print(f"\n✅ Dataset augmentation complete!")
    print(f"Augmented dataset saved to: {output_dir}/")
    print(f"Structure:")
    print(f"  {output_dir}/images/  - Augmented images")
    print(f"  {output_dir}/labels/ - Augmented YOLO annotations")

if __name__ == "__main__":
    main()