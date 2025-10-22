# WEB ANNOTATION TOOL - CLAUDE.MD

## Purpose
Modern, professional web-based annotation tool for YOLO object detection. Built with React + Flask for a smooth, responsive annotation experience.

## Architecture

### Technology Stack
- **Frontend:** React 18 + TypeScript + Tailwind CSS
- **Backend:** Flask (Python) REST API
- **Communication:** JSON REST API on localhost:5002
- **Startup:** Single `./start.sh` script manages both services

### Key Components

**Backend (Flask):**
- `app.py` - Main Flask application
  - Dataset selection and validation API endpoints
  - Image serving with optimized caching
  - Annotation CRUD operations
  - YOLO format conversion
  - Auto-label generation using YOLO model

**Frontend (React):**
- `App.tsx` - Main application container
- `DatasetSetup.tsx` - Dataset selection screen (NEW)
- `ImageCanvas.tsx` - Annotation canvas with drawing tools
- `Sidebar.tsx` - Control panel and navigation
- `api.ts` - API service layer

## NEW: Directory Selection & Structure

### Required Dataset Structure

**IMPORTANT:** The web tool now requires datasets to follow this structure:

```
your_dataset_folder/
├── images/
│   ├── image001.png
│   ├── image002.png
│   └── ...
└── labels/
    ├── image001.txt  (YOLO format)
    ├── image002.txt
    └── ...
```

### Workflow

1. **Start the tool:**
   ```bash
   cd labeling_tools/annotation_tool
   ./start.sh
   ```

2. **Open browser:** http://localhost:3000

3. **Dataset Selection Screen appears:**
   - Shows required folder structure
   - "Select Dataset Folder" button opens macOS file picker
   - User selects dataset folder
   - Tool validates `images/` and `labels/` subfolders exist

4. **Auto-Label Generation (if needed):**
   - If `labels/` folder is empty or has missing labels
   - Tool offers to auto-generate labels using YOLO model
   - User can choose "Auto-Generate" or "Skip (Manual)"

5. **Annotation Interface loads:**
   - All images from `images/` folder displayed
   - Labels loaded from `labels/` folder
   - All edits save back to `labels/` folder
   - Images in `images/` folder remain read-only

## API Endpoints

### Dataset Management (NEW)
- `GET /api/dataset/status` - Check if dataset is configured
- `POST /api/dataset/select` - Select and validate dataset directory
- `POST /api/dataset/generate-labels` - Auto-generate labels with YOLO

### Image & Annotation Operations
- `GET /api/images` - List all images with metadata
- `GET /api/image/<filename>` - Serve image file (with caching)
- `GET /api/annotations/<filename>` - Get annotations for image
- `POST /api/annotations/<filename>` - Save annotations for image

### Metadata
- `GET /api/classes` - Get available classes
- `GET /api/stats` - Get annotation statistics
- `GET /api/health` - Health check

## Features

### User Interface
- **Dataset Setup Screen:** Beautiful onboarding with clear instructions
- **Canvas Drawing:** Smooth, responsive bounding box creation
- **Trackpad Gestures:** Pinch-to-zoom, two-finger pan
- **Keyboard Shortcuts:** Extensive hotkey support for rapid workflow
- **Visual Feedback:** Color-coded classes, selection indicators
- **Real-time Stats:** Live progress tracking and class distribution

### Performance
- **Fast Navigation:** Instant image switching with preloaded data
- **Memory Efficient:** Smart caching for large datasets
- **60fps Interactions:** Smooth even with many annotations
- **Auto-save:** Background saving with progress indicators
- **ETag Caching:** Optimized image serving

### Keyboard Shortcuts
- `← →` - Navigate images
- `N` - New bounding box tool
- `V` - Select/move tool
- `H` - Pan tool
- `1-4` - Select class (straight, L-shape, U-shape, complex)
- `Cmd+S` - Save annotations
- `Delete/Backspace` - Delete selected annotation
- `Cmd+K` - Clear all annotations
- `Escape` - Deselect

## Technical Details

### YOLO Format Handling
- **Storage:** Normalized coordinates (0-1) relative to image dimensions
- **Format:** `class_id x_center y_center width height`
- **Conversion:** Automatic conversion between pixel coords (UI) and normalized coords (storage)

### Caching Strategy
- **ETag Generation:** Based on file path, size, modification time
- **HTTP Caching:** `Cache-Control: private, max-age=3600`
- **304 Not Modified:** Reduces bandwidth for unchanged images
- **CORS Headers:** Full support for cross-origin requests

### State Management
- **Global Backend State:** Dataset directories stored in Flask app globals
- **Frontend State:** React hooks for UI state and data
- **Persistence:** Labels saved to disk immediately on annotation changes
- **No localStorage:** All data on server (Claude.ai compatible)

## Setup & Installation

### First Time Setup
```bash
cd labeling_tools/annotation_tool

# Backend dependencies installed automatically by start.sh
# Frontend dependencies need npm install once:
cd frontend
npm install
cd ..
```

### Launch
```bash
./start.sh
```

This script:
1. Sets up Python virtual environment
2. Installs/updates Python dependencies
3. Starts Flask backend on port 5002
4. Starts React frontend on port 3000
5. Opens browser to http://localhost:3000

### Stop
Press `Ctrl+C` in the terminal where start.sh is running

## Configuration

### Backend Configuration (`backend/app.py`)
- **Model Path:** `models/best.pt` (auto-detected from project root)
- **Classes:** 4 shape classes (straight, L-shape, U-shape, complex)
- **API Port:** 5002 (can be changed in app.py)

### Frontend Configuration (`frontend/src/services/api.ts`)
- **API Base URL:** `http://localhost:5002/api`
- **Timeouts:** Browser default
- **Retry Logic:** Not implemented (relies on browser fetch)

## Development

### Backend Development
```bash
cd backend
source venv/bin/activate
python app.py
```

### Frontend Development
```bash
cd frontend
npm start
```

### Hot Reload
- **Backend:** Flask auto-reloads on file changes (debug mode)
- **Frontend:** React dev server hot-reloads on save

### Debugging
- **Backend:** Flask debugger available in terminal
- **Frontend:** React DevTools, browser console
- **API Calls:** Network tab in browser DevTools

## Troubleshooting

### Issue: "Dataset not configured" error
**Fix:** The web tool must start fresh each time. Select your dataset using the GUI when prompted.

### Issue: Flask dialog not appearing
**Fix:** Ensure Flask backend is running and accessible. Check terminal for errors. macOS might need permissions for Python to show dialogs.

### Issue: Images not loading
**Fix:**
- Verify dataset structure has `images/` subfolder with PNG files
- Check browser console for 404 errors
- Ensure Flask backend is serving on port 5002

### Issue: Labels not saving
**Fix:**
- Check `labels/` folder exists and is writable
- View terminal for Flask errors
- Verify no permission issues on labels directory

### Issue: Trackpad gestures not working
**Fix:**
- Use Safari or Chrome on macOS
- Check System Preferences > Trackpad settings
- Try Cmd+Scroll for zoom if pinch doesn't work

### Issue: Port already in use
**Fix:**
```bash
lsof -ti:5002,3000 | xargs kill -9
```

## Comparison with Desktop Tools

### Web Tool Advantages
- **Modern UI:** Professional, polished interface
- **Trackpad Gestures:** Smooth zoom/pan
- **Best Performance:** 60fps canvas rendering
- **Team Collaboration:** Easy to share (just a URL)

### Desktop Tools Advantages
- **Simpler Setup:** Just `python tool.py`
- **No Browser Required:** Native tkinter GUI
- **Faster Startup:** No npm dependencies

### When to Use Web Tool
- Professional annotation projects
- Large monitors with high-resolution images
- Need zoom/pan for detailed work
- Prefer modern web-based interfaces
- Want best possible user experience

### When to Use Desktop Tools
- Quick one-off labeling tasks
- Prefer simpler Python-only setup
- Don't need advanced zoom/pan features
- Working on remote server without browser

## Data Flow

```
User → Dataset Setup Screen → Select Folder (macOS Dialog)
     ↓
Backend validates structure (images/ + labels/)
     ↓
Auto-generate labels? (if needed)
     ↓
Annotation Interface loads
     ↓
User annotates → Labels save to labels/ folder
     ↓
Stats update in real-time
```

## Important Notes

- **Images are read-only:** Originals in `images/` folder never modified
- **Labels are editable:** All edits save to `labels/` folder
- **No persistent config:** Dataset selection resets when backend restarts
- **macOS optimized:** Designed for macOS trackpad, works on other platforms
- **PNG only:** Currently supports PNG images (can be extended)

## Future Enhancements

Potential improvements (not yet implemented):
- Persistent dataset selection (remember last used)
- Support for other image formats (JPG, JPEG)
- Batch operations (delete multiple, change class)
- Annotation export (JSON, COCO format)
- Multi-user support with annotation locking
- Undo/redo functionality
- Copy/paste annotations between images

## Contributing

When modifying this tool:
1. Update both frontend and backend if adding features
2. Test with all 3 dataset scenarios (labeled, unlabeled, invalid)
3. Ensure keyboard shortcuts still work
4. Check mobile/tablet compatibility if relevant
5. Update this CLAUDE.md with changes

## Dependencies

### Backend (Python)
- flask
- flask-cors
- opencv-python
- Pillow
- ultralytics (YOLO)
- torch

### Frontend (Node.js)
- react (18.2)
- typescript (4.9)
- tailwindcss
- lucide-react (icons)
- react-scripts (Create React App)

---

**Built for efficient YOLO dataset annotation** 🎯
