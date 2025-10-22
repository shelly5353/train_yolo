#!/usr/bin/env python3
"""
Test YOLO model on technical document
Save the document image and update the image_path below
"""

from ultralytics import YOLO
import cv2
import os

def test_document():
    # UPDATE THIS PATH to where you save the document image
    image_path = "/Users/shellysmac/Downloads/technical_document.png"

    model_path = "/Users/shellysmac/Downloads/best.pt"

    if not os.path.exists(model_path):
        print(f"❌ Model not found at {model_path}")
        return

    if not os.path.exists(image_path):
        print(f"❌ Image not found at {image_path}")
        print("Please save the document image and update the image_path in this script")
        return

    print("🤖 Loading improved YOLO model...")
    model = YOLO(model_path)

    print(f"🎯 Testing model on technical document...")
    print(f"📁 Image: {image_path}")

    # Run detection with lower confidence to catch more shapes
    results = model(image_path, conf=0.1, save=True, project="document_detection", name="technical_doc")

    class_names = {0: 'straight', 1: 'L-shape', 2: 'U-shape', 3: 'complex'}

    if len(results[0].boxes) > 0:
        boxes = results[0].boxes
        confidences = boxes.conf.cpu().numpy()
        classes = boxes.cls.cpu().numpy().astype(int)
        xyxy = boxes.xyxy.cpu().numpy()

        print(f"\n✅ Found {len(boxes)} geometric shapes:")

        # Sort by confidence (highest first)
        sorted_indices = confidences.argsort()[::-1]

        for i, idx in enumerate(sorted_indices):
            conf = confidences[idx]
            cls = classes[idx]
            box = xyxy[idx]
            class_name = class_names.get(cls, f"class_{cls}")
            x1, y1, x2, y2 = box.astype(int)

            print(f"   {i+1:2d}. {class_name:8s}: {conf:.3f} at ({x1:4d},{y1:4d}) to ({x2:4d},{y2:4d})")

        # Count detections by class
        class_counts = {name: 0 for name in class_names.values()}
        confidence_sums = {name: 0.0 for name in class_names.values()}

        for conf, cls in zip(confidences, classes):
            class_name = class_names.get(cls, f"class_{cls}")
            class_counts[class_name] += 1
            confidence_sums[class_name] += conf

        print(f"\n📊 Detection Summary:")
        print(f"   Total shapes detected: {len(boxes)}")

        for class_name, count in class_counts.items():
            if count > 0:
                avg_conf = confidence_sums[class_name] / count
                print(f"   {class_name:8s}: {count:2d} detections (avg conf: {avg_conf:.3f})")

        print(f"\n💾 Annotated image saved to: document_detection/technical_doc/")

    else:
        print("❌ No geometric shapes detected")
        print("Try lowering the confidence threshold or check if the image contains clear geometric shapes")

    print("✅ Testing complete!")

if __name__ == "__main__":
    test_document()