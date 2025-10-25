import React, { useCallback, useEffect, useState } from 'react';
import { Annotation, ResizeHandle as ResizeHandleType, InteractionMode, Point, ViewTransform } from '../types';
import { ResizeHandle } from './ResizeHandle';

interface AnnotationOverlayProps {
  annotation: Annotation;
  transform: ViewTransform;
  color: string;
  onPositionUpdate: (id: number, x1: number, y1: number, x2: number, y2: number) => void;
  onInteractionStart: () => void; // Notify parent when drag/resize starts
  onInteractionEnd: () => void; // Notify parent when drag/resize ends
}

const MIN_SIZE = 20; // Minimum annotation size in pixels

export const AnnotationOverlay: React.FC<AnnotationOverlayProps> = ({
  annotation,
  transform,
  color,
  onPositionUpdate,
  onInteractionStart,
  onInteractionEnd
}) => {
  const [mode, setMode] = useState<InteractionMode>(InteractionMode.SELECTED);
  const [dragStart, setDragStart] = useState<Point | null>(null);
  const [resizeHandle, setResizeHandle] = useState<ResizeHandleType | null>(null);
  const [initialBounds, setInitialBounds] = useState({ x1: 0, y1: 0, x2: 0, y2: 0 });

  // Track current position during drag/resize (in image coordinates)
  const [currentBounds, setCurrentBounds] = useState({
    x1: annotation.x1,
    y1: annotation.y1,
    x2: annotation.x2,
    y2: annotation.y2
  });

  // Update current bounds when annotation prop changes
  useEffect(() => {
    setCurrentBounds({
      x1: annotation.x1,
      y1: annotation.y1,
      x2: annotation.x2,
      y2: annotation.y2
    });
  }, [annotation]);

  // Convert screen coordinates to image coordinates
  const screenToImage = useCallback((screenX: number, screenY: number): Point => {
    return {
      x: screenX / transform.scale,
      y: screenY / transform.scale
    };
  }, [transform.scale]);

  // Handle mouse down on the annotation body (start drag)
  const handleBodyMouseDown = useCallback((e: React.MouseEvent) => {
    if (e.button !== 0) return; // Only left click

    e.stopPropagation();

    setMode(InteractionMode.DRAGGING);
    setDragStart({ x: e.clientX, y: e.clientY });
    setInitialBounds({ ...currentBounds });
    onInteractionStart();
  }, [currentBounds, onInteractionStart]);

  // Handle mouse down on resize handle (start resize)
  const handleResizeMouseDown = useCallback((e: React.MouseEvent, handle: ResizeHandleType) => {
    e.stopPropagation();

    setMode(InteractionMode.RESIZING);
    setResizeHandle(handle);
    setDragStart({ x: e.clientX, y: e.clientY });
    setInitialBounds({ ...currentBounds });
    onInteractionStart();
  }, [currentBounds, onInteractionStart]);

  // Handle mouse move for drag/resize
  useEffect(() => {
    if (mode !== InteractionMode.DRAGGING && mode !== InteractionMode.RESIZING) return;
    if (!dragStart) return;

    const handleMouseMove = (e: MouseEvent) => {
      const deltaX = e.clientX - dragStart.x;
      const deltaY = e.clientY - dragStart.y;
      const imageDelta = screenToImage(deltaX, deltaY);

      if (mode === InteractionMode.DRAGGING) {
        // Move the entire annotation
        setCurrentBounds({
          x1: initialBounds.x1 + imageDelta.x,
          y1: initialBounds.y1 + imageDelta.y,
          x2: initialBounds.x2 + imageDelta.x,
          y2: initialBounds.y2 + imageDelta.y
        });
      } else if (mode === InteractionMode.RESIZING && resizeHandle) {
        // Resize from the selected handle
        let { x1, y1, x2, y2 } = initialBounds;

        // Apply delta based on which handle is being dragged
        switch (resizeHandle) {
          case ResizeHandleType.TOP_LEFT:
            x1 += imageDelta.x;
            y1 += imageDelta.y;
            break;
          case ResizeHandleType.TOP:
            y1 += imageDelta.y;
            break;
          case ResizeHandleType.TOP_RIGHT:
            x2 += imageDelta.x;
            y1 += imageDelta.y;
            break;
          case ResizeHandleType.RIGHT:
            x2 += imageDelta.x;
            break;
          case ResizeHandleType.BOTTOM_RIGHT:
            x2 += imageDelta.x;
            y2 += imageDelta.y;
            break;
          case ResizeHandleType.BOTTOM:
            y2 += imageDelta.y;
            break;
          case ResizeHandleType.BOTTOM_LEFT:
            x1 += imageDelta.x;
            y2 += imageDelta.y;
            break;
          case ResizeHandleType.LEFT:
            x1 += imageDelta.x;
            break;
        }

        // Enforce minimum size in image coordinates
        const minSizeImage = MIN_SIZE / transform.scale;

        // Ensure x1 < x2 and y1 < y2, and enforce minimum size
        if (x2 - x1 < minSizeImage) {
          // Adjust based on which side is being moved
          if (resizeHandle.includes('left')) {
            x1 = x2 - minSizeImage;
          } else {
            x2 = x1 + minSizeImage;
          }
        }

        if (y2 - y1 < minSizeImage) {
          if (resizeHandle.includes('top')) {
            y1 = y2 - minSizeImage;
          } else {
            y2 = y1 + minSizeImage;
          }
        }

        setCurrentBounds({ x1, y1, x2, y2 });
      }
    };

    const handleMouseUp = () => {
      // Finalize the position update
      onPositionUpdate(annotation.id, currentBounds.x1, currentBounds.y1, currentBounds.x2, currentBounds.y2);

      setMode(InteractionMode.SELECTED);
      setDragStart(null);
      setResizeHandle(null);
      onInteractionEnd();
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseup', handleMouseUp);

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [mode, dragStart, initialBounds, resizeHandle, annotation.id, screenToImage, transform.scale, onPositionUpdate, onInteractionEnd, currentBounds]);

  // Calculate position in canvas/screen coordinates
  const canvasX = currentBounds.x1 * transform.scale + transform.x;
  const canvasY = currentBounds.y1 * transform.scale + transform.y;
  const canvasWidth = (currentBounds.x2 - currentBounds.x1) * transform.scale;
  const canvasHeight = (currentBounds.y2 - currentBounds.y1) * transform.scale;

  // Determine cursor style based on mode
  const getCursor = () => {
    if (mode === InteractionMode.DRAGGING) return 'grabbing';
    if (mode === InteractionMode.RESIZING) return 'inherit'; // Handles set their own cursor
    return 'grab';
  };

  return (
    <div
      className="absolute pointer-events-auto"
      style={{
        left: `${canvasX}px`,
        top: `${canvasY}px`,
        width: `${canvasWidth}px`,
        height: `${canvasHeight}px`,
        border: `2px solid ${color}`,
        borderRadius: '4px',
        cursor: getCursor(),
        boxSizing: 'border-box'
      }}
      onMouseDown={handleBodyMouseDown}
    >
      {/* Resize Handles - only show when not actively dragging */}
      {mode !== InteractionMode.DRAGGING && (
        <>
          <ResizeHandle position={ResizeHandleType.TOP_LEFT} onMouseDown={handleResizeMouseDown} />
          <ResizeHandle position={ResizeHandleType.TOP} onMouseDown={handleResizeMouseDown} />
          <ResizeHandle position={ResizeHandleType.TOP_RIGHT} onMouseDown={handleResizeMouseDown} />
          <ResizeHandle position={ResizeHandleType.RIGHT} onMouseDown={handleResizeMouseDown} />
          <ResizeHandle position={ResizeHandleType.BOTTOM_RIGHT} onMouseDown={handleResizeMouseDown} />
          <ResizeHandle position={ResizeHandleType.BOTTOM} onMouseDown={handleResizeMouseDown} />
          <ResizeHandle position={ResizeHandleType.BOTTOM_LEFT} onMouseDown={handleResizeMouseDown} />
          <ResizeHandle position={ResizeHandleType.LEFT} onMouseDown={handleResizeMouseDown} />
        </>
      )}
    </div>
  );
};
