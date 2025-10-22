#!/bin/bash

# YOLO Annotation Tool Startup Script
# This script starts both the Flask backend and React frontend

set -e

echo "🚀 Starting YOLO Annotation Tool..."
echo ""

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the annotation_tool directory"
    echo "   Expected structure:"
    echo "   annotation_tool/"
    echo "   ├── backend/"
    echo "   ├── frontend/"
    echo "   └── start.sh"
    exit 1
fi

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    # Kill all background processes
    jobs -p | xargs -r kill
    wait
    echo "✅ All services stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup INT TERM EXIT

# Start Backend
echo "🐍 Starting Flask backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -q -r requirements.txt

# Start Flask server in background
echo "🌐 Starting Flask server on http://localhost:5002..."
python app.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Check if backend is running
if ! curl -s http://localhost:5002/api/health > /dev/null; then
    echo "❌ Backend failed to start"
    exit 1
fi

echo "✅ Backend started successfully"
cd ..

# Start Frontend
echo "⚛️  Starting React frontend..."
cd frontend

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
fi

# Start React development server
echo "🌐 Starting React development server on http://localhost:3000..."
npm start &
FRONTEND_PID=$!

echo ""
echo "🎉 YOLO Annotation Tool is starting up!"
echo ""
echo "📍 Backend API:  http://localhost:5002"
echo "📍 Frontend App: http://localhost:3000"
echo ""
echo "⌨️  Keyboard Shortcuts:"
echo "   ← →     Navigate images"
echo "   N       New bounding box tool"
echo "   H       Pan tool"
echo "   V       Select tool"
echo "   1-4     Select class"
echo "   ⌘+S     Save annotations"
echo "   Del     Delete selected annotation"
echo "   ⌘+K     Clear all annotations"
echo ""
echo "🎯 Features:"
echo "   • Trackpad gestures (pinch to zoom, scroll to pan)"
echo "   • High-resolution image support"
echo "   • Real-time annotation statistics"
echo "   • YOLO format export"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for processes
wait