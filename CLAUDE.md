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
├── .gitignore                   # Git ignore rules
├── best.pt                     # Trained YOLO model weights (22.5MB)
├── data/                       # Original training images (312 files)
├── labeld_data/                # Labeled output directory
├── label_tool.py               # Original interactive YOLO labeling tool
├── enhanced_label_tool.py      # AI-assisted labeling tool with model integration
├── simple_edit_tool.py         # Simple editor for pre-generated labels
├── batch_detect.py             # Batch processing script for automated labeling
├── annotation_tool/            # Modern web-based annotation interface
│   ├── backend/                # Flask API server
│   │   ├── app.py             # Main Flask application
│   │   └── requirements.txt   # Backend Python dependencies
│   ├── frontend/              # React web application
│   │   ├── src/               # React source code
│   │   ├── package.json       # Frontend dependencies
│   │   └── tailwind.config.js # Styling configuration
│   ├── start.sh               # Auto-startup script
│   └── README.md              # Web tool documentation
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

### Recent Changes (Latest Update):
- **PDF Page Annotations Bug Fix** (2025-10-25): Fixed critical bug preventing PDF page annotations from loading
  - Issue: /api/annotations endpoint returned "Image not found" for PDF page requests (e.g., CO25S002554_page2.png)
  - Root Cause: Endpoint was checking for image existence in IMAGES_DIR, but PDF pages are cached in pdf_cache/ directory
  - Solution: Added PDF page handling logic to get_annotations function
    - Detect virtual PDF page filenames (format: filename_pageN.png)
    - Extract PDF stem and page number from filename
    - Verify source PDF exists and get dimensions from cached page
    - Mirrors the PDF handling logic already present in serve_image endpoint
  - Result: All 857 PDF page annotations now load correctly in web UI
  - Tested: Verified with multiple PDF pages via curl and browser testing
- **Critical Annotation Tool Improvements** (2025-10-25): Implemented three major enhancements
  - **Multi-Page PDF Support**: PDFs now automatically expand into individual page entries (filename_page1.png, etc.)
    - Added PyMuPDF dependency for PDF-to-PNG conversion at 150 DPI
    - Intelligent caching system in pdf_cache/ directory prevents re-conversion
    - Each page treated as separate image in annotation workflow
    - Labels saved with matching _pageN naming convention
  - **Auto-Run YOLO Before Annotation**: Enhanced auto-generation with full format support
    - Now processes PNG, JPG, and PDF pages (previously only PNG)
    - Converts all PDF pages to PNG cache before running inference
    - Detailed progress logging shows "Processing: X/Y images" with success/error indicators
    - Filters unlabeled images upfront for efficiency
  - **Prevent Label Duplication**: Added verification logging to annotation saving
    - Logs file mode ('w' for overwrite) before saving
    - Verifies line count matches sent annotations after save
    - Warns if mismatch detected, returns verified_line_count in API
- **Backend Path Handling Fix** (2025-10-24): Fixed image loading errors for datasets outside backend directory
  - Backend now handles both relative and absolute image paths
  - Allows annotation tool to work with datasets anywhere on filesystem (Desktop, external drives, etc.)
  - Prevents "not in subpath" 500 errors when loading images from external directories
  - DirectorySelector dropdown now fully functional with external datasets
- **Canvas Rendering Fix** (2025-10-24): Resolved critical bug in ImageCanvas component where images were loading but not displaying
  - Fixed useEffect infinite loop that was clearing canvas on every render
  - Added proper dependency arrays to prevent unnecessary re-renders
  - Separated canvas initialization from window resize handling
  - Web annotation tool now displays images correctly
- **Enhanced YOLO Labeling Tool**: Added AI-assisted labeling with auto-detection
- **Simple Edit Tool**: Quick editor for pre-generated labels
- **Batch Detection Script**: Automated processing of entire datasets
- **Modern Web Annotation Tool**: Full React/Flask web application with trackpad support
- **Complete Tool Suite**: Four different tools for various labeling workflows

### Tool Suite Overview:

#### 1. **Original Label Tool** (`label_tool.py`)
- Basic manual labeling with tkinter GUI
- Mouse-based bounding box drawing
- Class selection and keyboard shortcuts
- Original tool for ground-up labeling

#### 2. **Enhanced Label Tool** (`enhanced_label_tool.py`)
- **AI-Assisted Labeling**: Runs trained model first, then allows manual editing
- **Confidence Threshold Control**: Adjustable detection sensitivity
- **Full-screen Canvas**: Original image size with scrollbars
- **Smart Workflow**: Model detection + manual correction
- **Keyboard Shortcuts**: Press 'R' to run model detection

#### 3. **Simple Edit Tool** (`simple_edit_tool.py`)
- **Pre-label Editor**: Works on already labeled data
- **Fast Review**: Quickly review and correct batch-generated labels
- **Statistics Tracking**: Shows processed count and label statistics
- **Minimal Interface**: Focused on editing, not initial labeling

#### 4. **Batch Detection Script** (`batch_detect.py`)
- **Automated Processing**: Runs model on all images at once
- **Progress Tracking**: tqdm progress bars and statistics
- **Confidence Control**: Command-line confidence threshold
- **Mass Production**: Processes hundreds of images quickly
- Usage: `python batch_detect.py --confidence 0.3`

#### 5. **Modern Web Annotation Tool** (`annotation_tool/`)
- **React + Flask Architecture**: Modern web-based interface
- **Trackpad Gestures**: Native macOS pinch-to-zoom and pan
- **High Performance**: 60fps smooth interactions
- **Professional UI**: Color-coded classes, real-time statistics
- **Keyboard Shortcuts**: Extensive hotkey support (N, V, H, 1-4, Cmd+S)
- **Auto-startup**: Single `./start.sh` command launches everything

### Recommended Workflow:
1. **Batch Detection**: `python batch_detect.py` for initial AI labeling
2. **Web Tool Review**: `cd annotation_tool && ./start.sh` for professional editing
3. **Simple Editor**: `python simple_edit_tool.py` for quick corrections
4. **Enhanced Tool**: `python enhanced_label_tool.py` for AI-assisted refinement

### Technical Improvements:
- **Canvas Rendering**: Full-resolution display with scrollable interface
- **Coordinate Precision**: Pixel-perfect bounding box accuracy
- **Model Integration**: Direct YOLO model inference in labeling tools
- **Batch Processing**: Efficient handling of large datasets
- **Web Architecture**: Scalable React/Flask separation
- **Gesture Support**: Native trackpad integration for macOS
- **Performance**: Optimized for large images and many annotations

### Current Status:
- **Production Ready**: Complete suite of professional labeling tools
- **AI Integration**: Model inference integrated into workflow
- **Web Interface**: Modern browser-based annotation tool
- **Batch Processing**: Automated initial labeling capability
- **Cross-Platform**: Tools work on macOS, Linux, Windows

### Dependencies Added:
- `ultralytics` for YOLO model inference
- `torch` for model loading and processing
- `tqdm` for progress bars in batch processing
- React/TypeScript for web frontend
- Flask for API backend
- Tailwind CSS for modern styling