#!/usr/bin/env python3
"""
Click-to-Delete PDF Labeler
Full page viewing + click any box to delete it
"""
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
from pathlib import Path
import math

class ClickDeleteLabeler:
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
        self.delete_mode = False

        self.setup_gui()
        self.load_image()

    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("Click-to-Delete PDF Labeler")
        self.root.state('zoomed')

        # Left panel
        control_frame = tk.Frame(self.root, width=280, bg="lightgray")
        control_frame.pack(side=tk.LEFT, fill=tk.Y)
        control_frame.pack_propagate(False)

        # Title
        tk.Label(control_frame, text="PDF Labeler", font=("Arial", 16, "bold"), bg="lightgray").pack(pady=10)

        # Info
        self.info_label = tk.Label(control_frame, text="", bg="lightgray", font=("Arial", 10))
        self.info_label.pack(pady=5)

        # Mode selection
        tk.Label(control_frame, text="MODE:", font=("Arial", 14, "bold"), bg="lightgray").pack(pady=(20,5))

        self.mode_var = tk.StringVar(value="draw")
        tk.Radiobutton(control_frame, text="✏️ DRAW boxes", variable=self.mode_var, value="draw",
                      command=self.set_draw_mode, bg="lightgray", font=("Arial", 12)).pack(anchor=tk.W, padx=20)
        tk.Radiobutton(control_frame, text="🗑️ DELETE boxes (click box)", variable=self.mode_var, value="delete",
                      command=self.set_delete_mode, bg="lightgray", font=("Arial", 12)).pack(anchor=tk.W, padx=20)

        self.mode_label = tk.Label(control_frame, text="DRAW MODE", font=("Arial", 12, "bold"),
                                  bg="lightgreen", fg="black")
        self.mode_label.pack(pady=10, fill=tk.X, padx=20)

        # Navigation
        tk.Label(control_frame, text="Navigation:", font=("Arial", 12, "bold"), bg="lightgray").pack(pady=(20,5))
        tk.Button(control_frame, text="◄ Previous (A)", command=self.prev_image,
                 font=("Arial", 12), height=2, bg="lightblue").pack(pady=3, fill=tk.X, padx=20)
        tk.Button(control_frame, text="Next ► (D)", command=self.next_image,
                 font=("Arial", 12), height=2, bg="lightblue").pack(pady=3, fill=tk.X, padx=20)

        # Class selection
        tk.Label(control_frame, text="Shape Class:", font=("Arial", 12, "bold"), bg="lightgray").pack(pady=(20,5))

        self.class_var = tk.IntVar(value=0)
        for i, name in self.classes.items():
            color = self.colors[i]
            rb = tk.Radiobutton(control_frame, text=f"{i+1}. {name}", variable=self.class_var,
                               value=i, bg="lightgray", font=("Arial", 11), fg=color)
            rb.pack(anchor=tk.W, padx=20, pady=2)

        # Actions
        tk.Label(control_frame, text="Actions:", font=("Arial", 12, "bold"), bg="lightgray").pack(pady=(20,5))

        tk.Button(control_frame, text="💾 Save (S)", command=self.save,
                 font=("Arial", 12), height=2, bg="lightgreen").pack(pady=3, fill=tk.X, padx=20)
        tk.Button(control_frame, text="🗑️ Clear ALL (C)", command=self.clear_all,
                 font=("Arial", 12), height=2, bg="lightyellow").pack(pady=3, fill=tk.X, padx=20)
        tk.Button(control_frame, text="❌ Delete Last (X)", command=self.delete_last,
                 font=("Arial", 12), height=2, bg="lightcoral").pack(pady=3, fill=tk.X, padx=20)

        # Stats
        self.stats_label = tk.Label(control_frame, text="", bg="lightgray", font=("Arial", 10))
        self.stats_label.pack(pady=20)

        # Instructions
        instructions = """
DRAW MODE:
• Click & drag to draw boxes

DELETE MODE:
• Click on any box to delete it

Keys:
• A/D: Navigate images
• S: Save, C: Clear all
• X: Delete last box
• 1-4: Select class
        """
        tk.Label(control_frame, text=instructions, bg="lightgray",
                font=("Arial", 9), justify=tk.LEFT).pack(pady=10, padx=20)

        # Canvas
        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.canvas_frame, bg="white", cursor="crosshair")

        v_scroll = tk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        h_scroll = tk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)

        self.canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Bind events
        self.canvas.bind("<Button-1>", self.canvas_click)
        self.canvas.bind("<B1-Motion>", self.canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.canvas_release)

        self.root.bind("<Key>", self.on_key)
        self.root.focus_set()

    def set_draw_mode(self):
        self.delete_mode = False
        self.mode_label.config(text="DRAW MODE", bg="lightgreen")
        self.canvas.config(cursor="crosshair")

    def set_delete_mode(self):
        self.delete_mode = True
        self.mode_label.config(text="DELETE MODE", bg="lightcoral")
        self.canvas.config(cursor="dotbox")

    def canvas_click(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        if self.delete_mode:
            # Delete mode - find and delete clicked box
            self.delete_clicked_box(x, y)
        else:
            # Draw mode - start drawing
            self.drawing = True
            self.start_x = x
            self.start_y = y
            self.current_rect = None

    def canvas_drag(self, event):
        if self.drawing and not self.delete_mode:
            if self.current_rect:
                self.canvas.delete(self.current_rect)

            current_x = self.canvas.canvasx(event.x)
            current_y = self.canvas.canvasy(event.y)

            color = self.colors[self.class_var.get()]
            self.current_rect = self.canvas.create_rectangle(
                self.start_x, self.start_y, current_x, current_y,
                outline=color, width=3, dash=(8, 4)
            )

    def canvas_release(self, event):
        if self.drawing and not self.delete_mode:
            self.drawing = False
            end_x = self.canvas.canvasx(event.x)
            end_y = self.canvas.canvasy(event.y)

            if self.current_rect:
                self.canvas.delete(self.current_rect)
                self.current_rect = None

            # Check if box is big enough
            if abs(end_x - self.start_x) > 15 and abs(end_y - self.start_y) > 15:
                self.annotations.append({
                    'class': self.class_var.get(),
                    'x1': int(min(self.start_x, end_x)),
                    'y1': int(min(self.start_y, end_y)),
                    'x2': int(max(self.start_x, end_x)),
                    'y2': int(max(self.start_y, end_y))
                })

                self.draw_annotations()
                self.update_stats()

    def delete_clicked_box(self, click_x, click_y):
        """Delete the annotation that was clicked on"""
        for i, ann in enumerate(self.annotations):
            # Check if click is inside this box
            if (ann['x1'] <= click_x <= ann['x2'] and
                ann['y1'] <= click_y <= ann['y2']):

                # Delete this annotation
                del self.annotations[i]
                self.draw_annotations()
                self.update_stats()

                # Flash to show deletion
                self.root.title("DELETED BOX!")
                self.root.after(1000, lambda: self.root.title("Click-to-Delete PDF Labeler"))
                break

    def load_image(self):
        if not self.image_files:
            return

        # Load at full size
        image_path = self.image_files[self.current_index]
        img = cv2.imread(str(image_path))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        self.original_img = img

        # Display at full size
        pil_img = Image.fromarray(img)
        self.photo = ImageTk.PhotoImage(pil_img)

        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        self.canvas.configure(scrollregion=(0, 0, img.shape[1], img.shape[0]))

        self.load_annotations()
        self.draw_annotations()
        self.update_info()

    def draw_annotations(self):
        # Remove old annotations
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

            # Draw label with background
            text = f"{i+1}: {class_name}"
            self.canvas.create_text(
                ann['x1'], ann['y1'] - 10,
                text=text, fill=color, anchor=tk.SW, tags="annotation",
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
                cx = (ann['x1'] + ann['x2']) / 2 / width
                cy = (ann['y1'] + ann['y2']) / 2 / height
                w = (ann['x2'] - ann['x1']) / width
                h = (ann['y2'] - ann['y1']) / height

                f.write(f"{ann['class']} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}\n")

        self.root.title("SAVED!")
        self.root.after(1500, lambda: self.root.title("Click-to-Delete PDF Labeler"))
        self.update_stats()

    def clear_all(self):
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
        elif key == 'c': self.clear_all()
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
    app = ClickDeleteLabeler()
    app.run()