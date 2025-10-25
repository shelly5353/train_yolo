import React, { useEffect, useRef, useState } from 'react';
import { Check, Search } from 'lucide-react';
import { ClassInfo } from '../types';

interface ClassEditPopupProps {
  x: number;
  y: number;
  currentClassId: number;
  classes: ClassInfo[];
  onClassSelect: (classId: number) => void;
  onClose: () => void;
}

export const ClassEditPopup: React.FC<ClassEditPopupProps> = ({
  x,
  y,
  currentClassId,
  classes,
  onClassSelect,
  onClose
}) => {
  const popupRef = useRef<HTMLDivElement>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);
  const [searchQuery, setSearchQuery] = useState('');

  // Auto-focus search input when popup opens
  useEffect(() => {
    if (searchInputRef.current) {
      searchInputRef.current.focus();
    }
  }, []);

  // Close on Escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  // Close when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (popupRef.current && !popupRef.current.contains(e.target as Node)) {
        onClose();
      }
    };

    // Add delay to prevent immediate close from the click that opened it
    setTimeout(() => {
      window.addEventListener('mousedown', handleClickOutside);
    }, 100);

    return () => window.removeEventListener('mousedown', handleClickOutside);
  }, [onClose]);

  // Filter classes based on search query
  const filteredClasses = classes.filter(cls => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      cls.name.toLowerCase().includes(query) ||
      cls.id.toString().includes(query)
    );
  });

  // Smart boundary-aware positioning
  const getSmartPosition = () => {
    const POPUP_WIDTH = 250;
    const POPUP_MAX_HEIGHT = 400;
    const MARGIN = 10; // Minimum margin from screen edge

    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;

    // Calculate available space in all 4 directions
    const spaceRight = viewportWidth - x;
    const spaceLeft = x;
    const spaceBottom = viewportHeight - y;
    const spaceTop = y;

    // Determine horizontal position
    let left = x;
    if (spaceRight >= POPUP_WIDTH + MARGIN) {
      // Enough space on right - position to right of click
      left = x;
    } else if (spaceLeft >= POPUP_WIDTH + MARGIN) {
      // Not enough space on right, but enough on left - position to left
      left = x - POPUP_WIDTH;
    } else {
      // Not enough space on either side - center or align to edge
      left = Math.max(MARGIN, Math.min(x, viewportWidth - POPUP_WIDTH - MARGIN));
    }

    // Determine vertical position
    let top = y;
    if (spaceBottom >= POPUP_MAX_HEIGHT + MARGIN) {
      // Enough space below - position below click
      top = y;
    } else if (spaceTop >= POPUP_MAX_HEIGHT + MARGIN) {
      // Not enough space below, but enough above - position above
      top = y - POPUP_MAX_HEIGHT;
    } else {
      // Not enough space above or below - align to best fit
      top = Math.max(MARGIN, Math.min(y, viewportHeight - POPUP_MAX_HEIGHT - MARGIN));
    }

    return { left, top };
  };

  const adjustedPosition = getSmartPosition();

  const handleClassClick = (classId: number) => {
    onClassSelect(classId);
    onClose();
  };

  return (
    <div
      ref={popupRef}
      className="fixed z-50 bg-white rounded-lg shadow-2xl border-2 border-blue-500 overflow-hidden"
      style={{
        left: `${adjustedPosition.left}px`,
        top: `${adjustedPosition.top}px`,
        minWidth: '220px',
        maxWidth: '300px',
        maxHeight: '400px'
      }}
    >
      {/* Header with Search */}
      <div className="px-4 py-2 bg-blue-50 border-b border-blue-200">
        <div className="text-sm font-semibold text-blue-900 mb-2">Change Label</div>

        {/* Search Input */}
        <div className="relative">
          <Search className="absolute left-2 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-400" />
          <input
            ref={searchInputRef}
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search labels..."
            className="w-full pl-8 pr-3 py-1.5 text-xs border border-blue-200 rounded bg-white focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent"
          />
        </div>
      </div>

      {/* Classes List */}
      <div className="overflow-y-auto max-h-[280px]">
        {filteredClasses.length === 0 ? (
          <div className="px-4 py-3 text-sm text-gray-500 text-center">
            {searchQuery ? 'No matching labels' : 'No classes available'}
          </div>
        ) : (
          <div className="py-1">
            {filteredClasses.map((cls) => {
              const isSelected = cls.id === currentClassId;

              return (
                <button
                  key={cls.id}
                  onClick={() => handleClassClick(cls.id)}
                  className={`w-full px-4 py-2 text-left flex items-center gap-3 transition-colors ${
                    isSelected
                      ? 'bg-blue-100 text-blue-900 font-medium'
                      : 'hover:bg-gray-100 text-gray-700'
                  }`}
                >
                  {/* Check icon for selected class */}
                  <div className="w-5 flex-shrink-0">
                    {isSelected && <Check className="w-4 h-4 text-blue-600" />}
                  </div>

                  {/* Class info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-baseline gap-2">
                      <span className="text-xs font-mono text-gray-500">{cls.id}:</span>
                      <span className="text-sm truncate">{cls.name}</span>
                    </div>
                  </div>

                  {/* Color indicator */}
                  <div
                    className="w-3 h-3 rounded-full flex-shrink-0"
                    style={{
                      backgroundColor: getClassColor(cls.id)
                    }}
                  />
                </button>
              );
            })}
          </div>
        )}
      </div>

      {/* Footer hint */}
      <div className="px-4 py-2 bg-gray-50 border-t border-gray-200 text-xs text-gray-500 text-center">
        {filteredClasses.length > 0 && searchQuery && (
          <div className="mb-1 text-blue-600">
            {filteredClasses.length} of {classes.length} labels shown
          </div>
        )}
        Press <kbd className="px-1 py-0.5 bg-gray-200 rounded text-xs">Esc</kbd> to cancel
      </div>
    </div>
  );
};

// Helper function to get class colors (matches ImageCanvas colors)
function getClassColor(classId: number): string {
  const colors: { [key: number]: string } = {
    0: '#ef4444', // red - straight
    1: '#3b82f6', // blue - L-shape
    2: '#10b981', // green - U-shape
    3: '#f59e0b', // orange - complex
  };

  // For classes beyond the default ones, generate a color
  if (classId in colors) {
    return colors[classId];
  }

  // Generate color for custom classes
  const hue = (classId * 137) % 360; // Golden angle for good distribution
  return `hsl(${hue}, 70%, 55%)`;
}
