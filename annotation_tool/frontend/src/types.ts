export interface Annotation {
  id: number;
  class_id: number;
  class_name: string;
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  width: number;
  height: number;
}

export interface ImageInfo {
  filename: string;
  path: string;
  width: number;
  height: number;
  has_labels: boolean;
  label_count: number;
}

export interface ClassInfo {
  id: number;
  name: string;
}

export interface ViewTransform {
  x: number;
  y: number;
  scale: number;
}

export interface Point {
  x: number;
  y: number;
}

export interface BoundingBox {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

export interface AnnotationStats {
  total_images: number;
  labeled_images: number;
  unlabeled_images: number;
  total_annotations: number;
  class_distribution: Array<{
    class_id: number;
    class_name: string;
    count: number;
  }>;
  completion_rate: number;
}

export interface KeyboardShortcuts {
  [key: string]: () => void;
}

export enum Tool {
  POINTER = 'pointer',
  BBOX = 'bbox',
  PAN = 'pan'
}

export enum MouseButton {
  LEFT = 0,
  MIDDLE = 1,
  RIGHT = 2
}