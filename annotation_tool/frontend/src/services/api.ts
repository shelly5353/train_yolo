import { ImageInfo, Annotation, ClassInfo, AnnotationStats } from '../types';
import { DirectoryStats } from '../components/DirectorySelector';

// Use environment variable for API URL in production, localhost for development
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5002/api';

export class ApiService {
  static async setDirectory(path: string, autoGenerate: boolean = true): Promise<DirectoryStats> {
    const response = await fetch(`${API_BASE_URL}/set-directory`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        directory: path,
        auto_generate: autoGenerate
      })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to set directory');
    }

    return response.json();
  }
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

  // ======================================================================
  // LABEL MANAGEMENT METHODS
  // ======================================================================

  static async fetchLabelManagement(): Promise<{
    classes: Array<{
      id: number;
      name: string;
      count: number;
      is_complex: boolean;
    }>;
    total_classes: number;
    total_annotations: number;
  }> {
    const response = await fetch(`${API_BASE_URL}/labels/manage`);
    if (!response.ok) {
      throw new Error(`Failed to fetch label management info: ${response.statusText}`);
    }
    return response.json();
  }

  static async addLabelClass(name: string): Promise<{
    success: boolean;
    class_id: number;
    class_name: string;
    total_classes: number;
  }> {
    const response = await fetch(`${API_BASE_URL}/labels/add`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to add label class');
    }

    return response.json();
  }

  static async editLabelClass(classId: number, name: string): Promise<{
    success: boolean;
    class_id: number;
    old_name: string;
    new_name: string;
  }> {
    const response = await fetch(`${API_BASE_URL}/labels/edit/${classId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to edit label class');
    }

    return response.json();
  }

  static async deleteLabelClass(classId: number): Promise<{
    success: boolean;
    deleted_class_id: number;
    deleted_class_name: string;
  }> {
    const response = await fetch(`${API_BASE_URL}/labels/delete/${classId}`, {
      method: 'DELETE'
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || error.message || 'Failed to delete label class');
    }

    return response.json();
  }

  static async bulkReclassifyLabels(
    fromClassId: number,
    toClassId: number,
    imageFilenames?: string[]
  ): Promise<{
    success: boolean;
    updated_files: number;
    updated_annotations: number;
    from_class: { id: number; name: string };
    to_class: { id: number; name: string };
    errors?: string[];
  }> {
    const response = await fetch(`${API_BASE_URL}/labels/bulk-reclassify`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        from_class_id: fromClassId,
        to_class_id: toClassId,
        image_filenames: imageFilenames || []
      })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to bulk reclassify labels');
    }

    return response.json();
  }
}