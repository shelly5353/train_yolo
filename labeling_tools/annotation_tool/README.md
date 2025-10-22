# YOLO Annotation Tool

A modern, fast, and responsive image annotation tool specifically designed for YOLO object detection training data. Built with React frontend and Flask backend, optimized for macOS with trackpad gesture support.

![YOLO Annotation Tool](https://img.shields.io/badge/YOLO-Annotation_Tool-blue?style=for-the-badge)
![React](https://img.shields.io/badge/React-18.2-61dafb?style=flat-square&logo=react)
![Flask](https://img.shields.io/badge/Flask-2.3-000000?style=flat-square&logo=flask)
![TypeScript](https://img.shields.io/badge/TypeScript-4.9-3178c6?style=flat-square&logo=typescript)

## ✨ Features

### 🎯 **Core Functionality**
- **YOLO Format Support**: Native support for YOLO format labels (class + normalized bounding box)
- **High-Resolution Images**: Optimized for large scanned images with efficient rendering
- **Real-time Statistics**: Live annotation progress and class distribution tracking
- **Batch Operations**: Save annotations, clear all, navigate quickly through datasets

### 🖱️ **Intuitive Interface**
- **Canvas-based Drawing**: Smooth, responsive annotation drawing with pixel-perfect precision
- **Trackpad Gestures**: Native macOS trackpad support with pinch-to-zoom and two-finger pan
- **Keyboard Shortcuts**: Extensive hotkey support for rapid annotation workflow
- **Visual Feedback**: Color-coded classes, selection indicators, and real-time preview

### ⚡ **Performance Optimized**
- **Fast Navigation**: Instant switching between images with preloaded data
- **Memory Efficient**: Smart image loading and canvas rendering for large datasets
- **Responsive UI**: 60fps smooth interactions even with complex annotations
- **Auto-save**: Background saving with progress indicators

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **macOS** (optimized for, but works on other platforms)

### Dataset Structure (NEW - IMPORTANT)

Your dataset folder **must** follow this structure:

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

**Note:** The `labels/` folder can be empty - the tool will offer to auto-generate labels using YOLO if needed.

### Installation & Launch

1. **First time setup (frontend dependencies):**
   ```bash
   cd /path/to/train_yolo/annotation_tool/frontend
   npm install
   cd ..
   ```

2. **Start the application:**
   ```bash
   ./start.sh
   ```

   The script will:
   - Set up Python virtual environment
   - Install all dependencies
   - Start Flask backend on `http://localhost:5002`
   - Start React frontend on `http://localhost:3000`
   - Open your default browser

3. **Select your dataset:**
   - A dataset selection screen will appear
   - Click "Select Dataset Folder"
   - Navigate to your dataset folder
   - If labels are missing, choose to auto-generate or skip

4. **Start annotating:**
   - The tool validates your dataset structure
   - Annotation interface loads automatically
   - All edits save to the `labels/` folder

## 🎮 Usage Guide

### Navigation
- **← →** Arrow keys to navigate between images
- **Mouse/Trackpad** scroll to pan around image
- **Cmd + Scroll** or pinch gesture to zoom in/out

### Annotation Tools
- **N** - New bounding box tool (default)
- **V** - Select/move tool
- **H** - Pan tool for image navigation

### Classes
- **1-4** - Quick select annotation class
  - 1: Straight (red)
  - 2: L-shape (blue)
  - 3: U-shape (green)
  - 4: Complex (orange)

### Actions
- **Cmd+S** - Save current annotations
- **Right Click** - Delete selected annotation
- **Delete/Backspace** - Delete selected annotation
- **Cmd+K** - Clear all annotations on current image
- **Escape** - Deselect current annotation

### Annotation Workflow
1. Select desired class (1-4)
2. Press **N** for bounding box tool
3. Click and drag to create bounding box
4. Right-click to delete incorrect boxes
5. Use **Cmd+S** to save
6. Navigate with **→** to next image

## 📁 Project Structure

```
annotation_tool/
├── backend/                    # Flask API server
│   ├── app.py                 # Main Flask application
│   ├── requirements.txt       # Python dependencies
│   └── venv/                  # Python virtual environment
├── frontend/                  # React web application
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── ImageCanvas.tsx    # Main annotation canvas
│   │   │   └── Sidebar.tsx        # Control panel
│   │   ├── hooks/             # Custom React hooks
│   │   ├── services/          # API communication
│   │   └── types.ts           # TypeScript definitions
│   ├── public/
│   ├── package.json
│   └── tailwind.config.js
├── start.sh                   # Startup script
└── README.md                  # This file
```

## 🔧 Configuration

### Backend Configuration
Edit `backend/app.py` to modify:
- **Model path**: `MODEL_PATH` (default: `models/best.pt`)
- **Classes**: Update `CLASSES` dictionary for your dataset
- **API port**: Default is 5002

### Frontend Configuration
Edit `frontend/src/services/api.ts` to modify:
- **API base URL**: Default is `http://localhost:5002/api`
- **Request timeouts and retry logic**

### Dataset Selection
- Dataset directories are selected via GUI on startup
- No persistent configuration - selection resets when backend restarts
- Backend validates `images/` and `labels/` subfolder structure
- Auto-label generation uses YOLO model at `models/best.pt`

## 📊 Data Format

### Input Images
- **Location**: PNG files in the `images/` subdirectory
- **Naming**: Any filename (e.g., `image001.png`, `sample.png`)
- **Size**: Optimized for large high-resolution images
- **Read-only**: Images are never modified, only read for annotation

### Output Annotations
- **Format**: YOLO format text files
- **Location**: `labels/` subdirectory
- **Filename**: Same as image with `.txt` extension
- **Format**: `class_id x_center y_center width height` (normalized 0-1)

Example dataset structure:
```
my_dataset/
├── images/
│   └── image001.png
└── labels/
    └── image001.txt
```

Example annotation file `image001.txt`:
```
0 0.5 0.3 0.2 0.4
1 0.8 0.7 0.15 0.25
```

## 🛠️ Development

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

### API Endpoints

**Dataset Management (NEW):**
- `GET /api/dataset/status` - Check if dataset is configured
- `POST /api/dataset/select` - Select and validate dataset directory
- `POST /api/dataset/generate-labels` - Auto-generate labels with YOLO

**Image & Annotation Operations:**
- `GET /api/images` - List all images with metadata
- `GET /api/image/{filename}` - Serve image file (with caching)
- `GET /api/annotations/{filename}` - Get annotations for image
- `POST /api/annotations/{filename}` - Save annotations for image

**Metadata:**
- `GET /api/classes` - Get available classes
- `GET /api/stats` - Get annotation statistics
- `GET /api/health` - Health check

## 🎨 Customization

### Adding New Classes
1. Update `CLASSES` dictionary in `backend/app.py`
2. Add corresponding colors in `frontend/src/components/ImageCanvas.tsx`
3. Update keyboard shortcuts in `frontend/src/App.tsx`

### Styling Changes
- Modify `frontend/src/index.css` for global styles
- Update `frontend/tailwind.config.js` for theme colors
- Edit component files for specific UI changes

## 🐛 Troubleshooting

### Common Issues

**Backend won't start:**
- Check Python version: `python3 --version`
- Install dependencies: `cd backend && pip install -r requirements.txt`
- Check port availability: `lsof -i :5000`

**Frontend won't start:**
- Check Node.js version: `node --version`
- Install dependencies: `cd frontend && npm install`
- Clear cache: `npm start -- --reset-cache`

**Images not loading:**
- Verify dataset has `images/` subfolder with PNG files
- Check that dataset was selected via the setup screen
- Check file permissions and formats (PNG only)
- Check browser console for API errors
- Refresh the page and reselect dataset

**Dataset selection not working:**
- Ensure Flask backend has GUI permissions on macOS
- Check terminal for Python/tkinter errors
- Try clicking the button again
- Restart the tool if needed

**Trackpad gestures not working:**
- Ensure using Safari or Chrome on macOS
- Check System Preferences > Trackpad settings
- Try Ctrl+Scroll for zoom if pinch doesn't work

### Performance Issues
- **Large images**: Images are automatically scaled for display
- **Many annotations**: Canvas rendering is optimized for 100+ annotations
- **Memory usage**: Browser may use significant RAM with very large images

## 📝 License

This project is part of the YOLO training pipeline. See the main project license for details.

## 🤝 Contributing

1. Follow the existing code style (TypeScript for frontend, Python with type hints for backend)
2. Test changes with various image sizes and annotation counts
3. Ensure keyboard shortcuts and gestures continue working
4. Update this README for any new features or configuration changes

---

**Made for efficient YOLO dataset annotation** 🎯