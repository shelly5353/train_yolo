# UTILITIES FOLDER

## Purpose
Dataset management, preparation, and analysis scripts for the YOLO training pipeline.

## Available Utilities

### 1. augment_dataset.py - Data Augmentation
**Purpose:** Expand training dataset through image transformations

**Features:**
- Creates augmented versions of labeled images
- Preserves YOLO annotations with transformations
- Multiple augmentation techniques
- Organized output structure (images/ + labels/ subfolders)

**Augmentation Types:**
- Brightness increase (factor: 1.3)
- Brightness decrease/darkening (factor: 0.7)
- Horizontal flip (mirror image)
- Original (copies to augmented folder)

**Usage:**
```bash
cd utilities
python augment_dataset.py
```

**Input:** `../data/labeled/` (images + labels)
**Output:** `../data/augmented/` (images/ and labels/ subfolders)

**Result:** 4x dataset size
- Original: 100 images → Augmented: 400 images (100 original + 300 augmented)

**When to Use:**
- Small dataset (< 500 images)
- Improve model generalization
- Address class imbalance
- Before training to expand data

**File Naming:**
- Original: `image.png` → `image.png`
- Bright: `image.png` → `image_bright.png`
- Dark: `image.png` → `image_dark.png`
- Flipped: `image.png` → `image_hflip.png`

---

### 2. collect_latest_labels.py - Label Collection
**Purpose:** Gather latest annotations from multiple sources

**Features:**
- Scans multiple directories for label files
- Collects most recent versions
- Deduplicates based on filename
- Consolidates scattered labels

**Usage:**
```bash
cd utilities
python collect_latest_labels.py
```

**Use Cases:**
- Labels spread across multiple folders
- Need to consolidate work from different annotation sessions
- Preparing final dataset from various sources
- Quality control - collecting only latest versions

**Typical Sources:**
- `../data/labeled/`
- `../old_datasets/old_final_labeled_dataset/`
- `../old_datasets/old_labeled_new_dataset/`

**Output:** Consolidated label collection

---

### 3. create_training_dataset.py - Training Package Builder
**Purpose:** Prepare dataset in YOLO training format

**Features:**
- Creates train/val split
- Generates YOLO dataset.yaml configuration
- Organizes files for Ultralytics training
- Validates dataset structure

**Usage:**
```bash
cd utilities
python create_training_dataset.py
```

**Input:** Labeled data from `../data/labeled/` or `../data/augmented/`

**Output Structure:**
```
training_dataset/
├── images/
│   ├── train/    (80% of images)
│   └── val/      (20% of images)
├── labels/
│   ├── train/    (80% of labels)
│   └── val/      (20% of labels)
└── dataset.yaml  (YOLO config file)
```

**dataset.yaml Contents:**
```yaml
path: /path/to/training_dataset
train: images/train
val: images/val
nc: 4  # number of classes
names: ['straight', 'L-shape', 'U-shape', 'complex']
```

**When to Use:**
- Before every training run
- After adding new labeled data
- After running augmentation
- Preparing data for Google Colab

**Split Ratio:** 80% train, 20% validation (configurable in script)

---

### 4. dataset_stats.py - Dataset Analysis
**Purpose:** Analyze dataset composition and class distribution

**Features:**
- Counts images and labels
- Class distribution statistics
- Bounding box statistics (size, position)
- Identifies missing labels
- Generates summary report

**Usage:**
```bash
cd utilities
python dataset_stats.py
```

**Output Example:**
```
Dataset Statistics:
==================
Total images: 310
Total labels: 620
Average labels per image: 2.0

Class Distribution:
  Class 0 (straight): 245 (39.5%)
  Class 1 (L-shape): 180 (29.0%)
  Class 2 (U-shape): 125 (20.2%)
  Class 3 (complex): 70 (11.3%)

Missing labels: 0 images
```

**When to Use:**
- Before training to check dataset balance
- Identify class imbalance issues
- Verify annotation completeness
- Quality control checkpoint
- Document dataset characteristics

**Insights:**
- Class imbalance → Use data augmentation
- Missing labels → Need more annotation work
- Unusual bounding box sizes → Check annotation quality

---

### 5. prepare_colab_dataset.py - Google Colab Package
**Purpose:** Create dataset package for Google Colab training

**Features:**
- Combines labeled and augmented data
- Creates train/val split
- Generates dataset.yaml
- Packages into portable format
- Colab-ready structure

**Usage:**
```bash
cd utilities
python prepare_colab_dataset.py
```

**Input Sources:**
- `../data/labeled/`
- `../data/augmented/` (if available)

**Output:**
- Folder: `../colab_training_dataset/`
- Optional: ZIP file for easy upload

**When to Use:**
- Training on Google Colab
- Need to upload dataset to cloud
- Creating portable dataset package
- Sharing dataset with collaborators

**Colab Workflow:**
1. Run `prepare_colab_dataset.py`
2. Upload ZIP to Google Drive
3. Mount Drive in Colab
4. Extract and train
5. Download trained model

---

## Typical Workflow

### Complete Pipeline: From Labels to Training

```bash
# 1. Check dataset statistics
cd utilities
python dataset_stats.py

# 2. Augment data if needed (small dataset)
python augment_dataset.py

# 3. Create training package
python create_training_dataset.py

# 4. Optional: Prepare for Colab
python prepare_colab_dataset.py

# 5. Move to training_tools for actual training
cd ../training_tools
```

### Quick Dataset Update

```bash
# After adding new labels
cd utilities
python create_training_dataset.py
```

### Dataset Health Check

```bash
cd utilities
python dataset_stats.py
# Review output for issues
```

## Configuration

Most scripts use these default paths (editable in each script):
- **Input Data:** `../data/labeled/` or `../data/augmented/`
- **Output:** Various (see individual tool descriptions)
- **Model Path:** `../models/best_v2_updated_classes.pt`

## Best Practices

1. **Always run `dataset_stats.py`** before training
2. **Use augmentation** for datasets < 500 images
3. **Recreate training dataset** after any label changes
4. **Keep backups** of training packages before modifying
5. **Check class balance** - aim for similar counts per class
6. **Validate dataset.yaml** before training

## Dependencies

```bash
pip install opencv-python Pillow numpy pyyaml
```

## Troubleshooting

**Issue:** augment_dataset.py creates distorted images
**Fix:** Check input images are valid, not corrupted

**Issue:** create_training_dataset.py finds no labels
**Fix:** Verify labels exist in `../data/labeled/` with .txt extension

**Issue:** Class imbalance (one class has 80% of data)
**Fix:** Label more images of underrepresented classes, or use weighted loss in training

**Issue:** dataset_stats.py shows missing labels
**Fix:** Run labeling tools on images without labels

## Next Steps

After preparing dataset:
1. Review `dataset_stats.py` output
2. Move to `../training_tools/` for model training
3. After training, use `../testing_tools/` for validation
4. Iterate: label more data → augment → retrain
