#!/usr/bin/env python3
"""
Flask Backend for Modern Image Annotation Tool
Handles image serving, annotation CRUD operations, and YOLO format conversion
"""

import os
import json
from pathlib import Path
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import cv2
import numpy as np
from PIL import Image
from typing import Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration - Now dynamic, set via API
DATA_DIR: Optional[Path] = None
LABELED_DATA_DIR: Optional[Path] = None
IMAGES_DIR: Optional[Path] = None
LABELS_DIR: Optional[Path] = None

CLASSES = {
    0: 'straight',
    1: 'L-shape',
    2: 'U-shape',
    3: 'complex'
}

def ensure_directories():
    """Ensure required directories exist"""
    if DATA_DIR:
        DATA_DIR.mkdir(exist_ok=True)
    if LABELED_DATA_DIR:
        LABELED_DATA_DIR.mkdir(exist_ok=True)
    if LABELS_DIR and not LABELS_DIR.exists():
        LABELS_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created labels directory: {LABELS_DIR}")

def generate_missing_labels(images_dir: Path, labels_dir: Path, model_path: str = "../../models/best.pt", confidence: float = 0.25) -> Tuple[int, int]:
    """
    Run YOLO on images without labels

    Returns:
        Tuple of (generated_count, error_count)
    """
    try:
        # Import YOLO only when needed
        from ultralytics import YOLO

        # Get absolute model path
        model_abs_path = Path(__file__).parent / model_path
        if not model_abs_path.exists():
            logger.error(f"Model not found at {model_abs_path}")
            return 0, 0

        # Load model
        logger.info(f"Loading YOLO model from {model_abs_path}")
        model = YOLO(str(model_abs_path))

        # Ensure labels directory exists
        labels_dir.mkdir(parents=True, exist_ok=True)

        # Get all PNG files
        image_files = list(images_dir.glob("*.png"))
        generated_count = 0
        error_count = 0

        for img_path in image_files:
            label_path = labels_dir / f"{img_path.stem}.txt"

            # Skip if label already exists
            if label_path.exists():
                continue

            try:
                # Run inference
                results = model(str(img_path), conf=confidence, verbose=False)

                if results and len(results) > 0:
                    result = results[0]

                    if result.boxes and len(result.boxes) > 0:
                        # Get image dimensions
                        img_height, img_width = result.orig_shape

                        # Write YOLO format labels
                        with open(label_path, 'w') as f:
                            for box in result.boxes:
                                cls = int(box.cls[0])
                                # Convert xyxy to xywh normalized
                                x1, y1, x2, y2 = box.xyxy[0].tolist()
                                x_center = ((x1 + x2) / 2) / img_width
                                y_center = ((y1 + y2) / 2) / img_height
                                width = (x2 - x1) / img_width
                                height = (y2 - y1) / img_height

                                f.write(f"{cls} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")

                        generated_count += 1
                        logger.info(f"Generated labels for {img_path.name}")
                    else:
                        # Create empty label file for images with no detections
                        label_path.touch()
                        logger.info(f"No detections for {img_path.name}, created empty label file")

            except Exception as e:
                logger.error(f"Error processing {img_path.name}: {e}")
                error_count += 1

        logger.info(f"Label generation complete: {generated_count} generated, {error_count} errors")
        return generated_count, error_count

    except ImportError:
        logger.error("ultralytics package not installed. Please install with: pip install ultralytics")
        return 0, 0
    except Exception as e:
        logger.error(f"Error in generate_missing_labels: {e}")
        return 0, 0

@app.route('/api/browse-directories', methods=['GET'])
def browse_directories():
    """
    Return list of common directories and recent datasets
    """
    try:
        home = Path.home()

        # Common paths to check
        common_paths = [
            home / "Desktop",
            home / "Documents",
            home / "Documents" / "Work",
            home / "Documents" / "Work" / "data",
            home / "Documents" / "Work" / "train_yolo",
            Path("/Users/shellysmac/Documents/Work/data"),  # Add specific known path
        ]

        available_dirs = []

        for base_path in common_paths:
            if not base_path.exists():
                continue

            try:
                # Check subdirectories for valid datasets
                for item in base_path.iterdir():
                    if item.is_dir():
                        # Check if it's a valid dataset directory
                        images_dir = item / "images"
                        if images_dir.exists():
                            png_count = len(list(images_dir.glob("*.png")))
                            pdf_count = len(list(images_dir.glob("*.pdf")))
                            jpg_count = len(list(images_dir.glob("*.jpg"))) + len(list(images_dir.glob("*.jpeg")))
                            total_images = png_count + pdf_count + jpg_count

                            if total_images > 0:
                                labels_dir = item / "labels"
                                txt_count = len(list(labels_dir.glob("*.txt"))) if labels_dir.exists() else 0

                                available_dirs.append({
                                    'path': str(item),
                                    'name': item.name,
                                    'parent': str(base_path),
                                    'images_count': total_images,
                                    'labels_count': txt_count,
                                    'has_labels': txt_count > 0,
                                    'file_types': f"PNG:{png_count} PDF:{pdf_count} JPG:{jpg_count}" if (pdf_count > 0 or jpg_count > 0) else None
                                })
            except PermissionError:
                continue

        # Sort by path
        available_dirs.sort(key=lambda x: x['path'])

        return jsonify({
            'directories': available_dirs,
            'home': str(home)
        })

    except Exception as e:
        logger.error(f"Error browsing directories: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/set-directory', methods=['POST'])
def set_directory():
    """
    Set working directory for images and labels
    Request body: {"directory": "/absolute/path/to/dataset"}
    """
    global DATA_DIR, LABELED_DATA_DIR, IMAGES_DIR, LABELS_DIR

    try:
        data = request.get_json()
        logger.info(f"Received set-directory request: {data}")  # Debug logging

        directory = data.get('directory')

        if not directory:
            logger.error("No directory path provided")
            return jsonify({'error': 'Directory path is required'}), 400

        # Convert to Path object
        base_dir = Path(directory)
        logger.info(f"Checking directory: {base_dir}")

        # Validate directory exists
        if not base_dir.exists():
            logger.error(f"Directory not found: {directory}")
            return jsonify({'error': f'Directory not found: {directory}'}), 400

        if not base_dir.is_dir():
            logger.error(f"Path is not a directory: {directory}")
            return jsonify({'error': f'Path is not a directory: {directory}'}), 400

        # Check for images/ subfolder
        images_dir = base_dir / "images"
        if not images_dir.exists():
            logger.error(f"Missing images/ subfolder in {directory}")
            return jsonify({'error': "Missing 'images/' subfolder in the selected directory"}), 400

        # Check for image files (PNG or PDF)
        png_files = list(images_dir.glob("*.png"))
        pdf_files = list(images_dir.glob("*.pdf"))
        jpg_files = list(images_dir.glob("*.jpg"))
        jpeg_files = list(images_dir.glob("*.jpeg"))

        all_image_files = png_files + pdf_files + jpg_files + jpeg_files

        if not all_image_files:
            logger.error(f"No image files (PNG/PDF/JPG) found in {images_dir}")
            return jsonify({'error': "No image files (PNG/PDF/JPG) found in images/ subfolder"}), 400

        # Log what type of files we found
        logger.info(f"Found {len(png_files)} PNG, {len(pdf_files)} PDF, {len(jpg_files + jpeg_files)} JPG files")

        # Create labels/ folder if it doesn't exist
        labels_dir = base_dir / "labels"
        if not labels_dir.exists():
            labels_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created labels directory: {labels_dir}")

        # Count existing labels
        existing_labels = len(list(labels_dir.glob("*.txt")))

        # Set global directory variables
        DATA_DIR = images_dir  # For backward compatibility
        LABELED_DATA_DIR = base_dir  # For backward compatibility
        IMAGES_DIR = images_dir
        LABELS_DIR = labels_dir

        # Auto-generate missing labels if requested
        auto_generate = data.get('auto_generate', True)
        generated_count = 0
        error_count = 0

        if auto_generate:
            logger.info("Auto-generating missing labels...")
            generated_count, error_count = generate_missing_labels(images_dir, labels_dir)

        # Return success with statistics
        response = {
            'success': True,
            'directory': str(base_dir),
            'images_dir': str(images_dir),
            'labels_dir': str(labels_dir),
            'images_count': len(all_image_files),
            'existing_labels': existing_labels,
            'generated_labels': generated_count,
            'generation_errors': error_count,
            'total_labels': existing_labels + generated_count,
            'file_types': {
                'png': len(png_files),
                'pdf': len(pdf_files),
                'jpg': len(jpg_files + jpeg_files)
            }
        }

        logger.info(f"Directory set successfully: {base_dir}")
        logger.info(f"Images: {len(png_files)}, Existing labels: {existing_labels}, Generated: {generated_count}")

        return jsonify(response)

    except Exception as e:
        logger.error(f"Error setting directory: {e}")
        return jsonify({'error': str(e)}), 500

def get_image_dimensions(image_path):
    """Get image dimensions without loading full image"""
    # Handle PDF files - return default dimensions
    if str(image_path).lower().endswith('.pdf'):
        # Default A4 size at 72 DPI
        return (612, 792)  # (width, height)

    try:
        with Image.open(image_path) as img:
            return img.size  # (width, height)
    except Exception as e:
        logger.warning(f"Could not get dimensions for {image_path}: {e}")
        return (800, 600)  # Default dimensions if we can't read the file

def yolo_to_bbox(yolo_coords, img_width, img_height):
    """Convert YOLO format to pixel bounding box"""
    class_id, x_center, y_center, width, height = yolo_coords

    x1 = int((x_center - width/2) * img_width)
    y1 = int((y_center - height/2) * img_height)
    x2 = int((x_center + width/2) * img_width)
    y2 = int((y_center + height/2) * img_height)

    return {
        'class_id': class_id,
        'x1': x1,
        'y1': y1,
        'x2': x2,
        'y2': y2,
        'width': x2 - x1,
        'height': y2 - y1
    }

def bbox_to_yolo(bbox, img_width, img_height):
    """Convert pixel bounding box to YOLO format"""
    x_center = (bbox['x1'] + bbox['x2']) / 2 / img_width
    y_center = (bbox['y1'] + bbox['y2']) / 2 / img_height
    width = (bbox['x2'] - bbox['x1']) / img_width
    height = (bbox['y2'] - bbox['y1']) / img_height

    return [bbox['class_id'], x_center, y_center, width, height]

@app.route('/api/images', methods=['GET'])
def get_images():
    """Get list of all available images"""
    try:
        # Check if directory is set
        if not IMAGES_DIR or not LABELS_DIR:
            return jsonify({
                'error': 'No directory selected. Please select a dataset directory first.',
                'needs_directory': True
            }), 400

        images = []
        # Get all supported image files
        all_files = list(IMAGES_DIR.glob("*.png")) + \
                   list(IMAGES_DIR.glob("*.pdf")) + \
                   list(IMAGES_DIR.glob("*.jpg")) + \
                   list(IMAGES_DIR.glob("*.jpeg"))

        for img_path in sorted(all_files):
            width, height = get_image_dimensions(img_path)

            # Check if labels exist
            label_file = LABELS_DIR / f"{img_path.stem}.txt"
            has_labels = label_file.exists()
            label_count = 0

            if has_labels:
                try:
                    with open(label_file, 'r') as f:
                        label_count = len([line for line in f if line.strip()])
                except:
                    label_count = 0

            # Try to get relative path, but fall back to absolute if it fails
            try:
                path_str = str(img_path.relative_to(Path.cwd()))
            except ValueError:
                # Image is not relative to current directory, use absolute path
                path_str = str(img_path)

            images.append({
                'filename': img_path.name,
                'path': path_str,
                'width': width,
                'height': height,
                'has_labels': has_labels,
                'label_count': label_count
            })

        return jsonify({
            'images': images,
            'total': len(images),
            'classes': CLASSES
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/image/<filename>')
def serve_image(filename):
    """Serve image file"""
    try:
        # Check if directory is set
        if not IMAGES_DIR:
            return jsonify({'error': 'No directory selected'}), 400

        image_path = IMAGES_DIR / filename
        if not image_path.exists():
            return jsonify({'error': 'Image not found'}), 404

        return send_file(str(image_path))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/annotations/<filename>', methods=['GET'])
def get_annotations(filename):
    """Get annotations for specific image"""
    try:
        # Check if directory is set
        if not IMAGES_DIR or not LABELS_DIR:
            return jsonify({'error': 'No directory selected'}), 400

        image_path = IMAGES_DIR / filename
        if not image_path.exists():
            return jsonify({'error': 'Image not found'}), 404

        # Get image dimensions
        img_width, img_height = get_image_dimensions(image_path)

        # Load annotations
        label_file = LABELS_DIR / f"{Path(filename).stem}.txt"
        annotations = []

        if label_file.exists():
            with open(label_file, 'r') as f:
                for i, line in enumerate(f):
                    parts = line.strip().split()
                    if len(parts) == 5:
                        try:
                            yolo_coords = [float(parts[0])] + [float(x) for x in parts[1:]]
                            bbox = yolo_to_bbox(yolo_coords, img_width, img_height)
                            bbox['id'] = i
                            bbox['class_name'] = CLASSES.get(bbox['class_id'], 'unknown')
                            annotations.append(bbox)
                        except (ValueError, KeyError):
                            continue

        return jsonify({
            'filename': filename,
            'width': img_width,
            'height': img_height,
            'annotations': annotations
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/annotations/<filename>', methods=['POST'])
def save_annotations(filename):
    """Save annotations for specific image"""
    try:
        # Check if directory is set
        if not IMAGES_DIR or not LABELS_DIR:
            return jsonify({'error': 'No directory selected'}), 400

        data = request.get_json()
        annotations = data.get('annotations', [])

        # Get image dimensions
        image_path = IMAGES_DIR / filename
        if not image_path.exists():
            return jsonify({'error': 'Image not found'}), 404

        img_width, img_height = get_image_dimensions(image_path)

        # Convert annotations to YOLO format and save
        label_file = LABELS_DIR / f"{Path(filename).stem}.txt"

        with open(label_file, 'w') as f:
            for annotation in annotations:
                yolo_coords = bbox_to_yolo(annotation, img_width, img_height)
                class_id, x_center, y_center, width, height = yolo_coords
                f.write(f"{int(class_id)} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")

        return jsonify({
            'success': True,
            'message': f'Saved {len(annotations)} annotations for {filename}',
            'annotation_count': len(annotations)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/classes', methods=['GET'])
def get_classes():
    """Get available classes"""
    return jsonify({
        'classes': CLASSES,
        'class_list': [{'id': k, 'name': v} for k, v in CLASSES.items()]
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get annotation statistics"""
    try:
        # Check if directory is set
        if not IMAGES_DIR or not LABELS_DIR:
            return jsonify({
                'total_images': 0,
                'labeled_images': 0,
                'unlabeled_images': 0,
                'total_annotations': 0,
                'class_distribution': [],
                'completion_rate': 0,
                'needs_directory': True
            })

        total_images = len(list(IMAGES_DIR.glob("*.png")))
        labeled_images = len(list(LABELS_DIR.glob("*.txt")))

        # Count total annotations
        total_annotations = 0
        class_counts = {class_id: 0 for class_id in CLASSES.keys()}

        for label_file in LABELS_DIR.glob("*.txt"):
            with open(label_file, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) == 5:
                        try:
                            class_id = int(parts[0])
                            total_annotations += 1
                            if class_id in class_counts:
                                class_counts[class_id] += 1
                        except ValueError:
                            continue

        return jsonify({
            'total_images': total_images,
            'labeled_images': labeled_images,
            'unlabeled_images': total_images - labeled_images,
            'total_annotations': total_annotations,
            'class_distribution': [
                {'class_id': k, 'class_name': CLASSES[k], 'count': v}
                for k, v in class_counts.items()
            ],
            'completion_rate': round((labeled_images / total_images * 100) if total_images > 0 else 0, 1)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'data_dir': str(DATA_DIR.absolute()) if DATA_DIR else None,
        'labeled_data_dir': str(LABELED_DATA_DIR.absolute()) if LABELED_DATA_DIR else None,
        'images_dir': str(IMAGES_DIR.absolute()) if IMAGES_DIR else None,
        'labels_dir': str(LABELS_DIR.absolute()) if LABELS_DIR else None,
        'directory_set': bool(IMAGES_DIR and LABELS_DIR)
    })

if __name__ == '__main__':
    print("Annotation Tool Backend Starting...")
    print("Waiting for directory selection via API...")
    print(f"Classes: {CLASSES}")
    app.run(debug=True, host='0.0.0.0', port=5002)