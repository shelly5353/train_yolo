#!/usr/bin/env python3
"""
Configuration Manager for YOLO Labeling System
Manages file paths and user preferences for all labeling tools
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, List
import tkinter as tk
from tkinter import filedialog, messagebox


class PathConfig:
    """Manages file paths for the YOLO labeling system"""

    # Default configuration structure
    DEFAULT_CONFIG = {
        "paths": {
            "last_data_dir": "",
            "last_labels_dir": "",
            "last_output_dir": "",
            "model_path": "models/best.pt"
        },
        "recent_directories": [],
        "preferences": {
            "remember_last_directory": True,
            "show_directory_dialog": True,
            "max_recent_directories": 10
        }
    }

    def __init__(self, config_file: str = 'config.json'):
        """
        Initialize PathConfig

        Args:
            config_file: Path to configuration file (relative to project root)
        """
        self.project_root = Path(__file__).parent.parent
        self.config_file = self.project_root / config_file
        self.config = self.load_config()

    def load_config(self) -> Dict:
        """
        Load configuration from file or create default

        Returns:
            Configuration dictionary
        """
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                # Merge with defaults to ensure all keys exist
                config = self.DEFAULT_CONFIG.copy()
                self._deep_update(config, loaded_config)
                return config
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load config file: {e}")
                print("Using default configuration")
                return self.DEFAULT_CONFIG.copy()
        else:
            # Create default config file
            config = self.DEFAULT_CONFIG.copy()
            self.save_config(config)
            return config

    def _deep_update(self, base: Dict, update: Dict) -> None:
        """Deep update dictionary (modify in place)"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_update(base[key], value)
            else:
                base[key] = value

    def save_config(self, config: Optional[Dict] = None) -> None:
        """
        Save current configuration to file

        Args:
            config: Configuration to save (uses self.config if None)
        """
        if config is None:
            config = self.config

        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save config file: {e}")

    def select_directory(self, title: str = "Select Directory",
                        initial_dir: Optional[str] = None) -> Optional[str]:
        """
        Open file browser to select directory

        Args:
            title: Dialog window title
            initial_dir: Initial directory to show

        Returns:
            Selected directory path or None if cancelled
        """
        root = tk.Tk()
        root.withdraw()  # Hide main window
        root.attributes('-topmost', True)  # Bring to front

        if initial_dir is None:
            # Try to use last used directory
            initial_dir = self.get_last_directory()

        directory = filedialog.askdirectory(
            title=title,
            initialdir=initial_dir,
            mustexist=True
        )

        root.destroy()

        return directory if directory else None

    def get_data_dir(self) -> Optional[str]:
        """Get last used data directory"""
        path = self.config['paths'].get('last_data_dir', '')
        return path if path and Path(path).exists() else None

    def set_data_dir(self, path: str) -> None:
        """
        Set data directory and save to config

        Args:
            path: Directory path
        """
        self.config['paths']['last_data_dir'] = str(path)
        self._add_to_recent(path)
        self.save_config()

    def get_labels_dir(self) -> Optional[str]:
        """Get last used labels directory"""
        path = self.config['paths'].get('last_labels_dir', '')
        return path if path and Path(path).exists() else None

    def set_labels_dir(self, path: str) -> None:
        """
        Set labels directory and save to config

        Args:
            path: Directory path
        """
        self.config['paths']['last_labels_dir'] = str(path)
        self._add_to_recent(path)
        self.save_config()

    def get_output_dir(self) -> Optional[str]:
        """Get last used output directory"""
        path = self.config['paths'].get('last_output_dir', '')
        return path if path and Path(path).exists() else None

    def set_output_dir(self, path: str) -> None:
        """
        Set output directory and save to config

        Args:
            path: Directory path
        """
        self.config['paths']['last_output_dir'] = str(path)
        self._add_to_recent(path)
        self.save_config()

    def get_model_path(self) -> str:
        """Get model path (relative or absolute)"""
        model_path = self.config['paths'].get('model_path', 'models/best.pt')

        # If relative path, make it relative to project root
        if not Path(model_path).is_absolute():
            model_path = str(self.project_root / model_path)

        return model_path

    def set_model_path(self, path: str) -> None:
        """
        Set model path and save to config

        Args:
            path: Model file path
        """
        self.config['paths']['model_path'] = str(path)
        self.save_config()

    def get_or_select_directory(self, key: str, title: str,
                                default: Optional[str] = None) -> str:
        """
        Get directory from config or prompt user to select

        Args:
            key: Config key (e.g., 'last_data_dir')
            title: Dialog title
            default: Default directory if not in config

        Returns:
            Directory path

        Raises:
            ValueError: If no directory selected
        """
        # Check if we should remember last directory
        if self.config['preferences']['remember_last_directory']:
            path = self.config['paths'].get(key, '')
            if path and Path(path).exists():
                # Ask user if they want to use it
                if not self.config['preferences']['show_directory_dialog']:
                    return path

                root = tk.Tk()
                root.withdraw()
                root.attributes('-topmost', True)

                result = messagebox.askyesno(
                    "Use Last Directory?",
                    f"Use last directory?\n\n{path}\n\nClick 'No' to choose a different directory.",
                    parent=root
                )
                root.destroy()

                if result:
                    return path

        # Show directory selection dialog
        initial_dir = default or self.get_last_directory()
        directory = self.select_directory(title=title, initial_dir=initial_dir)

        if not directory:
            raise ValueError(f"No directory selected for {key}")

        # Save the selected directory
        self.config['paths'][key] = directory
        self._add_to_recent(directory)
        self.save_config()

        return directory

    def get_last_directory(self) -> Optional[str]:
        """Get the most recently used directory"""
        recent = self.config.get('recent_directories', [])
        if recent:
            # Return first existing directory
            for path in recent:
                if Path(path).exists():
                    return path
        return None

    def _add_to_recent(self, path: str) -> None:
        """
        Add directory to recent list

        Args:
            path: Directory path
        """
        path = str(Path(path).resolve())
        recent = self.config.get('recent_directories', [])

        # Remove if already in list
        if path in recent:
            recent.remove(path)

        # Add to front of list
        recent.insert(0, path)

        # Limit size
        max_recent = self.config['preferences'].get('max_recent_directories', 10)
        self.config['recent_directories'] = recent[:max_recent]

    def get_recent_directories(self) -> List[str]:
        """
        Get list of recent directories (that still exist)

        Returns:
            List of directory paths
        """
        recent = self.config.get('recent_directories', [])
        return [path for path in recent if Path(path).exists()]

    def validate_directory(self, path: str, create: bool = False) -> bool:
        """
        Validate that directory exists

        Args:
            path: Directory path
            create: Create directory if it doesn't exist

        Returns:
            True if valid, False otherwise
        """
        path_obj = Path(path)

        if path_obj.exists():
            return path_obj.is_dir()
        elif create:
            try:
                path_obj.mkdir(parents=True, exist_ok=True)
                return True
            except OSError:
                return False
        return False

    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults"""
        self.config = self.DEFAULT_CONFIG.copy()
        self.save_config()

    def get_preference(self, key: str, default=None):
        """
        Get user preference value

        Args:
            key: Preference key
            default: Default value if not found

        Returns:
            Preference value
        """
        return self.config['preferences'].get(key, default)

    def set_preference(self, key: str, value) -> None:
        """
        Set user preference

        Args:
            key: Preference key
            value: Preference value
        """
        self.config['preferences'][key] = value
        self.save_config()


# Convenience function for quick directory selection
def get_directory(title: str = "Select Directory",
                 config_key: Optional[str] = None,
                 remember: bool = True) -> Optional[str]:
    """
    Quick function to get a directory with optional config management

    Args:
        title: Dialog title
        config_key: Config key to save/load from (e.g., 'last_data_dir')
        remember: Whether to remember the selection

    Returns:
        Selected directory or None
    """
    if config_key and remember:
        config = PathConfig()
        return config.get_or_select_directory(config_key, title)
    else:
        config = PathConfig()
        return config.select_directory(title)


def prepare_directory_for_labeling(directory_path: str, model_path: Optional[str] = None,
                                   confidence: float = 0.25, verbose: bool = True) -> Path:
    """
    Prepare a directory for labeling by checking if labels exist and running YOLO if needed.

    Args:
        directory_path: Path to directory containing images
        model_path: Path to YOLO model (uses default from config if None)
        confidence: Confidence threshold for YOLO detection
        verbose: Print status messages

    Returns:
        Path object of the directory

    Raises:
        FileNotFoundError: If no PNG images found in directory
        ImportError: If required packages (ultralytics, cv2) not available
    """
    from pathlib import Path
    import cv2
    from ultralytics import YOLO
    from tqdm import tqdm

    directory = Path(directory_path)

    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    # Get all PNG images
    image_files = sorted(list(directory.glob("*.png")))

    if not image_files:
        raise FileNotFoundError(f"No PNG images found in {directory}")

    # Check how many images already have labels
    labeled_count = sum(1 for img in image_files if (directory / f"{img.stem}.txt").exists())

    if labeled_count == len(image_files):
        if verbose:
            print(f"✅ All {len(image_files)} images already have labels")
        return directory

    # Some images need labels - run YOLO
    unlabeled_count = len(image_files) - labeled_count

    if verbose:
        print(f"⚠️  Found {unlabeled_count} unlabeled images (out of {len(image_files)} total)")
        print(f"🔄 Running YOLO model to generate labels...")

    # Get model path
    if model_path is None:
        config = PathConfig()
        model_path = config.get_model_path()

    if not Path(model_path).exists():
        raise FileNotFoundError(f"YOLO model not found: {model_path}")

    # Load YOLO model
    model = YOLO(model_path)

    # Process unlabeled images
    processed = 0
    for img_path in tqdm(image_files, desc="Detecting objects", disable=not verbose):
        label_file = directory / f"{img_path.stem}.txt"

        # Skip if label already exists
        if label_file.exists():
            continue

        # Run detection
        image = cv2.imread(str(img_path))
        if image is None:
            if verbose:
                print(f"⚠️  Could not read image: {img_path.name}")
            continue

        results = model(image, conf=confidence, verbose=False)

        # Save labels in YOLO format
        labels = []
        if results and len(results) > 0:
            detections = results[0]
            if detections.boxes is not None and len(detections.boxes) > 0:
                boxes = detections.boxes
                img_h, img_w = image.shape[:2]

                for box in boxes:
                    # Get box coordinates (xyxy format)
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    class_id = int(box.cls[0].cpu().numpy())

                    # Convert to YOLO format (normalized xywh)
                    x_center = ((x1 + x2) / 2) / img_w
                    y_center = ((y1 + y2) / 2) / img_h
                    width = (x2 - x1) / img_w
                    height = (y2 - y1) / img_h

                    labels.append(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")

        # Write label file (even if empty)
        with open(label_file, 'w') as f:
            if labels:
                f.write('\n'.join(labels) + '\n')

        processed += 1

    if verbose:
        print(f"✅ Generated labels for {processed} images")
        print(f"📁 Directory ready for labeling: {directory}")

    return directory


if __name__ == "__main__":
    # Test the configuration manager
    print("Testing PathConfig...")

    config = PathConfig()
    print(f"Config file: {config.config_file}")
    print(f"Project root: {config.project_root}")
    print(f"\nCurrent configuration:")
    print(json.dumps(config.config, indent=2))

    print(f"\nModel path: {config.get_model_path()}")
    print(f"Recent directories: {config.get_recent_directories()}")
