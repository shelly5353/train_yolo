#!/usr/bin/env python3
"""
Improved PDF Image Labeler
A tkinter-based tool with zoom and better image viewing for large PDF images.
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
from pathlib import Path
import argparse

class ImprovedPDFLabeler:
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
        self.original_image = None
        self.current_photo = None
        self.annotations = []
        self.drawing = False
        self.start_x = 0
        self.start_y = 0
        self.current_rect = None
        self.selected_class = 0
        self.scale_factor = 1.0

        # Setup GUI
        self.setup_gui()
        self.load_image()

    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("Improved PDF Image Labeler")
        self.root.geometry("1600x1000")

        # Try to maximize window
        try:
            self.root.state('zoomed')  # Windows
        except:
            try:
                self.root.attributes('-zoomed', True)  # Linux
            except:
                pass  # macOS doesn't have this

        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Control panel (left side)
        control_frame = ttk.Frame(main_frame, width=280)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        control_frame.pack_propagate(False)

        # Image info
        info_frame = ttk.LabelFrame(control_frame, text="Image Info")
        info_frame.pack(fill=tk.X, pady=(0, 5))

        self.image_label = ttk.Label(info_frame, text="", wraplength=260, font=("Arial", 9))
        self.image_label.pack(pady=2)

        self.progress_label = ttk.Label(info_frame, text="", font=("Arial", 9, "bold"))
        self.progress_label.pack(pady=2)

        # Zoom controls
        zoom_frame = ttk.LabelFrame(control_frame, text="Zoom & View")
        zoom_frame.pack(fill=tk.X, pady=(0, 5))

        self.zoom_var = tk.DoubleVar(value=1.0)

        zoom_buttons = ttk.Frame(zoom_frame)
        zoom_buttons.pack(fill=tk.X, pady=2)

        ttk.Button(zoom_buttons, text="Fit", command=self.fit_to_window, width=8).pack(side=tk.LEFT, padx=1)
        ttk.Button(zoom_buttons, text="100%", command=self.zoom_100, width=8).pack(side=tk.LEFT, padx=1)
        ttk.Button(zoom_buttons, text="200%", command=self.zoom_200, width=8).pack(side=tk.LEFT, padx=1)

        zoom_controls = ttk.Frame(zoom_frame)
        zoom_controls.pack(fill=tk.X, pady=2)

        ttk.Button(zoom_controls, text="- Out", command=self.zoom_out, width=8).pack(side=tk.LEFT, padx=1)
        ttk.Button(zoom_controls, text="+ In", command=self.zoom_in, width=8).pack(side=tk.LEFT, padx=1)

        self.zoom_label = ttk.Label(zoom_frame, text="100%", font=("Arial", 10, "bold"))
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
            btn = ttk.Radiobutton(class_frame, text=f"{class_id+1}. {class_name}",
                          variable=self.class_var, value=class_id)
            btn.pack(anchor=tk.W, pady=1)

        # Actions
        action_frame = ttk.LabelFrame(control_frame, text="Actions")
        action_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Button(action_frame, text="💾 Save (S)", command=self.save_annotations).pack(fill=tk.X, pady=1)
        ttk.Button(action_frame, text="🗑️ Clear All (C)", command=self.clear_annotations).pack(fill=tk.X, pady=1)
        ttk.Button(action_frame, text="❌ Delete Last (X)", command=self.delete_last).pack(fill=tk.X, pady=1)

        # Statistics
        stats_frame = ttk.LabelFrame(control_frame, text="Statistics")
        stats_frame.pack(fill=tk.X, pady=(0, 5))

        self.stats_label = ttk.Label(stats_frame, text="", wraplength=260, font=("Arial", 9))
        self.stats_label.pack(pady=2)

        # Instructions
        instructions_frame = ttk.LabelFrame(control_frame, text="Shortcuts")
        instructions_frame.pack(fill=tk.X, expand=True)

        instructions = [
            "• Click & drag to draw boxes",
            "• Select class first (1-4 keys)",
            "• A/D: Previous/Next image",
            "• Mouse wheel: Zoom in/out",
            "• +/-: Zoom in/out",
            "• S: Save annotations",
            "• C: Clear all boxes",
            "• X: Delete last box"
        ]

        for instruction in instructions:
            ttk.Label(instructions_frame, text=instruction, font=("Arial", 8)).pack(anchor=tk.W, pady=0)

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

        # Mouse wheel binding for both platforms
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)  # Windows/Mac
        self.canvas.bind("<Button-4>", self.on_mousewheel)    # Linux scroll up
        self.canvas.bind("<Button-5>", self.on_mousewheel)    # Linux scroll down

        # Keyboard bindings
        self.root.bind("<Key>", self.on_key_press)
        self.root.focus_set()

    def load_image(self):
        """Load and display the current image"""
        if not self.image_files:
            return

        # Load image
        image_path = self.image_files[self.current_index]
        self.original_image = cv2.imread(str(image_path))
        self.original_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)

        # Start with fit to window
        self.root.after(100, self.fit_to_window)

        # Load existing annotations
        self.load_annotations()

        # Update info
        self.update_info()
        self.update_stats()

    def update_image_display(self):
        """Update the image display with current scaling"""
        if self.original_image is None:
            return

        # Scale image
        height, width = self.original_image.shape[:2]
        new_width = int(width * self.scale_factor)
        new_height = int(height * self.scale_factor)

        # Resize image
        if self.scale_factor != 1.0:
            self.current_image = cv2.resize(self.original_image, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
        else:
            self.current_image = self.original_image

        # Create PIL image for display
        pil_image = Image.fromarray(self.current_image)
        self.current_photo = ImageTk.PhotoImage(pil_image)

        # Update canvas
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.current_photo)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        # Redraw annotations
        self.draw_annotations()

        # Update zoom label
        self.zoom_label.config(text=f"{int(self.scale_factor * 100)}%")

    def fit_to_window(self):
        """Fit image to canvas window"""
        if self.original_image is None:
            return

        # Get canvas size
        self.canvas.update_idletasks()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width <= 1 or canvas_height <= 1:
            # Canvas not ready, try again later
            self.root.after(100, self.fit_to_window)
            return

        # Calculate scale to fit
        img_height, img_width = self.original_image.shape[:2]
        scale_x = (canvas_width - 40) / img_width  # Leave margin for scrollbars
        scale_y = (canvas_height - 40) / img_height
        self.scale_factor = min(scale_x, scale_y, 1.0)  # Don't scale up beyond 100%

        self.update_image_display()

    def zoom_100(self):
        """Set zoom to 100%"""
        self.scale_factor = 1.0
        self.update_image_display()

    def zoom_200(self):
        """Set zoom to 200%"""
        self.scale_factor = 2.0
        self.update_image_display()

    def zoom_in(self):
        """Zoom in"""
        self.scale_factor = min(self.scale_factor * 1.25, 5.0)  # Max 500%
        self.update_image_display()

    def zoom_out(self):
        """Zoom out"""
        self.scale_factor = max(self.scale_factor / 1.25, 0.1)  # Min 10%
        self.update_image_display()

    def on_mousewheel(self, event):
        """Handle mouse wheel for zooming"""
        # Check if mouse is over canvas
        x, y = event.x_root - self.canvas.winfo_rootx(), event.y_root - self.canvas.winfo_rooty()
        if 0 <= x <= self.canvas.winfo_width() and 0 <= y <= self.canvas.winfo_height():
            if event.delta > 0 or event.num == 4:
                self.zoom_in()
            elif event.delta < 0 or event.num == 5:
                self.zoom_out()

    def load_annotations(self):
        """Load existing annotations for current image"""
        self.annotations = []
        image_name = self.image_files[self.current_index].stem
        label_file = self.labeled_dir / f"{image_name}.txt"

        if label_file.exists():
            height, width = self.original_image.shape[:2]
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

    def draw_annotations(self):
        """Draw all annotations on the canvas"""
        # Clear existing annotation drawings
        self.canvas.delete("annotation")

        for i, ann in enumerate(self.annotations):
            color = self.class_colors[ann['class']]
            class_name = self.classes[ann['class']]

            # Scale coordinates
            x1 = int(ann['x1'] * self.scale_factor)
            y1 = int(ann['y1'] * self.scale_factor)
            x2 = int(ann['x2'] * self.scale_factor)
            y2 = int(ann['y2'] * self.scale_factor)

            # Draw rectangle
            self.canvas.create_rectangle(
                x1, y1, x2, y2,
                outline=color, width=2, tags="annotation"
            )

            # Draw label with background
            text = f"{i+1}: {class_name}"
            text_obj = self.canvas.create_text(
                x1, y1 - 15,
                text=text,
                fill=color, anchor=tk.SW, tags="annotation",
                font=("Arial", 10, "bold")
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
                outline=color, width=3, dash=(8, 4)
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
                # Convert canvas coordinates back to original image coordinates
                x1 = int(min(self.start_x, end_x) / self.scale_factor)
                y1 = int(min(self.start_y, end_y) / self.scale_factor)
                x2 = int(max(self.start_x, end_x) / self.scale_factor)
                y2 = int(max(self.start_y, end_y) / self.scale_factor)

                # Add annotation
                self.annotations.append({
                    'class': self.class_var.get(),
                    'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2
                })

                self.draw_annotations()
                self.update_stats()

    def save_annotations(self):
        """Save annotations in YOLO format"""
        image_name = self.image_files[self.current_index].stem
        label_file = self.labeled_dir / f"{image_name}.txt"

        height, width = self.original_image.shape[:2]

        with open(label_file, 'w') as f:
            for ann in self.annotations:
                # Convert to YOLO format
                cx = (ann['x1'] + ann['x2']) / 2 / width
                cy = (ann['y1'] + ann['y2']) / 2 / height
                w = (ann['x2'] - ann['x1']) / width
                h = (ann['y2'] - ann['y1']) / height

                f.write(f"{ann['class']} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}\n")

        # Show success message briefly
        self.root.title(f"PDF Labeler - SAVED: {image_name}")
        self.root.after(1000, lambda: self.root.title("Improved PDF Image Labeler"))
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
        elif key == 'plus' or key == 'equal':
            self.zoom_in()
        elif key == 'minus':
            self.zoom_out()

    def update_info(self):
        """Update image information display"""
        image_name = self.image_files[self.current_index].name
        progress = f"{self.current_index + 1} / {len(self.image_files)}"

        # Get image dimensions
        if self.original_image is not None:
            height, width = self.original_image.shape[:2]
            size_info = f"({width}x{height})"
        else:
            size_info = ""

        self.image_label.config(text=f"{image_name}\n{size_info}")
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
        completion = f"{labeled_count}/{len(self.image_files)}"

        stats_text = f"📦 Boxes on image: {total_annotations}\n"
        stats_text += f"✅ Labeled images: {completion}\n"
        stats_text += f"📊 Progress: {int(labeled_count/len(self.image_files)*100)}%\n\n"

        if class_counts:
            stats_text += "Current image breakdown:\n"
            for class_name, count in class_counts.items():
                stats_text += f"  • {class_name}: {count}\n"

        self.stats_label.config(text=stats_text)

    def run(self):
        """Start the labeling tool"""
        self.root.mainloop()

def main():
    parser = argparse.ArgumentParser(description='Improved PDF Image Labeler')
    parser.add_argument('--data_dir', type=str, default='pdf_labeling_data',
                        help='Directory containing PDF images to label')

    args = parser.parse_args()

    if not Path(args.data_dir).exists():
        print(f"Error: Directory {args.data_dir} does not exist")
        return

    app = ImprovedPDFLabeler(args.data_dir)
    app.run()

if __name__ == "__main__":
    main()