import React, { useRef, useEffect, useState, useCallback } from 'react';
import { Annotation, ViewTransform, Point, BoundingBox, Tool, MouseButton } from '../types';

interface ImageCanvasProps {
  imageUrl: string;
  imageWidth: number;
  imageHeight: number;
  annotations: Annotation[];
  selectedAnnotation: number | null;
  currentTool: Tool;
  currentClass: number;
  onAnnotationCreate: (bbox: BoundingBox, classId: number) => void;
  onAnnotationSelect: (id: number | null) => void;
  onAnnotationDelete: (id: number) => void;
  className?: string;
}

const CLASS_COLORS = {
  0: '#ef4444', // red - straight
  1: '#3b82f6', // blue - L-shape
  2: '#10b981', // green - U-shape
  3: '#f59e0b'  // orange - complex
};

const CLASS_NAMES = {
  0: 'straight',
  1: 'L-shape',
  2: 'U-shape',
  3: 'complex'
};

export const ImageCanvas: React.FC<ImageCanvasProps> = ({
  imageUrl,
  imageWidth,
  imageHeight,
  annotations,
  selectedAnnotation,
  currentTool,
  currentClass,
  onAnnotationCreate,
  onAnnotationSelect,
  onAnnotationDelete,
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

  // Load image
  useEffect(() => {
    const img = new Image();
    img.onload = () => {
      imageRef.current = img;
      setImageLoaded(true);
      fitImageToCanvas();
    };
    img.src = imageUrl;
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

  // Convert image coordinates to canvas coordinates
  const imageToCanvas = useCallback((imageX: number, imageY: number): Point => {
    return {
      x: imageX * transform.scale + transform.x,
      y: imageY * transform.scale + transform.y
    };
  }, [transform]);

  // Handle mouse wheel for zooming (with trackpad support)
  const handleWheel = useCallback((event: React.WheelEvent) => {
    event.preventDefault();

    if (!canvasRef.current) return;

    const rect = canvasRef.current.getBoundingClientRect();
    const mouseX = event.clientX - rect.left;
    const mouseY = event.clientY - rect.top;

    // Detect trackpad pinch gesture
    const isPinch = event.ctrlKey || Math.abs(event.deltaX) > Math.abs(event.deltaY);

    let scaleFactor: number;

    if (isPinch) {
      // Pinch zoom
      scaleFactor = event.deltaY > 0 ? 0.9 : 1.1;
    } else {
      // Regular scroll for pan
      const panSpeed = 1;
      setTransform(prev => ({
        ...prev,
        x: prev.x - event.deltaX * panSpeed,
        y: prev.y - event.deltaY * panSpeed
      }));
      return;
    }

    setTransform(prev => {
      const newScale = Math.max(0.1, Math.min(5, prev.scale * scaleFactor));
      const scaleRatio = newScale / prev.scale;

      // Zoom towards mouse position
      const newX = mouseX - (mouseX - prev.x) * scaleRatio;
      const newY = mouseY - (mouseY - prev.y) * scaleRatio;

      return { x: newX, y: newY, scale: newScale };
    });
  }, []);

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
        onAnnotationSelect(clickedAnnotation.id);
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
      }
    }
  }, [currentTool, annotations, onAnnotationSelect, screenToImage]);

  const handleMouseMove = useCallback((event: React.MouseEvent) => {
    if (isPanning && dragStart) {
      // Pan the image
      const deltaX = event.clientX - dragStart.x;
      const deltaY = event.clientY - dragStart.y;

      setTransform(prev => ({
        ...prev,
        x: prev.x + deltaX,
        y: prev.y + deltaY
      }));

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
      const color = CLASS_COLORS[annotation.class_id as keyof typeof CLASS_COLORS] || '#666';
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
      const className = CLASS_NAMES[annotation.class_id as keyof typeof CLASS_NAMES] || 'unknown';
      const label = `${annotation.class_id}: ${className}`;

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
      const color = CLASS_COLORS[currentClass as keyof typeof CLASS_COLORS] || '#666';
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
    </div>
  );
};