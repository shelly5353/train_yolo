# ============================================================
# GOOGLE COLAB YOLO TRAINING - CONTINUE FROM EXISTING MODEL
# ============================================================
# This script continues training from your existing best.pt model
# Follow the cells in order

# ============================================================
# CELL 1: Mount Google Drive and Install Dependencies
# ============================================================
from google.colab import drive
import zipfile
import os

# Mount Google Drive
drive.mount('/content/drive')

# Install YOLOv8
!pip install ultralytics

print("✅ Setup complete!")

# ============================================================
# CELL 2: Extract Dataset and Model from Google Drive
# ============================================================
import zipfile

# Extract dataset (UPDATE PATH if your ZIP is in a different Drive folder)
dataset_zip_path = '/content/drive/MyDrive/yolo_training_dataset.zip'
model_path = '/content/drive/MyDrive/best.pt'  # Your existing model

print("📦 Extracting dataset...")
with zipfile.ZipFile(dataset_zip_path, 'r') as zip_ref:
    zip_ref.extractall('/content/')

print("✅ Dataset extracted to /content/yolo_training_dataset/")
print(f"✅ Model found at {model_path}")

# Verify files exist
print("\n📊 Checking dataset structure...")
!ls -lh /content/yolo_training_dataset/
!ls -lh /content/yolo_training_dataset/images/train/ | head -5
!ls -lh /content/yolo_training_dataset/images/val/ | head -5

# ============================================================
# CELL 3: Check GPU and Continue Training
# ============================================================
from ultralytics import YOLO
import torch

# Check GPU availability
print(f"🔥 CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"🎮 GPU device: {torch.cuda.get_device_name(0)}")
    print(f"💾 GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
else:
    print("⚠️ No GPU found - training will be slow!")

# Load your existing model to CONTINUE training
print("\n📂 Loading existing model...")
model = YOLO(model_path)

# Continue training on new dataset
print("\n🚀 Starting training...")
results = model.train(
    data='/content/yolo_training_dataset/dataset.yaml',  # path to dataset YAML
    epochs=50,                                           # additional epochs to train
    imgsz=640,                                          # image size
    batch=16,                                           # batch size (reduce to 8 if memory error)
    device=0,                                           # GPU device
    project='shape_detection',                          # project name
    name='continued_training',                          # experiment name
    save=True,                                          # save model checkpoints
    verbose=True,                                       # verbose output
    plots=True,                                         # save training plots
    val=True,                                           # validate during training
    patience=15,                                        # early stopping patience
    save_period=5,                                      # save checkpoint every 5 epochs
    resume=False,                                       # False = continue from loaded model
)

print("\n✅ Training completed!")
print(f"📁 Results saved at: {results.save_dir}")

# ============================================================
# CELL 4: Validate and Check Results
# ============================================================
# Validate the trained model
print("🧪 Running validation...")
metrics = model.val()

print(f"\n📊 Validation Metrics:")
print(f"mAP50: {metrics.box.map50:.3f}")
print(f"mAP50-95: {metrics.box.map:.3f}")

# Show training plots
from IPython.display import Image, display
import os

results_dir = results.save_dir
print(f"\n📈 Training plots saved in: {results_dir}")

# Display confusion matrix
confusion_matrix_path = os.path.join(results_dir, 'confusion_matrix.png')
if os.path.exists(confusion_matrix_path):
    display(Image(filename=confusion_matrix_path))

# ============================================================
# CELL 5: Download the New Best Model
# ============================================================
from google.colab import files
import shutil

# The new best model will be at:
best_model_path = os.path.join(results.save_dir, 'weights', 'best.pt')

print(f"📥 Downloading new best model from: {best_model_path}")
print(f"Model size: {os.path.getsize(best_model_path) / 1e6:.1f} MB")

# Copy to Drive (backup)
drive_backup_path = '/content/drive/MyDrive/best_v3_trained.pt'
shutil.copy(best_model_path, drive_backup_path)
print(f"✅ Backed up to Google Drive: {drive_backup_path}")

# Download to your computer
files.download(best_model_path)
print("✅ Download started!")
