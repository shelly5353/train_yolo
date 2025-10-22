import { ImageInfo, Annotation, ClassInfo, AnnotationStats } from '../types';

const API_BASE_URL = 'http://localhost:5002/api';

export class ApiService {
  static async fetchImages(): Promise<{ images: ImageInfo[]; classes: { [key: number]: string } }> {
    const response = await fetch(`${API_BASE_URL}/images`);
    if (!response.ok) {
      throw new Error(`Failed to fetch images: ${response.statusText}`);
    }
    return response.json();
  }

  static async fetchAnnotations(filename: string): Promise<{
    filename: string;
    width: number;
    height: number;
    annotations: Annotation[];
  }> {
    const response = await fetch(`${API_BASE_URL}/annotations/${filename}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch annotations: ${response.statusText}`);
    }
    return response.json();
  }

  static async saveAnnotations(filename: string, annotations: Annotation[]): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/annotations/${filename}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ annotations }),
    });

    if (!response.ok) {
      throw new Error(`Failed to save annotations: ${response.statusText}`);
    }
  }

  static async fetchClasses(): Promise<ClassInfo[]> {
    const response = await fetch(`${API_BASE_URL}/classes`);
    if (!response.ok) {
      throw new Error(`Failed to fetch classes: ${response.statusText}`);
    }
    const data = await response.json();
    return data.class_list;
  }

  static async fetchStats(): Promise<AnnotationStats> {
    const response = await fetch(`${API_BASE_URL}/stats`);
    if (!response.ok) {
      throw new Error(`Failed to fetch stats: ${response.statusText}`);
    }
    return response.json();
  }

  static getImageUrl(filename: string): string {
    return `${API_BASE_URL}/image/${filename}`;
  }

  static async healthCheck(): Promise<{ status: string; [key: string]: any }> {
    const response = await fetch(`${API_BASE_URL}/health`);
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.statusText}`);
    }
    return response.json();
  }

  static async getDatasetStatus(): Promise<{
    configured: boolean;
    dataset_dir: string | null;
    images_dir: string | null;
    labels_dir: string | null;
  }> {
    const response = await fetch(`${API_BASE_URL}/dataset/status`);
    if (!response.ok) {
      throw new Error(`Failed to get dataset status: ${response.statusText}`);
    }
    return response.json();
  }

  static async selectDataset(path?: string): Promise<{
    success: boolean;
    dataset_dir: string;
    images_dir: string;
    labels_dir: string;
    total_images: number;
    unlabeled_images: number;
    needs_labels: boolean;
    error?: string;
    invalid_structure?: boolean;
  }> {
    const response = await fetch(`${API_BASE_URL}/dataset/select`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ path }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || 'Failed to select dataset');
    }

    return data;
  }

  static async generateLabels(confidence: number = 0.25): Promise<{
    success: boolean;
    total_images: number;
    labeled_images: number;
    message: string;
  }> {
    const response = await fetch(`${API_BASE_URL}/dataset/generate-labels`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ confidence }),
    });

    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.error || 'Failed to generate labels');
    }

    return response.json();
  }
}