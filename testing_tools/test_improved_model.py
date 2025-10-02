#!/usr/bin/env python3
"""
Test the improved YOLO model on new images
"""

import cv2
import numpy as np
from ultralytics import YOLO
from pathlib import Path
import os

def test_improved_model():
    """Test the improved model on the specified test images"""

    # Load the improved model
    model_path = "/Users/shellysmac/Downloads/best.pt"
    if not os.path.exists(model_path):
        print(f"❌ Model not found at {model_path}")
        return

    print("🤖 Loading improved YOLO model...")
    model = YOLO(model_path)

    # Test image paths
    test_images = [
        "/Users/shellysmac/Downloads/drive-download-20250920T154642Z-1-001/drawing_row_8.png",
        "/Users/shellysmac/Downloads/drive-download-20250920T154642Z-1-001/drawing_row_9.png",
        "/Users/shellysmac/Downloads/drive-download-20250920T154642Z-1-001/drawing_row_5.png",
        "/Users/shellysmac/Downloads/drive-download-20250920T154642Z-1-001/drawing_row_6.png",
        "/Users/shellysmac/Downloads/drive-download-20250920T154642Z-1-001/drawing_row_7.png",
        "/Users/shellysmac/Downloads/drive-download-20250920T154642Z-1-001/drawing_row_4.png",
        "/Users/shellysmac/Downloads/drive-download-20250920T154642Z-1-001/drawing_row_10.png",
        "/Users/shellysmac/Downloads/drive-download-20250920T154642Z-1-001/drawing_row_3.png",
        "/Users/shellysmac/Downloads/drive-download-20250920T154642Z-1-001/drawing_row_1.png",
        "/Users/shellysmac/Downloads/drive-download-20250920T154642Z-1-001/drawing_row_2.png"
    ]

    # Class names
    class_names = {0: 'straight', 1: 'L-shape', 2: 'U-shape', 3: 'complex'}

    # Create output directory
    output_dir = Path("test_results_improved")
    output_dir.mkdir(exist_ok=True)

    print(f"\n🎯 Testing improved model on {len(test_images)} images...")

    total_detections = 0
    results_summary = []

    for i, image_path in enumerate(test_images, 1):
        if not os.path.exists(image_path):
            print(f"⚠️  Image {i}: File not found - {Path(image_path).name}")
            continue

        print(f"\n📸 Image {i}/{len(test_images)}: {Path(image_path).name}")

        # Run detection
        results = model(image_path, conf=0.25)  # Lower confidence for more detections

        # Load image for visualization
        image = cv2.imread(image_path)
        if image is None:
            print(f"❌ Could not load image: {image_path}")
            continue

        image_height, image_width = image.shape[:2]

        # Process results
        detections = []
        if len(results[0].boxes) > 0:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            confidences = results[0].boxes.conf.cpu().numpy()
            classes = results[0].boxes.cls.cpu().numpy().astype(int)

            for box, conf, cls in zip(boxes, confidences, classes):
                x1, y1, x2, y2 = map(int, box)
                class_name = class_names.get(cls, f"class_{cls}")
                detections.append({
                    'class': class_name,
                    'confidence': conf,
                    'bbox': (x1, y1, x2, y2)
                })

                # Draw bounding box
                color = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)][cls]
                cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)

                # Draw label
                label = f"{class_name}: {conf:.2f}"
                label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
                cv2.rectangle(image, (x1, y1 - label_size[1] - 10),
                             (x1 + label_size[0], y1), color, -1)
                cv2.putText(image, label, (x1, y1 - 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        # Save annotated image
        output_path = output_dir / f"detected_{Path(image_path).name}"
        cv2.imwrite(str(output_path), image)

        # Print results
        if detections:
            print(f"   ✅ Found {len(detections)} objects:")
            for det in detections:
                print(f"      • {det['class']}: {det['confidence']:.3f}")
        else:
            print("   ❌ No objects detected")

        total_detections += len(detections)
        results_summary.append({
            'image': Path(image_path).name,
            'detections': len(detections),
            'objects': detections
        })

    # Print summary
    print(f"\n📊 Detection Summary:")
    print(f"   Total images processed: {len([r for r in results_summary if r is not None])}")
    print(f"   Total objects detected: {total_detections}")
    print(f"   Average detections per image: {total_detections / len(results_summary):.1f}")

    # Count by class
    class_counts = {name: 0 for name in class_names.values()}
    for result in results_summary:
        for obj in result['objects']:
            class_counts[obj['class']] += 1

    print(f"\n🎯 Detections by class:")
    for class_name, count in class_counts.items():
        print(f"   {class_name}: {count}")

    print(f"\n💾 Annotated images saved to: {output_dir}/")
    print("✅ Testing complete!")

if __name__ == "__main__":
    test_improved_model()