import React, { useState } from 'react';
import { FolderOpen, AlertCircle, CheckCircle, Loader2, Play } from 'lucide-react';
import { ApiService } from '../services/api';

interface DatasetSetupProps {
  onDatasetConfigured: () => void;
}

export const DatasetSetup: React.FC<DatasetSetupProps> = ({ onDatasetConfigured }) => {
  const [isSelecting, setIsSelecting] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [datasetInfo, setDatasetInfo] = useState<{
    dataset_dir: string;
    total_images: number;
    unlabeled_images: number;
    needs_labels: boolean;
  } | null>(null);

  const handleSelectDataset = async () => {
    try {
      setIsSelecting(true);
      setError(null);

      const result = await ApiService.selectDataset();

      setDatasetInfo({
        dataset_dir: result.dataset_dir,
        total_images: result.total_images,
        unlabeled_images: result.unlabeled_images,
        needs_labels: result.needs_labels
      });

      // If no labels needed, proceed directly
      if (!result.needs_labels) {
        onDatasetConfigured();
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to select dataset');
    } finally {
      setIsSelecting(false);
    }
  };

  const handleGenerateLabels = async () => {
    try {
      setIsGenerating(true);
      setError(null);

      await ApiService.generateLabels(0.25);

      // Labels generated, proceed to annotation
      onDatasetConfigured();

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate labels');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSkipGeneration = () => {
    // Proceed without generating labels (user will annotate manually)
    onDatasetConfigured();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="max-w-2xl w-full bg-white rounded-2xl shadow-xl p-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
            <FolderOpen className="w-8 h-8 text-blue-600" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Dataset Selection
          </h1>
          <p className="text-gray-600">
            Select a dataset folder to begin annotation
          </p>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-red-900">Error</p>
              <p className="text-sm text-red-700 whitespace-pre-wrap">{error}</p>
            </div>
          </div>
        )}

        {/* Dataset not selected yet */}
        {!datasetInfo && (
          <div className="space-y-6">
            <div className="bg-gray-50 rounded-lg p-6 border-2 border-dashed border-gray-300">
              <h3 className="font-semibold text-gray-900 mb-3">Required Structure:</h3>
              <pre className="text-sm text-gray-700 bg-white p-4 rounded border border-gray-200 font-mono">
{`your_dataset/
├── images/
│   ├── image001.png
│   ├── image002.png
│   └── ...
└── labels/
    ├── image001.txt
    ├── image002.txt
    └── ...`}
              </pre>
              <p className="text-sm text-gray-600 mt-3">
                The labels/ folder can be empty - we'll generate labels automatically using YOLO if needed.
              </p>
            </div>

            <button
              onClick={handleSelectDataset}
              disabled={isSelecting}
              className="w-full py-4 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isSelecting ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Opening File Browser...
                </>
              ) : (
                <>
                  <FolderOpen className="w-5 h-5" />
                  Select Dataset Folder
                </>
              )}
            </button>

            <p className="text-xs text-center text-gray-500">
              A macOS file browser dialog will appear
            </p>
          </div>
        )}

        {/* Dataset selected, needs label generation */}
        {datasetInfo && datasetInfo.needs_labels && (
          <div className="space-y-6">
            <div className="bg-blue-50 rounded-lg p-6 border border-blue-200">
              <div className="flex items-start gap-3 mb-4">
                <CheckCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold text-blue-900">Dataset Selected</p>
                  <p className="text-sm text-blue-700 mt-1 break-all">{datasetInfo.dataset_dir}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 mt-4">
                <div className="bg-white rounded p-3">
                  <div className="text-2xl font-bold text-gray-900">{datasetInfo.total_images}</div>
                  <div className="text-sm text-gray-600">Total Images</div>
                </div>
                <div className="bg-white rounded p-3">
                  <div className="text-2xl font-bold text-orange-600">{datasetInfo.unlabeled_images}</div>
                  <div className="text-sm text-gray-600">Need Labels</div>
                </div>
              </div>
            </div>

            <div className="bg-amber-50 rounded-lg p-6 border border-amber-200">
              <div className="flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <p className="font-semibold text-amber-900 mb-2">Auto-Generate Labels?</p>
                  <p className="text-sm text-amber-700 mb-4">
                    {datasetInfo.unlabeled_images} images don't have labels yet.
                    We can automatically generate initial labels using the YOLO model, or you can create them manually.
                  </p>

                  <div className="flex gap-3">
                    <button
                      onClick={handleGenerateLabels}
                      disabled={isGenerating}
                      className="flex-1 py-3 bg-amber-600 text-white font-semibold rounded-lg hover:bg-amber-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                    >
                      {isGenerating ? (
                        <>
                          <Loader2 className="w-5 h-5 animate-spin" />
                          Generating...
                        </>
                      ) : (
                        <>
                          <Play className="w-5 h-5" />
                          Auto-Generate
                        </>
                      )}
                    </button>

                    <button
                      onClick={handleSkipGeneration}
                      disabled={isGenerating}
                      className="flex-1 py-3 bg-gray-200 text-gray-700 font-semibold rounded-lg hover:bg-gray-300 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Skip (Manual)
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <button
              onClick={() => setDatasetInfo(null)}
              className="w-full py-2 text-gray-600 text-sm hover:text-gray-900 transition-colors"
            >
              ← Choose Different Folder
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
