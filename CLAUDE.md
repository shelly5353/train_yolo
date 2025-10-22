# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**YOLO Object Detection Training Pipeline** - Complete end-to-end system for labeling images, training models, and detecting 4 shape classes: straight, L-shape, U-shape, and complex.

**Active Model:** `models/best.pt` (21MB, YOLOv8, Sept 28 2025)

## Architecture Overview

### Multi-Stage Pipeline

```
unlabeled images → labeling tools → labeled dataset → utilities → training → testing → deployment
```

**Key Architectural Decision:** Tools are separated by function (labeling/utilities/training/testing) rather than by technology. This allows mixing GUI tools (tkinter), web apps (React/Flask), and CLI scripts within their functional categories.

### Data Flow

1. **Input:** Raw images in `data/unlabeled/` (310 images)
2. **Annotation:** Multiple tool options produce YOLO format (class_id x_center y_center width height, normalized 0-1)
3. **Processing:** Utilities augment and package data
4. **Training:** Google Colab scripts (local training possible but slower)
5. **Testing:** Validation suite before deployment
6. **Output:** Trained .pt model file

### Model Integration Pattern

All labeling tools can load `models/best.pt` for AI-assisted annotation. The model is a standard Ultralytics YOLOv8 checkpoint that includes:
- Model architecture and weights
- Class names metadata (4 classes)
- Training configuration

**Critical:** When modifying tools, always check if they reference model paths. Default is `best.pt` or `../models/best.pt` from tool directories.

### Web Annotation Tool Architecture

The `labeling_tools/annotation_tool/` uses a React/Flask split:
- **Backend (Flask):** File I/O, YOLO format parsing, model inference API
- **Frontend (React):** Canvas rendering, trackpad gestures, keyboard shortcuts
- **Communication:** REST API on localhost:5002
- **Startup:** Single `./start.sh` script manages both services

## Path Configuration System

**NEW:** All tools now support flexible directory selection without hardcoded paths.

### Configuration Manager

The `utilities/config_manager.py` module provides centralized path management:
- **Persistent Storage:** Last-used directories saved in `config.json`
- **GUI Dialogs:** File browser for easy directory selection
- **CLI Support:** Optional command-line arguments
- **Recent Directories:** Quick access to frequently-used paths

### Using Tools with Path Configuration

**Option 1: GUI Selection (Default)**
```bash
# Tools will prompt for directory if not specified
python labeling_tools/simple_edit_tool.py
# Opens file browser dialog to select directory
```

**Option 2: Command Line Arguments**
```bash
# Specify directory directly
python labeling_tools/simple_edit_tool.py --dir /path/to/labeled/images
```

**Option 3: Remembered Paths**
```bash
# Tools remember last used directory
# First time: prompts for selection
# Next time: asks if you want to use the same directory
```

### Configuration File

`config.json` (auto-created on first run):
```json
{
  "paths": {
    "last_data_dir": "/Users/username/Documents/Work/data/unlabeled",
    "last_labels_dir": "/Users/username/Documents/Work/data/labeled",
    "last_output_dir": "/Users/username/Documents/Work/data/labeled",
    "model_path": "models/best.pt"
  },
  "recent_directories": [
    "/Users/username/Documents/Work/data/unlabeled",
    "/Users/username/Documents/Work/data/labeled"
  ],
  "preferences": {
    "remember_last_directory": true,
    "show_directory_dialog": false,
    "max_recent_directories": 10
  }
}
```

**Note:** `config.json` is user-specific and excluded from git (in `.gitignore`).

### Preferences

- `remember_last_directory`: Auto-use last directory (default: true)
- `show_directory_dialog`: Always show directory picker (default: false)
- `max_recent_directories`: Number of recent dirs to remember (default: 10)

## Common Commands

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Setup web annotation tool (first time only)
cd labeling_tools/annotation_tool/frontend
npm install
cd ../../..
```

### Labeling Workflows

```bash
# Quick batch labeling with AI model
cd labeling_tools
python batch_detect.py --confidence 0.3

# Review/edit labels with web interface
cd labeling_tools/annotation_tool
./start.sh
# Opens http://localhost:3000

# Manual labeling (no AI)
cd labeling_tools
python label_tool.py

# AI-assisted labeling (hybrid)
cd labeling_tools
python enhanced_label_tool.py
```

### Dataset Preparation

```bash
# Check dataset statistics
cd utilities
python dataset_stats.py

# Augment dataset (4x expansion)
cd utilities
python augment_dataset.py

# Create training package
cd utilities
python create_training_dataset.py
# Output: training_dataset/ with train/val split

# Prepare for Google Colab
cd utilities
python prepare_colab_dataset.py
```

### Model Training

Training is designed for Google Colab (free GPU access):

```bash
# On Colab: Initial training
!python colab_training_script.py

# On Colab: Continue/fine-tune existing model
!python colab_continue_training.py
```

### Testing

```bash
# Quick single image test
cd testing_tools
python test_single_image.py

# Full validation suite
cd testing_tools
python test_improved_model.py
# Output: test_results/ with metrics and confusion matrix
```

## Git Workflow

**Critical:** Always work on `dev` branch, never commit directly to `main`.

```bash
# Ensure on dev branch
git checkout dev

# After changes
git add -A
git commit -m "Description"

# Before syncing to GitHub, ask user permission
gh repo sync --source dev
```

When renaming or moving functions:
1. **Always rename old implementations** with `_old` suffix or similar
2. **Move deprecated code** to `old_tools/` folder
3. **Update all references** before removing old code
4. **Test** that nothing breaks after moves

## Project Organization Principles

### Active vs Archived

- **Active work:** `data/`, `models/`, `labeling_tools/`, `utilities/`, `training_tools/`, `testing_tools/`
- **Archive:** `old_tools/`, `old_datasets/` - kept for reference but not maintained

### Folder-Level Documentation

Each major folder has its own `CLAUDE.md` with specific details:
- `data/CLAUDE.md` - YOLO format explanation, data workflow
- `models/CLAUDE.md` - Model versions, usage examples
- `labeling_tools/CLAUDE.md` - All 5 tools documented with selection guide
- `utilities/CLAUDE.md` - Each utility script's purpose and usage
- `training_tools/CLAUDE.md` - Colab setup, hyperparameters
- `testing_tools/CLAUDE.md` - Testing procedures, metrics interpretation

**Read these folder-level docs** before modifying code in those folders.

## Model Management

**Current Model:** `models/best.pt` (Sept 28, 2025)

When updating model:
1. Backup current model with date: `best_YYYY-MM-DD.pt`
2. Test new model thoroughly
3. Update `models/CLAUDE.md` with changes
4. Only replace if performance improves
5. Keep single active model named `best.pt` for simplicity

## Key Technical Details

### YOLO Label Format
```
class_id x_center y_center width height
```
All coordinates normalized 0.0-1.0 relative to image dimensions.

### Classes
```python
{
    0: 'straight',
    1: 'L-shape',
    2: 'U-shape',
    3: 'complex'
}
```

### File Naming Convention
- Images: `filename.png`
- Labels: `filename.txt` (same basename, different extension)
- Both must exist in same directory for training

### Web Tool Ports
- Backend API: `http://localhost:5002`
- Frontend App: `http://localhost:3000`

## Troubleshooting Quick Reference

**Model not found:** Check path references to `models/best.pt`

**Import errors:** Ensure working directory matches script expectations (most scripts assume run from their folder)

**Web tool won't start:**
```bash
cd labeling_tools/annotation_tool/frontend
npm install  # Install dependencies
cd ..
./start.sh
```

**Low detection confidence:** Adjust `--confidence` threshold (try 0.15-0.4 range)

## Development Notes

### Recent Major Changes (October 2025)

1. **Project Reorganization:** Consolidated scattered files into functional folders
2. **Model Naming:** Clear v1/v2 naming with backup strategy
3. **Dataset Consolidation:** Single `data/` folder with status subfolders
4. **Documentation:** Comprehensive CLAUDE.md in each major folder

### Tool Evolution

The project evolved from PDF processing (abandoned) to direct image labeling. Old PDF-related tools in `old_tools/` are not maintained. Current workflow uses direct image input only.

### Preferred Tools by Use Case

- **Small batch (<50 images):** `label_tool.py` or web tool
- **Large batch (>100 images):** `batch_detect.py` → review with `simple_edit_tool.py`
- **Professional workflow:** Web annotation tool (`./annotation_tool/start.sh`)
- **AI-assisted:** `enhanced_label_tool.py`

## Dependencies Management

Root `requirements.txt` covers Python dependencies for all tools except web annotation:
- Core: `opencv-python`, `Pillow`, `torch`, `ultralytics`
- Utilities: `tqdm`, `PyMuPDF`
- Web backend: `Flask`, `Flask-CORS`

Web frontend has separate `package.json` in `labeling_tools/annotation_tool/frontend/`.

## Important Reminders

- **Always work on dev branch** (not main)
- **Read folder-specific CLAUDE.md** before modifying code
- **Backup models before replacing** with new versions
- **Use absolute paths** or ensure correct working directory
- **Test after moving/renaming** functions
- **When deprecating, mark as old** and move to `old_tools/`
- **Ask user before** syncing to GitHub
- **Check model path references** when moving files
