import React, { useState, useRef, useEffect } from 'react';
import { ZoomIn, ZoomOut, Maximize2, RotateCcw } from 'lucide-react';

interface ZoomControlsProps {
  zoom: number;
  minZoom?: number;
  maxZoom?: number;
  onZoomChange: (newZoom: number) => void;
  onFitToScreen: () => void;
  onReset: () => void;
  className?: string;
}

export const ZoomControls: React.FC<ZoomControlsProps> = ({
  zoom,
  minZoom = 0.1,
  maxZoom = 5,
  onZoomChange,
  onFitToScreen,
  onReset,
  className = ''
}) => {
  const [isEditingZoom, setIsEditingZoom] = useState(false);
  const [inputValue, setInputValue] = useState(Math.round(zoom * 100).toString());
  const inputRef = useRef<HTMLInputElement>(null);

  // Update input value when zoom changes externally
  useEffect(() => {
    if (!isEditingZoom) {
      setInputValue(Math.round(zoom * 100).toString());
    }
  }, [zoom, isEditingZoom]);

  const handleZoomIn = () => {
    const newZoom = Math.min(maxZoom, zoom * 1.25);
    onZoomChange(newZoom);
  };

  const handleZoomOut = () => {
    const newZoom = Math.max(minZoom, zoom / 1.25);
    onZoomChange(newZoom);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value);
  };

  const handleInputSubmit = () => {
    const value = parseInt(inputValue, 10);
    if (!isNaN(value) && value >= minZoom * 100 && value <= maxZoom * 100) {
      onZoomChange(value / 100);
    } else {
      // Reset to current zoom if invalid
      setInputValue(Math.round(zoom * 100).toString());
    }
    setIsEditingZoom(false);
  };

  const handleInputKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleInputSubmit();
    } else if (e.key === 'Escape') {
      setInputValue(Math.round(zoom * 100).toString());
      setIsEditingZoom(false);
    }
  };

  const handleInputFocus = () => {
    setIsEditingZoom(true);
    inputRef.current?.select();
  };

  return (
    <div className={`flex items-center gap-1 bg-white/95 backdrop-blur-sm rounded-lg shadow-lg border border-gray-200 p-1 ${className}`}>
      {/* Zoom Out Button */}
      <button
        onClick={handleZoomOut}
        disabled={zoom <= minZoom}
        className="p-2 rounded hover:bg-gray-100 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
        title="Zoom Out (Cmd+-)"
      >
        <ZoomOut className="w-4 h-4 text-gray-700" />
      </button>

      {/* Zoom Percentage Input */}
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={inputValue}
          onChange={handleInputChange}
          onFocus={handleInputFocus}
          onBlur={handleInputSubmit}
          onKeyDown={handleInputKeyDown}
          className="w-16 px-2 py-1 text-center text-sm font-medium border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          title="Enter zoom percentage (10-500%)"
        />
        <span className="absolute right-2 top-1/2 -translate-y-1/2 text-xs text-gray-500 pointer-events-none">
          %
        </span>
      </div>

      {/* Zoom In Button */}
      <button
        onClick={handleZoomIn}
        disabled={zoom >= maxZoom}
        className="p-2 rounded hover:bg-gray-100 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
        title="Zoom In (Cmd++)"
      >
        <ZoomIn className="w-4 h-4 text-gray-700" />
      </button>

      {/* Divider */}
      <div className="w-px h-6 bg-gray-300 mx-1" />

      {/* Fit to Screen Button */}
      <button
        onClick={onFitToScreen}
        className="p-2 rounded hover:bg-gray-100 transition-colors"
        title="Fit to Screen"
      >
        <Maximize2 className="w-4 h-4 text-gray-700" />
      </button>

      {/* Reset to 100% Button */}
      <button
        onClick={onReset}
        className="p-2 rounded hover:bg-gray-100 transition-colors"
        title="Reset to 100%"
      >
        <RotateCcw className="w-4 h-4 text-gray-700" />
      </button>
    </div>
  );
};
