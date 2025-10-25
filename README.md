# YOLO Training and Labeling Suite

A comprehensive collection of tools for labeling images and training YOLO object detection models to identify different shapes. From basic manual labeling to AI-assisted annotation and modern web interfaces.

## Overview

This project provides a complete solution for training YOLO models to detect and classify four different shape types:
- **Straight** shapes (Class 0 - Red)
- **L-shape** objects (Class 1 - Blue)
- **U-shape** objects (Class 2 - Green)
- **Complex** shapes (Class 3 - Orange)

## 🚀 Quick Start

Choose your preferred labeling workflow:

### Option 1: AI-Assisted Workflow (Recommended)
```bash
# 1. Generate initial labels with AI
python batch_detect.py --confidence 0.25

# 2. Review and edit with modern web interface
cd annotation_tool
./start.sh
```

### Option 2: Manual Labeling
```bash
# Start with basic manual labeling tool
python label_tool.py
```

### Option 3: Edit Existing Labels
```bash
# Quick editor for pre-labeled data
python simple_edit_tool.py
```

## 🛠️ Tool Suite

### 1. **Batch Detection Script** (`batch_detect.py`)
**Best for:** Initial automated labeling of large datasets
- Runs trained YOLO model on all images
- Configurable confidence threshold
- Progress tracking with statistics
- Mass processes hundreds of images quickly

```bash
python batch_detect.py --confidence 0.3 --data_dir data --output_dir labeld_data
```

### 2. **Modern Web Annotation Tool** (`annotation_tool/`)
**Best for:** Professional annotation with modern interface
- **React + Flask architecture** for smooth performance
- **Trackpad gestures** (pinch-to-zoom, scroll-to-pan)
- **Keyboard shortcuts** (N, V, H, 1-4, Cmd+S)
- **Real-time statistics** and progress tracking
- **High-resolution image support** with pixel-perfect precision

```bash
cd annotation_tool
./start.sh  # Starts both backend and frontend
# Access at http://localhost:3000
```

### 3. **Enhanced Label Tool** (`enhanced_label_tool.py`)
**Best for:** AI-assisted manual correction
- **Model integration**: Run YOLO detection, then manually edit
- **Confidence slider**: Adjust detection sensitivity in real-time
- **Full-size canvas**: Work with original image resolution
- **Smart workflow**: AI detection + human correction

```bash
python enhanced_label_tool.py
# Press 'R' to run model detection, then edit results
```

### 4. **Simple Edit Tool** (`simple_edit_tool.py`)
**Best for:** Quick review of pre-generated labels
- **Fast editing**: Focus on correction, not initial labeling
- **Statistics display**: Track progress and label counts
- **Minimal interface**: Streamlined for efficiency
- **Batch review**: Quickly process already-labeled datasets

```bash
python simple_edit_tool.py
```

### 5. **Original Label Tool** (`label_tool.py`)
**Best for:** Basic manual labeling from scratch
- **Tkinter GUI**: Simple, reliable interface
- **Manual drawing**: Traditional click-and-drag bounding boxes
- **Basic controls**: Essential features for ground-truth labeling

```bash
python label_tool.py
```

## Installation

### Requirements
```bash
pip install -r requirements.txt
```

### Python Dependencies
```bash
pip install -r requirements.txt
```

Core dependencies:
- `opencv-python>=4.0.0` - Image processing and display
- `Pillow>=8.0.0` - Image handling and conversion
- `torch>=1.7.0` - PyTorch framework for model loading
- `ultralytics>=8.0.0` - YOLO implementation and inference
- `tqdm` - Progress bars for batch processing

### Web Tool Dependencies
The modern web annotation tool has additional requirements:
- **Python 3.8+** with Flask
- **Node.js 16+** with npm
- **macOS recommended** (for trackpad gesture support)

## Usage

### Running the Labeling Tool
```bash
python label_tool.py
```

### Controls
- **Left Click + Drag**: Create bounding box
- **Right Click**: Delete bounding box
- **Arrow Keys**: Navigate between images
- **Space Bar**: Save and move to next image
- **Delete Key**: Clear all labels on current image

### Workflow
1. Launch the tool with `python label_tool.py`
2. Select appropriate shape class from dropdown
3. Draw bounding boxes around objects
4. Use keyboard shortcuts for efficient processing
5. Labeled data automatically saved to `labeld_data/` directory

## Project Structure

```
train_yolo/
├── README.md                    # This documentation
├── CLAUDE.md                    # Development notes and technical details
├── requirements.txt             # Python dependencies
├── .gitignore                   # Git ignore rules
├── best.pt                     # Trained YOLO model weights (22.5MB)
├── data/                       # Original training images
├── labeld_data/                # Output directory for labeled data
├── label_tool.py               # Original manual labeling tool
├── enhanced_label_tool.py      # AI-assisted labeling tool
├── simple_edit_tool.py         # Quick editor for existing labels
├── batch_detect.py             # Automated batch processing
└── annotation_tool/            # Modern web annotation interface
    ├── backend/                # Flask API server
    ├── frontend/               # React web application
    ├── start.sh               # Auto-startup script
    └── README.md              # Web tool documentation
```

## Model Information

- **Model Type**: YOLO (You Only Look Once) object detection
- **Classes**: 4 shape categories (0: straight, 1: L-shape, 2: U-shape, 3: complex)
- **Format**: Normalized bounding box coordinates
- **Weights**: Pre-trained model available in `best.pt`

## Output Format

Labels are saved in YOLO format:
```
class_id x_center y_center width height
```
All coordinates are normalized (0.0 to 1.0) relative to image dimensions.

## Recommended Workflows

### 🤖 AI-Assisted Workflow (Fastest)
Perfect for large datasets with a trained model:

1. **Batch detect**: `python batch_detect.py --confidence 0.25`
2. **Web review**: `cd annotation_tool && ./start.sh`
3. **Access tool**: Open http://localhost:3000 in browser
4. **Review/edit**: Use trackpad gestures and keyboard shortcuts

### 🖐️ Manual Workflow (Most Control)
For new datasets or ground-truth labeling:

1. **Manual labeling**: `python enhanced_label_tool.py`
2. **Use AI assist**: Press 'R' to run model detection
3. **Correct labels**: Edit AI predictions manually
4. **Save progress**: Use keyboard shortcuts for efficiency

### ⚡ Quick Edit Workflow (Existing Labels)
For reviewing pre-labeled data:

1. **Generate labels**: Use batch detection or other tools first
2. **Quick edit**: `python simple_edit_tool.py`
3. **Fast review**: Navigate through images rapidly
4. **Final corrections**: Make adjustments as needed

## Training Data

- **Images**: Place training images (PNG format) in the `data/` directory
- **Labels**: Generated automatically in `labeld_data/` as you work
- **Validation**: Visual feedback ensures accurate labeling

## Deployment

This project can be deployed to Vercel or other hosting platforms. See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

### Quick Deploy to Vercel

1. Push this repository to GitHub
2. Connect repository to Vercel
3. Deploy with one click (configuration in `vercel.json`)

For detailed instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

## Support

For issues or questions about the labeling tool or YOLO training process, refer to the project documentation or create an issue in the repository.