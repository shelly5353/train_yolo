#!/usr/bin/env python3
"""
Flask Backend for Modern Image Annotation Tool
Handles image serving, annotation CRUD operations, and YOLO format conversion
"""

import os
import json
import hashlib
from pathlib import Path
from flask import Flask, request, jsonify, send_file, send_from_directory, make_response
from flask_cors import CORS
import cv2
import numpy as np
from PIL import Image

app = Flask(__name__)
CORS(app)

# Configuration
DATA_DIR = Path("/Users/shellysmac/Documents/Work/data/unlabeled")
LABELED_DATA_DIR = Path("/Users/shellysmac/Documents/Work/data/labeled")
CLASSES = {
    0: 'straight',
    1: 'L-shape',
    2: 'U-shape',
    3: 'complex'
}

def ensure_directories():
    """Ensure required directories exist"""
    DATA_DIR.mkdir(exist_ok=True)
    LABELED_DATA_DIR.mkdir(exist_ok=True)

def get_image_dimensions(image_path):
    """Get image dimensions without loading full image"""
    with Image.open(image_path) as img:
        return img.size  # (width, height)

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

def generate_etag(file_path):
    """Generate ETag based on file path, size, and modification time"""
    stat = file_path.stat()
    etag_data = f"{file_path.name}-{stat.st_size}-{stat.st_mtime}"
    return hashlib.md5(etag_data.encode()).hexdigest()[:16]

@app.route('/api/images', methods=['GET'])
def get_images():
    """Get list of all available images"""
    try:
        images = []
        for img_path in sorted(DATA_DIR.glob("*.png")):
            width, height = get_image_dimensions(img_path)

            # Check if labels exist
            label_file = LABELED_DATA_DIR / f"{img_path.stem}.txt"
            has_labels = label_file.exists()
            label_count = 0

            if has_labels:
                try:
                    with open(label_file, 'r') as f:
                        label_count = len([line for line in f if line.strip()])
                except:
                    label_count = 0

            images.append({
                'filename': img_path.name,
                'path': str(img_path),
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
    """Serve image file with optimized caching"""
    try:
        # First try data directory
        image_path = DATA_DIR / filename
        if not image_path.exists():
            # Try labeled data directory
            image_path = LABELED_DATA_DIR / filename
            if not image_path.exists():
                return jsonify({'error': 'Image not found'}), 404

        # Generate ETag for this file
        etag = generate_etag(image_path)

        # Check if client has cached version
        if_none_match = request.headers.get('If-None-Match')
        if if_none_match and etag in if_none_match:
            # Client has current version, return 304 Not Modified
            response = make_response('', 304)
            response.headers['ETag'] = f'"{etag}"'
            response.headers['Cache-Control'] = 'private, max-age=3600, must-revalidate'
            return response

        # Create response with the file
        response = make_response(send_file(
            str(image_path.resolve()),
            mimetype=f'image/{image_path.suffix[1:]}',
            as_attachment=False,
            conditional=True
        ))

        # Add caching headers
        response.headers['ETag'] = f'"{etag}"'
        response.headers['Cache-Control'] = 'private, max-age=3600, must-revalidate'
        response.headers['Last-Modified'] = image_path.stat().st_mtime

        # Add CORS headers specifically for images
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'If-None-Match, Cache-Control'
        response.headers['Access-Control-Expose-Headers'] = 'ETag, Cache-Control, Last-Modified'

        return response

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/image/<filename>', methods=['OPTIONS'])
def serve_image_options(filename):
    """Handle CORS preflight for image requests"""
    response = make_response('', 200)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'If-None-Match, Cache-Control'
    response.headers['Access-Control-Expose-Headers'] = 'ETag, Cache-Control, Last-Modified'
    response.headers['Access-Control-Max-Age'] = '86400'  # 24 hours
    return response

@app.route('/api/annotations/<filename>', methods=['GET'])
def get_annotations(filename):
    """Get annotations for specific image"""
    try:
        image_path = DATA_DIR / filename
        if not image_path.exists():
            image_path = LABELED_DATA_DIR / filename
            if not image_path.exists():
                return jsonify({'error': 'Image not found'}), 404

        # Get image dimensions
        img_width, img_height = get_image_dimensions(image_path)

        # Load annotations
        label_file = LABELED_DATA_DIR / f"{Path(filename).stem}.txt"
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
        data = request.get_json()
        annotations = data.get('annotations', [])

        # Get image dimensions
        image_path = DATA_DIR / filename
        if not image_path.exists():
            image_path = LABELED_DATA_DIR / filename
            if not image_path.exists():
                return jsonify({'error': 'Image not found'}), 404

        img_width, img_height = get_image_dimensions(image_path)

        # Copy image to labeled data directory if not already there
        output_image_path = LABELED_DATA_DIR / filename
        if not output_image_path.exists():
            import shutil
            shutil.copy2(image_path, output_image_path)

        # Convert annotations to YOLO format and save
        label_file = LABELED_DATA_DIR / f"{Path(filename).stem}.txt"

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
        total_images = len(list(DATA_DIR.glob("*.png")))
        labeled_images = len(list(LABELED_DATA_DIR.glob("*.txt")))

        # Count total annotations
        total_annotations = 0
        class_counts = {class_id: 0 for class_id in CLASSES.keys()}

        for label_file in LABELED_DATA_DIR.glob("*.txt"):
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
        'data_dir': str(DATA_DIR.absolute()),
        'labeled_data_dir': str(LABELED_DATA_DIR.absolute()),
        'data_dir_exists': DATA_DIR.exists(),
        'labeled_data_dir_exists': LABELED_DATA_DIR.exists()
    })

if __name__ == '__main__':
    ensure_directories()
    print(f"Data directory: {DATA_DIR.absolute()}")
    print(f"Labeled data directory: {LABELED_DATA_DIR.absolute()}")
    print(f"Classes: {CLASSES}")
    app.run(debug=True, host='0.0.0.0', port=5002)