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

### Installation & Launch

1. **Clone or navigate to the annotation tool directory:**
   ```bash
   cd /path/to/train_yolo/annotation_tool
   ```

2. **Start the application:**
   ```bash
   ./start.sh
   ```

   The script will:
   - Set up Python virtual environment
   - Install all dependencies
   - Start Flask backend on `http://localhost:5000`
   - Start React frontend on `http://localhost:3000`
   - Open your default browser

3. **Access the tool:**
   - **Web Interface**: http://localhost:3000
   - **API Endpoints**: http://localhost:5000/api

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
- **Data directories**: `DATA_DIR` and `LABELED_DATA_DIR` paths
- **Classes**: Update `CLASSES` dictionary for your dataset
- **API port**: Default is 5000

### Frontend Configuration
Edit `frontend/src/services/api.ts` to modify:
- **API base URL**: Default is `http://localhost:5000/api`
- **Request timeouts and retry logic**

## 📊 Data Format

### Input Images
- **Format**: PNG files in the `data/` directory
- **Naming**: Any filename (e.g., `image001.png`, `sample.png`)
- **Size**: Optimized for large high-resolution images

### Output Annotations
- **Format**: YOLO format text files
- **Location**: `labeld_data/` directory
- **Filename**: Same as image with `.txt` extension
- **Format**: `class_id x_center y_center width height` (normalized 0-1)

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
- `GET /api/images` - List all images with metadata
- `GET /api/annotations/{filename}` - Get annotations for image
- `POST /api/annotations/{filename}` - Save annotations for image
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
- Verify images are in `../../data/` directory relative to backend
- Check file permissions and formats (PNG only)
- Check browser console for API errors

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