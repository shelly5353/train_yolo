#!/usr/bin/env python3
"""
Simple PDF Image Labeler
A straightforward tkinter-based tool for labeling PDF images.
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
from pathlib import Path
import argparse

class SimplePDFLabeler:
    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
        self.labeled_dir = self.data_dir / "labels"
        self.labeled_dir.mkdir(exist_ok=True)

        # Class mapping
        self.classes = {0: 'straight', 1: 'L-shape', 2: 'U-shape', 3: 'complex'}
        self.class_colors = {0: 'red', 1: 'green', 2: 'blue', 3: 'orange'}

        # Get all images
        self.image_files = sorted(list(self.data_dir.glob("*.png")))
        if not self.image_files:
            messagebox.showerror("Error", f"No PNG images found in {data_dir}")
            return

        self.current_index = 0
        self.current_image = None
        self.current_photo = None
        self.annotations = []
        self.drawing = False
        self.start_x = 0
        self.start_y = 0
        self.current_rect = None
        self.selected_class = 0

        # Setup GUI
        self.setup_gui()
        self.load_image()

    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("Simple PDF Image Labeler")
        self.root.geometry("1400x900")
        self.root.state('zoomed') if hasattr(self.root, 'state') else None  # Maximize on Windows

        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Control panel (left side) - make narrower
        control_frame = ttk.Frame(main_frame, width=250)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        control_frame.pack_propagate(False)

        # Image info
        info_frame = ttk.LabelFrame(control_frame, text="Image Info")
        info_frame.pack(fill=tk.X, pady=(0, 5))

        self.image_label = ttk.Label(info_frame, text="", wraplength=230)
        self.image_label.pack(pady=2)

        self.progress_label = ttk.Label(info_frame, text="")
        self.progress_label.pack(pady=2)

        # Zoom controls
        zoom_frame = ttk.LabelFrame(control_frame, text="Zoom")
        zoom_frame.pack(fill=tk.X, pady=(0, 5))

        self.scale_var = tk.DoubleVar(value=1.0)
        ttk.Button(zoom_frame, text="Fit to Window", command=self.fit_to_window).pack(fill=tk.X, pady=1)
        ttk.Button(zoom_frame, text="100%", command=self.zoom_100).pack(fill=tk.X, pady=1)
        ttk.Button(zoom_frame, text="Zoom In (+)", command=self.zoom_in).pack(fill=tk.X, pady=1)
        ttk.Button(zoom_frame, text="Zoom Out (-)", command=self.zoom_out).pack(fill=tk.X, pady=1)

        self.zoom_label = ttk.Label(zoom_frame, text="100%")
        self.zoom_label.pack(pady=2)

        # Navigation
        nav_frame = ttk.LabelFrame(control_frame, text="Navigation")
        nav_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Button(nav_frame, text="← Previous (A)", command=self.prev_image).pack(fill=tk.X, pady=1)
        ttk.Button(nav_frame, text="Next → (D)", command=self.next_image).pack(fill=tk.X, pady=1)

        # Class selection
        class_frame = ttk.LabelFrame(control_frame, text="Shape Class")
        class_frame.pack(fill=tk.X, pady=(0, 5))

        self.class_var = tk.IntVar(value=0)
        for class_id, class_name in self.classes.items():
            color = self.class_colors[class_id]
            ttk.Radiobutton(class_frame, text=f"{class_id+1}. {class_name}",
                          variable=self.class_var, value=class_id).pack(anchor=tk.W, pady=1)

        # Actions
        action_frame = ttk.LabelFrame(control_frame, text="Actions")
        action_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Button(action_frame, text="Save (S)", command=self.save_annotations).pack(fill=tk.X, pady=1)
        ttk.Button(action_frame, text="Clear All (C)", command=self.clear_annotations).pack(fill=tk.X, pady=1)
        ttk.Button(action_frame, text="Delete Last (X)", command=self.delete_last).pack(fill=tk.X, pady=1)

        # Statistics
        stats_frame = ttk.LabelFrame(control_frame, text="Statistics")
        stats_frame.pack(fill=tk.X, pady=(0, 5))

        self.stats_label = ttk.Label(stats_frame, text="", wraplength=230)
        self.stats_label.pack(pady=2)

        # Instructions
        instructions_frame = ttk.LabelFrame(control_frame, text="Instructions")
        instructions_frame.pack(fill=tk.X, expand=True)

        instructions = [
            "• Click and drag to draw boxes",
            "• Select class before drawing",
            "• A/D: Previous/Next image",
            "• +/-: Zoom in/out",
            "• S: Save annotations",
            "• C: Clear all boxes",
            "• X: Delete last box",
            "• 1-4: Select class"
        ]

        for instruction in instructions:
            ttk.Label(instructions_frame, text=instruction, font=("Arial", 8)).pack(anchor=tk.W, pady=1)

        # Canvas frame (right side)
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Canvas with scrollbars
        self.canvas = tk.Canvas(canvas_frame, bg="white", highlightthickness=1, highlightbackground="gray")

        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)

        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Bind events
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw_motion)
        self.canvas.bind("<ButtonRelease-1>", self.end_draw)
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)  # Windows/Linux
        self.canvas.bind("<Button-4>", self.on_mousewheel)    # Linux
        self.canvas.bind("<Button-5>", self.on_mousewheel)    # Linux

        # Keyboard bindings
        self.root.bind("<Key>", self.on_key_press)
        self.root.focus_set()

    def load_image(self):
        """Load and display the current image"""
        if not self.image_files:
            return

        # Load image
        image_path = self.image_files[self.current_index]
        self.current_image = cv2.imread(str(image_path))
        self.current_image = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2RGB)

        # Create PIL image for display
        pil_image = Image.fromarray(self.current_image)
        self.current_photo = ImageTk.PhotoImage(pil_image)

        # Update canvas
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.current_photo)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        # Load existing annotations
        self.load_annotations()

        # Update info
        self.update_info()
        self.update_stats()

    def load_annotations(self):
        """Load existing annotations for current image"""
        self.annotations = []
        image_name = self.image_files[self.current_index].stem
        label_file = self.labeled_dir / f"{image_name}.txt"

        if label_file.exists():
            height, width = self.current_image.shape[:2]
            with open(label_file, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) == 5:
                        class_id = int(parts[0])
                        cx, cy, w, h = map(float, parts[1:])

                        # Convert from YOLO format to pixel coordinates
                        x1 = int((cx - w/2) * width)
                        y1 = int((cy - h/2) * height)
                        x2 = int((cx + w/2) * width)
                        y2 = int((cy + h/2) * height)

                        self.annotations.append({
                            'class': class_id,
                            'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2
                        })

        self.draw_annotations()

    def draw_annotations(self):
        """Draw all annotations on the canvas"""
        # Clear existing annotation drawings
        self.canvas.delete("annotation")

        for i, ann in enumerate(self.annotations):
            color = self.class_colors[ann['class']]
            class_name = self.classes[ann['class']]

            # Draw rectangle
            self.canvas.create_rectangle(
                ann['x1'], ann['y1'], ann['x2'], ann['y2'],
                outline=color, width=2, tags="annotation"
            )

            # Draw label
            self.canvas.create_text(
                ann['x1'], ann['y1'] - 10,
                text=f"{i+1}: {class_name}",
                fill=color, anchor=tk.SW, tags="annotation"
            )

    def start_draw(self, event):
        """Start drawing a bounding box"""
        self.drawing = True
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)

    def draw_motion(self, event):
        """Update the current drawing rectangle"""
        if self.drawing:
            if self.current_rect:
                self.canvas.delete(self.current_rect)

            current_x = self.canvas.canvasx(event.x)
            current_y = self.canvas.canvasy(event.y)

            color = self.class_colors[self.class_var.get()]
            self.current_rect = self.canvas.create_rectangle(
                self.start_x, self.start_y, current_x, current_y,
                outline=color, width=2, dash=(5, 5)
            )

    def end_draw(self, event):
        """Finish drawing a bounding box"""
        if self.drawing:
            self.drawing = False
            end_x = self.canvas.canvasx(event.x)
            end_y = self.canvas.canvasy(event.y)

            # Clean up temporary rectangle
            if self.current_rect:
                self.canvas.delete(self.current_rect)
                self.current_rect = None

            # Check if box is big enough
            if abs(end_x - self.start_x) > 10 and abs(end_y - self.start_y) > 10:
                # Add annotation
                self.annotations.append({
                    'class': self.class_var.get(),
                    'x1': int(min(self.start_x, end_x)),
                    'y1': int(min(self.start_y, end_y)),
                    'x2': int(max(self.start_x, end_x)),
                    'y2': int(max(self.start_y, end_y))
                })

                self.draw_annotations()
                self.update_stats()

    def save_annotations(self):
        """Save annotations in YOLO format"""
        image_name = self.image_files[self.current_index].stem
        label_file = self.labeled_dir / f"{image_name}.txt"

        height, width = self.current_image.shape[:2]

        with open(label_file, 'w') as f:
            for ann in self.annotations:
                # Convert to YOLO format
                cx = (ann['x1'] + ann['x2']) / 2 / width
                cy = (ann['y1'] + ann['y2']) / 2 / height
                w = (ann['x2'] - ann['x1']) / width
                h = (ann['y2'] - ann['y1']) / height

                f.write(f"{ann['class']} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}\n")

        messagebox.showinfo("Saved", f"Annotations saved to {label_file.name}")
        self.update_stats()

    def clear_annotations(self):
        """Clear all annotations"""
        self.annotations = []
        self.draw_annotations()
        self.update_stats()

    def delete_last(self):
        """Delete the last annotation"""
        if self.annotations:
            self.annotations.pop()
            self.draw_annotations()
            self.update_stats()

    def prev_image(self):
        """Go to previous image"""
        if self.current_index > 0:
            self.current_index -= 1
            self.load_image()

    def next_image(self):
        """Go to next image"""
        if self.current_index < len(self.image_files) - 1:
            self.current_index += 1
            self.load_image()

    def on_key_press(self, event):
        """Handle keyboard shortcuts"""
        key = event.keysym.lower()

        if key == 'a':
            self.prev_image()
        elif key == 'd':
            self.next_image()
        elif key == 's':
            self.save_annotations()
        elif key == 'c':
            self.clear_annotations()
        elif key == 'x':
            self.delete_last()
        elif key in ['1', '2', '3', '4']:
            class_id = int(key) - 1
            if class_id in self.classes:
                self.class_var.set(class_id)

    def update_info(self):
        """Update image information display"""
        image_name = self.image_files[self.current_index].name
        progress = f"{self.current_index + 1} / {len(self.image_files)}"

        self.image_label.config(text=f"Image: {image_name}")
        self.progress_label.config(text=f"Progress: {progress}")

    def update_stats(self):
        """Update statistics display"""
        total_annotations = len(self.annotations)
        class_counts = {}
        for ann in self.annotations:
            class_name = self.classes[ann['class']]
            class_counts[class_name] = class_counts.get(class_name, 0) + 1

        # Count labeled images
        labeled_count = len(list(self.labeled_dir.glob("*.txt")))

        stats_text = f"Boxes: {total_annotations}\n"
        stats_text += f"Labeled images: {labeled_count}/{len(self.image_files)}\n\n"

        for class_name, count in class_counts.items():
            stats_text += f"{class_name}: {count}\n"

        self.stats_label.config(text=stats_text)

    def run(self):
        """Start the labeling tool"""
        self.root.mainloop()

def main():
    parser = argparse.ArgumentParser(description='Simple PDF Image Labeler')
    parser.add_argument('--data_dir', type=str, default='pdf_labeling_data',
                        help='Directory containing PDF images to label')

    args = parser.parse_args()

    if not Path(args.data_dir).exists():
        print(f"Error: Directory {args.data_dir} does not exist")
        return

    app = SimplePDFLabeler(args.data_dir)
    app.run()

if __name__ == "__main__":
    main()