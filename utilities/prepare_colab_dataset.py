#!/usr/bin/env python3
"""
Prepare YOLO dataset for Google Colab training
Creates proper train/val split and YOLO format structure
"""

import os
import shutil
import random
from pathlib import Path

def create_yolo_dataset_structure():
    """Create YOLO training dataset structure for Colab"""

    # Create main dataset directory
    dataset_dir = Path("yolo_training_dataset")
    dataset_dir.mkdir(exist_ok=True)

    # Create subdirectories
    (dataset_dir / "images" / "train").mkdir(parents=True, exist_ok=True)
    (dataset_dir / "images" / "val").mkdir(parents=True, exist_ok=True)
    (dataset_dir / "labels" / "train").mkdir(parents=True, exist_ok=True)
    (dataset_dir / "labels" / "val").mkdir(parents=True, exist_ok=True)

    return dataset_dir

def split_dataset(source_images_dir, source_labels_dir, output_dir, train_ratio=0.8):
    """Split dataset into train/validation sets"""

    # Get all image files
    image_files = list(Path(source_images_dir).glob("*.png"))

    # Filter to only files with corresponding labels
    valid_files = []
    for img_file in image_files:
        label_file = Path(source_labels_dir) / f"{img_file.stem}.txt"
        if label_file.exists():
            valid_files.append(img_file.stem)

    # Shuffle and split
    random.seed(42)  # For reproducible splits
    random.shuffle(valid_files)

    split_idx = int(len(valid_files) * train_ratio)
    train_files = valid_files[:split_idx]
    val_files = valid_files[split_idx:]

    print(f"Total files: {len(valid_files)}")
    print(f"Training files: {len(train_files)}")
    print(f"Validation files: {len(val_files)}")

    # Copy files to appropriate directories
    for file_stem in train_files:
        # Copy image
        src_img = Path(source_images_dir) / f"{file_stem}.png"
        dst_img = output_dir / "images" / "train" / f"{file_stem}.png"
        shutil.copy2(src_img, dst_img)

        # Copy label
        src_label = Path(source_labels_dir) / f"{file_stem}.txt"
        dst_label = output_dir / "labels" / "train" / f"{file_stem}.txt"
        shutil.copy2(src_label, dst_label)

    for file_stem in val_files:
        # Copy image
        src_img = Path(source_images_dir) / f"{file_stem}.png"
        dst_img = output_dir / "images" / "val" / f"{file_stem}.png"
        shutil.copy2(src_img, dst_img)

        # Copy label
        src_label = Path(source_labels_dir) / f"{file_stem}.txt"
        dst_label = output_dir / "labels" / "val" / f"{file_stem}.txt"
        shutil.copy2(src_label, dst_label)

    return len(train_files), len(val_files)

def create_dataset_yaml(output_dir):
    """Create dataset.yaml configuration file"""

    yaml_content = """# YOLO Shape Detection Dataset
# Classes: straight, L-shape, U-shape, complex

# Dataset paths (relative to this file)
path: .  # dataset root dir
train: images/train  # train images (relative to 'path')
val: images/val  # val images (relative to 'path')

# Classes
nc: 4  # number of classes
names: ['straight', 'L-shape', 'U-shape', 'complex']  # class names
"""

    yaml_file = output_dir / "dataset.yaml"
    with open(yaml_file, 'w') as f:
        f.write(yaml_content)

    print(f"Created dataset.yaml at {yaml_file}")

def create_training_script():
    """Create a training script for Colab"""

    training_script = """# Google Colab YOLO Training Script
# Run this in Google Colab after uploading your dataset

# Install YOLOv8
!pip install ultralytics

# Import libraries
from ultralytics import YOLO
import torch

# Check GPU availability
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPU device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")

# Load a pretrained YOLOv8 model
model = YOLO('yolov8n.pt')  # nano model (fastest)
# model = YOLO('yolov8s.pt')  # small model
# model = YOLO('yolov8m.pt')  # medium model

# Train the model
results = model.train(
    data='yolo_training_dataset/dataset.yaml',  # path to dataset YAML
    epochs=100,                                 # number of training epochs
    imgsz=640,                                  # image size
    batch=16,                                   # batch size (adjust based on GPU memory)
    device=0,                                   # GPU device (0 for first GPU, 'cpu' for CPU)
    project='shape_detection',                  # project name
    name='yolov8_shapes',                      # experiment name
    save=True,                                  # save model checkpoints
    verbose=True,                               # verbose output
    plots=True,                                 # save training plots
    val=True,                                   # validate during training
    patience=10,                                # early stopping patience
    save_period=10,                             # save checkpoint every N epochs
)

# Validate the model
metrics = model.val()

# Export the model
model.export(format='onnx')  # export to ONNX format

print("Training completed!")
print(f"Best model saved at: {results.save_dir}")
"""

    with open("colab_training_script.py", 'w') as f:
        f.write(training_script)

    print("Created colab_training_script.py")

def create_colab_instructions():
    """Create instructions for using the dataset in Colab"""

    instructions = """# Google Colab Training Instructions

## 1. Upload Dataset to Google Drive
1. Compress the 'yolo_training_dataset' folder to ZIP
2. Upload the ZIP file to your Google Drive
3. Or use the upload method below in Colab

## 2. Google Colab Setup

### Option A: Upload directly to Colab
```python
from google.colab import files
import zipfile

# Upload the dataset ZIP file
uploaded = files.upload()

# Extract the dataset
for filename in uploaded.keys():
    with zipfile.ZipFile(filename, 'r') as zip_ref:
        zip_ref.extractall('.')
```

### Option B: Mount Google Drive
```python
from google.colab import drive
import zipfile

# Mount Google Drive
drive.mount('/content/drive')

# Extract dataset from Drive
with zipfile.ZipFile('/content/drive/MyDrive/yolo_training_dataset.zip', 'r') as zip_ref:
    zip_ref.extractall('/content/')
```

## 3. Training Configuration

### Recommended settings by GPU:
- **T4 GPU (Free Colab)**: batch=8, imgsz=640, model='yolov8n.pt'
- **V100/A100 (Colab Pro)**: batch=16, imgsz=640, model='yolov8s.pt'

### Training parameters:
- **epochs**: 50-100 (start with 50)
- **patience**: 10 (early stopping)
- **imgsz**: 640 (standard YOLO size)

## 4. Files to Upload:
- yolo_training_dataset.zip (main dataset)
- colab_training_script.py (training script)

## 5. Expected Training Time:
- Free Colab (T4): ~2-3 hours for 50 epochs
- Colab Pro (V100): ~1-1.5 hours for 50 epochs

## 6. Download Results:
After training, download:
- best.pt (best model weights)
- Training plots and metrics
- Validation results
"""

    with open("COLAB_INSTRUCTIONS.md", 'w') as f:
        f.write(instructions)

    print("Created COLAB_INSTRUCTIONS.md")

def main():
    print("🚀 Preparing YOLO dataset for Google Colab training")

    # Create dataset structure
    print("\n📁 Creating YOLO dataset structure...")
    output_dir = create_yolo_dataset_structure()

    # Split dataset
    print("\n🔄 Splitting dataset into train/validation sets...")
    train_count, val_count = split_dataset(
        "augmented_dataset/images",
        "augmented_dataset/labels",
        output_dir,
        train_ratio=0.8
    )

    # Create configuration files
    print("\n📝 Creating configuration files...")
    create_dataset_yaml(output_dir)
    create_training_script()
    create_colab_instructions()

    print(f"\n✅ Dataset preparation complete!")
    print(f"📊 Dataset summary:")
    print(f"   Training images: {train_count}")
    print(f"   Validation images: {val_count}")
    print(f"   Total images: {train_count + val_count}")

    print(f"\n📦 Files ready for Colab:")
    print(f"   1. Compress 'yolo_training_dataset/' folder to ZIP")
    print(f"   2. Upload ZIP to Google Drive or Colab")
    print(f"   3. Use colab_training_script.py for training")
    print(f"   4. Follow COLAB_INSTRUCTIONS.md")

if __name__ == "__main__":
    main()