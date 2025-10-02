#!/usr/bin/env python3
"""
Ultra Simple PDF Labeler
Minimal, crash-resistant labeling tool.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import cv2
from pathlib import Path
import sys

class UltraSimpleLabeler:
    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
        self.labeled_dir = self.data_dir / "labels"
        self.labeled_dir.mkdir(exist_ok=True)

        self.classes = {0: 'straight', 1: 'L-shape', 2: 'U-shape', 3: 'complex'}
        self.colors = {0: 'red', 1: 'green', 2: 'blue', 3: 'orange'}

        self.image_files = sorted(list(self.data_dir.glob("*.png")))
        if not self.image_files:
            print("No images found!")
            return

        self.current_index = 0
        self.annotations = []
        self.drawing = False
        self.start_x = 0
        self.start_y = 0
        self.current_rect = None
        self.scale = 0.5  # Start with smaller scale

        self.setup_gui()
        self.load_image()

    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("Ultra Simple PDF Labeler")
        self.root.geometry("1200x800")

        # Left panel - VERY simple
        left_frame = tk.Frame(self.root, width=200, bg="lightgray")
        left_frame.pack(side=tk.LEFT, fill=tk.Y)
        left_frame.pack_propagate(False)

        # Image info
        self.info_label = tk.Label(left_frame, text="", bg="lightgray", wraplength=180)
        self.info_label.pack(pady=10)

        # Navigation
        tk.Button(left_frame, text="← Previous (A)", command=self.prev_image, width=15).pack(pady=5)
        tk.Button(left_frame, text="Next → (D)", command=self.next_image, width=15).pack(pady=5)

        # Scale controls
        tk.Label(left_frame, text="Image Size:", bg="lightgray").pack(pady=(20,5))
        tk.Button(left_frame, text="Smaller", command=self.make_smaller, width=15).pack(pady=2)
        tk.Button(left_frame, text="Bigger", command=self.make_bigger, width=15).pack(pady=2)
        self.scale_label = tk.Label(left_frame, text="50%", bg="lightgray")
        self.scale_label.pack(pady=5)

        # Class selection - VERY simple
        tk.Label(left_frame, text="Shape Class:", bg="lightgray", font=("Arial", 10, "bold")).pack(pady=(20,5))

        self.class_var = tk.IntVar(value=0)
        for i, name in self.classes.items():
            tk.Radiobutton(left_frame, text=f"{i+1}. {name}", variable=self.class_var,
                          value=i, bg="lightgray").pack(anchor=tk.W, padx=10)

        # Actions
        tk.Label(left_frame, text="Actions:", bg="lightgray", font=("Arial", 10, "bold")).pack(pady=(20,5))
        tk.Button(left_frame, text="Save (S)", command=self.save_annotations, width=15, bg="lightgreen").pack(pady=2)
        tk.Button(left_frame, text="Clear (C)", command=self.clear_annotations, width=15, bg="yellow").pack(pady=2)
        tk.Button(left_frame, text="Delete Last (X)", command=self.delete_last, width=15, bg="pink").pack(pady=2)

        # Stats
        self.stats_label = tk.Label(left_frame, text="", bg="lightgray", wraplength=180)
        self.stats_label.pack(pady=20)

        # Right panel - Canvas ONLY
        self.canvas = tk.Canvas(self.root, bg="white")
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Simple bindings
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw_motion)
        self.canvas.bind("<ButtonRelease-1>", self.end_draw)

        self.root.bind("<Key>", self.on_key_press)
        self.root.focus_set()

    def load_image(self):
        try:
            if not self.image_files:
                return

            image_path = self.image_files[self.current_index]
            print(f"Loading: {image_path.name}")

            # Load with OpenCV
            img = cv2.imread(str(image_path))
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # Resize to manageable size
            h, w = img.shape[:2]
            new_w = int(w * self.scale)
            new_h = int(h * self.scale)

            self.original_img = img
            self.display_img = cv2.resize(img, (new_w, new_h))

            # Convert to PIL
            pil_img = Image.fromarray(self.display_img)
            self.photo = ImageTk.PhotoImage(pil_img)

            # Clear canvas and add image
            self.canvas.delete("all")
            self.canvas.create_image(10, 10, anchor=tk.NW, image=self.photo)

            # Load annotations
            self.load_annotations()
            self.draw_annotations()
            self.update_info()

        except Exception as e:
            print(f"Error loading image: {e}")
            messagebox.showerror("Error", f"Could not load image: {e}")

    def make_smaller(self):
        self.scale = max(0.2, self.scale - 0.1)
        self.scale_label.config(text=f"{int(self.scale*100)}%")
        self.load_image()

    def make_bigger(self):
        self.scale = min(1.0, self.scale + 0.1)
        self.scale_label.config(text=f"{int(self.scale*100)}%")
        self.load_image()

    def start_draw(self, event):
        self.drawing = True
        self.start_x = event.x
        self.start_y = event.y

    def draw_motion(self, event):
        if self.drawing:
            if self.current_rect:
                self.canvas.delete(self.current_rect)

            color = self.colors[self.class_var.get()]
            self.current_rect = self.canvas.create_rectangle(
                self.start_x, self.start_y, event.x, event.y,
                outline=color, width=2, dash=(5, 5)
            )

    def end_draw(self, event):
        if self.drawing:
            self.drawing = False

            if self.current_rect:
                self.canvas.delete(self.current_rect)
                self.current_rect = None

            # Check if box is big enough
            if abs(event.x - self.start_x) > 10 and abs(event.y - self.start_y) > 10:
                # Convert to original image coordinates
                x1 = int((min(self.start_x, event.x) - 10) / self.scale)
                y1 = int((min(self.start_y, event.y) - 10) / self.scale)
                x2 = int((max(self.start_x, event.x) - 10) / self.scale)
                y2 = int((max(self.start_y, event.y) - 10) / self.scale)

                # Add annotation
                self.annotations.append({
                    'class': self.class_var.get(),
                    'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2
                })

                self.draw_annotations()
                self.update_stats()

    def draw_annotations(self):
        # Clear existing annotations
        items = self.canvas.find_all()
        for item in items:
            tags = self.canvas.gettags(item)
            if "annotation" in tags:
                self.canvas.delete(item)

        # Draw all annotations
        for i, ann in enumerate(self.annotations):
            color = self.colors[ann['class']]
            class_name = self.classes[ann['class']]

            # Scale coordinates for display
            x1 = int(ann['x1'] * self.scale) + 10
            y1 = int(ann['y1'] * self.scale) + 10
            x2 = int(ann['x2'] * self.scale) + 10
            y2 = int(ann['y2'] * self.scale) + 10

            # Draw rectangle
            self.canvas.create_rectangle(x1, y1, x2, y2, outline=color, width=2, tags="annotation")

            # Draw label
            self.canvas.create_text(x1, y1-15, text=f"{i+1}:{class_name}",
                                  fill=color, anchor=tk.SW, tags="annotation")

    def load_annotations(self):
        self.annotations = []
        image_name = self.image_files[self.current_index].stem
        label_file = self.labeled_dir / f"{image_name}.txt"

        if label_file.exists():
            height, width = self.original_img.shape[:2]

            with open(label_file, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) == 5:
                        class_id = int(parts[0])
                        cx, cy, w, h = map(float, parts[1:])

                        # Convert from YOLO to pixel coordinates
                        x1 = int((cx - w/2) * width)
                        y1 = int((cy - h/2) * height)
                        x2 = int((cx + w/2) * width)
                        y2 = int((cy + h/2) * height)

                        self.annotations.append({
                            'class': class_id,
                            'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2
                        })

    def save_annotations(self):
        try:
            image_name = self.image_files[self.current_index].stem
            label_file = self.labeled_dir / f"{image_name}.txt"

            height, width = self.original_img.shape[:2]

            with open(label_file, 'w') as f:
                for ann in self.annotations:
                    # Convert to YOLO format
                    cx = (ann['x1'] + ann['x2']) / 2 / width
                    cy = (ann['y1'] + ann['y2']) / 2 / height
                    w = (ann['x2'] - ann['x1']) / width
                    h = (ann['y2'] - ann['y1']) / height

                    f.write(f"{ann['class']} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}\n")

            self.root.title(f"SAVED: {image_name}")
            self.root.after(1000, lambda: self.root.title("Ultra Simple PDF Labeler"))
            self.update_stats()
            print(f"Saved: {image_name}")

        except Exception as e:
            print(f"Save error: {e}")

    def clear_annotations(self):
        self.annotations = []
        self.draw_annotations()
        self.update_stats()

    def delete_last(self):
        if self.annotations:
            self.annotations.pop()
            self.draw_annotations()
            self.update_stats()

    def prev_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.load_image()

    def next_image(self):
        if self.current_index < len(self.image_files) - 1:
            self.current_index += 1
            self.load_image()

    def on_key_press(self, event):
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
            self.class_var.set(int(key) - 1)

    def update_info(self):
        image_name = self.image_files[self.current_index].name
        progress = f"{self.current_index + 1}/{len(self.image_files)}"

        info_text = f"Image:\n{image_name}\n\nProgress:\n{progress}"
        self.info_label.config(text=info_text)

    def update_stats(self):
        total = len(self.annotations)
        labeled_count = len(list(self.labeled_dir.glob("*.txt")))

        stats_text = f"Boxes: {total}\nLabeled: {labeled_count}/{len(self.image_files)}"
        self.stats_label.config(text=stats_text)

    def run(self):
        self.root.mainloop()

def main():
    data_dir = "pdf_labeling_data"
    if not Path(data_dir).exists():
        print(f"Directory {data_dir} not found!")
        return

    app = UltraSimpleLabeler(data_dir)
    app.run()

if __name__ == "__main__":
    main()