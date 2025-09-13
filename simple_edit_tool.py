#!/usr/bin/env python3
"""
Simple YOLO Label Editor
Loads pre-generated labels and allows editing
"""

import os
import cv2
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

class SimpleYOLOEditor:
    def __init__(self, output_dir="labeld_data"):
        self.output_dir = Path(output_dir)

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

        # Load all images from output directory
        self.image_files = sorted(list(self.output_dir.glob("*.png")))
        print(f"Found {len(self.image_files)} images to edit")

        if not self.image_files:
            print("No images found in labeld_data/ directory!")
            print("Run batch_detect.py first to generate initial labels.")
            return

        self.setup_gui()
        self.load_image()

    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title(f"Simple YOLO Editor - {len(self.image_files)} images")
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

        # Stats
        self.stats_label = ttk.Label(nav_frame, text="", font=('Arial', 10))
        self.stats_label.pack(side=tk.LEFT, padx=20)

        # Class selection
        class_frame = ttk.Frame(control_frame)
        class_frame.pack(side=tk.LEFT, padx=20)

        ttk.Label(class_frame, text="Add Class:").pack(side=tk.LEFT)
        self.class_var = tk.StringVar(value="0: straight")
        class_combo = ttk.Combobox(class_frame, textvariable=self.class_var, width=15, state="readonly")
        class_combo['values'] = [f"{k}: {v}" for k, v in self.classes.items()]
        class_combo.bind('<<ComboboxSelected>>', self.on_class_change)
        class_combo.pack(side=tk.LEFT, padx=5)

        # Actions
        action_frame = ttk.Frame(control_frame)
        action_frame.pack(side=tk.RIGHT)

        ttk.Button(action_frame, text="Clear All", command=self.clear_labels).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Save", command=self.save_labels).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Save & Next", command=self.save_and_next).pack(side=tk.LEFT, padx=5)

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

        self.status_var = tk.StringVar(value="Ready to edit pre-generated labels")
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var, font=('Arial', 10, 'bold'))
        self.status_label.pack(side=tk.LEFT)

        instructions = "Left drag: add box | Right click: delete box | Arrow keys: navigate | Space: save & next"
        ttk.Label(status_frame, text=instructions, font=('Arial', 9)).pack(side=tk.RIGHT)

        # Bind keyboard shortcuts
        self.root.bind('<Left>', lambda e: self.prev_image())
        self.root.bind('<Right>', lambda e: self.next_image())
        self.root.bind('<space>', lambda e: self.save_and_next())
        self.root.bind('<Delete>', lambda e: self.clear_labels())
        self.root.bind('<s>', lambda e: self.save_labels())
        self.root.bind('<S>', lambda e: self.save_labels())

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

        # Use original size for better precision
        self.display_width = self.img_width
        self.display_height = self.img_height
        self.scale_factor = 1.0

        self.photo = ImageTk.PhotoImage(Image.fromarray(image_rgb))

        # Update canvas
        self.canvas.delete("all")
        self.canvas.config(scrollregion=(0, 0, self.display_width, self.display_height))
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

        # Load existing labels
        self.load_existing_labels()
        self.draw_all_boxes()

        # Update stats
        total_processed = len([f for f in self.output_dir.glob("*.txt")])
        self.stats_label.config(text=f"Labels: {len(self.current_labels)} | Processed: {self.current_image_idx + 1}/{total_processed}")

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

        self.status_var.set(f"Loaded {len(self.current_labels)} existing labels - Edit as needed")

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
        x1 = x1 / self.scale_factor
        y1 = y1 / self.scale_factor
        x2 = x2 / self.scale_factor
        y2 = y2 / self.scale_factor

        x_center = (x1 + x2) / 2 / self.img_width
        y_center = (y1 + y2) / 2 / self.img_height
        width = (x2 - x1) / self.img_width
        height = (y2 - y1) / self.img_height

        return x_center, y_center, width, height

    def draw_all_boxes(self):
        """Draw all existing bounding boxes"""
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
            self.canvas.create_rectangle(x1, y1-25, x1+len(label_text)*8, y1-5,
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
        self.status_var.set("All labels cleared")

    def save_labels(self):
        """Save current labels in YOLO format"""
        image_path = self.image_files[self.current_image_idx]
        label_file = self.output_dir / f"{image_path.stem}.txt"

        with open(label_file, 'w') as f:
            for label in self.current_labels:
                class_id, x_center, y_center, width, height = label
                f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")

        self.status_var.set(f"Saved {len(self.current_labels)} labels for {image_path.name}")
        print(f"Saved: {image_path.name} with {len(self.current_labels)} labels")

    def save_and_next(self):
        self.save_labels()
        self.next_image()

    def next_image(self):
        if self.current_image_idx < len(self.image_files) - 1:
            self.current_image_idx += 1
            self.load_image()
        else:
            messagebox.showinfo("Complete", f"All {len(self.image_files)} images reviewed!")

    def prev_image(self):
        if self.current_image_idx > 0:
            self.current_image_idx -= 1
            self.load_image()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    tool = SimpleYOLOEditor()
    if tool.image_files:
        tool.run()