#!/bin/bash
# Launch YOLO Labeling Tool
# Usage: ./launch_labeling_tool.sh [simple|label|enhanced|batch]

cd "$(dirname "$0")"

TOOL="${1:-simple}"

case "$TOOL" in
    simple)
        echo "Launching Simple Edit Tool..."
        python labeling_tools/simple_edit_tool.py
        ;;
    label)
        echo "Launching Label Tool..."
        python labeling_tools/label_tool.py
        ;;
    enhanced)
        echo "Launching Enhanced Label Tool..."
        python labeling_tools/enhanced_label_tool.py
        ;;
    batch)
        echo "Launching Batch Detect..."
        python labeling_tools/batch_detect.py
        ;;
    *)
        echo "Usage: ./launch_labeling_tool.sh [simple|label|enhanced|batch]"
        echo ""
        echo "Available tools:"
        echo "  simple   - Simple YOLO Editor (default)"
        echo "  label    - Full Label Tool"
        echo "  enhanced - Enhanced Label Tool"
        echo "  batch    - Batch Detection"
        echo ""
        echo "Note: All tools require dataset structure:"
        echo "  your_dataset/"
        echo "  ├── images/  (PNG files)"
        echo "  └── labels/  (TXT files, auto-generated if missing)"
        exit 1
        ;;
esac
