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
from typing import Optional, Tuple, List, Dict
import logging
import fitz  # PyMuPDF
import io

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# PDF page cache directory
PDF_CACHE_DIR = Path(__file__).parent / "pdf_cache"
PDF_CACHE_DIR.mkdir(exist_ok=True)

# Configuration - Now dynamic, set via API
DATA_DIR: Optional[Path] = None
LABELED_DATA_DIR: Optional[Path] = None
IMAGES_DIR: Optional[Path] = None
LABELS_DIR: Optional[Path] = None
CLASSES_FILE: Optional[Path] = None

# Default classes - can be overridden by classes.txt
CLASSES = {
    0: 'straight',
    1: 'L-shape',
    2: 'U-shape',
    3: 'complex'
}

def load_classes_from_file():
    """Load classes from classes.txt file if it exists"""
    global CLASSES, CLASSES_FILE

    if CLASSES_FILE and CLASSES_FILE.exists():
        try:
            with open(CLASSES_FILE, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]
                CLASSES = {idx: name for idx, name in enumerate(lines)}
            logger.info(f"Loaded {len(CLASSES)} classes from {CLASSES_FILE}")
            return True
        except Exception as e:
            logger.error(f"Error loading classes from file: {e}")
            return False
    return False

def save_classes_to_file():
    """Save current classes to classes.txt file"""
    global CLASSES, CLASSES_FILE

    if not CLASSES_FILE:
        logger.error("CLASSES_FILE not set, cannot save classes")
        return False

    try:
        logger.info(f"Saving {len(CLASSES)} classes to {CLASSES_FILE}")
        logger.info(f"File path exists: {CLASSES_FILE.parent.exists()}")
        logger.info(f"File path is writable: {os.access(CLASSES_FILE.parent, os.W_OK)}")

        with open(CLASSES_FILE, 'w', encoding='utf-8') as f:
            # Sort by ID and write one class per line
            for class_id in sorted(CLASSES.keys()):
                line = f"{CLASSES[class_id]}\n"
                logger.debug(f"Writing line: {repr(line)}")
                f.write(line)

        logger.info(f"✓ Saved {len(CLASSES)} classes to {CLASSES_FILE}")
        logger.info(f"File size: {CLASSES_FILE.stat().st_size} bytes")
        return True
    except Exception as e:
        logger.error(f"Error saving classes to file: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def get_pdf_page_count(pdf_path: Path) -> int:
    """Get the number of pages in a PDF file"""
    try:
        doc = fitz.open(str(pdf_path))
        page_count = len(doc)
        doc.close()
        return page_count
    except Exception as e:
        logger.error(f"Error reading PDF {pdf_path}: {e}")
        return 1  # Default to 1 page if error

def convert_pdf_page_to_image(pdf_path: Path, page_num: int, dpi: int = 150) -> Optional[Image.Image]:
    """
    Convert a specific page of a PDF to a PIL Image

    Args:
        pdf_path: Path to PDF file
        page_num: Page number (0-indexed)
        dpi: Resolution for conversion (default 150)

    Returns:
        PIL Image or None if error
    """
    try:
        doc = fitz.open(str(pdf_path))

        if page_num >= len(doc):
            logger.error(f"Page {page_num} does not exist in {pdf_path} (total pages: {len(doc)})")
            doc.close()
            return None

        page = doc[page_num]

        # Convert to image with specified DPI
        # zoom = dpi / 72 (72 is default DPI)
        zoom = dpi / 72
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)

        # Convert to PIL Image
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))

        doc.close()
        return img

    except Exception as e:
        logger.error(f"Error converting PDF page {pdf_path} page {page_num}: {e}")
        return None

def get_or_create_pdf_page_cache(pdf_path: Path, page_num: int) -> Optional[Path]:
    """
    Get cached PNG for a PDF page, or create it if it doesn't exist

    Args:
        pdf_path: Path to original PDF file
        page_num: Page number (1-indexed for display, converted to 0-indexed internally)

    Returns:
        Path to cached PNG file or None if error
    """
    # Create cache filename: pdf_name_pageN.png
    cache_filename = f"{pdf_path.stem}_page{page_num}.png"
    cache_path = PDF_CACHE_DIR / cache_filename

    # Return cached version if it exists
    if cache_path.exists():
        return cache_path

    # Convert PDF page to image (page_num is 1-indexed, convert to 0-indexed)
    logger.info(f"Converting {pdf_path.name} page {page_num} to PNG...")
    img = convert_pdf_page_to_image(pdf_path, page_num - 1)

    if img is None:
        return None

    # Save to cache
    img.save(cache_path, "PNG")
    logger.info(f"Cached PDF page: {cache_path}")

    return cache_path

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
    Run YOLO on images without labels (PNG and JPG only - PDFs need conversion first)

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

        # Get all supported image files (PNG and JPG)
        image_files = (
            list(images_dir.glob("*.png")) +
            list(images_dir.glob("*.jpg")) +
            list(images_dir.glob("*.jpeg"))
        )

        # Get PDF files and expand to individual pages
        pdf_files = list(images_dir.glob("*.pdf"))
        pdf_page_images = []

        for pdf_path in pdf_files:
            page_count = get_pdf_page_count(pdf_path)
            logger.info(f"Found PDF {pdf_path.name} with {page_count} pages")

            for page_num in range(1, page_count + 1):
                # Convert PDF page to PNG and cache it
                cached_page = get_or_create_pdf_page_cache(pdf_path, page_num)
                if cached_page:
                    # Create a virtual path object for this page
                    page_info = {
                        'path': cached_page,
                        'stem': f"{pdf_path.stem}_page{page_num}"
                    }
                    pdf_page_images.append(page_info)

        # Filter to only unlabeled images (regular images)
        unlabeled_images = []
        for img_path in image_files:
            label_path = labels_dir / f"{img_path.stem}.txt"
            if not label_path.exists():
                unlabeled_images.append({'path': img_path, 'stem': img_path.stem})

        # Filter to only unlabeled PDF pages
        for page_info in pdf_page_images:
            label_path = labels_dir / f"{page_info['stem']}.txt"
            if not label_path.exists():
                unlabeled_images.append(page_info)

        total_unlabeled = len(unlabeled_images)
        if total_unlabeled == 0:
            logger.info("No unlabeled images found - all images already have labels")
            return 0, 0

        logger.info(f"Found {total_unlabeled} unlabeled images - starting auto-generation")
        generated_count = 0
        error_count = 0

        for idx, img_info in enumerate(unlabeled_images, start=1):
            img_path = img_info['path']
            img_stem = img_info['stem']
            label_path = labels_dir / f"{img_stem}.txt"

            try:
                # Log progress (Issue 2 requirement)
                img_name = img_path.name if hasattr(img_path, 'name') else str(img_path)
                logger.info(f"Processing: {idx}/{total_unlabeled} images ({img_name})")

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
                        logger.info(f"✓ Generated {len(result.boxes)} labels for {img_name}")
                    else:
                        # Create empty label file for images with no detections
                        label_path.touch()
                        logger.info(f"✓ No detections for {img_name}, created empty label file")

            except Exception as e:
                logger.error(f"✗ Error processing {img_name}: {e}")
                error_count += 1

        logger.info(f"Auto-generation complete: {generated_count}/{total_unlabeled} labels generated, {error_count} errors")
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
    global DATA_DIR, LABELED_DATA_DIR, IMAGES_DIR, LABELS_DIR, CLASSES_FILE

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
        CLASSES_FILE = base_dir / "classes.txt"

        logger.info(f"Set CLASSES_FILE to: {CLASSES_FILE}")
        logger.info(f"CLASSES_FILE exists: {CLASSES_FILE.exists()}")

        # Load classes from classes.txt if it exists, otherwise create it
        if not load_classes_from_file():
            # File doesn't exist, create it with default classes
            logger.info("classes.txt not found, creating with default classes")
            if not save_classes_to_file():
                logger.error("Failed to create initial classes.txt file")
            else:
                logger.info("Successfully created initial classes.txt file")

        # Auto-generate missing labels if requested
        auto_generate = data.get('auto_generate', True)
        generated_count = 0
        error_count = 0

        if auto_generate:
            logger.info("Auto-generating missing labels...")
            logger.info(f"Starting generation for {len(all_image_files)} source files...")
            generated_count, error_count = generate_missing_labels(images_dir, labels_dir)
            logger.info(f"Generation complete: {generated_count} labels created, {error_count} errors")

        # RE-COUNT labels after generation (critical for accurate stats)
        final_label_count = len(list(labels_dir.glob("*.txt")))

        # Count total pages (for PDFs, each page is separate)
        total_pages = len(png_files) + len(jpg_files + jpeg_files)
        for pdf_file in pdf_files:
            page_count = get_pdf_page_count(pdf_file)
            total_pages += page_count

        # Return success with statistics
        response = {
            'success': True,
            'directory': str(base_dir),
            'images_dir': str(images_dir),
            'labels_dir': str(labels_dir),
            'images_count': total_pages,  # Total pages (including PDF pages)
            'source_files': len(all_image_files),  # Original file count
            'existing_labels': existing_labels,  # Labels before generation
            'generated_labels': generated_count,  # Newly created labels
            'generation_errors': error_count,
            'total_labels': final_label_count,  # UPDATED count after generation
            'file_types': {
                'png': len(png_files),
                'pdf': len(pdf_files),
                'jpg': len(jpg_files + jpeg_files)
            }
        }

        logger.info(f"Directory set successfully: {base_dir}")
        logger.info(f"Total pages: {total_pages}, Labels before: {existing_labels}, Generated: {generated_count}, Labels after: {final_label_count}")

        return jsonify(response)

    except Exception as e:
        logger.error(f"Error setting directory: {e}")
        return jsonify({'error': str(e)}), 500

def get_image_dimensions(image_path):
    """
    Get image dimensions without loading full image

    For PDFs, this expects the image_path to be in format "filename_pageN.png"
    and will look up the cached converted page
    """
    path_str = str(image_path)

    # Handle PDF page references (e.g., "filename_page1.png")
    if '_page' in path_str and not Path(image_path).exists():
        # This is a PDF page reference, get dimensions from cache
        cache_path = PDF_CACHE_DIR / Path(image_path).name
        if cache_path.exists():
            try:
                with Image.open(cache_path) as img:
                    return img.size
            except Exception as e:
                logger.warning(f"Could not get dimensions from cache {cache_path}: {e}")
                return (1275, 1650)  # Default A4 at 150 DPI

    # Handle direct PDF files
    if path_str.lower().endswith('.pdf'):
        # Try to convert first page to get dimensions
        pdf_path = Path(image_path)
        if pdf_path.exists():
            img = convert_pdf_page_to_image(pdf_path, 0)
            if img:
                return img.size
        # Default A4 size at 150 DPI
        return (1275, 1650)  # (width, height)

    # Handle regular image files
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
    """
    Get list of all available images

    For PDF files, this expands each PDF into separate entries for each page
    (e.g., "document.pdf" with 3 pages becomes "document_page1.png", "document_page2.png", "document_page3.png")
    """
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
            # Handle PDF files - create entry for each page
            if img_path.suffix.lower() == '.pdf':
                page_count = get_pdf_page_count(img_path)
                logger.info(f"PDF {img_path.name} has {page_count} pages")

                for page_num in range(1, page_count + 1):
                    # Create virtual filename for this page
                    page_filename = f"{img_path.stem}_page{page_num}.png"

                    # Get or create cached page image
                    cached_page = get_or_create_pdf_page_cache(img_path, page_num)

                    if cached_page:
                        width, height = get_image_dimensions(cached_page)
                    else:
                        width, height = (1275, 1650)  # Default A4 at 150 DPI

                    # Check if labels exist for this page
                    label_file = LABELS_DIR / f"{img_path.stem}_page{page_num}.txt"
                    has_labels = label_file.exists()
                    label_count = 0

                    if has_labels:
                        try:
                            with open(label_file, 'r') as f:
                                label_count = len([line for line in f if line.strip()])
                        except:
                            label_count = 0

                    images.append({
                        'filename': page_filename,
                        'path': page_filename,  # Virtual path
                        'width': width,
                        'height': height,
                        'has_labels': has_labels,
                        'label_count': label_count,
                        'is_pdf_page': True,
                        'source_pdf': img_path.name,
                        'page_number': page_num,
                        'total_pages': page_count
                    })

            else:
                # Handle regular image files (PNG, JPG)
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

        logger.info(f"Returning {len(images)} images (including PDF pages)")

        return jsonify({
            'images': images,
            'total': len(images),
            'classes': CLASSES
        })
    except Exception as e:
        logger.error(f"Error in get_images: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/image/<filename>')
def serve_image(filename):
    """
    Serve image file

    For PDF pages (e.g., "document_page1.png"), serves the cached converted PNG
    For regular images, serves the original file
    """
    try:
        # Check if directory is set
        if not IMAGES_DIR:
            return jsonify({'error': 'No directory selected'}), 400

        # Check if this is a PDF page request (format: filename_pageN.png)
        if '_page' in filename and filename.endswith('.png'):
            # Extract page number
            try:
                base_name = filename.replace('.png', '')
                parts = base_name.rsplit('_page', 1)
                if len(parts) == 2:
                    pdf_stem = parts[0]
                    page_num = int(parts[1])

                    # Find the original PDF
                    pdf_path = IMAGES_DIR / f"{pdf_stem}.pdf"

                    if pdf_path.exists():
                        # Get or create cached page
                        cached_page = get_or_create_pdf_page_cache(pdf_path, page_num)

                        if cached_page and cached_page.exists():
                            return send_file(str(cached_page), mimetype='image/png')
                        else:
                            return jsonify({'error': f'Could not convert PDF page {page_num}'}), 500
                    else:
                        return jsonify({'error': f'Source PDF not found: {pdf_stem}.pdf'}), 404
            except (ValueError, IndexError) as e:
                logger.error(f"Error parsing PDF page filename {filename}: {e}")
                return jsonify({'error': 'Invalid PDF page filename format'}), 400

        # Regular image file
        image_path = IMAGES_DIR / filename
        if not image_path.exists():
            return jsonify({'error': 'Image not found'}), 404

        return send_file(str(image_path))
    except Exception as e:
        logger.error(f"Error serving image {filename}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/annotations/<filename>', methods=['GET'])
def get_annotations(filename):
    """Get annotations for specific image"""
    try:
        # Check if directory is set
        if not IMAGES_DIR or not LABELS_DIR:
            return jsonify({'error': 'No directory selected'}), 400

        # Handle PDF page requests (format: filename_pageN.png)
        if '_page' in filename and filename.endswith('.png'):
            # Extract PDF name and page number
            base_name = filename.replace('.png', '')
            parts = base_name.rsplit('_page', 1)
            if len(parts) == 2:
                pdf_stem = parts[0]
                page_num = int(parts[1])

                # Check if source PDF exists
                pdf_path = IMAGES_DIR / f"{pdf_stem}.pdf"
                if not pdf_path.exists():
                    return jsonify({'error': f'Source PDF not found: {pdf_stem}.pdf'}), 404

                # Get dimensions from cached page or convert
                cached_page = get_or_create_pdf_page_cache(pdf_path, page_num)
                if cached_page:
                    img_width, img_height = get_image_dimensions(cached_page)
                else:
                    # Use default dimensions if cache fails
                    img_width, img_height = (1275, 1650)
            else:
                return jsonify({'error': 'Invalid PDF page filename format'}), 400
        else:
            # Regular image file
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

        # Log before saving (Issue 3 debugging)
        logger.info(f"Saving {len(annotations)} annotations to {label_file}")
        logger.info(f"File mode: 'w' (overwrite)")

        with open(label_file, 'w') as f:
            for annotation in annotations:
                yolo_coords = bbox_to_yolo(annotation, img_width, img_height)
                class_id, x_center, y_center, width, height = yolo_coords
                f.write(f"{int(class_id)} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")

        # Verify file contents after saving (Issue 3 verification)
        with open(label_file, 'r') as f:
            saved_lines = [line for line in f if line.strip()]
            line_count = len(saved_lines)

        logger.info(f"Verified: Label file contains {line_count} lines")

        # Warn if mismatch between sent annotations and saved lines
        if line_count != len(annotations):
            logger.warning(f"Mismatch! Received {len(annotations)} annotations but saved {line_count} lines")

        return jsonify({
            'success': True,
            'message': f'Saved {len(annotations)} annotations for {filename}',
            'annotation_count': len(annotations),
            'verified_line_count': line_count
        })
    except Exception as e:
        logger.error(f"Error saving annotations for {filename}: {e}")
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
        'classes_file': str(CLASSES_FILE.absolute()) if CLASSES_FILE else None,
        'classes_file_exists': CLASSES_FILE.exists() if CLASSES_FILE else False,
        'directory_set': bool(IMAGES_DIR and LABELS_DIR),
        'current_classes': dict(CLASSES),
        'classes_count': len(CLASSES)
    })

@app.route('/api/debug/state', methods=['GET'])
def debug_state():
    """Debug endpoint to show current backend state"""
    state = {
        'CLASSES_FILE': str(CLASSES_FILE) if CLASSES_FILE else None,
        'CLASSES_FILE_exists': CLASSES_FILE.exists() if CLASSES_FILE else False,
        'CLASSES_FILE_parent_exists': CLASSES_FILE.parent.exists() if CLASSES_FILE else False,
        'CLASSES_FILE_parent_writable': os.access(CLASSES_FILE.parent, os.W_OK) if CLASSES_FILE and CLASSES_FILE.parent.exists() else False,
        'CLASSES': dict(CLASSES),
        'IMAGES_DIR': str(IMAGES_DIR) if IMAGES_DIR else None,
        'LABELS_DIR': str(LABELS_DIR) if LABELS_DIR else None,
    }

    # Try to read classes.txt if it exists
    if CLASSES_FILE and CLASSES_FILE.exists():
        try:
            with open(CLASSES_FILE, 'r', encoding='utf-8') as f:
                state['classes_txt_content'] = f.read()
        except Exception as e:
            state['classes_txt_read_error'] = str(e)

    return jsonify(state)

# ============================================================================
# LABEL MANAGEMENT ENDPOINTS
# ============================================================================

@app.route('/api/labels/manage', methods=['GET'])
def get_label_management_info():
    """
    Get all classes with statistics (count of objects per class)
    """
    try:
        if not LABELS_DIR:
            return jsonify({'error': 'No directory selected'}), 400

        # Count objects per class
        class_counts = {class_id: 0 for class_id in CLASSES.keys()}
        total_annotations = 0

        for label_file in LABELS_DIR.glob("*.txt"):
            try:
                with open(label_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) == 5:
                            try:
                                class_id = int(parts[0])
                                if class_id in class_counts:
                                    class_counts[class_id] += 1
                                total_annotations += 1
                            except ValueError:
                                continue
            except Exception as e:
                logger.error(f"Error reading {label_file}: {e}")
                continue

        # Build response
        classes_info = [
            {
                'id': class_id,
                'name': name,
                'count': class_counts.get(class_id, 0),
                'is_complex': name.lower() == 'complex'
            }
            for class_id, name in CLASSES.items()
        ]

        return jsonify({
            'classes': classes_info,
            'total_classes': len(CLASSES),
            'total_annotations': total_annotations
        })

    except Exception as e:
        logger.error(f"Error in get_label_management_info: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/labels/add', methods=['POST'])
def add_label_class():
    """
    Add a new label class
    Request body: {"name": "new_class_name"}
    """
    try:
        logger.info("=== ADD LABEL CLASS REQUEST ===")
        logger.info(f"CLASSES_FILE: {CLASSES_FILE}")
        logger.info(f"Current CLASSES: {CLASSES}")

        if not CLASSES_FILE:
            logger.error("CLASSES_FILE is not set")
            return jsonify({'error': 'No directory selected'}), 400

        data = request.get_json()
        logger.info(f"Received data: {data}")

        new_class_name = data.get('name', '').strip()
        logger.info(f"New class name (stripped): '{new_class_name}'")

        if not new_class_name:
            logger.error("Class name is empty")
            return jsonify({'error': 'Class name is required'}), 400

        # Check if class name already exists
        if new_class_name in CLASSES.values():
            logger.warning(f"Class '{new_class_name}' already exists")
            return jsonify({'error': f'Class "{new_class_name}" already exists'}), 400

        # Find next available ID
        new_id = max(CLASSES.keys()) + 1 if CLASSES else 0
        logger.info(f"Assigned new ID: {new_id}")

        # Add to CLASSES dict
        CLASSES[new_id] = new_class_name
        logger.info(f"Updated CLASSES dict: {CLASSES}")

        # Save to file
        logger.info(f"Attempting to save to: {CLASSES_FILE}")
        if not save_classes_to_file():
            logger.error("save_classes_to_file() returned False")
            return jsonify({'error': 'Failed to save classes to file'}), 500

        # Verify file was written
        if CLASSES_FILE.exists():
            with open(CLASSES_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
                logger.info(f"File contents after save:\n{content}")
        else:
            logger.error(f"File does not exist after save: {CLASSES_FILE}")

        logger.info(f"✓ Successfully added class: {new_id} = '{new_class_name}'")

        return jsonify({
            'success': True,
            'class_id': new_id,
            'class_name': new_class_name,
            'total_classes': len(CLASSES)
        })

    except Exception as e:
        logger.error(f"Error adding class: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/labels/edit/<int:class_id>', methods=['PUT'])
def edit_label_class(class_id: int):
    """
    Edit an existing label class name
    Request body: {"name": "updated_class_name"}
    """
    try:
        if not CLASSES_FILE or not LABELS_DIR:
            return jsonify({'error': 'No directory selected'}), 400

        if class_id not in CLASSES:
            return jsonify({'error': f'Class ID {class_id} not found'}), 404

        data = request.get_json()
        new_name = data.get('name', '').strip()

        if not new_name:
            return jsonify({'error': 'Class name is required'}), 400

        # Check if new name already exists (but allow same name)
        if new_name != CLASSES[class_id] and new_name in CLASSES.values():
            return jsonify({'error': f'Class "{new_name}" already exists'}), 400

        old_name = CLASSES[class_id]
        CLASSES[class_id] = new_name

        # Save to file
        if not save_classes_to_file():
            return jsonify({'error': 'Failed to save classes to file'}), 500

        logger.info(f"Updated class {class_id}: '{old_name}' → '{new_name}'")

        return jsonify({
            'success': True,
            'class_id': class_id,
            'old_name': old_name,
            'new_name': new_name
        })

    except Exception as e:
        logger.error(f"Error editing class: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/labels/delete/<int:class_id>', methods=['DELETE'])
def delete_label_class(class_id: int):
    """
    Delete a label class
    WARNING: This will not remove annotations with this class from label files
    """
    try:
        if not CLASSES_FILE:
            return jsonify({'error': 'No directory selected'}), 400

        if class_id not in CLASSES:
            return jsonify({'error': f'Class ID {class_id} not found'}), 404

        # Check if this class is being used in annotations
        usage_count = 0
        if LABELS_DIR:
            for label_file in LABELS_DIR.glob("*.txt"):
                try:
                    with open(label_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            parts = line.strip().split()
                            if len(parts) == 5 and int(parts[0]) == class_id:
                                usage_count += 1
                except:
                    continue

        if usage_count > 0:
            return jsonify({
                'error': f'Cannot delete class that is in use',
                'usage_count': usage_count,
                'message': f'This class is used in {usage_count} annotations. Please reclassify them first.'
            }), 400

        # Delete from CLASSES
        deleted_name = CLASSES.pop(class_id)

        # Save to file
        if not save_classes_to_file():
            return jsonify({'error': 'Failed to save classes to file'}), 500

        logger.info(f"Deleted class {class_id}: '{deleted_name}'")

        return jsonify({
            'success': True,
            'deleted_class_id': class_id,
            'deleted_class_name': deleted_name
        })

    except Exception as e:
        logger.error(f"Error deleting class: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/labels/bulk-reclassify', methods=['POST'])
def bulk_reclassify_labels():
    """
    Bulk reclassify annotations from one class to another
    Request body: {
        "from_class_id": 3,
        "to_class_id": 4,
        "image_filenames": ["image1.png", "image2.png"] # optional, if empty does all images
    }
    """
    try:
        if not LABELS_DIR:
            return jsonify({'error': 'No directory selected'}), 400

        data = request.get_json()
        from_class_id = data.get('from_class_id')
        to_class_id = data.get('to_class_id')
        target_images = data.get('image_filenames', [])

        if from_class_id is None or to_class_id is None:
            return jsonify({'error': 'from_class_id and to_class_id are required'}), 400

        if from_class_id not in CLASSES:
            return jsonify({'error': f'Source class ID {from_class_id} not found'}), 404

        if to_class_id not in CLASSES:
            return jsonify({'error': f'Target class ID {to_class_id} not found'}), 404

        # Get label files to process
        if target_images:
            label_files = [LABELS_DIR / f"{Path(img).stem}.txt" for img in target_images]
            label_files = [f for f in label_files if f.exists()]
        else:
            label_files = list(LABELS_DIR.glob("*.txt"))

        updated_files = 0
        updated_annotations = 0
        errors = []

        for label_file in label_files:
            try:
                # Read all lines
                with open(label_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                # Update lines
                updated_lines = []
                file_updated = False

                for line in lines:
                    parts = line.strip().split()
                    if len(parts) == 5:
                        try:
                            class_id = int(parts[0])
                            if class_id == from_class_id:
                                # Replace class ID
                                updated_line = f"{to_class_id} {' '.join(parts[1:])}\n"
                                updated_lines.append(updated_line)
                                file_updated = True
                                updated_annotations += 1
                            else:
                                updated_lines.append(line)
                        except ValueError:
                            updated_lines.append(line)
                    else:
                        updated_lines.append(line)

                # Write back if updated
                if file_updated:
                    with open(label_file, 'w', encoding='utf-8') as f:
                        f.writelines(updated_lines)
                    updated_files += 1

            except Exception as e:
                errors.append(f"{label_file.name}: {str(e)}")
                logger.error(f"Error processing {label_file}: {e}")

        from_name = CLASSES.get(from_class_id, f"Class {from_class_id}")
        to_name = CLASSES.get(to_class_id, f"Class {to_class_id}")

        logger.info(f"Bulk reclassify: {updated_annotations} annotations from '{from_name}' → '{to_name}' in {updated_files} files")

        return jsonify({
            'success': True,
            'updated_files': updated_files,
            'updated_annotations': updated_annotations,
            'from_class': {'id': from_class_id, 'name': from_name},
            'to_class': {'id': to_class_id, 'name': to_name},
            'errors': errors if errors else None
        })

    except Exception as e:
        logger.error(f"Error in bulk_reclassify_labels: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Annotation Tool Backend Starting...")
    print("Waiting for directory selection via API...")
    print(f"Classes: {CLASSES}")
    app.run(debug=True, host='0.0.0.0', port=5002)