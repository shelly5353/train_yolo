#!/usr/bin/env python3
"""
Full Page Labeler - Shows complete PDF page, no zoom complications
"""
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
from pathlib import Path

class FullPageLabeler:
    def __init__(self):
        self.data_dir = Path("pdf_labeling_data")
        self.labeled_dir = self.data_dir / "labels"
        self.labeled_dir.mkdir(exist_ok=True)

        self.classes = {0: 'straight', 1: 'L-shape', 2: 'U-shape', 3: 'complex'}
        self.colors = {0: 'red', 1: 'green', 2: 'blue', 3: 'orange'}

        self.image_files = sorted(list(self.data_dir.glob("*.png")))
        self.current_index = 0
        self.annotations = []
        self.drawing = False

        self.setup_gui()
        self.load_image()

    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("Full Page PDF Labeler")
        self.root.state('zoomed')  # Full screen

        # Left panel - controls
        control_frame = tk.Frame(self.root, width=250, bg="lightblue")
        control_frame.pack(side=tk.LEFT, fill=tk.Y)
        control_frame.pack_propagate(False)

        # Info
        tk.Label(control_frame, text="PDF Page Labeler", font=("Arial", 14, "bold"), bg="lightblue").pack(pady=10)

        self.info_label = tk.Label(control_frame, text="", bg="lightblue", font=("Arial", 10))
        self.info_label.pack(pady=5)

        # Navigation
        tk.Label(control_frame, text="Navigation:", font=("Arial", 12, "bold"), bg="lightblue").pack(pady=(20,5))
        tk.Button(control_frame, text="◄ Previous (A)", command=self.prev_image,
                 font=("Arial", 12), height=2).pack(pady=3, fill=tk.X, padx=10)
        tk.Button(control_frame, text="Next ► (D)", command=self.next_image,
                 font=("Arial", 12), height=2).pack(pady=3, fill=tk.X, padx=10)

        # Class selection
        tk.Label(control_frame, text="Shape Class:", font=("Arial", 12, "bold"), bg="lightblue").pack(pady=(20,5))

        self.class_var = tk.IntVar(value=0)
        for i, name in self.classes.items():
            color = self.colors[i]
            rb = tk.Radiobutton(control_frame, text=f"{i+1}. {name}", variable=self.class_var,
                               value=i, bg="lightblue", font=("Arial", 11), fg=color)
            rb.pack(anchor=tk.W, padx=20, pady=2)

        # Actions
        tk.Label(control_frame, text="Actions:", font=("Arial", 12, "bold"), bg="lightblue").pack(pady=(20,5))

        tk.Button(control_frame, text="💾 Save (S)", command=self.save,
                 font=("Arial", 12), height=2, bg="lightgreen").pack(pady=3, fill=tk.X, padx=10)
        tk.Button(control_frame, text="🗑️ Clear (C)", command=self.clear,
                 font=("Arial", 12), height=2, bg="lightyellow").pack(pady=3, fill=tk.X, padx=10)
        tk.Button(control_frame, text="❌ Delete Last (X)", command=self.delete_last,
                 font=("Arial", 12), height=2, bg="lightcoral").pack(pady=3, fill=tk.X, padx=10)

        # Stats
        self.stats_label = tk.Label(control_frame, text="", bg="lightblue", font=("Arial", 10))
        self.stats_label.pack(pady=20)

        # Instructions
        instructions = """
Instructions:
• Click & drag to draw boxes
• Choose shape class first
• A/D keys to navigate
• S to save, C to clear
• X to delete last box
• 1-4 keys for classes
        """
        tk.Label(control_frame, text=instructions, bg="lightblue",
                font=("Arial", 9), justify=tk.LEFT).pack(pady=10, padx=10)

        # Main canvas - fills remaining space
        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Canvas with scrollbars
        self.canvas = tk.Canvas(self.canvas_frame, bg="white")

        # Scrollbars
        v_scroll = tk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        h_scroll = tk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)

        self.canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        # Pack scrollbars and canvas
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Bind events
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw_motion)
        self.canvas.bind("<ButtonRelease-1>", self.end_draw)

        self.root.bind("<Key>", self.on_key)
        self.root.focus_set()

    def load_image(self):
        if not self.image_files:
            return

        # Load image at FULL SIZE - no scaling
        image_path = self.image_files[self.current_index]
        img = cv2.imread(str(image_path))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        self.original_img = img

        # Convert to PIL and display at FULL SIZE
        pil_img = Image.fromarray(img)
        self.photo = ImageTk.PhotoImage(pil_img)

        # Clear canvas and show full image
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

        # Set scroll region to image size
        self.canvas.configure(scrollregion=(0, 0, img.shape[1], img.shape[0]))

        # Load and draw existing annotations
        self.load_annotations()
        self.draw_annotations()
        self.update_info()

    def start_draw(self, event):
        self.drawing = True
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        self.current_rect = None

    def draw_motion(self, event):
        if self.drawing:
            if self.current_rect:
                self.canvas.delete(self.current_rect)

            current_x = self.canvas.canvasx(event.x)
            current_y = self.canvas.canvasy(event.y)

            color = self.colors[self.class_var.get()]
            self.current_rect = self.canvas.create_rectangle(
                self.start_x, self.start_y, current_x, current_y,
                outline=color, width=3, dash=(8, 4)
            )

    def end_draw(self, event):
        if self.drawing:
            self.drawing = False
            end_x = self.canvas.canvasx(event.x)
            end_y = self.canvas.canvasy(event.y)

            if self.current_rect:
                self.canvas.delete(self.current_rect)
                self.current_rect = None

            # Check if box is big enough
            if abs(end_x - self.start_x) > 15 and abs(end_y - self.start_y) > 15:
                # Add annotation (coordinates are already in image pixels)
                self.annotations.append({
                    'class': self.class_var.get(),
                    'x1': int(min(self.start_x, end_x)),
                    'y1': int(min(self.start_y, end_y)),
                    'x2': int(max(self.start_x, end_x)),
                    'y2': int(max(self.start_y, end_y))
                })

                self.draw_annotations()
                self.update_stats()

    def draw_annotations(self):
        # Remove old annotation drawings
        for item in self.canvas.find_all():
            tags = self.canvas.gettags(item)
            if "annotation" in tags:
                self.canvas.delete(item)

        # Draw all annotations
        for i, ann in enumerate(self.annotations):
            color = self.colors[ann['class']]
            class_name = self.classes[ann['class']]

            # Draw rectangle
            self.canvas.create_rectangle(
                ann['x1'], ann['y1'], ann['x2'], ann['y2'],
                outline=color, width=3, tags="annotation"
            )

            # Draw label
            self.canvas.create_text(
                ann['x1'], ann['y1'] - 10,
                text=f"{i+1}: {class_name}",
                fill=color, anchor=tk.SW, tags="annotation",
                font=("Arial", 12, "bold")
            )

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

    def save(self):
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

        self.root.title(f"Full Page Labeler - SAVED: {image_name}")
        self.root.after(2000, lambda: self.root.title("Full Page PDF Labeler"))
        self.update_stats()

    def clear(self):
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

    def on_key(self, event):
        key = event.keysym.lower()
        if key == 'a': self.prev_image()
        elif key == 'd': self.next_image()
        elif key == 's': self.save()
        elif key == 'c': self.clear()
        elif key == 'x': self.delete_last()
        elif key in ['1', '2', '3', '4']:
            self.class_var.set(int(key) - 1)

    def update_info(self):
        name = self.image_files[self.current_index].name
        progress = f"{self.current_index + 1} / {len(self.image_files)}"
        h, w = self.original_img.shape[:2]

        info = f"Image: {name}\nSize: {w}x{h}\nProgress: {progress}"
        self.info_label.config(text=info)

    def update_stats(self):
        boxes = len(self.annotations)
        labeled = len(list(self.labeled_dir.glob("*.txt")))
        total = len(self.image_files)

        stats = f"Boxes: {boxes}\nLabeled: {labeled}/{total}\nDone: {int(labeled/total*100)}%"
        self.stats_label.config(text=stats)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = FullPageLabeler()
    app.run()