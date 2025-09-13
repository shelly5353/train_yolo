import React, { useState, useEffect, useCallback } from 'react';
import { ImageCanvas } from './components/ImageCanvas';
import { Sidebar } from './components/Sidebar';
import { useKeyboardShortcuts } from './hooks/useKeyboardShortcuts';
import { ApiService } from './services/api';
import {
  ImageInfo,
  ClassInfo,
  Annotation,
  Tool,
  BoundingBox,
  AnnotationStats
} from './types';
import { AlertCircle, Loader2 } from 'lucide-react';

function App() {
  // State
  const [images, setImages] = useState<ImageInfo[]>([]);
  const [classes, setClasses] = useState<ClassInfo[]>([]);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [annotations, setAnnotations] = useState<Annotation[]>([]);
  const [selectedAnnotation, setSelectedAnnotation] = useState<number | null>(null);
  const [currentTool, setCurrentTool] = useState<Tool>(Tool.BBOX);
  const [currentClass, setCurrentClass] = useState(0);
  const [stats, setStats] = useState<AnnotationStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load initial data
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        setIsLoading(true);
        setError(null);

        // Health check
        await ApiService.healthCheck();

        // Load images and classes
        const [imagesData, classesData, statsData] = await Promise.all([
          ApiService.fetchImages(),
          ApiService.fetchClasses(),
          ApiService.fetchStats()
        ]);

        setImages(imagesData.images);
        setClasses(classesData);
        setStats(statsData);

        // Load annotations for first image
        if (imagesData.images.length > 0) {
          await loadAnnotations(imagesData.images[0].filename);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data');
      } finally {
        setIsLoading(false);
      }
    };

    loadInitialData();
  }, []);

  // Load annotations for current image
  const loadAnnotations = async (filename: string) => {
    try {
      const data = await ApiService.fetchAnnotations(filename);
      setAnnotations(data.annotations);
      setSelectedAnnotation(null);
    } catch (err) {
      console.error('Failed to load annotations:', err);
      setAnnotations([]);
    }
  };

  // Save annotations
  const saveAnnotations = useCallback(async () => {
    if (images.length === 0) return;

    try {
      setIsSaving(true);
      const currentImage = images[currentImageIndex];
      await ApiService.saveAnnotations(currentImage.filename, annotations);

      // Update stats
      const statsData = await ApiService.fetchStats();
      setStats(statsData);

      // Update image info
      const updatedImages = [...images];
      updatedImages[currentImageIndex] = {
        ...updatedImages[currentImageIndex],
        has_labels: annotations.length > 0,
        label_count: annotations.length
      };
      setImages(updatedImages);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save annotations');
    } finally {
      setIsSaving(false);
    }
  }, [images, currentImageIndex, annotations]);

  // Navigation
  const goToPrevious = useCallback(() => {
    if (currentImageIndex > 0) {
      const newIndex = currentImageIndex - 1;
      setCurrentImageIndex(newIndex);
      loadAnnotations(images[newIndex].filename);
    }
  }, [currentImageIndex, images]);

  const goToNext = useCallback(() => {
    if (currentImageIndex < images.length - 1) {
      const newIndex = currentImageIndex + 1;
      setCurrentImageIndex(newIndex);
      loadAnnotations(images[newIndex].filename);
    }
  }, [currentImageIndex, images]);

  const selectImage = useCallback((index: number) => {
    if (index >= 0 && index < images.length) {
      setCurrentImageIndex(index);
      loadAnnotations(images[index].filename);
    }
  }, [images]);

  // Annotation operations
  const createAnnotation = useCallback((bbox: BoundingBox, classId: number) => {
    const newAnnotation: Annotation = {
      id: Date.now(), // Simple ID generation
      class_id: classId,
      class_name: classes.find(c => c.id === classId)?.name || 'unknown',
      x1: Math.round(bbox.x1),
      y1: Math.round(bbox.y1),
      x2: Math.round(bbox.x2),
      y2: Math.round(bbox.y2),
      width: Math.round(bbox.x2 - bbox.x1),
      height: Math.round(bbox.y2 - bbox.y1)
    };

    setAnnotations(prev => [...prev, newAnnotation]);
    setSelectedAnnotation(newAnnotation.id);
  }, [classes]);

  const deleteAnnotation = useCallback((id: number) => {
    setAnnotations(prev => prev.filter(ann => ann.id !== id));
    setSelectedAnnotation(null);
  }, []);

  const clearAllAnnotations = useCallback(() => {
    setAnnotations([]);
    setSelectedAnnotation(null);
  }, []);

  // Keyboard shortcuts
  const shortcuts = {
    // Navigation
    'arrowleft': goToPrevious,
    'arrowright': goToNext,

    // Tools
    'v': () => setCurrentTool(Tool.POINTER),
    'n': () => setCurrentTool(Tool.BBOX),
    'h': () => setCurrentTool(Tool.PAN),

    // Classes
    '1': () => setCurrentClass(0),
    '2': () => setCurrentClass(1),
    '3': () => setCurrentClass(2),
    '4': () => setCurrentClass(3),

    // Actions
    'cmd+s': saveAnnotations,
    'delete': () => {
      if (selectedAnnotation !== null) {
        deleteAnnotation(selectedAnnotation);
      }
    },
    'backspace': () => {
      if (selectedAnnotation !== null) {
        deleteAnnotation(selectedAnnotation);
      }
    },

    // Clear all (Cmd+K)
    'cmd+k': clearAllAnnotations,

    // Escape to deselect
    'escape': () => setSelectedAnnotation(null)
  };

  useKeyboardShortcuts(shortcuts, !isLoading && !error);

  // Loading state
  if (isLoading) {
    return (
      <div className="h-screen flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-600" />
          <div className="text-lg font-medium text-gray-900">Loading annotation tool...</div>
          <div className="text-sm text-gray-500">Connecting to backend and loading images</div>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="h-screen flex items-center justify-center">
        <div className="text-center max-w-md">
          <AlertCircle className="w-12 h-12 mx-auto mb-4 text-red-500" />
          <div className="text-lg font-medium text-gray-900 mb-2">Connection Error</div>
          <div className="text-sm text-gray-600 mb-4">{error}</div>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Retry
          </button>
          <div className="mt-4 text-xs text-gray-500">
            Make sure the Flask backend is running on port 5000
          </div>
        </div>
      </div>
    );
  }

  // No images state
  if (images.length === 0) {
    return (
      <div className="h-screen flex items-center justify-center">
        <div className="text-center max-w-md">
          <div className="text-lg font-medium text-gray-900 mb-2">No Images Found</div>
          <div className="text-sm text-gray-600">
            No images found in the data directory. Please add some PNG images to get started.
          </div>
        </div>
      </div>
    );
  }

  const currentImage = images[currentImageIndex];

  return (
    <div className="h-screen flex bg-gray-50">
      {/* Sidebar */}
      <Sidebar
        images={images}
        currentImageIndex={currentImageIndex}
        classes={classes}
        currentClass={currentClass}
        currentTool={currentTool}
        stats={stats}
        onImageSelect={selectImage}
        onClassSelect={setCurrentClass}
        onToolSelect={setCurrentTool}
        onSave={saveAnnotations}
        onPrevious={goToPrevious}
        onNext={goToNext}
        onClearAll={clearAllAnnotations}
        isSaving={isSaving}
      />

      {/* Main content */}
      <div className="flex-1 flex flex-col">
        {/* Status bar */}
        <div className="h-12 bg-white border-b border-gray-200 flex items-center px-4">
          <div className="flex items-center gap-4 text-sm text-gray-600">
            <div>
              <span className="font-medium">{currentImage.filename}</span>
              <span className="ml-2 text-gray-400">
                {currentImage.width} × {currentImage.height}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span>{annotations.length} annotations</span>
            </div>
          </div>

          {isSaving && (
            <div className="ml-auto flex items-center gap-2 text-blue-600">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span className="text-sm">Saving...</span>
            </div>
          )}
        </div>

        {/* Canvas */}
        <div className="flex-1">
          <ImageCanvas
            imageUrl={ApiService.getImageUrl(currentImage.filename)}
            imageWidth={currentImage.width}
            imageHeight={currentImage.height}
            annotations={annotations}
            selectedAnnotation={selectedAnnotation}
            currentTool={currentTool}
            currentClass={currentClass}
            onAnnotationCreate={createAnnotation}
            onAnnotationSelect={setSelectedAnnotation}
            onAnnotationDelete={deleteAnnotation}
          />
        </div>
      </div>
    </div>
  );
}

export default App;