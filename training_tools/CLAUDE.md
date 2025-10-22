# TRAINING TOOLS

## Purpose
Scripts for training and continuing training of YOLO models, optimized for Google Colab.

## Available Scripts

### 1. colab_training_script.py - Initial Model Training
**Purpose:** Train a new YOLO model from scratch or fine-tune existing model

**Features:**
- YOLOv8-based training
- Configurable hyperparameters
- GPU-optimized for Google Colab
- Automatic checkpointing
- Training metrics logging
- Validation during training

**Usage:**

**On Google Colab:**
```python
# Upload this script and dataset to Colab
!python colab_training_script.py
```

**Locally (if GPU available):**
```bash
cd training_tools
python colab_training_script.py
```

**Configuration Options (edit in script):**
```python
# Dataset
data_yaml = 'path/to/dataset.yaml'

# Model
model = 'yolov8n.pt'  # nano, small, medium, large, xlarge

# Training
epochs = 50
batch_size = 16
imgsz = 640
device = 0  # GPU ID, 'cpu' for CPU training

# Optimization
optimizer = 'SGD'  # SGD, Adam, AdamW
lr0 = 0.01  # initial learning rate
```

**Output:**
- `runs/detect/train/weights/best.pt` - Best model weights
- `runs/detect/train/weights/last.pt` - Last epoch weights
- `runs/detect/train/results.png` - Training curves
- `runs/detect/train/confusion_matrix.png` - Confusion matrix

**Training Time:**
- Small dataset (500 images): 30-60 minutes on Colab GPU
- Medium dataset (1000 images): 1-2 hours
- Large dataset (2000+ images): 3-4 hours

**When to Use:**
- Starting fresh training from pretrained YOLO weights
- Retraining entire model on new dataset
- Experimenting with different model sizes
- Initial model development

---

### 2. colab_continue_training.py - Resume Training
**Purpose:** Continue training from a checkpoint or fine-tune existing model

**Features:**
- Load existing model weights
- Resume from interrupted training
- Fine-tune trained models with new data
- Preserve previous training progress
- Incremental improvement

**Usage:**

**On Google Colab:**
```python
!python colab_continue_training.py
```

**Locally:**
```bash
cd training_tools
python colab_continue_training.py
```

**Configuration (edit in script):**
```python
# Model checkpoint to continue from
model = '../models/best_v2_updated_classes.pt'

# Additional epochs
epochs = 20

# Fine-tuning settings
lr0 = 0.001  # Lower learning rate for fine-tuning
```

**When to Use:**
- Training was interrupted
- Want to train more epochs on existing model
- Adding new labeled data to existing model
- Fine-tuning with additional data
- Improving model performance incrementally

**Workflow:**
1. Load existing `best_v2_updated_classes.pt`
2. Add new training data
3. Continue training for more epochs
4. Compare performance with previous version
5. Replace model if improved

---

## Google Colab Setup

### Step-by-Step Colab Training

1. **Prepare Dataset Locally:**
```bash
cd utilities
python prepare_colab_dataset.py
# Creates colab_training_dataset/ folder
```

2. **Upload to Google Drive:**
- Compress dataset: `zip -r dataset.zip colab_training_dataset/`
- Upload to Google Drive

3. **Colab Notebook Setup:**
```python
# Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

# Install dependencies
!pip install ultralytics

# Extract dataset
!unzip /content/drive/MyDrive/dataset.zip -d /content/

# Copy training script
!cp /content/drive/MyDrive/colab_training_script.py /content/

# Run training
!python colab_training_script.py
```

4. **Download Trained Model:**
```python
# After training completes
!cp runs/detect/train/weights/best.pt /content/drive/MyDrive/trained_model.pt
```

5. **Local Model Deployment:**
- Download `trained_model.pt` from Google Drive
- Copy to `../models/best_v2_updated_classes.pt`
- Test with `../testing_tools/`

---

## Training Best Practices

### Data Preparation
1. ✅ Run `../utilities/dataset_stats.py` to check balance
2. ✅ Use augmentation for small datasets (< 500 images)
3. ✅ Ensure 80/20 train/val split
4. ✅ Verify dataset.yaml paths are correct

### Hyperparameter Selection

**For Small Datasets (< 500 images):**
- Model: `yolov8n.pt` (nano - smallest, fastest)
- Epochs: 50-100
- Batch size: 16
- Learning rate: 0.01

**For Medium Datasets (500-1500 images):**
- Model: `yolov8s.pt` (small)
- Epochs: 100-150
- Batch size: 16-32
- Learning rate: 0.01

**For Large Datasets (1500+ images):**
- Model: `yolov8m.pt` (medium)
- Epochs: 150-300
- Batch size: 32
- Learning rate: 0.01

### Training Monitoring

**Watch These Metrics:**
- **mAP50:** Should increase steadily (target: > 0.7)
- **mAP50-95:** Overall accuracy (target: > 0.5)
- **Precision:** Reduce false positives (target: > 0.8)
- **Recall:** Catch all objects (target: > 0.7)
- **Loss:** Should decrease steadily

**Warning Signs:**
- Loss stops decreasing → May be overfitting
- Validation mAP < Training mAP → Overfitting
- Both mAP very low → Need more/better labeled data

### After Training

1. **Download best.pt** from Colab
2. **Rename with version:** `best_v3_DATE.pt`
3. **Backup old model** before replacing
4. **Test new model** with `../testing_tools/`
5. **Compare performance** old vs new
6. **Update `../models/CLAUDE.md`** with changes
7. **If better:** Replace active model, if worse: keep old model

---

## Training Workflow

### Initial Training (From Scratch)
```bash
# 1. Prepare data
cd utilities
python dataset_stats.py
python augment_dataset.py
python prepare_colab_dataset.py

# 2. Upload to Colab and train
# (Use Colab notebook with colab_training_script.py)

# 3. Download and test
cd testing_tools
python test_improved_model.py

# 4. Deploy if good
cp ~/Downloads/trained_model.pt ../models/best_v2_updated_classes.pt
```

### Incremental Improvement
```bash
# 1. Label more images
cd labeling_tools
python batch_detect.py
python simple_edit_tool.py

# 2. Update training dataset
cd utilities
python create_training_dataset.py

# 3. Continue training on Colab
# (Use colab_continue_training.py)

# 4. Test and compare
cd testing_tools
python test_improved_model.py
```

---

## Troubleshooting

**Issue:** Out of memory on Colab
**Fix:** Reduce batch_size (try 8 or 16)

**Issue:** Training very slow
**Fix:** Ensure GPU is enabled (Runtime → Change runtime type → GPU)

**Issue:** Low mAP after training
**Fix:**
- Check dataset.yaml paths are correct
- Verify labels are accurate
- Increase epochs
- Use data augmentation
- Add more training data

**Issue:** Model overfitting (train mAP high, val mAP low)
**Fix:**
- Add more validation data
- Use data augmentation
- Reduce model size (e.g., nano instead of small)
- Add early stopping

**Issue:** Colab disconnects during training
**Fix:**
- Use `colab_continue_training.py` to resume
- Keep browser tab active
- Use Colab Pro for longer sessions

---

## Dependencies

```bash
pip install ultralytics torch torchvision
```

**GPU Requirements:**
- Colab: Free T4 GPU (sufficient for most training)
- Local: NVIDIA GPU with CUDA support
- CPU training: Possible but very slow (not recommended)

---

## Advanced Topics

### Transfer Learning
Start from pretrained YOLO weights (yolov8n.pt) for faster training and better results with limited data.

### Custom Hyperparameters
Edit training scripts to tune:
- Learning rate schedules
- Augmentation settings
- Loss function weights
- Anchor box sizes

### Multi-GPU Training
Colab supports single GPU. For multi-GPU, use local setup with `device=[0,1,2,3]`.

---

## Next Steps After Training

1. Test model: `cd ../testing_tools/`
2. Evaluate performance
3. If satisfactory: Deploy to `../models/`
4. Update all tools to use new model
5. Document changes in root CLAUDE.md
