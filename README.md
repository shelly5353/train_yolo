# YOLO Training and Labeling Tool

A Python-based interactive tool for labeling images and training YOLO object detection models to identify different shapes.

## Overview

This project provides a complete solution for training YOLO models to detect and classify four different shape types:
- **Straight** shapes
- **L-shape** objects
- **U-shape** objects
- **Complex** shapes

## Features

### Interactive Labeling Tool
- **GUI Interface**: User-friendly tkinter-based interface
- **Mouse Drawing**: Click and drag to create bounding boxes
- **Class Selection**: Dropdown menu for shape classification
- **Visual Feedback**: Color-coded bounding boxes with labels
- **Keyboard Shortcuts**: Efficient navigation and editing
- **YOLO Format**: Automatic export in YOLO training format

### Key Capabilities
- Process 312+ training images
- Real-time label visualization
- Easy label correction and deletion
- Automatic coordinate normalization
- Batch processing support

## Installation

### Requirements
```bash
pip install -r requirements.txt
```

### Dependencies
- `opencv-python>=4.0.0` - Image processing
- `Pillow>=8.0.0` - Image handling
- `torch>=1.7.0` - PyTorch framework
- `ultralytics>=8.0.0` - YOLO implementation

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
├── label_tool.py           # Main labeling application
├── requirements.txt        # Python dependencies
├── best.pt                # Trained model weights
├── data/                  # Original training images (312 files)
├── labeld_data/           # Output directory for labeled data
├── README.md              # This file
└── CLAUDE.md              # Development documentation
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

## Getting Started

1. **Clone/Download** the project files
2. **Install dependencies** with `pip install -r requirements.txt`
3. **Add training images** to the `data/` directory
4. **Run the labeling tool** with `python label_tool.py`
5. **Start labeling** your images using the interactive interface

## Training Data

- **Images**: Place training images (PNG format) in the `data/` directory
- **Labels**: Generated automatically in `labeld_data/` as you work
- **Validation**: Visual feedback ensures accurate labeling

## Support

For issues or questions about the labeling tool or YOLO training process, refer to the project documentation or create an issue in the repository.