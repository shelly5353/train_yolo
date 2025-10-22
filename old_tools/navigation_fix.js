// Navigation fix for React frontend
// This addresses the missing labels and navigation loop issues

// ISSUE 1: Missing labels when going back
// CAUSE: Annotations aren't auto-saved before navigation
// FIX: Auto-save annotations before changing images

// ISSUE 2: Navigation loop / repeating same image
// CAUSE: Possible race condition in state updates or index boundaries
// FIX: Add proper boundary checks and state synchronization

// Modified navigation functions should:
const goToPrevious = useCallback(async () => {
  if (currentImageIndex > 0) {
    // Auto-save current annotations before navigating
    if (annotations.length > 0) {
      await saveAnnotations();
    }

    const newIndex = currentImageIndex - 1;
    setCurrentImageIndex(newIndex);
    await loadAnnotations(images[newIndex].filename);
  }
}, [currentImageIndex, images, annotations, saveAnnotations]);

const goToNext = useCallback(async () => {
  if (currentImageIndex < images.length - 1) {
    // Auto-save current annotations before navigating
    if (annotations.length > 0) {
      await saveAnnotations();
    }

    const newIndex = currentImageIndex + 1;
    setCurrentImageIndex(newIndex);
    await loadAnnotations(images[newIndex].filename);
  }
}, [currentImageIndex, images, annotations, saveAnnotations]);

// Also need to prevent navigation button spam
// Add loading state during navigation to prevent rapid clicks