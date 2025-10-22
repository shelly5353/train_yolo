#!/usr/bin/env python3
"""
Test script for YOLO model with updated class labels
Usage: python test_new_labels.py <image_path>
"""
import sys
from ultralytics import YOLO
from pathlib import Path

def test_model(image_path):
    """Test the model on an image and display results with new class names"""

    # Load the model with updated class names
    model = YOLO('models/best.pt')

    print("="*60)
    print("YOLO Model with Updated Class Labels")
    print("="*60)
    print(f"\nModel class names: {model.names}")
    print(f"Testing on: {image_path}")
    print("\nRunning detection...\n")

    # Run inference
    results = model.predict(
        source=image_path,
        conf=0.25,  # confidence threshold
        save=True,   # save annotated image
        project='test_results',
        name='new_labels_test',
        exist_ok=True
    )

    # Print detection results
    result = results[0]

    if len(result.boxes) == 0:
        print("No objects detected.")
    else:
        print(f"Detected {len(result.boxes)} objects:\n")

        for i, box in enumerate(result.boxes):
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            cls_name = model.names[cls_id]
            coords = box.xyxy[0].tolist()

            print(f"Detection {i+1}:")
            print(f"  Class: {cls_name} (ID: {cls_id})")
            print(f"  Confidence: {conf:.2%}")
            print(f"  Bounding box: [{coords[0]:.1f}, {coords[1]:.1f}, {coords[2]:.1f}, {coords[3]:.1f}]")
            print()

    print("="*60)
    print(f"Annotated image saved to: test_results/new_labels_test/")
    print("="*60)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Default test image if no argument provided
        test_image = "data/unlabeled/CO25S006978-1.png"
        print(f"No image specified, using default: {test_image}\n")
    else:
        test_image = sys.argv[1]

    if not Path(test_image).exists():
        print(f"Error: Image not found: {test_image}")
        print("\nUsage: python test_new_labels.py <image_path>")
        sys.exit(1)

    test_model(test_image)
