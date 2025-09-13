import React from 'react';
import {
  Image,
  Save,
  SkipForward,
  SkipBack,
  Trash2,
  Mouse,
  Square,
  Hand,
  Zap,
  BarChart3,
  Keyboard
} from 'lucide-react';
import { ImageInfo, ClassInfo, Tool, AnnotationStats } from '../types';

interface SidebarProps {
  images: ImageInfo[];
  currentImageIndex: number;
  classes: ClassInfo[];
  currentClass: number;
  currentTool: Tool;
  stats: AnnotationStats | null;
  onImageSelect: (index: number) => void;
  onClassSelect: (classId: number) => void;
  onToolSelect: (tool: Tool) => void;
  onSave: () => void;
  onPrevious: () => void;
  onNext: () => void;
  onClearAll: () => void;
  isSaving: boolean;
}

const TOOL_INFO = {
  [Tool.POINTER]: { icon: Mouse, label: 'Select', shortcut: 'V' },
  [Tool.BBOX]: { icon: Square, label: 'Bounding Box', shortcut: 'N' },
  [Tool.PAN]: { icon: Hand, label: 'Pan', shortcut: 'H' }
};

const CLASS_COLORS = {
  0: 'bg-red-500',
  1: 'bg-blue-500',
  2: 'bg-green-500',
  3: 'bg-orange-500'
};

export const Sidebar: React.FC<SidebarProps> = ({
  images,
  currentImageIndex,
  classes,
  currentClass,
  currentTool,
  stats,
  onImageSelect,
  onClassSelect,
  onToolSelect,
  onSave,
  onPrevious,
  onNext,
  onClearAll,
  isSaving
}) => {
  const currentImage = images[currentImageIndex];

  return (
    <div className="sidebar">
      {/* Header */}
      <div className="sidebar-section">
        <div className="flex items-center gap-2 mb-4">
          <Image className="w-6 h-6 text-blue-600" />
          <h1 className="text-xl font-bold text-gray-900">YOLO Annotator</h1>
        </div>

        {/* Stats */}
        {stats && (
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div className="bg-gray-50 rounded-lg p-3">
              <div className="text-gray-600">Progress</div>
              <div className="text-lg font-bold text-gray-900">
                {stats.completion_rate}%
              </div>
              <div className="text-xs text-gray-500">
                {stats.labeled_images}/{stats.total_images} images
              </div>
            </div>
            <div className="bg-gray-50 rounded-lg p-3">
              <div className="text-gray-600">Annotations</div>
              <div className="text-lg font-bold text-gray-900">
                {stats.total_annotations}
              </div>
              <div className="text-xs text-gray-500">total objects</div>
            </div>
          </div>
        )}
      </div>

      {/* Navigation */}
      <div className="sidebar-section">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-semibold text-gray-700">Navigation</h3>
          <span className="text-sm text-gray-500">
            {currentImageIndex + 1} / {images.length}
          </span>
        </div>

        <div className="flex gap-2 mb-3">
          <button
            onClick={onPrevious}
            disabled={currentImageIndex === 0}
            className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-gray-100
                     hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg transition-colors"
          >
            <SkipBack className="w-4 h-4" />
            <span className="text-sm">Previous</span>
          </button>
          <button
            onClick={onNext}
            disabled={currentImageIndex === images.length - 1}
            className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-gray-100
                     hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg transition-colors"
          >
            <span className="text-sm">Next</span>
            <SkipForward className="w-4 h-4" />
          </button>
        </div>

        {currentImage && (
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="text-sm font-medium text-gray-700 mb-1">
              {currentImage.filename}
            </div>
            <div className="text-xs text-gray-500">
              {currentImage.width} × {currentImage.height}
              {currentImage.has_labels && (
                <span className="ml-2 inline-flex items-center gap-1">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  {currentImage.label_count} labels
                </span>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Tools */}
      <div className="sidebar-section">
        <h3 className="font-semibold text-gray-700 mb-3">Tools</h3>

        <div className="grid grid-cols-1 gap-2">
          {Object.entries(TOOL_INFO).map(([tool, info]) => {
            const Icon = info.icon;
            const isActive = currentTool === tool;

            return (
              <button
                key={tool}
                onClick={() => onToolSelect(tool as Tool)}
                className={`flex items-center gap-3 px-3 py-2 rounded-lg text-left transition-colors ${
                  isActive
                    ? 'bg-blue-100 text-blue-700 border border-blue-200'
                    : 'hover:bg-gray-100 text-gray-700'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span className="flex-1 text-sm">{info.label}</span>
                <span className="hotkey">{info.shortcut}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Classes */}
      <div className="sidebar-section">
        <h3 className="font-semibold text-gray-700 mb-3">Classes</h3>

        <div className="space-y-2">
          {classes.map((cls) => (
            <button
              key={cls.id}
              onClick={() => onClassSelect(cls.id)}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left transition-colors ${
                currentClass === cls.id
                  ? 'bg-blue-100 text-blue-700 border border-blue-200'
                  : 'hover:bg-gray-100 text-gray-700'
              }`}
            >
              <div className={`w-4 h-4 rounded ${CLASS_COLORS[cls.id as keyof typeof CLASS_COLORS]} flex-shrink-0`}></div>
              <span className="flex-1 text-sm">{cls.name}</span>
              <span className="hotkey">{cls.id + 1}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Actions */}
      <div className="sidebar-section">
        <h3 className="font-semibold text-gray-700 mb-3">Actions</h3>

        <div className="space-y-2">
          <button
            onClick={onSave}
            disabled={isSaving}
            className="w-full flex items-center gap-3 px-3 py-2 bg-blue-600 hover:bg-blue-700
                     disabled:opacity-50 text-white rounded-lg transition-colors"
          >
            <Save className="w-4 h-4" />
            <span className="flex-1 text-sm">
              {isSaving ? 'Saving...' : 'Save'}
            </span>
            <span className="text-xs opacity-75">⌘S</span>
          </button>

          <button
            onClick={onClearAll}
            className="w-full flex items-center gap-3 px-3 py-2 bg-red-600 hover:bg-red-700
                     text-white rounded-lg transition-colors"
          >
            <Trash2 className="w-4 h-4" />
            <span className="flex-1 text-sm">Clear All</span>
            <span className="text-xs opacity-75">Del</span>
          </button>
        </div>
      </div>

      {/* Keyboard Shortcuts */}
      <div className="sidebar-section">
        <h3 className="font-semibold text-gray-700 mb-3 flex items-center gap-2">
          <Keyboard className="w-4 h-4" />
          Shortcuts
        </h3>

        <div className="space-y-2 text-sm text-gray-600">
          <div className="flex justify-between">
            <span>Navigate</span>
            <span className="text-xs">← →</span>
          </div>
          <div className="flex justify-between">
            <span>Zoom</span>
            <span className="text-xs">⌘ + scroll</span>
          </div>
          <div className="flex justify-between">
            <span>Pan</span>
            <span className="text-xs">scroll or H</span>
          </div>
          <div className="flex justify-between">
            <span>Delete</span>
            <span className="text-xs">right click</span>
          </div>
          <div className="flex justify-between">
            <span>Classes</span>
            <span className="text-xs">1-4</span>
          </div>
        </div>
      </div>

      {/* Class Distribution */}
      {stats && (
        <div className="sidebar-section flex-1">
          <h3 className="font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <BarChart3 className="w-4 h-4" />
            Distribution
          </h3>

          <div className="space-y-2">
            {stats.class_distribution.map((item) => (
              <div key={item.class_id} className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded ${CLASS_COLORS[item.class_id as keyof typeof CLASS_COLORS]}`}></div>
                <span className="text-sm text-gray-600 flex-1">{item.class_name}</span>
                <span className="text-sm font-medium text-gray-900">{item.count}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};