import { ImageInfo, Annotation, ClassInfo, AnnotationStats } from '../types';
import { DirectoryStats } from '../components/DirectorySelector';

const API_BASE_URL = 'http://localhost:5002/api';

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
}