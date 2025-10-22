#!/usr/bin/env python3
"""
PDF to Images Converter
Converts all PDF files in a directory to individual page images.
Each page of each PDF becomes a separate image file.
"""

import os
import sys
from pathlib import Path
import fitz  # PyMuPDF
from tqdm import tqdm
import argparse

def convert_pdf_to_images(pdf_path, output_dir, dpi=300):
    """
    Convert a single PDF to images, one image per page.

    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save images
        dpi: Resolution for image conversion

    Returns:
        List of created image paths
    """
    try:
        # Open PDF
        pdf_document = fitz.open(pdf_path)
        pdf_name = Path(pdf_path).stem
        created_images = []

        # Create subdirectory for this PDF
        pdf_output_dir = output_dir / pdf_name
        pdf_output_dir.mkdir(exist_ok=True)

        # Convert each page
        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]

            # Create transformation matrix for higher resolution
            mat = fitz.Matrix(dpi/72, dpi/72)
            pix = page.get_pixmap(matrix=mat)

            # Save image
            image_filename = f"{pdf_name}_page_{page_num + 1:03d}.png"
            image_path = pdf_output_dir / image_filename
            pix.save(str(image_path))
            created_images.append(image_path)

        pdf_document.close()
        return created_images

    except Exception as e:
        print(f"Error converting {pdf_path}: {e}")
        return []

def main():
    parser = argparse.ArgumentParser(description='Convert PDF files to images')
    parser.add_argument('--input_dir', type=str, required=True,
                        help='Directory containing PDF files')
    parser.add_argument('--output_dir', type=str, default='pdf_images',
                        help='Output directory for images (default: pdf_images)')
    parser.add_argument('--dpi', type=int, default=300,
                        help='Image resolution in DPI (default: 300)')

    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)

    if not input_dir.exists():
        print(f"Error: Input directory {input_dir} does not exist")
        sys.exit(1)

    # Create output directory
    output_dir.mkdir(exist_ok=True)

    # Find all PDF files
    pdf_files = list(input_dir.glob("*.pdf"))
    if not pdf_files:
        print(f"No PDF files found in {input_dir}")
        sys.exit(1)

    print(f"Found {len(pdf_files)} PDF files")
    print(f"Output directory: {output_dir}")
    print(f"Resolution: {args.dpi} DPI")
    print()

    total_images = 0
    total_pdfs = len(pdf_files)

    # Process each PDF
    for i, pdf_path in enumerate(tqdm(pdf_files, desc="Converting PDFs")):
        print(f"\nProcessing {pdf_path.name} ({i+1}/{total_pdfs})")

        # Convert PDF to images
        images = convert_pdf_to_images(pdf_path, output_dir, args.dpi)
        total_images += len(images)

        if images:
            print(f"  Created {len(images)} images")
        else:
            print(f"  Failed to convert {pdf_path.name}")

    print(f"\n=== Conversion Complete ===")
    print(f"Total PDFs processed: {total_pdfs}")
    print(f"Total images created: {total_images}")
    print(f"Images saved to: {output_dir}")

if __name__ == "__main__":
    main()