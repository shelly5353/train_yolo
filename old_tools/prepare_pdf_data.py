#!/usr/bin/env python3
"""
Prepare PDF Images for YOLO Labeling
Consolidates all PDF images into a single directory for labeling workflow.
"""

import os
import shutil
from pathlib import Path
import argparse
from tqdm import tqdm

def prepare_pdf_images_for_labeling(source_dir, output_dir, copy_mode=True):
    """
    Prepare PDF images for labeling by organizing them into a flat structure.

    Args:
        source_dir: Directory containing PDF subdirectories with images
        output_dir: Output directory for organized images
        copy_mode: If True, copy files. If False, create symlinks.
    """
    source_path = Path(source_dir)
    output_path = Path(output_dir)

    if not source_path.exists():
        print(f"Error: Source directory {source_path} does not exist")
        return

    # Create output directory
    output_path.mkdir(exist_ok=True)

    # Find all image files
    image_files = []
    for pdf_dir in source_path.iterdir():
        if pdf_dir.is_dir():
            for img_file in pdf_dir.glob("*.png"):
                image_files.append(img_file)

    print(f"Found {len(image_files)} images from PDF conversion")
    print(f"Output directory: {output_path}")
    print(f"Mode: {'Copy' if copy_mode else 'Symlink'}")
    print()

    # Process each image
    copied_count = 0
    skipped_count = 0

    for img_file in tqdm(image_files, desc="Processing images"):
        # Use original filename (already unique with PDF name prefix)
        dest_file = output_path / img_file.name

        if dest_file.exists():
            skipped_count += 1
            continue

        try:
            if copy_mode:
                shutil.copy2(img_file, dest_file)
            else:
                dest_file.symlink_to(img_file.absolute())
            copied_count += 1
        except Exception as e:
            print(f"Error processing {img_file}: {e}")

    print(f"\n=== Preparation Complete ===")
    print(f"Images processed: {copied_count}")
    print(f"Images skipped (already exist): {skipped_count}")
    print(f"Total images available for labeling: {len(list(output_path.glob('*.png')))}")

    return output_path

def main():
    parser = argparse.ArgumentParser(description='Prepare PDF images for YOLO labeling')
    parser.add_argument('--source_dir', type=str, default='pdf_images',
                        help='Source directory with PDF image subdirectories')
    parser.add_argument('--output_dir', type=str, default='pdf_labeling_data',
                        help='Output directory for labeling workflow')
    parser.add_argument('--symlink', action='store_true',
                        help='Use symlinks instead of copying files')

    args = parser.parse_args()

    copy_mode = not args.symlink
    result_dir = prepare_pdf_images_for_labeling(args.source_dir, args.output_dir, copy_mode)

    if result_dir:
        print(f"\n=== Next Steps ===")
        print(f"Your PDF images are ready for labeling in: {result_dir}")
        print(f"\nChoose your labeling tool:")
        print(f"1. Web annotation tool (recommended): cd annotation_tool && ./start.sh")
        print(f"2. Enhanced labeling tool: python enhanced_label_tool.py --data_dir {result_dir}")
        print(f"3. Basic labeling tool: python label_tool.py")
        print(f"4. Batch detection first: python batch_detect.py --input_dir {result_dir} --confidence 0.3")

if __name__ == "__main__":
    main()