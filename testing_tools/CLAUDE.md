# TESTING TOOLS

## Purpose
Scripts for validating model performance, running inference tests, and evaluating detection quality.

## Available Scripts

### 1. test_single_image.py - Quick Single Image Test
**Purpose:** Fast test of model inference on one image

**Features:**
- Loads model and runs inference on single image
- Displays detection results
- Shows confidence scores
- Visual output with bounding boxes
- Quick sanity check

**Usage:**
```bash
cd testing_tools
python test_single_image.py
```

**Configuration (edit in script):**
```python
# Model to test
model_path = '../models/best_v2_updated_classes.pt'

# Image to test
image_path = '../data/unlabeled/sample_image.png'

# Confidence threshold
confidence = 0.25
```

**Output:**
- Console: Detected classes and confidence scores
- Visual: Image with drawn bounding boxes
- Saved: `test_output.png`

**When to Use:**
- Quick model validation after training
- Testing if model loads correctly
- Checking detection on specific problem images
- Debugging detection issues
- Rapid iteration testing

**Example Output:**
```
Loading model: ../models/best_v2_updated_classes.pt
Running inference on: sample_image.png

Detections:
  Class: straight (0), Confidence: 0.89
  Class: L-shape (1), Confidence: 0.76
  Class: U-shape (2), Confidence: 0.82

Results saved to: test_output.png
```

---

### 2. test_improved_model.py - Comprehensive Model Testing
**Purpose:** Thorough evaluation of model performance on test dataset

**Features:**
- Tests on multiple images
- Calculates performance metrics
- Compares with ground truth labels
- Precision, recall, F1-score
- Per-class accuracy
- Confusion matrix generation
- Detailed performance report

**Usage:**
```bash
cd testing_tools
python test_improved_model.py
```

**Configuration (edit in script):**
```python
# Model to evaluate
model_path = '../models/best_v2_updated_classes.pt'

# Test dataset
test_data_path = '../data/labeled/'  # Uses validation split

# Confidence threshold
confidence = 0.25

# IoU threshold for matching predictions to ground truth
iou_threshold = 0.5
```

**Output:**
- `test_results/` folder with:
  - `metrics.txt` - Performance metrics
  - `confusion_matrix.png` - Visual confusion matrix
  - `sample_predictions/` - Annotated images showing predictions
  - `errors.txt` - List of failed detections

**Metrics Reported:**
- **Precision:** (TP / (TP + FP)) - How many detections are correct
- **Recall:** (TP / (TP + FN)) - How many objects are detected
- **F1-Score:** Harmonic mean of precision and recall
- **mAP50:** Mean Average Precision at IoU 0.5
- **Per-class metrics:** Individual class performance

**When to Use:**
- After training a new model
- Comparing old vs new model versions
- Before deploying model to production
- Understanding model strengths/weaknesses
- Quality assurance checkpoint

**Interpretation:**
```
Good Model Performance:
  Precision: > 0.80
  Recall: > 0.75
  F1-Score: > 0.77
  mAP50: > 0.70

Needs Improvement:
  Precision: < 0.70 → Too many false positives
  Recall: < 0.65 → Missing objects
  Imbalanced per-class → Need more data for weak classes
```

---

### 3. test_document.py - Full Document Testing
**Purpose:** Test model on complete document images (multi-page scenarios)

**Features:**
- Tests on full-page document images
- Handles multiple detections per page
- Visual output with all detections
- Document-level statistics
- Page navigation through results

**Usage:**
```bash
cd testing_tools
python test_document.py
```

**Configuration (edit in script):**
```python
# Model
model_path = '../models/best_v2_updated_classes.pt'

# Document images folder
document_folder = '../test_documents/'

# Settings
confidence = 0.3
save_visualizations = True
```

**Output:**
- Annotated document images
- Per-page detection summary
- Document-level report:
  ```
  Document: document_001.png
  Total detections: 8
    - straight: 3
    - L-shape: 2
    - U-shape: 2
    - complex: 1
  ```

**When to Use:**
- Testing on production-like document images
- Validating end-to-end pipeline
- Real-world scenario testing
- Client demo preparation
- Document processing workflow validation

---

### 4. test_results/ - Test Output Folder
**Purpose:** Storage for all test outputs and results

**Contents:**
- Performance metric files
- Confusion matrices
- Sample prediction images
- Error logs
- Comparison reports

**Organization:**
```
test_results/
├── run_YYYYMMDD_HHMMSS/    (timestamped test runs)
│   ├── metrics.txt
│   ├── confusion_matrix.png
│   ├── predictions/
│   └── errors.txt
```

---

## Testing Workflow

### Quick Test (After Training)
```bash
cd testing_tools
python test_single_image.py
# Visual check: Does model detect shapes?
```

### Full Evaluation (Before Deployment)
```bash
cd testing_tools
python test_improved_model.py
# Review metrics.txt
# Check confusion_matrix.png
# Identify weak areas
```

### Production Validation
```bash
cd testing_tools
python test_document.py
# Test on real document samples
# Verify performance matches expectations
```

---

## Model Comparison Workflow

### Compare Old vs New Model

1. **Test Current Model:**
```bash
cd testing_tools
# Edit test_improved_model.py: model_path = '../models/best_v2_updated_classes.pt'
python test_improved_model.py
# Note metrics: Precision, Recall, mAP
```

2. **Test New Model:**
```bash
# Edit test_improved_model.py: model_path = '../models/best_v3_new.pt'
python test_improved_model.py
# Note metrics
```

3. **Compare Results:**
```
Model Comparison:
                Old (v2)    New (v3)    Change
Precision:      0.82        0.85        +3.7%
Recall:         0.78        0.81        +3.8%
F1-Score:       0.80        0.83        +3.8%
mAP50:          0.74        0.78        +5.4%

Decision: New model is better → Deploy v3
```

4. **Deploy if Better:**
```bash
cp ../models/best_v3_new.pt ../models/best_v2_updated_classes.pt
# Or rename and update model path in all tools
```

---

## Performance Benchmarks

### Target Metrics (by Dataset Size)

**Small Dataset (< 500 images):**
- Precision: 0.75+
- Recall: 0.70+
- mAP50: 0.65+

**Medium Dataset (500-1500 images):**
- Precision: 0.80+
- Recall: 0.75+
- mAP50: 0.72+

**Large Dataset (1500+ images):**
- Precision: 0.85+
- Recall: 0.80+
- mAP50: 0.78+

### Confidence Threshold Tuning

Test different thresholds to optimize precision/recall balance:

```bash
# High precision (fewer false positives)
confidence = 0.5  # More conservative

# Balanced
confidence = 0.3  # Default

# High recall (catch more objects)
confidence = 0.15  # More detections, more false positives
```

**Recommendation:** Start with 0.3, adjust based on use case
- **Critical accuracy** → Increase to 0.4-0.5
- **Must catch everything** → Decrease to 0.2-0.25

---

## Troubleshooting

### Low Precision (Many False Positives)
**Symptoms:** Model detects shapes that don't exist
**Fixes:**
- Increase confidence threshold
- Add more negative examples (images without shapes)
- Review false positives and retrain
- Use harder negative mining

### Low Recall (Missing Objects)
**Symptoms:** Model misses obvious shapes
**Fixes:**
- Decrease confidence threshold
- Check if missing classes need more training data
- Review missed examples
- Add more augmentation
- Train longer

### Class Confusion (e.g., L-shape detected as U-shape)
**Symptoms:** High confusion matrix off-diagonal values
**Fixes:**
- Add more training examples of confused classes
- Review annotation quality for those classes
- Ensure class definitions are clear
- May need more distinctive features

### Slow Inference
**Symptoms:** Test takes too long
**Fixes:**
- Use smaller model (yolov8n instead of yolov8m)
- Reduce image size in preprocessing
- Use GPU if available
- Batch process images

---

## Best Practices

1. **Always test after training** before deploying
2. **Keep test results** for version comparison
3. **Test on diverse images** not just validation set
4. **Document performance changes** in root CLAUDE.md
5. **Maintain test dataset** separate from training
6. **Regular regression testing** when updating model

---

## Test Dataset Preparation

### Creating Good Test Set

1. **Separate from Training:** Never test on training images
2. **Representative:** Include all classes and scenarios
3. **Size:** At least 20% of total dataset (validation split)
4. **Diverse:** Various image qualities, lighting, angles
5. **Edge Cases:** Include difficult examples

### Test Data Location
```
Option 1: Use validation split from training
  ../data/labeled/ → Split by create_training_dataset.py

Option 2: Separate test folder
  ../data/test_set/
```

---

## Next Steps After Testing

1. **Review metrics** - Meet target performance?
2. **Analyze errors** - What's failing?
3. **If good:** Deploy model, update docs
4. **If poor:**
   - Label more data for weak classes
   - Run augmentation
   - Adjust hyperparameters
   - Retrain model
   - Test again

---

## Dependencies

```bash
pip install ultralytics opencv-python Pillow numpy matplotlib seaborn
```

---

## Quick Reference

```bash
# Quick visual test
python test_single_image.py

# Full evaluation
python test_improved_model.py

# Document testing
python test_document.py

# View results
cat test_results/metrics.txt
open test_results/confusion_matrix.png
```
