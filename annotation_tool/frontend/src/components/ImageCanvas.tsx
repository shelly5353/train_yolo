import React, { useRef, useEffect, useState, useCallback } from 'react';
import { Annotation, ViewTransform, Point, BoundingBox, Tool, MouseButton, ClassInfo } from '../types';
import { ClassEditPopup } from './ClassEditPopup';
import { ZoomControls } from './ZoomControls';
import { AnnotationOverlay } from './AnnotationOverlay';

interface ImageCanvasProps {
  imageUrl: string;
  imageWidth: number;
  imageHeight: number;
  annotations: Annotation[];
  selectedAnnotation: number | null;
  currentTool: Tool;
  currentClass: number;
  classes: ClassInfo[];
  onAnnotationCreate: (bbox: BoundingBox, classId: number) => void;
  onAnnotationSelect: (id: number | null) => void;
  onAnnotationDelete: (id: number) => void;
  onAnnotationUpdate: (id: number, newClassId: number) => void;
  onAnnotationPositionUpdate: (id: number, x1: number, y1: number, x2: number, y2: number) => void;
  className?: string;
}

// Default colors for first 4 classes
const DEFAULT_CLASS_COLORS: { [key: number]: string } = {
  0: '#ef4444', // red - straight
  1: '#3b82f6', // blue - L-shape
  2: '#10b981', // green - U-shape
  3: '#f59e0b'  // orange - complex
};

// Helper function to get class color (matches ClassEditPopup)
function getClassColor(classId: number): string {
  if (classId in DEFAULT_CLASS_COLORS) {
    return DEFAULT_CLASS_COLORS[classId];
  }

  // Generate color for custom classes using golden angle for good distribution
  const hue = (classId * 137) % 360;
  return `hsl(${hue}, 70%, 55%)`;
}

// Helper function to get class name from classes array
function getClassName(classId: number, classes: ClassInfo[]): string {
  const classInfo = classes.find(c => c.id === classId);
  return classInfo?.name || 'unknown';
}

export const ImageCanvas: React.FC<ImageCanvasProps> = ({
  imageUrl,
  imageWidth,
  imageHeight,
  annotations,
  selectedAnnotation,
  currentTool,
  currentClass,
  classes,
  onAnnotationCreate,
  onAnnotationSelect,
  onAnnotationDelete,
  onAnnotationUpdate,
  onAnnotationPositionUpdate,
  className = ''
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [transform, setTransform] = useState<ViewTransform>({ x: 0, y: 0, scale: 1 });
  const [isDragging, setIsDragging] = useState(false);
  const [isPanning, setIsPanning] = useState(false);
  const [dragStart, setDragStart] = useState<Point | null>(null);
  const [currentBBox, setCurrentBBox] = useState<BoundingBox | null>(null);
  const [imageLoaded, setImageLoaded] = useState(false);
  const imageRef = useRef<HTMLImageElement | null>(null);

  // Gesture state for native MacBook trackpad support
  const [isGesturing, setIsGesturing] = useState(false);
  const gestureStartScaleRef = useRef<number>(1);
  const gestureStartTransformRef = useRef<ViewTransform>({ x: 0, y: 0, scale: 1 });

  // Class edit popup state
  const [showClassPopup, setShowClassPopup] = useState(false);
  const [popupPosition, setPopupPosition] = useState({ x: 0, y: 0 });
  const [editingAnnotationId, setEditingAnnotationId] = useState<number | null>(null);

  // Track interaction state to prevent popup during drag/resize
  const [isInteracting, setIsInteracting] = useState(false);

  // Load image
  useEffect(() => {
    const img = new Image();
    img.onload = () => {
      imageRef.current = img;
      setImageLoaded(true);
      fitImageToCanvas();
    };
    img.src = imageUrl;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [imageUrl]);

  // Fit image to canvas on window resize
  useEffect(() => {
    const handleResize = () => {
      if (imageLoaded) {
        fitImageToCanvas();
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [imageLoaded]);

  const fitImageToCanvas = useCallback(() => {
    if (!containerRef.current || !imageLoaded) return;

    const container = containerRef.current;
    const containerWidth = container.clientWidth;
    const containerHeight = container.clientHeight;

    const scaleX = containerWidth / imageWidth;
    const scaleY = containerHeight / imageHeight;
    const scale = Math.min(scaleX, scaleY, 1); // Don't scale up beyond original size

    const scaledWidth = imageWidth * scale;
    const scaledHeight = imageHeight * scale;

    const x = (containerWidth - scaledWidth) / 2;
    const y = (containerHeight - scaledHeight) / 2;

    setTransform({ x, y, scale });
  }, [imageWidth, imageHeight, imageLoaded]);

  // Convert screen coordinates to image coordinates
  const screenToImage = useCallback((screenX: number, screenY: number): Point => {
    if (!canvasRef.current) return { x: 0, y: 0 };

    const rect = canvasRef.current.getBoundingClientRect();
    const canvasX = screenX - rect.left;
    const canvasY = screenY - rect.top;

    const imageX = (canvasX - transform.x) / transform.scale;
    const imageY = (canvasY - transform.y) / transform.scale;

    return { x: imageX, y: imageY };
  }, [transform]);

  // Convert image coordinates to canvas coordinates (currently unused but may be needed)
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const imageToCanvas = useCallback((imageX: number, imageY: number): Point => {
    return {
      x: imageX * transform.scale + transform.x,
      y: imageY * transform.scale + transform.y
    };
  }, [transform]);

  // Apply pan bounds to keep image visible
  const applyPanBounds = useCallback((x: number, y: number, scale: number): Point => {
    if (!containerRef.current) return { x, y };

    const containerWidth = containerRef.current.clientWidth;
    const containerHeight = containerRef.current.clientHeight;
    const scaledWidth = imageWidth * scale;
    const scaledHeight = imageHeight * scale;

    // Calculate bounds - allow at least 20% of image to remain visible
    const minVisibleWidth = scaledWidth * 0.2;
    const minVisibleHeight = scaledHeight * 0.2;

    const maxX = containerWidth - minVisibleWidth;
    const minX = -scaledWidth + minVisibleWidth;
    const maxY = containerHeight - minVisibleHeight;
    const minY = -scaledHeight + minVisibleHeight;

    return {
      x: Math.max(minX, Math.min(maxX, x)),
      y: Math.max(minY, Math.min(maxY, y))
    };
  }, [imageWidth, imageHeight]);

  // Zoom to specific scale at a point
  const zoomToPoint = useCallback((newScale: number, centerX: number, centerY: number) => {
    setTransform(prev => {
      const clampedScale = Math.max(0.1, Math.min(5, newScale));
      const scaleRatio = clampedScale / prev.scale;

      // Zoom towards the specified point
      let newX = centerX - (centerX - prev.x) * scaleRatio;
      let newY = centerY - (centerY - prev.y) * scaleRatio;

      // Apply bounds
      const bounded = applyPanBounds(newX, newY, clampedScale);

      return { x: bounded.x, y: bounded.y, scale: clampedScale };
    });
  }, [applyPanBounds]);

  // Zoom control handlers
  const handleZoomChange = useCallback((newZoom: number) => {
    if (!containerRef.current) return;

    const container = containerRef.current;
    const centerX = container.clientWidth / 2;
    const centerY = container.clientHeight / 2;

    zoomToPoint(newZoom, centerX, centerY);
  }, [zoomToPoint]);

  const handleResetZoom = useCallback(() => {
    if (!containerRef.current) return;

    const container = containerRef.current;
    const containerWidth = container.clientWidth;
    const containerHeight = container.clientHeight;

    // Reset to 100% scale, centered
    const scaledWidth = imageWidth;
    const scaledHeight = imageHeight;

    const x = (containerWidth - scaledWidth) / 2;
    const y = (containerHeight - scaledHeight) / 2;

    setTransform({ x, y, scale: 1 });
  }, [imageWidth, imageHeight]);

  // Handle mouse wheel for zooming (Cmd/Ctrl + scroll)
  const handleWheel = useCallback((event: React.WheelEvent) => {
    event.preventDefault();

    if (!canvasRef.current) return;

    const rect = canvasRef.current.getBoundingClientRect();
    const mouseX = event.clientX - rect.left;
    const mouseY = event.clientY - rect.top;

    // Check if this is a zoom gesture (Cmd/Ctrl + scroll or pinch on trackpad)
    const isZoom = event.ctrlKey || event.metaKey;

    if (isZoom) {
      // Smooth zoom with deltaY
      const zoomSensitivity = 0.002; // Reduced for smoother zoom
      const delta = -event.deltaY * zoomSensitivity;
      const scaleFactor = 1 + delta;

      zoomToPoint(transform.scale * scaleFactor, mouseX, mouseY);
    } else {
      // Pan with scroll
      const panSpeed = 1;
      setTransform(prev => {
        const newX = prev.x - event.deltaX * panSpeed;
        const newY = prev.y - event.deltaY * panSpeed;
        const bounded = applyPanBounds(newX, newY, prev.scale);
        return { ...prev, x: bounded.x, y: bounded.y };
      });
    }
  }, [transform.scale, zoomToPoint, applyPanBounds]);

  // Handle native gesture events (MacBook trackpad pinch)
  const handleGestureStart = useCallback((event: any) => {
    event.preventDefault();
    setIsGesturing(true);
    gestureStartScaleRef.current = event.scale || 1;
    gestureStartTransformRef.current = transform;
  }, [transform]);

  const handleGestureChange = useCallback((event: any) => {
    event.preventDefault();

    if (!canvasRef.current || !isGesturing) return;

    const rect = canvasRef.current.getBoundingClientRect();
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;

    // Calculate new scale based on gesture
    const gestureScale = event.scale || 1;
    const scaleDelta = gestureScale / gestureStartScaleRef.current;
    const newScale = gestureStartTransformRef.current.scale * scaleDelta;

    zoomToPoint(newScale, centerX, centerY);
  }, [isGesturing, zoomToPoint]);

  const handleGestureEnd = useCallback((event: any) => {
    event.preventDefault();
    setIsGesturing(false);
  }, []);

  // Attach native gesture event listeners
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    // Add gesture event listeners for Safari/WebKit (MacBook trackpad)
    canvas.addEventListener('gesturestart', handleGestureStart as any);
    canvas.addEventListener('gesturechange', handleGestureChange as any);
    canvas.addEventListener('gestureend', handleGestureEnd as any);

    return () => {
      canvas.removeEventListener('gesturestart', handleGestureStart as any);
      canvas.removeEventListener('gesturechange', handleGestureChange as any);
      canvas.removeEventListener('gestureend', handleGestureEnd as any);
    };
  }, [handleGestureStart, handleGestureChange, handleGestureEnd]);

  // Handle mouse events
  const handleMouseDown = useCallback((event: React.MouseEvent) => {
    const button = event.button as MouseButton;
    const point = screenToImage(event.clientX, event.clientY);

    if (button === MouseButton.MIDDLE || currentTool === Tool.PAN) {
      // Pan mode
      setIsPanning(true);
      setDragStart({ x: event.clientX, y: event.clientY });
      return;
    }

    if (button === MouseButton.LEFT && currentTool === Tool.BBOX) {
      // Check if clicking on existing annotation
      const clickedAnnotation = annotations.find(ann =>
        point.x >= ann.x1 && point.x <= ann.x2 &&
        point.y >= ann.y1 && point.y <= ann.y2
      );

      if (clickedAnnotation) {
        // If clicking on an already-selected annotation, the overlay will handle it
        // Only handle clicks on non-selected annotations
        if (clickedAnnotation.id !== selectedAnnotation) {
          // Select the annotation
          onAnnotationSelect(clickedAnnotation.id);

          // Show class edit popup only if not interacting
          if (!isInteracting) {
            setEditingAnnotationId(clickedAnnotation.id);
            setPopupPosition({ x: event.clientX + 10, y: event.clientY + 10 });
            setShowClassPopup(true);
          }
        }
        // If clicking on already-selected annotation, overlay handles drag/resize
      } else {
        // Start drawing new bounding box
        setIsDragging(true);
        setDragStart(point);
        setCurrentBBox({
          x1: point.x,
          y1: point.y,
          x2: point.x,
          y2: point.y
        });
        onAnnotationSelect(null);
        setShowClassPopup(false); // Close popup when drawing new box
      }
    }
  }, [currentTool, annotations, selectedAnnotation, isInteracting, onAnnotationSelect, screenToImage]);

  const handleMouseMove = useCallback((event: React.MouseEvent) => {
    if (isPanning && dragStart) {
      // Pan the image with bounds
      const deltaX = event.clientX - dragStart.x;
      const deltaY = event.clientY - dragStart.y;

      setTransform(prev => {
        const newX = prev.x + deltaX;
        const newY = prev.y + deltaY;
        const bounded = applyPanBounds(newX, newY, prev.scale);
        return { ...prev, x: bounded.x, y: bounded.y };
      });

      setDragStart({ x: event.clientX, y: event.clientY });
    } else if (isDragging && dragStart && currentBBox) {
      // Update current bounding box
      const point = screenToImage(event.clientX, event.clientY);
      setCurrentBBox({
        x1: Math.min(dragStart.x, point.x),
        y1: Math.min(dragStart.y, point.y),
        x2: Math.max(dragStart.x, point.x),
        y2: Math.max(dragStart.y, point.y)
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isPanning, isDragging, dragStart, currentBBox, screenToImage]);

  const handleMouseUp = useCallback(() => {
    if (isDragging && currentBBox) {
      // Create new annotation if bbox is large enough
      const minSize = 10 / transform.scale; // Minimum 10 pixels at current zoom
      if (Math.abs(currentBBox.x2 - currentBBox.x1) > minSize &&
          Math.abs(currentBBox.y2 - currentBBox.y1) > minSize) {
        onAnnotationCreate(currentBBox, currentClass);
      }
    }

    setIsDragging(false);
    setIsPanning(false);
    setDragStart(null);
    setCurrentBBox(null);
  }, [isDragging, currentBBox, transform.scale, onAnnotationCreate, currentClass]);

  const handleContextMenu = useCallback((event: React.MouseEvent) => {
    event.preventDefault();

    if (selectedAnnotation !== null) {
      onAnnotationDelete(selectedAnnotation);
    }
  }, [selectedAnnotation, onAnnotationDelete]);

  // Draw everything on canvas
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !imageLoaded || !imageRef.current) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Save context
    ctx.save();

    // Apply transform
    ctx.translate(transform.x, transform.y);
    ctx.scale(transform.scale, transform.scale);

    // Draw image
    ctx.drawImage(imageRef.current, 0, 0, imageWidth, imageHeight);

    // Draw annotations
    annotations.forEach(annotation => {
      const color = getClassColor(annotation.class_id);
      const isSelected = annotation.id === selectedAnnotation;

      ctx.strokeStyle = color;
      ctx.lineWidth = isSelected ? 3 / transform.scale : 2 / transform.scale;
      ctx.setLineDash([]);

      // Draw bounding box
      ctx.strokeRect(
        annotation.x1,
        annotation.y1,
        annotation.width,
        annotation.height
      );

      // Draw class label
      const classNameText = getClassName(annotation.class_id, classes);
      const label = `${annotation.class_id}: ${classNameText}`;

      ctx.fillStyle = color;
      const fontSize = 12 / transform.scale;
      ctx.font = `bold ${fontSize}px -apple-system, BlinkMacSystemFont, sans-serif`;

      const textMetrics = ctx.measureText(label);
      const textWidth = textMetrics.width;
      const textHeight = fontSize;

      // Label background
      ctx.fillRect(
        annotation.x1,
        annotation.y1 - textHeight - 4,
        textWidth + 8,
        textHeight + 4
      );

      // Label text
      ctx.fillStyle = 'white';
      ctx.fillText(label, annotation.x1 + 4, annotation.y1 - 4);
    });

    // Draw current bounding box being drawn
    if (currentBBox && isDragging) {
      const color = getClassColor(currentClass);
      ctx.strokeStyle = color;
      ctx.lineWidth = 2 / transform.scale;
      ctx.setLineDash([5 / transform.scale, 5 / transform.scale]);

      ctx.strokeRect(
        currentBBox.x1,
        currentBBox.y1,
        currentBBox.x2 - currentBBox.x1,
        currentBBox.y2 - currentBBox.y1
      );
    }

    // Restore context
    ctx.restore();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [transform, annotations, selectedAnnotation, currentBBox, isDragging, currentClass, imageLoaded, imageWidth, imageHeight]);

  // Update canvas size only when container dimensions change
  useEffect(() => {
    if (canvasRef.current && containerRef.current) {
      const canvas = canvasRef.current;
      const container = containerRef.current;

      const newWidth = container.clientWidth;
      const newHeight = container.clientHeight;

      // Only update if dimensions actually changed (to avoid clearing canvas unnecessarily)
      if (canvas.width !== newWidth || canvas.height !== newHeight) {
        canvas.width = newWidth;
        canvas.height = newHeight;
      }
    }
  }, []); // Run once on mount

  // Handle window resize to update canvas size
  useEffect(() => {
    const handleResize = () => {
      if (canvasRef.current && containerRef.current) {
        const canvas = canvasRef.current;
        const container = containerRef.current;
        const newWidth = container.clientWidth;
        const newHeight = container.clientHeight;

        if (canvas.width !== newWidth || canvas.height !== newHeight) {
          canvas.width = newWidth;
          canvas.height = newHeight;
        }
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const getCursorStyle = () => {
    if (isPanning) return 'grabbing';
    if (currentTool === Tool.PAN) return 'grab';
    if (currentTool === Tool.BBOX) return 'crosshair';
    return 'default';
  };

  // Handle class selection from popup
  const handleClassSelect = useCallback((newClassId: number) => {
    if (editingAnnotationId !== null) {
      onAnnotationUpdate(editingAnnotationId, newClassId);
      setShowClassPopup(false);
      setEditingAnnotationId(null);
    }
  }, [editingAnnotationId, onAnnotationUpdate]);

  // Get current class for editing annotation
  const getEditingAnnotationClass = () => {
    if (editingAnnotationId === null) return 0;
    const annotation = annotations.find(ann => ann.id === editingAnnotationId);
    return annotation?.class_id ?? 0;
  };

  // Get selected annotation object
  const selectedAnnotationObj = selectedAnnotation !== null
    ? annotations.find(ann => ann.id === selectedAnnotation)
    : null;

  return (
    <div
      ref={containerRef}
      className={`relative w-full h-full overflow-hidden ${className}`}
      style={{ cursor: getCursorStyle() }}
    >
      <canvas
        ref={canvasRef}
        className="absolute inset-0 w-full h-full"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onWheel={handleWheel}
        onContextMenu={handleContextMenu}
      />

      {/* Annotation Overlay - interactive drag/resize layer */}
      {selectedAnnotationObj && (
        <div className="absolute inset-0 pointer-events-none">
          <AnnotationOverlay
            annotation={selectedAnnotationObj}
            transform={transform}
            color={getClassColor(selectedAnnotationObj.class_id)}
            onPositionUpdate={onAnnotationPositionUpdate}
            onInteractionStart={() => {
              setIsInteracting(true);
              setShowClassPopup(false); // Close popup when starting drag/resize
            }}
            onInteractionEnd={() => {
              setIsInteracting(false);
            }}
          />
        </div>
      )}

      {/* Zoom Controls */}
      <ZoomControls
        zoom={transform.scale}
        minZoom={0.1}
        maxZoom={5}
        onZoomChange={handleZoomChange}
        onFitToScreen={fitImageToCanvas}
        onReset={handleResetZoom}
        className="absolute bottom-4 right-4"
      />

      {/* Class Edit Popup */}
      {showClassPopup && editingAnnotationId !== null && (
        <ClassEditPopup
          x={popupPosition.x}
          y={popupPosition.y}
          currentClassId={getEditingAnnotationClass()}
          classes={classes}
          onClassSelect={handleClassSelect}
          onClose={() => {
            setShowClassPopup(false);
            setEditingAnnotationId(null);
          }}
        />
      )}
    </div>
  );
};