# Install YOLOv8
!pip install ultralytics

# Import libraries
from ultralytics import YOLO
import torch
from google.colab import drive, files

print("🚀 YOLO Shape Detection - Continue Training Existing Model")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")

# Mount Google Drive
drive.mount('/content/drive')

# Upload your existing best.pt model
print("\n📤 Upload your existing best.pt model:")
uploaded = files.upload()

# Get the uploaded model filename
model_file = list(uploaded.keys())[0]
print(f"Using model: {model_file}")

# Load your existing trained model
print(f"\n🤖 Loading your existing model: {model_file}")
model = YOLO(model_file)  # Load your existing model

# Continue training with more data
print("\n🎯 Continuing training with augmented dataset...")
results = model.train(
    data='/content/drive/MyDrive/yolo_training_dataset/dataset.yaml',
    epochs=50,          # Additional epochs
    imgsz=640,          
    batch=8,            # Adjust for GPU memory
    device=0,           
    project='shape_detection_continued',
    name='yolov8_shapes_v2',
    save=True,
    plots=True,
    val=True,
    patience=15,        # More patience for fine-tuning
    save_period=10,
    resume=False,       # Start fresh training with existing weights
)

# Validate the improved model
print("\n📊 Validating improved model...")
metrics = model.val()

# Download the improved model
print("\n💾 Downloading improved model...")
files.download(f"{results.save_dir}/weights/best.pt")
files.download(f"{results.save_dir}/weights/last.pt")

print("\n✅ Continued training complete!")
print("Your model has been improved with the augmented dataset!")
