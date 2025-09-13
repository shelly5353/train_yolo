# CLAUDE.md

## PROJECT OVERVIEW
- **Project Name:** YOLO Training and Labeling Tool
- **Primary Goal/MVP:** Create and train a YOLO object detection model for identifying different shapes (straight, L-shape, U-shape, complex)
- **Project Type:** AI/ML Computer Vision Project
- **Main Language(s):** Python

## GIT WORKFLOW RULES
- Always work on 'dev' branch, never commit directly to main
- Commit after every significant change with clear descriptions
- Ask user before syncing dev branch to GitHub
- Use GitHub CLI: gh repo sync --source [branch-name]

## PROJECT STRUCTURE
```
train_yolo/
├── CLAUDE.md                    # This file - project documentation and development notes
├── README.md                    # User-facing project documentation
├── requirements.txt             # Python dependencies
├── label_tool.py               # Interactive YOLO labeling tool with GUI
├── best.pt                     # Trained YOLO model weights (22.5MB)
├── data/                       # Original training images (312 files)
├── labeld_data/                # Labeled output directory
└── .claude/                    # Claude Code configuration
```

## CORE FUNCTIONALITY

### YOLO Labeling Tool (label_tool.py)
- **Purpose:** Interactive GUI tool for labeling images for YOLO training
- **Classes:** 4 shape categories (straight, L-shape, U-shape, complex)
- **Features:**
  - Tkinter GUI with image display and navigation
  - Mouse-based bounding box drawing
  - Class selection dropdown
  - Keyboard shortcuts (Left/Right arrows, Space, Delete)
  - YOLO format export (normalized coordinates)
  - Real-time label visualization with color coding

### Model Components
- **Model File:** best.pt (trained YOLO weights)
- **Training Data:** 312 images in data/ directory
- **Output Format:** YOLO txt format with normalized bounding boxes

### Dependencies
- opencv-python>=4.0.0 (image processing)
- Pillow>=8.0.0 (image handling)
- torch>=1.7.0 (PyTorch for YOLO)
- ultralytics>=8.0.0 (YOLO implementation)

## DEVELOPMENT NOTES

### Recent Changes:
- Initial project setup completed
- YOLO labeling tool fully functional
- Model training completed with best.pt weights
- 312 training images available for labeling/re-labeling

### Technical Implementation:
- GUI built with tkinter for cross-platform compatibility
- Image scaling and coordinate conversion between display and YOLO formats
- Mouse event handling for intuitive bounding box creation
- Right-click deletion for easy label correction
- Automatic saving to labeld_data/ directory

### Current Status:
- Labeling tool is production-ready
- Model weights available (best.pt)
- Ready for further training iterations or deployment

### Usage Instructions:
1. Run `python label_tool.py` to start the GUI
2. Use mouse to draw bounding boxes around objects
3. Select appropriate class from dropdown
4. Use keyboard shortcuts for efficient navigation
5. Labels automatically saved in YOLO format

### Next Steps:
- Documentation creation and git repository setup
- Potential model retraining with additional labeled data
- Integration with training pipeline