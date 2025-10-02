#!/usr/bin/env python3
"""
Batch YOLO Detection
Runs your trained model on all images and saves initial labels
"""

import os
import cv2
from pathlib import Path
from ultralytics import YOLO
from tqdm import tqdm

def batch_detect(data_dir="data", output_dir="labeld_data", model_path="best.pt", confidence=0.25):
    """Run model detection on all images"""

    data_dir = Path(data_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    # Load model
    print(f"Loading YOLO model from {model_path}...")
    model = YOLO(model_path)

    # Get all images
    image_files = sorted(list(data_dir.glob("*.png")))
    print(f"Found {len(image_files)} images to process")

    # Process each image
    total_detections = 0
    processed_images = 0

    for image_path in tqdm(image_files, desc="Processing images"):
        try:
            # Load image
            image = cv2.imread(str(image_path))
            if image is None:
                print(f"Warning: Could not load {image_path}")
                continue

            img_height, img_width = image.shape[:2]

            # Run detection
            results = model(image, conf=confidence, verbose=False)

            # Copy image to output directory
            output_image_path = output_dir / image_path.name
            cv2.imwrite(str(output_image_path), image)

            # Process detections and save labels
            labels = []
            if results and len(results) > 0:
                detections = results[0]
                if detections.boxes is not None:
                    boxes = detections.boxes

                    for i in range(len(boxes)):
                        # Get box coordinates (xyxy format)
                        x1, y1, x2, y2 = boxes.xyxy[i].cpu().numpy()
                        confidence_score = boxes.conf[i].cpu().numpy()
                        class_id = int(boxes.cls[i].cpu().numpy())

                        # Convert to YOLO format (normalized center coordinates)
                        x_center = ((x1 + x2) / 2) / img_width
                        y_center = ((y1 + y2) / 2) / img_height
                        width = (x2 - x1) / img_width
                        height = (y2 - y1) / img_height

                        labels.append([class_id, x_center, y_center, width, height])

            # Save labels to txt file
            label_file = output_dir / f"{image_path.stem}.txt"
            with open(label_file, 'w') as f:
                for label in labels:
                    class_id, x_center, y_center, width, height = label
                    f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")

            total_detections += len(labels)
            processed_images += 1

            if len(labels) > 0:
                print(f"✓ {image_path.name}: {len(labels)} detections")

        except Exception as e:
            print(f"Error processing {image_path}: {e}")
            continue

    print(f"\n=== BATCH PROCESSING COMPLETE ===")
    print(f"Processed: {processed_images}/{len(image_files)} images")
    print(f"Total detections: {total_detections}")
    print(f"Average detections per image: {total_detections/processed_images:.1f}")
    print(f"Output saved to: {output_dir}")
    print(f"\nNow you can run the editing tool to review and modify labels:")
    print(f"python3 simple_edit_tool.py")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Batch YOLO detection on all images")
    parser.add_argument("--confidence", "-c", type=float, default=0.25, help="Detection confidence threshold")
    parser.add_argument("--data_dir", default="data", help="Input image directory")
    parser.add_argument("--output_dir", default="labeld_data", help="Output directory")
    parser.add_argument("--model", default="best.pt", help="Model file path")

    args = parser.parse_args()

    # Check requirements
    if not os.path.exists(args.data_dir):
        print(f"Error: Directory '{args.data_dir}' not found!")
        exit(1)

    if not os.path.exists(args.model):
        print(f"Error: Model file '{args.model}' not found!")
        exit(1)

    batch_detect(args.data_dir, args.output_dir, args.model, args.confidence)