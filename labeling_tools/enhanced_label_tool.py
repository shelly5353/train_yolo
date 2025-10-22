#!/usr/bin/env python3
"""
Enhanced YOLO Image Labeling Tool
Runs your trained model first to detect objects, then allows editing
"""

import os
import cv2
import json
import glob
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import torch
from ultralytics import YOLO

class EnhancedYOLOLabelTool:
    def __init__(self, data_dir="data", output_dir="labeld_data", model_path="best.pt"):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Load your trained model
        print(f"Loading YOLO model from {model_path}...")
        self.model = YOLO(model_path)

        # YOLO classes from your model
        self.classes = {
            0: 'straight',
            1: 'L-shape',
            2: 'U-shape',
            3: 'complex'
        }

        self.current_image_idx = 0
        self.current_labels = []
        self.drawing = False
        self.start_x = self.start_y = 0
        self.current_class = 0

        # Load all images
        self.image_files = sorted(list(self.data_dir.glob("*.png")))
        print(f"Found {len(self.image_files)} images to label")

        self.setup_gui()
        self.load_image()

    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title(f"Enhanced YOLO Labeling Tool - {len(self.image_files)} images")
        self.root.geometry("1400x900")

        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Control panel
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        # Navigation
        nav_frame = ttk.Frame(control_frame)
        nav_frame.pack(side=tk.LEFT)

        ttk.Button(nav_frame, text="Previous", command=self.prev_image).pack(side=tk.LEFT, padx=5)
        self.image_label = ttk.Label(nav_frame, text="")
        self.image_label.pack(side=tk.LEFT, padx=10)
        ttk.Button(nav_frame, text="Next", command=self.next_image).pack(side=tk.LEFT, padx=5)

        # Class selection
        class_frame = ttk.Frame(control_frame)
        class_frame.pack(side=tk.LEFT, padx=20)

        ttk.Label(class_frame, text="Class:").pack(side=tk.LEFT)
        self.class_var = tk.StringVar(value="0: straight")
        class_combo = ttk.Combobox(class_frame, textvariable=self.class_var, width=15, state="readonly")
        class_combo['values'] = [f"{k}: {v}" for k, v in self.classes.items()]
        class_combo.bind('<<ComboboxSelected>>', self.on_class_change)
        class_combo.pack(side=tk.LEFT, padx=5)

        # Model actions
        model_frame = ttk.Frame(control_frame)
        model_frame.pack(side=tk.LEFT, padx=20)

        ttk.Button(model_frame, text="Run Model", command=self.run_model_detection).pack(side=tk.LEFT, padx=5)
        self.confidence_var = tk.DoubleVar(value=0.25)
        ttk.Label(model_frame, text="Conf:").pack(side=tk.LEFT, padx=(10,0))
        conf_scale = ttk.Scale(model_frame, from_=0.1, to=0.9, variable=self.confidence_var, orient=tk.HORIZONTAL, length=100)
        conf_scale.pack(side=tk.LEFT, padx=5)

        # Actions
        action_frame = ttk.Frame(control_frame)
        action_frame.pack(side=tk.RIGHT)

        ttk.Button(action_frame, text="Clear All", command=self.clear_labels).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Save & Next", command=self.save_and_next).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Skip", command=self.next_image).pack(side=tk.LEFT, padx=5)

        # Image canvas frame
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        # Canvas with scrollbars
        canvas_container = ttk.Frame(canvas_frame)
        canvas_container.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(canvas_container, bg="white")
        h_scrollbar = ttk.Scrollbar(canvas_container, orient="horizontal", command=self.canvas.xview)
        v_scrollbar = ttk.Scrollbar(canvas_container, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)

        h_scrollbar.pack(side="bottom", fill="x")
        v_scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Bind mouse events
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw_rect)
        self.canvas.bind("<ButtonRelease-1>", self.end_draw)
        self.canvas.bind("<Button-3>", self.delete_bbox)  # Right click to delete

        # Status and instructions
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(10, 0))

        self.status_var = tk.StringVar(value="Ready - Click 'Run Model' to auto-detect objects")
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var, font=('Arial', 10, 'bold'))
        self.status_label.pack(side=tk.LEFT)

        instructions = "Left drag: draw box | Right click: delete box | Run Model: auto-detect | Arrow keys: navigate"
        ttk.Label(status_frame, text=instructions, font=('Arial', 9)).pack(side=tk.RIGHT)

        # Bind keyboard shortcuts
        self.root.bind('<Left>', lambda e: self.prev_image())
        self.root.bind('<Right>', lambda e: self.next_image())
        self.root.bind('<space>', lambda e: self.save_and_next())
        self.root.bind('<Delete>', lambda e: self.clear_labels())
        self.root.bind('<r>', lambda e: self.run_model_detection())
        self.root.bind('<R>', lambda e: self.run_model_detection())

        self.root.focus_set()

    def load_image(self):
        if not self.image_files or self.current_image_idx >= len(self.image_files):
            return

        image_path = self.image_files[self.current_image_idx]
        self.image_label.config(text=f"{self.current_image_idx + 1}/{len(self.image_files)}: {image_path.name}")

        # Load image
        self.original_image = cv2.imread(str(image_path))
        self.img_height, self.img_width = self.original_image.shape[:2]

        # Convert for display
        image_rgb = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)

        # Use original size for better labeling precision
        self.display_width = self.img_width
        self.display_height = self.img_height
        self.scale_factor = 1.0

        self.photo = ImageTk.PhotoImage(Image.fromarray(image_rgb))

        # Update canvas
        self.canvas.delete("all")
        self.canvas.config(scrollregion=(0, 0, self.display_width, self.display_height))
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

        # Load existing labels if they exist
        self.load_existing_labels()
        self.draw_all_boxes()

        # Update status
        self.status_var.set(f"Image loaded. {len(self.current_labels)} existing labels. Press 'Run Model' to detect objects.")

    def run_model_detection(self):
        """Run your trained model to detect objects in the current image"""
        if not hasattr(self, 'original_image'):
            return

        self.status_var.set("Running model detection...")
        self.root.update()

        try:
            # Run inference
            results = self.model(self.original_image, conf=self.confidence_var.get(), verbose=False)

            # Clear existing labels and add model predictions
            self.current_labels = []

            # Process detections
            if results and len(results) > 0:
                detections = results[0]
                if detections.boxes is not None:
                    boxes = detections.boxes

                    for i in range(len(boxes)):
                        # Get box coordinates (xyxy format)
                        x1, y1, x2, y2 = boxes.xyxy[i].cpu().numpy()
                        confidence = boxes.conf[i].cpu().numpy()
                        class_id = int(boxes.cls[i].cpu().numpy())

                        # Convert to YOLO format (normalized center coordinates)
                        x_center = ((x1 + x2) / 2) / self.img_width
                        y_center = ((y1 + y2) / 2) / self.img_height
                        width = (x2 - x1) / self.img_width
                        height = (y2 - y1) / self.img_height

                        self.current_labels.append([class_id, x_center, y_center, width, height])

            # Redraw all boxes
            self.draw_all_boxes()

            detected_count = len(self.current_labels)
            self.status_var.set(f"Model detected {detected_count} objects. Edit as needed, then Save & Next.")

        except Exception as e:
            self.status_var.set(f"Model error: {str(e)}")
            print(f"Detection error: {e}")

    def load_existing_labels(self):
        """Load existing YOLO format labels"""
        image_path = self.image_files[self.current_image_idx]
        label_file = self.output_dir / f"{image_path.stem}.txt"

        self.current_labels = []
        if label_file.exists():
            with open(label_file, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) == 5:
                        class_id = int(parts[0])
                        x_center = float(parts[1])
                        y_center = float(parts[2])
                        width = float(parts[3])
                        height = float(parts[4])
                        self.current_labels.append([class_id, x_center, y_center, width, height])

    def yolo_to_pixel(self, yolo_coords):
        """Convert YOLO format (normalized) to pixel coordinates"""
        class_id, x_center, y_center, width, height = yolo_coords

        x1 = int((x_center - width/2) * self.img_width * self.scale_factor)
        y1 = int((y_center - height/2) * self.img_height * self.scale_factor)
        x2 = int((x_center + width/2) * self.img_width * self.scale_factor)
        y2 = int((y_center + height/2) * self.img_height * self.scale_factor)

        return x1, y1, x2, y2

    def pixel_to_yolo(self, x1, y1, x2, y2):
        """Convert pixel coordinates to YOLO format (normalized)"""
        # Convert from display coordinates to original image coordinates
        x1 = x1 / self.scale_factor
        y1 = y1 / self.scale_factor
        x2 = x2 / self.scale_factor
        y2 = y2 / self.scale_factor

        # Convert to YOLO format
        x_center = (x1 + x2) / 2 / self.img_width
        y_center = (y1 + y2) / 2 / self.img_height
        width = (x2 - x1) / self.img_width
        height = (y2 - y1) / self.img_height

        return x_center, y_center, width, height

    def draw_all_boxes(self):
        """Draw all existing bounding boxes"""
        # Clear existing boxes
        self.canvas.delete("bbox")

        colors = ['red', 'blue', 'green', 'orange']
        for i, label in enumerate(self.current_labels):
            class_id = label[0]
            x1, y1, x2, y2 = self.yolo_to_pixel(label)

            color = colors[class_id % len(colors)]
            tag = f"bbox_{i}"

            # Draw rectangle
            self.canvas.create_rectangle(x1, y1, x2, y2, outline=color, width=3, tags=(tag, "bbox"))

            # Draw class label with background
            class_name = self.classes[class_id]
            label_text = f"{class_id}: {class_name}"

            # Create text background
            text_bg = self.canvas.create_rectangle(x1, y1-25, x1+len(label_text)*8, y1-5,
                                                 fill=color, outline=color, tags=(tag, "bbox"))
            self.canvas.create_text(x1+2, y1-15, text=label_text, fill="white",
                                  anchor=tk.W, font=('Arial', 9, 'bold'), tags=(tag, "bbox"))

    def start_draw(self, event):
        self.drawing = True
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)

    def draw_rect(self, event):
        if self.drawing:
            current_x = self.canvas.canvasx(event.x)
            current_y = self.canvas.canvasy(event.y)
            self.canvas.delete("temp_rect")
            self.canvas.create_rectangle(self.start_x, self.start_y, current_x, current_y,
                                       outline="yellow", width=3, tags="temp_rect")

    def end_draw(self, event):
        if self.drawing:
            self.drawing = False
            current_x = self.canvas.canvasx(event.x)
            current_y = self.canvas.canvasy(event.y)
            self.canvas.delete("temp_rect")

            # Only add if rectangle is big enough
            if abs(current_x - self.start_x) > 20 and abs(current_y - self.start_y) > 20:
                x1, y1 = min(self.start_x, current_x), min(self.start_y, current_y)
                x2, y2 = max(self.start_x, current_x), max(self.start_y, current_y)

                # Convert to YOLO format
                x_center, y_center, width, height = self.pixel_to_yolo(x1, y1, x2, y2)

                # Add label
                self.current_labels.append([self.current_class, x_center, y_center, width, height])
                self.draw_all_boxes()

                self.status_var.set(f"Added {self.classes[self.current_class]} box. Total: {len(self.current_labels)} labels")

    def delete_bbox(self, event):
        """Delete bounding box on right click"""
        click_x = self.canvas.canvasx(event.x)
        click_y = self.canvas.canvasy(event.y)

        # Find which bbox was clicked
        overlapping = self.canvas.find_overlapping(click_x-5, click_y-5, click_x+5, click_y+5)

        for item in overlapping:
            tags = self.canvas.gettags(item)
            for tag in tags:
                if tag.startswith("bbox_"):
                    idx = int(tag.split("_")[1])
                    if idx < len(self.current_labels):
                        deleted_class = self.classes[self.current_labels[idx][0]]
                        del self.current_labels[idx]
                        self.draw_all_boxes()
                        self.status_var.set(f"Deleted {deleted_class} box. Total: {len(self.current_labels)} labels")
                        return

    def on_class_change(self, event=None):
        selected = self.class_var.get()
        self.current_class = int(selected.split(":")[0])

    def clear_labels(self):
        self.current_labels = []
        self.draw_all_boxes()
        self.status_var.set("All labels cleared. Draw new boxes or run model detection.")

    def save_labels(self):
        """Save current labels in YOLO format"""
        image_path = self.image_files[self.current_image_idx]

        # Save image to output directory
        output_image_path = self.output_dir / image_path.name
        cv2.imwrite(str(output_image_path), self.original_image)

        # Save labels
        label_file = self.output_dir / f"{image_path.stem}.txt"
        with open(label_file, 'w') as f:
            for label in self.current_labels:
                class_id, x_center, y_center, width, height = label
                f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")

        self.status_var.set(f"Saved: {output_image_path.name} with {len(self.current_labels)} labels")
        print(f"Saved: {output_image_path.name} with {len(self.current_labels)} labels")

    def save_and_next(self):
        self.save_labels()
        self.next_image()

    def next_image(self):
        if self.current_image_idx < len(self.image_files) - 1:
            self.current_image_idx += 1
            self.load_image()
        else:
            messagebox.showinfo("Complete", f"All {len(self.image_files)} images processed!")

    def prev_image(self):
        if self.current_image_idx > 0:
            self.current_image_idx -= 1
            self.load_image()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    import sys

    # Check if directories and model exist
    if not os.path.exists("data"):
        print("Error: 'data' directory not found!")
        sys.exit(1)

    if not os.path.exists("best.pt"):
        print("Error: 'best.pt' model file not found!")
        sys.exit(1)

    tool = EnhancedYOLOLabelTool()
    tool.run()