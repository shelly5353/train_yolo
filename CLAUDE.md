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
├── CLAUDE.md                        # Project documentation and development notes
├── README.md                        # User-facing project documentation
├── requirements.txt                 # Python dependencies
├── .gitignore                       # Git ignore rules
│
├── data/                           # Training data organized by status
│   ├── unlabeled/                  # Original unlabeled images (310 images)
│   ├── labeled/                    # Images with YOLO annotations (images + .txt files)
│   └── augmented/                  # Augmented dataset (images + labels subfolders)
│
├── models/                         # Trained YOLO model weights
│   ├── best_v2_updated_classes.pt  # Current model with new class names (ACTIVE)
│   ├── best_v2_backup1.pt          # Backup of updated model
│   ├── best_v2_backup2.pt          # Second backup of updated model
│   └── best_v1_original_classes.pt # Original model with old class names
│
├── labeling_tools/                 # Interactive labeling applications
│   ├── label_tool.py               # Basic manual labeling tool (tkinter)
│   ├── enhanced_label_tool.py      # AI-assisted labeling with model integration
│   ├── simple_edit_tool.py         # Quick editor for pre-labeled data
│   ├── batch_detect.py             # Automated batch processing script
│   └── annotation_tool/            # Modern web-based annotation interface
│       ├── backend/                # Flask API server
│       ├── frontend/               # React web application
│       └── start.sh                # Auto-startup script
│
├── utilities/                      # Dataset management and preparation tools
│   ├── create_training_dataset.py  # Prepare datasets for training
│   ├── collect_latest_labels.py    # Gather latest annotations
│   ├── augment_dataset.py          # Data augmentation utility
│   ├── prepare_colab_dataset.py    # Prepare data for Google Colab
│   └── dataset_stats.py            # Dataset statistics and analysis
│
├── training_tools/                 # Model training scripts
│   ├── colab_training_script.py    # Initial training script for Colab
│   └── colab_continue_training.py  # Continue training from checkpoint
│
├── testing_tools/                  # Model testing and validation
│   ├── test_single_image.py        # Test model on single image
│   ├── test_improved_model.py      # Model performance testing
│   ├── test_document.py            # Document-level testing
│   └── test_results/               # Test output and results
│
├── old_tools/                      # Deprecated experimental tools
│   ├── simple_pdf_labeler.py       # Old PDF labeling experiments
│   ├── improved_pdf_labeler.py     # PDF labeling iterations
│   ├── robust_pdf_labeler.py       # PDF labeling attempts
│   ├── fullpage_labeler.py         # Full-page PDF labeler
│   ├── ultra_simple_labeler.py     # Minimal labeler experiment
│   ├── click_delete_labeler.py     # Alternative labeler interface
│   ├── pdf_to_images.py            # PDF conversion utility
│   ├── prepare_pdf_data.py         # PDF data preparation
│   ├── modify_class_names.py       # One-time model class renaming utility
│   ├── verify_model_changes.py     # Model verification script
│   └── navigation_fix.js           # JavaScript fix experiment
│
└── old_datasets/                   # Archived dataset versions
    ├── old_labeld_data/            # Original labeled data folder
    ├── old_final_labeled_dataset/  # Previous final labeled version
    ├── old_labeled_new_dataset/    # Previous new dataset
    ├── old_augmented_dataset/      # Previous augmented data
    ├── old_pdf_labeling_data/      # PDF labeling experiments
    ├── old_pdf_images/             # PDF image extractions
    ├── old_new_dataset/            # Old new dataset version
    ├── old_new_dataset_flat/       # Flattened dataset version
    ├── old_training_dataset_final/ # Previous training dataset
    ├── old_yolo_training_dataset/  # Previous YOLO dataset
    └── old_yolo_training_dataset.zip # Archived YOLO dataset
```

## CORE FUNCTIONALITY

### Active Model
- **Current Model:** `models/best_v2_updated_classes.pt` (with updated class names)
- **Previous Model:** `models/best_v1_original_classes.pt` (original class names)
- **Classes:** 4 shape categories (straight, L-shape, U-shape, complex)
- **Output Format:** YOLO txt format with normalized bounding boxes

### Training Data
- **Unlabeled Images:** 310 images in `data/unlabeled/`
- **Labeled Data:** Images with annotations in `data/labeled/`
- **Augmented Data:** Enhanced dataset in `data/augmented/`

### Dependencies
- opencv-python>=4.0.0 (image processing)
- Pillow>=8.0.0 (image handling)
- torch>=1.7.0 (PyTorch for YOLO)
- ultralytics>=8.0.0 (YOLO implementation)

## DEVELOPMENT NOTES

### Recent Changes (Latest Update):
- **Enhanced YOLO Labeling Tool**: Added AI-assisted labeling with auto-detection
- **Simple Edit Tool**: Quick editor for pre-generated labels
- **Batch Detection Script**: Automated processing of entire datasets
- **Modern Web Annotation Tool**: Full React/Flask web application with trackpad support
- **Complete Tool Suite**: Four different tools for various labeling workflows

### Tool Suite Overview:

#### 1. **Original Label Tool** (`labeling_tools/label_tool.py`)
- Basic manual labeling with tkinter GUI
- Mouse-based bounding box drawing
- Class selection and keyboard shortcuts
- Original tool for ground-up labeling

#### 2. **Enhanced Label Tool** (`labeling_tools/enhanced_label_tool.py`)
- **AI-Assisted Labeling**: Runs trained model first, then allows manual editing
- **Confidence Threshold Control**: Adjustable detection sensitivity
- **Full-screen Canvas**: Original image size with scrollbars
- **Smart Workflow**: Model detection + manual correction
- **Keyboard Shortcuts**: Press 'R' to run model detection

#### 3. **Simple Edit Tool** (`labeling_tools/simple_edit_tool.py`)
- **Pre-label Editor**: Works on already labeled data
- **Fast Review**: Quickly review and correct batch-generated labels
- **Statistics Tracking**: Shows processed count and label statistics
- **Minimal Interface**: Focused on editing, not initial labeling

#### 4. **Batch Detection Script** (`labeling_tools/batch_detect.py`)
- **Automated Processing**: Runs model on all images at once
- **Progress Tracking**: tqdm progress bars and statistics
- **Confidence Control**: Command-line confidence threshold
- **Mass Production**: Processes hundreds of images quickly
- Usage: `cd labeling_tools && python batch_detect.py --confidence 0.3`

#### 5. **Modern Web Annotation Tool** (`labeling_tools/annotation_tool/`)
- **React + Flask Architecture**: Modern web-based interface
- **Trackpad Gestures**: Native macOS pinch-to-zoom and pan
- **High Performance**: 60fps smooth interactions
- **Professional UI**: Color-coded classes, real-time statistics
- **Keyboard Shortcuts**: Extensive hotkey support (N, V, H, 1-4, Cmd+S)
- **Auto-startup**: Single `./start.sh` command launches everything

### Recommended Workflow:
1. **Batch Detection**: `cd labeling_tools && python batch_detect.py` for initial AI labeling
2. **Web Tool Review**: `cd labeling_tools/annotation_tool && ./start.sh` for professional editing
3. **Simple Editor**: `cd labeling_tools && python simple_edit_tool.py` for quick corrections
4. **Enhanced Tool**: `cd labeling_tools && python enhanced_label_tool.py` for AI-assisted refinement

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

---

## PROJECT REORGANIZATION (October 2, 2025)

### Major Structure Update:
The project has been completely reorganized for better clarity and maintainability:

1. **New Folder Structure:**
   - `data/` - Centralized data storage with unlabeled/labeled/augmented subfolders
   - `models/` - All model weights with clear version naming
   - `labeling_tools/` - All active labeling applications
   - `utilities/` - Dataset management and preparation scripts
   - `training_tools/` - Model training scripts
   - `testing_tools/` - Model testing and validation
   - `old_tools/` - Deprecated experimental tools
   - `old_datasets/` - Archived dataset versions

2. **Model Naming Convention:**
   - `best_v2_updated_classes.pt` - Current active model (NEW CLASS NAMES)
   - `best_v1_original_classes.pt` - Original model (old class names)
   - `best_v2_backup1.pt` & `best_v2_backup2.pt` - Backups of current model

3. **Dataset Organization:**
   - Active data consolidated in `data/` with clear status (unlabeled/labeled/augmented)
   - All old/experimental datasets moved to `old_datasets/` with 'old_' prefix
   - Eliminates confusion about which dataset is current

4. **Tool Categorization:**
   - Active labeling tools in `labeling_tools/`
   - Dataset utilities in `utilities/`
   - PDF-related experimental tools archived in `old_tools/`
   - Training and testing tools in dedicated folders

5. **Benefits:**
   - Clear separation between active and deprecated files
   - Easy to find current model and datasets
   - Reduced root directory clutter
   - Better understanding of project evolution
   - Easier onboarding for new developers