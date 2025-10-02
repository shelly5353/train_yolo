# Google Colab YOLO Training Script
# Upload this notebook to Colab and run

# Install YOLOv8
!pip install ultralytics

# Import libraries
from ultralytics import YOLO
import torch
from google.colab import files
import zipfile

print("🚀 YOLO Shape Detection Training")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")

# Upload and extract dataset
print("\n📁 Upload your yolo_training_dataset.zip file:")
uploaded = files.upload()

# Extract dataset
for filename in uploaded.keys():
    print(f"Extracting {filename}...")
    with zipfile.ZipFile(filename, 'r') as zip_ref:
        zip_ref.extractall('.')

# Load pretrained model
print("\n🤖 Loading YOLOv8 model...")
model = YOLO('yolov8n.pt')  # Use 'yolov8s.pt' for better accuracy

# Training configuration
print("\n🎯 Starting training...")
results = model.train(
    data='yolo_training_dataset/dataset.yaml',
    epochs=50,          # Adjust based on time available
    imgsz=640,          # Image size
    batch=8,            # Adjust based on GPU memory (8 for T4, 16 for V100)
    device=0,           # GPU device
    project='shape_detection',
    name='yolov8_shapes',
    save=True,
    plots=True,
    val=True,
    patience=10,        # Early stopping
    save_period=10,     # Save every 10 epochs
)

# Validate the model
print("\n📊 Validating model...")
metrics = model.val()

# Download the trained model
print("\n💾 Downloading trained model...")
files.download(f"{results.save_dir}/weights/best.pt")
files.download(f"{results.save_dir}/weights/last.pt")

print("\n✅ Training complete!")
print(f"Best model saved and downloaded!")
