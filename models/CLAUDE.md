# MODELS FOLDER

## Purpose
Storage for trained YOLO model weights.

## Current Model

### ✅ best.pt (ACTIVE MODEL)
- **Status:** Current production model - USE THIS
- **Size:** 21 MB
- **Classes:** 4 shape categories (straight, L-shape, U-shape, complex)
- **Training Date:** September 28, 2025
- **Performance:** Latest trained version
- **Usage:** Default model for all labeling tools and inference
- **Location Reference:** Use `models/best.pt` or `best.pt` (from labeling_tools/) in scripts

## Model Architecture

- **Framework:** YOLOv8 (Ultralytics)
- **Task:** Object Detection
- **Input:** Document images (variable resolution)
- **Output:** Bounding boxes with class predictions
- **Classes:** 4 shape categories
  - Class 0: straight
  - Class 1: L-shape
  - Class 2: U-shape
  - Class 3: complex

## Usage Examples

### Python Inference
```python
from ultralytics import YOLO

# Load the current model
model = YOLO('models/best.pt')

# Run inference
results = model.predict('image.png', conf=0.3)

# Process results
for result in results:
    boxes = result.boxes
    for box in boxes:
        class_id = int(box.cls)
        confidence = float(box.conf)
        print(f"Detected: class {class_id}, confidence: {confidence}")
```

### Command Line
```bash
# Using Ultralytics CLI
yolo predict model=models/best.pt source=image.png conf=0.3
```

## Best Practices

1. **Always use best.pt** for active work
2. **Create backups** before making any model modifications (use date suffix: `best_YYYY-MM-DD.pt`)
3. **Test model changes** on small datasets before full deployment
4. **Document model updates** in root CLAUDE.md

## Model Modification

If you need to modify the model (change classes, fine-tune, etc.):

1. Create a dated backup: `best_2025-10-02.pt`
2. Make modifications
3. Test thoroughly
4. Update this CLAUDE.md with changes
5. Update root CLAUDE.md with model change notes
6. Keep single active model as `best.pt`

## Notes

- Model is tracked in git
- Compatible with Ultralytics YOLO framework
- No retraining needed unless expanding classes or improving performance
- Keep model naming simple: active model is always `best.pt`
