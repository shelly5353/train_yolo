#!/usr/bin/env python3
from ultralytics import YOLO
import cv2
import numpy as np

def test_single_image(image_path):
    model_path = "/Users/shellysmac/Downloads/best.pt"
    
    print("🤖 Loading improved YOLO model...")
    model = YOLO(model_path)

    class_names = {0: 'straight', 1: 'L-shape', 2: 'U-shape', 3: 'complex'}
    
    print(f"🎯 Testing model on: {image_path}")

    # Run detection with lower confidence to catch more objects
    results = model(image_path, conf=0.15, save=True, project="single_test", name="document_test")

    # Process results
    if len(results[0].boxes) > 0:
        boxes = results[0].boxes
        confidences = boxes.conf.cpu().numpy()
        classes = boxes.cls.cpu().numpy().astype(int)
        xyxy = boxes.xyxy.cpu().numpy()

        print(f"\n✅ Found {len(boxes)} objects:")
        for i, (conf, cls, box) in enumerate(zip(confidences, classes, xyxy)):
            class_name = class_names.get(cls, f"class_{cls}")
            x1, y1, x2, y2 = box.astype(int)
            print(f"   {i+1}. {class_name}: {conf:.3f} at ({x1},{y1}) to ({x2},{y2})")

        # Count by class
        class_counts = {name: 0 for name in class_names.values()}
        for cls in classes:
            class_name = class_names.get(cls, f"class_{cls}")
            class_counts[class_name] += 1

        print(f"\n📊 Detection summary:")
        print(f"   Total objects: {len(boxes)}")
        for class_name, count in class_counts.items():
            if count > 0:
                print(f"   {class_name}: {count}")

    else:
        print("❌ No objects detected")

    print(f"\n💾 Results saved to: single_test/document_test/")
    print("✅ Testing complete!")

if __name__ == "__main__":
    # Test the uploaded image
    test_single_image("/tmp/uploaded_image.png")
