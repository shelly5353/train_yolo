# LABELING TOOLS

## Purpose
Interactive applications for creating, editing, and managing YOLO annotations for training data.

## Available Tools

### 1. label_tool.py - Original Manual Labeler
**Best For:** Ground-up manual labeling without AI assistance

**Features:**
- Tkinter-based GUI
- Mouse-driven bounding box drawing
- Class selection dropdown (0-3)
- Keyboard navigation (Left/Right arrows, Space)
- Delete selected boxes (Delete key)
- Real-time label visualization with color coding
- Saves in YOLO format (normalized coordinates)

**Usage:**
```bash
cd labeling_tools
python label_tool.py
```

**When to Use:**
- Starting from completely unlabeled images
- Need full manual control over every annotation
- Small batch labeling (< 50 images)
- Learning the annotation process

---

### 2. enhanced_label_tool.py - AI-Assisted Labeler
**Best For:** Semi-automated labeling with manual correction

**Features:**
- Full-screen canvas with scrollbars
- AI model integration (auto-detection)
- Adjustable confidence threshold
- Press 'R' to run model detection
- Manual editing of AI-generated labels
- Smart workflow: AI suggests, human corrects

**Usage:**
```bash
cd labeling_tools
python enhanced_label_tool.py
```

**When to Use:**
- Model already trained and somewhat accurate
- Large batch labeling (100+ images)
- Want to speed up annotation process
- Correcting or refining existing labels

**Workflow:**
1. Load image
2. Press 'R' to run AI detection
3. Review AI-generated boxes
4. Add/delete/modify as needed
5. Save and move to next image

---

### 3. simple_edit_tool.py - Quick Label Editor
**Best For:** Reviewing and fixing pre-labeled data

**Features:**
- Minimal interface focused on editing
- Works on already-labeled images
- Statistics tracking (processed count)
- Fast navigation
- Quick corrections

**Usage:**
```bash
cd labeling_tools
python simple_edit_tool.py
```

**When to Use:**
- Data already has labels (from batch_detect.py)
- Quick review and correction needed
- Quality control pass on dataset
- Final cleanup before training

---

### 4. batch_detect.py - Automated Batch Processor
**Best For:** Mass auto-labeling of large datasets

**Features:**
- Processes entire folders at once
- No GUI - runs in terminal
- Progress bars (tqdm)
- Configurable confidence threshold
- Statistics summary
- Fast processing (seconds per image)

**Usage:**
```bash
cd labeling_tools
python batch_detect.py --confidence 0.3
```

**Arguments:**
- `--data_dir`: Input directory (default: ../data/unlabeled)
- `--output_dir`: Output directory (default: ../data/labeled)
- `--model`: Model path (default: ../models/best_v2_updated_classes.pt)
- `--confidence`: Confidence threshold 0-1 (default: 0.25)

**When to Use:**
- Hundreds of images to label
- Model is reasonably accurate (>70%)
- Initial labeling pass before manual review
- Automated pipeline processing

**Workflow:**
1. Run batch_detect.py on unlabeled images
2. Use simple_edit_tool.py to review results
3. Use enhanced_label_tool.py for corrections

---

### 5. annotation_tool/ - Modern Web Interface
**Best For:** Professional annotation with advanced features

**Features:**
- React + Flask web application
- Modern browser-based UI
- Trackpad gestures (pinch-to-zoom, pan)
- 60fps smooth interactions
- Color-coded class visualization
- Real-time statistics
- Extensive keyboard shortcuts
- Professional user experience

**Usage:**
```bash
cd labeling_tools/annotation_tool
./start.sh
```

**Access:** Opens browser to `http://localhost:3000`

**Keyboard Shortcuts:**
- `N` - Next image
- `V` - Toggle label visibility
- `H` - Toggle help
- `1-4` - Select class (straight, L-shape, U-shape, complex)
- `Cmd+S` - Save annotations
- `Delete` - Remove selected box

**When to Use:**
- Want modern, professional interface
- Working on large monitor
- Need zoom/pan for detailed work
- Prefer web-based tools
- Collaborating with team

**Note:** Requires `npm install` in frontend folder on first use

---

## Recommended Workflows

### Workflow 1: Starting from Scratch
1. **Manual labeling** with `label_tool.py` on 50-100 images
2. **Train initial model** with those labels
3. **Batch process** remaining images with `batch_detect.py`
4. **Review/correct** with `simple_edit_tool.py` or `enhanced_label_tool.py`

### Workflow 2: Model Already Trained
1. **Batch process** all images with `batch_detect.py --confidence 0.3`
2. **Quick review** with `simple_edit_tool.py`
3. **Detailed corrections** with `annotation_tool/` web interface

### Workflow 3: Small Dataset (<100 images)
1. **Web interface** (`annotation_tool/`) for all labeling
2. Clean, professional workflow from start to finish

### Workflow 4: Continuous Improvement
1. **New images** → `batch_detect.py` for initial labels
2. **Quality check** → `simple_edit_tool.py` for quick fixes
3. **Edge cases** → `enhanced_label_tool.py` for detailed work
4. **Retrain model** → Repeat cycle with improved model

## Tool Selection Guide

| Scenario | Best Tool | Reason |
|----------|-----------|--------|
| New unlabeled images | label_tool.py | Full manual control |
| 100+ images, model trained | batch_detect.py | Speed and automation |
| Review AI labels | simple_edit_tool.py | Quick corrections |
| Complex corrections | enhanced_label_tool.py | AI assist + manual |
| Professional workflow | annotation_tool/ | Modern UI, best UX |
| Large documents | annotation_tool/ | Zoom/pan support |

## Technical Notes

- All tools save to YOLO format (normalized coordinates 0-1)
- Coordinate format: `class_id x_center y_center width height`
- Model path: `../models/best_v2_updated_classes.pt`
- Default data paths can be modified in each script
- All tools support the same 4 classes (0-3)

## Dependencies

Python tools require:
- opencv-python
- Pillow
- ultralytics (for AI-assisted tools)
- torch (for model inference)
- tqdm (for batch_detect.py)

Web tool requires:
- Python: flask, flask-cors
- Node.js: react, typescript, tailwindcss

## Troubleshooting

**Issue:** Model not found
**Fix:** Check model path points to `../models/best_v2_updated_classes.pt`

**Issue:** GUI not displaying images
**Fix:** Verify tkinter installed: `python -m tkinter`

**Issue:** Web tool won't start
**Fix:** Run `npm install` in `annotation_tool/frontend/`

**Issue:** Low detection confidence
**Fix:** Adjust `--confidence` threshold in batch_detect.py (try 0.15-0.4)

## Next Steps After Labeling

1. Verify labels are in `../data/labeled/` folder
2. Run `../utilities/dataset_stats.py` to check dataset balance
3. Use `../utilities/create_training_dataset.py` to prepare training package
4. Train/retrain model with updated labels
