# Google Colab Training Instructions

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
