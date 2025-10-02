# MODELS FOLDER

## Purpose
Storage for all trained YOLO model weights with clear version control and naming.

## Current Models

### ✅ best_v2_updated_classes.pt (ACTIVE MODEL)
- **Status:** Current production model - USE THIS
- **Size:** 22.5 MB
- **Classes:** Updated class names (straight, L-shape, U-shape, complex)
- **Training Date:** Recent (September 2025)
- **Performance:** Latest trained version with improved class naming
- **Usage:** Default model for all labeling tools and inference
- **Location Reference:** Use `models/best_v2_updated_classes.pt` in all scripts

### 🔄 best_v2_backup1.pt
- **Status:** Backup copy of updated model
- **Size:** 22.5 MB
- **Purpose:** Safety backup before any model modifications
- **Created:** September 28, 2025
- **Note:** Identical to v2_updated_classes, kept for rollback capability

### 🔄 best_v2_backup2.pt
- **Status:** Secondary backup of updated model
- **Size:** 22.5 MB
- **Purpose:** Additional safety backup
- **Created:** October 2, 2025
- **Note:** Redundant backup for extra safety

### 🗄️ best_v1_original_classes.pt (DEPRECATED)
- **Status:** Original model - DO NOT USE for new work
- **Size:** 22.5 MB
- **Classes:** Old class naming system
- **Purpose:** Historical reference only
- **Issue:** Outdated class names, replaced by v2
- **Keep For:** Comparison and historical record

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
model = YOLO('models/best_v2_updated_classes.pt')

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
yolo predict model=models/best_v2_updated_classes.pt source=image.png conf=0.3
```

## Model Training History

1. **v1 (Original)** - Initial training with basic class names
2. **v2 (Updated Classes)** - Retrained/modified with improved class nomenclature
   - Better class name clarity
   - Maintained model weights and performance
   - Updated class metadata

## Best Practices

1. **Always use v2_updated_classes.pt** for active work
2. **Keep backups** before making any model modifications
3. **Never delete v1** - maintain for historical comparison
4. **Test model changes** on small datasets before full deployment
5. **Document model updates** in root CLAUDE.md

## Model Modification

If you need to modify the model (change classes, fine-tune, etc.):

1. Create a dated backup: `best_v2_backup_YYYY-MM-DD.pt`
2. Make modifications
3. Test thoroughly
4. Update this CLAUDE.md with changes
5. Update root CLAUDE.md with model change notes

## Notes

- Models are now tracked in git (previously excluded by .gitignore)
- Total storage: ~90 MB for all models
- Models are compatible with Ultralytics YOLO framework
- No retraining needed unless expanding classes or improving performance
