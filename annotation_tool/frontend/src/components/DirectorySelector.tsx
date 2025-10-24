import React, { useState, useEffect } from 'react';
import { Folder, FolderOpen, AlertCircle, CheckCircle2, Loader2, FolderTree, ChevronDown } from 'lucide-react';

interface DirectorySelectorProps {
  onDirectorySelected: (path: string, stats: DirectoryStats) => void;
}

export interface DirectoryStats {
  success: boolean;
  directory: string;
  images_dir: string;
  labels_dir: string;
  images_count: number;
  existing_labels: number;
  generated_labels: number;
  generation_errors: number;
  total_labels: number;
}

interface AvailableDirectory {
  path: string;
  name: string;
  parent: string;
  images_count: number;
  labels_count: number;
  has_labels: boolean;
}

export const DirectorySelector: React.FC<DirectorySelectorProps> = ({ onDirectorySelected }) => {
  const [directoryPath, setDirectoryPath] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState<DirectoryStats | null>(null);
  const [autoGenerate, setAutoGenerate] = useState(true);
  const [availableDirectories, setAvailableDirectories] = useState<AvailableDirectory[]>([]);
  const [isLoadingDirs, setIsLoadingDirs] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);

  // Fetch available directories on mount
  useEffect(() => {
    const fetchDirectories = async () => {
      setIsLoadingDirs(true);
      try {
        const response = await fetch('http://localhost:5002/api/browse-directories');
        if (response.ok) {
          const data = await response.json();
          setAvailableDirectories(data.directories || []);
        }
      } catch (err) {
        console.error('Failed to fetch directories:', err);
      } finally {
        setIsLoadingDirs(false);
      }
    };

    fetchDirectories();
  }, []);

  const handleSelectDirectory = (path: string) => {
    setDirectoryPath(path);
    setShowDropdown(false);
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!directoryPath.trim()) {
      setError('Please enter a directory path');
      return;
    }

    setIsLoading(true);
    setError(null);
    setStats(null);

    try {
      const response = await fetch('http://localhost:5002/api/set-directory', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          directory: directoryPath.trim(),
          auto_generate: autoGenerate
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to set directory');
      }

      setStats(data);

      // Wait a moment to show the success state
      setTimeout(() => {
        onDirectorySelected(directoryPath.trim(), data);
      }, 1500);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to set directory');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-2xl w-full mx-auto p-8">
        <div className="bg-white rounded-xl shadow-lg p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
              <FolderOpen className="w-8 h-8 text-blue-600" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Select Dataset Directory
            </h1>
            <p className="text-gray-600">
              Choose a directory containing your image dataset to begin annotation
            </p>
          </div>

          {/* Expected Structure Info */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <div className="flex gap-3">
              <FolderTree className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <div className="text-sm font-medium text-blue-900 mb-2">
                  Expected Directory Structure:
                </div>
                <pre className="text-xs text-blue-800 font-mono">
{`selected_dataset/
├── images/       ← PNG files here
│   ├── img001.png
│   └── img002.png
└── labels/       ← YOLO format labels (optional)
    ├── img001.txt
    └── img002.txt`}
                </pre>
              </div>
            </div>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit}>
            {/* Available Directories Dropdown */}
            {availableDirectories.length > 0 && (
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Quick Select from Available Datasets
                </label>
                <div className="relative">
                  <button
                    type="button"
                    onClick={() => setShowDropdown(!showDropdown)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg text-left bg-white hover:bg-gray-50 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 flex items-center justify-between"
                    disabled={isLoading}
                  >
                    <span className="text-gray-700">
                      {directoryPath && availableDirectories.find(d => d.path === directoryPath)
                        ? availableDirectories.find(d => d.path === directoryPath)?.name
                        : 'Select a dataset...'}
                    </span>
                    <ChevronDown className={`w-5 h-5 text-gray-400 transition-transform ${showDropdown ? 'transform rotate-180' : ''}`} />
                  </button>

                  {showDropdown && (
                    <div className="absolute z-10 mt-1 w-full bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-auto">
                      {isLoadingDirs ? (
                        <div className="px-4 py-3 text-center text-gray-500">
                          <Loader2 className="w-4 h-4 animate-spin inline mr-2" />
                          Loading directories...
                        </div>
                      ) : (
                        availableDirectories.map((dir) => (
                          <button
                            key={dir.path}
                            type="button"
                            onClick={() => handleSelectDirectory(dir.path)}
                            className="w-full px-4 py-2 text-left hover:bg-blue-50 flex items-center justify-between group"
                          >
                            <div className="flex items-center gap-2">
                              <Folder className="w-4 h-4 text-gray-400" />
                              <div>
                                <div className="font-medium text-gray-900">{dir.name}</div>
                                <div className="text-xs text-gray-500">{dir.parent}</div>
                              </div>
                            </div>
                            <div className="text-xs text-gray-500">
                              {dir.images_count} images
                              {dir.has_labels && ` • ${dir.labels_count} labels`}
                            </div>
                          </button>
                        ))
                      )}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Manual Input */}
            <div className="mb-4">
              <label htmlFor="directory" className="block text-sm font-medium text-gray-700 mb-2">
                {availableDirectories.length > 0 ? 'Or Enter Path Manually' : 'Dataset Directory Path'}
              </label>
              <input
                id="directory"
                type="text"
                value={directoryPath}
                onChange={(e) => setDirectoryPath(e.target.value)}
                placeholder="/path/to/your/dataset"
                className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  error ? 'border-red-500' : 'border-gray-300'
                }`}
                disabled={isLoading}
              />
            </div>

            {/* Auto-generate checkbox */}
            <div className="mb-6">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={autoGenerate}
                  onChange={(e) => setAutoGenerate(e.target.checked)}
                  disabled={isLoading}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">
                  Auto-generate labels for unlabeled images using YOLO model
                </span>
              </label>
            </div>

            {/* Error Message */}
            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
                <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <div className="text-sm font-medium text-red-900">Error</div>
                  <div className="text-sm text-red-700">{error}</div>
                  {error.includes('images/') && (
                    <div className="mt-2 text-xs text-red-600">
                      Make sure your directory has an "images/" subfolder containing PNG files
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Success Stats */}
            {stats && stats.success && (
              <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-start gap-2">
                  <CheckCircle2 className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                  <div className="flex-1">
                    <div className="text-sm font-medium text-green-900 mb-2">
                      Directory Set Successfully!
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-xs text-green-700">
                      <div>• Total images: {stats.images_count}</div>
                      <div>• Existing labels: {stats.existing_labels}</div>
                      {autoGenerate && stats.generated_labels > 0 && (
                        <>
                          <div>• Generated labels: {stats.generated_labels}</div>
                          <div>• Total labels: {stats.total_labels}</div>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading || !directoryPath.trim()}
              className={`w-full py-3 px-4 rounded-lg font-medium transition-colors ${
                isLoading || !directoryPath.trim()
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
            >
              {isLoading ? (
                <span className="flex items-center justify-center gap-2">
                  <Loader2 className="w-5 h-5 animate-spin" />
                  {autoGenerate ? 'Setting Directory & Generating Labels...' : 'Setting Directory...'}
                </span>
              ) : stats?.success ? (
                <span className="flex items-center justify-center gap-2">
                  <CheckCircle2 className="w-5 h-5" />
                  Loading Annotation Tool...
                </span>
              ) : (
                <span className="flex items-center justify-center gap-2">
                  <Folder className="w-5 h-5" />
                  Set Directory
                </span>
              )}
            </button>
          </form>

          {/* Example Paths */}
          <div className="mt-6 pt-6 border-t border-gray-200">
            <div className="text-xs text-gray-500">
              <div className="font-medium mb-1">Example paths:</div>
              <div>• /Users/username/Desktop/my_dataset</div>
              <div>• /home/user/projects/training_data</div>
              <div>• /Users/shellysmac/Documents/Work/train_yolo/new_dataset</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};