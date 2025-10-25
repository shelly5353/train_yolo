import React from 'react';
import { ResizeHandle as ResizeHandleType } from '../types';

interface ResizeHandleProps {
  position: ResizeHandleType;
  onMouseDown: (e: React.MouseEvent, handle: ResizeHandleType) => void;
}

// Map handle positions to CSS cursor styles
const CURSOR_STYLES: Record<ResizeHandleType, string> = {
  [ResizeHandleType.TOP_LEFT]: 'nw-resize',
  [ResizeHandleType.TOP]: 'n-resize',
  [ResizeHandleType.TOP_RIGHT]: 'ne-resize',
  [ResizeHandleType.RIGHT]: 'e-resize',
  [ResizeHandleType.BOTTOM_RIGHT]: 'se-resize',
  [ResizeHandleType.BOTTOM]: 's-resize',
  [ResizeHandleType.BOTTOM_LEFT]: 'sw-resize',
  [ResizeHandleType.LEFT]: 'w-resize'
};

// Map handle positions to CSS positioning (using Tailwind)
const POSITION_STYLES: Record<ResizeHandleType, string> = {
  [ResizeHandleType.TOP_LEFT]: 'top-0 left-0 -translate-x-1/2 -translate-y-1/2',
  [ResizeHandleType.TOP]: 'top-0 left-1/2 -translate-x-1/2 -translate-y-1/2',
  [ResizeHandleType.TOP_RIGHT]: 'top-0 right-0 translate-x-1/2 -translate-y-1/2',
  [ResizeHandleType.RIGHT]: 'top-1/2 right-0 translate-x-1/2 -translate-y-1/2',
  [ResizeHandleType.BOTTOM_RIGHT]: 'bottom-0 right-0 translate-x-1/2 translate-y-1/2',
  [ResizeHandleType.BOTTOM]: 'bottom-0 left-1/2 -translate-x-1/2 translate-y-1/2',
  [ResizeHandleType.BOTTOM_LEFT]: 'bottom-0 left-0 -translate-x-1/2 translate-y-1/2',
  [ResizeHandleType.LEFT]: 'top-1/2 left-0 -translate-x-1/2 -translate-y-1/2'
};

export const ResizeHandle: React.FC<ResizeHandleProps> = ({ position, onMouseDown }) => {
  const handleMouseDown = (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent triggering drag on parent
    onMouseDown(e, position);
  };

  return (
    <div
      className={`absolute w-2 h-2 bg-white border-2 border-blue-500 rounded-sm hover:bg-blue-100 transition-colors z-10 ${POSITION_STYLES[position]}`}
      style={{ cursor: CURSOR_STYLES[position] }}
      onMouseDown={handleMouseDown}
    />
  );
};
