import React, { useState, useEffect } from 'react';
import {
  Settings,
  Plus,
  Edit2,
  Trash2,
  X,
  Save,
  AlertCircle,
  CheckCircle,
  Loader2,
  RefreshCw,
  ArrowRight
} from 'lucide-react';
import { ApiService } from '../services/api';

interface LabelClass {
  id: number;
  name: string;
  count: number;
  is_complex: boolean;
}

interface LabelManagerProps {
  isOpen: boolean;
  onClose: () => void;
  onLabelsUpdated: () => void; // Callback to refresh main app data
}

export const LabelManager: React.FC<LabelManagerProps> = ({
  isOpen,
  onClose,
  onLabelsUpdated
}) => {
  const [classes, setClasses] = useState<LabelClass[]>([]);
  const [totalAnnotations, setTotalAnnotations] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Add/Edit state
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editingName, setEditingName] = useState('');
  const [isAdding, setIsAdding] = useState(false);
  const [newClassName, setNewClassName] = useState('');

  // Bulk reclassify state
  const [showBulkMode, setShowBulkMode] = useState(false);
  const [bulkFromClass, setBulkFromClass] = useState<number | null>(null);
  const [bulkToClass, setBulkToClass] = useState<number | null>(null);
  const [bulkProcessing, setBulkProcessing] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadClasses();
    }
  }, [isOpen]);

  const loadClasses = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await ApiService.fetchLabelManagement();
      setClasses(data.classes);
      setTotalAnnotations(data.total_annotations);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load classes');
    } finally {
      setLoading(false);
    }
  };

  const handleAddClass = async () => {
    if (!newClassName.trim()) {
      setError('Class name cannot be empty');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      await ApiService.addLabelClass(newClassName.trim());
      setSuccess(`Added class "${newClassName}"`);
      setNewClassName('');
      setIsAdding(false);
      await loadClasses();
      onLabelsUpdated();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add class');
    } finally {
      setLoading(false);
    }
  };

  const handleEditClass = async (classId: number) => {
    if (!editingName.trim()) {
      setError('Class name cannot be empty');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      await ApiService.editLabelClass(classId, editingName.trim());
      setSuccess(`Updated class to "${editingName}"`);
      setEditingId(null);
      setEditingName('');
      await loadClasses();
      onLabelsUpdated();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to edit class');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteClass = async (classId: number, className: string) => {
    if (!window.confirm(`Are you sure you want to delete class "${className}"?`)) {
      return;
    }

    try {
      setLoading(true);
      setError(null);
      await ApiService.deleteLabelClass(classId);
      setSuccess(`Deleted class "${className}"`);
      await loadClasses();
      onLabelsUpdated();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete class');
    } finally {
      setLoading(false);
    }
  };

  const handleBulkReclassify = async () => {
    if (bulkFromClass === null || bulkToClass === null) {
      setError('Please select both source and target classes');
      return;
    }

    if (bulkFromClass === bulkToClass) {
      setError('Source and target classes must be different');
      return;
    }

    const fromClass = classes.find(c => c.id === bulkFromClass);
    const toClass = classes.find(c => c.id === bulkToClass);

    if (!window.confirm(
      `Reclassify ALL "${fromClass?.name}" annotations (${fromClass?.count} total) to "${toClass?.name}"?\n\n` +
      `This will update all label files in the dataset.`
    )) {
      return;
    }

    try {
      setBulkProcessing(true);
      setError(null);

      const result = await ApiService.bulkReclassifyLabels(bulkFromClass, bulkToClass);

      setSuccess(
        `Bulk reclassify complete!\n` +
        `Updated ${result.updated_annotations} annotations in ${result.updated_files} files\n` +
        `${result.from_class.name} → ${result.to_class.name}`
      );

      setShowBulkMode(false);
      setBulkFromClass(null);
      setBulkToClass(null);

      await loadClasses();
      onLabelsUpdated();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to bulk reclassify');
    } finally {
      setBulkProcessing(false);
    }
  };

  const startEdit = (classItem: LabelClass) => {
    setEditingId(classItem.id);
    setEditingName(classItem.name);
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditingName('');
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <Settings className="w-6 h-6 text-blue-600" />
            <h2 className="text-2xl font-bold text-gray-900">Manage Labels</h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* Error/Success Messages */}
          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div className="text-sm text-red-800 whitespace-pre-line">{error}</div>
              <button
                onClick={() => setError(null)}
                className="ml-auto p-1 hover:bg-red-100 rounded"
              >
                <X className="w-4 h-4 text-red-600" />
              </button>
            </div>
          )}

          {success && (
            <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
              <div className="text-sm text-green-800 whitespace-pre-line">{success}</div>
              <button
                onClick={() => setSuccess(null)}
                className="ml-auto p-1 hover:bg-green-100 rounded"
              >
                <X className="w-4 h-4 text-green-600" />
              </button>
            </div>
          )}

          {/* Stats */}
          <div className="mb-6 grid grid-cols-3 gap-4">
            <div className="bg-blue-50 rounded-lg p-4">
              <div className="text-sm text-blue-600 font-medium">Total Classes</div>
              <div className="text-2xl font-bold text-blue-900">{classes.length}</div>
            </div>
            <div className="bg-purple-50 rounded-lg p-4">
              <div className="text-sm text-purple-600 font-medium">Total Annotations</div>
              <div className="text-2xl font-bold text-purple-900">{totalAnnotations}</div>
            </div>
            <div className="bg-orange-50 rounded-lg p-4">
              <div className="text-sm text-orange-600 font-medium">Complex Labels</div>
              <div className="text-2xl font-bold text-orange-900">
                {classes.find(c => c.is_complex)?.count || 0}
              </div>
            </div>
          </div>

          {/* Bulk Reclassify Section */}
          <div className="mb-6">
            <button
              onClick={() => setShowBulkMode(!showBulkMode)}
              className="flex items-center gap-2 px-4 py-2 bg-orange-100 text-orange-700
                       rounded-lg hover:bg-orange-200 transition-colors font-medium"
            >
              <RefreshCw className="w-4 h-4" />
              {showBulkMode ? 'Hide' : 'Show'} Bulk Reclassify
            </button>

            {showBulkMode && (
              <div className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
                <h3 className="font-semibold text-gray-900 mb-3">Bulk Reclassify Annotations</h3>
                <div className="flex items-center gap-3 flex-wrap">
                  <div className="flex-1 min-w-[200px]">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      From Class
                    </label>
                    <select
                      value={bulkFromClass || ''}
                      onChange={(e) => setBulkFromClass(Number(e.target.value))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2
                               focus:ring-blue-500 focus:border-blue-500"
                      disabled={bulkProcessing}
                    >
                      <option value="">Select source class...</option>
                      {classes.map(cls => (
                        <option key={cls.id} value={cls.id}>
                          {cls.name} ({cls.count} annotations)
                        </option>
                      ))}
                    </select>
                  </div>

                  <ArrowRight className="w-5 h-5 text-gray-400 flex-shrink-0 mt-6" />

                  <div className="flex-1 min-w-[200px]">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      To Class
                    </label>
                    <select
                      value={bulkToClass || ''}
                      onChange={(e) => setBulkToClass(Number(e.target.value))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2
                               focus:ring-blue-500 focus:border-blue-500"
                      disabled={bulkProcessing}
                    >
                      <option value="">Select target class...</option>
                      {classes.map(cls => (
                        <option key={cls.id} value={cls.id}>
                          {cls.name}
                        </option>
                      ))}
                    </select>
                  </div>

                  <button
                    onClick={handleBulkReclassify}
                    disabled={bulkProcessing || bulkFromClass === null || bulkToClass === null}
                    className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700
                             disabled:opacity-50 disabled:cursor-not-allowed transition-colors
                             flex items-center gap-2 mt-6"
                  >
                    {bulkProcessing ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Processing...
                      </>
                    ) : (
                      <>
                        <RefreshCw className="w-4 h-4" />
                        Reclassify All
                      </>
                    )}
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Classes Table */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-gray-900">Label Classes</h3>
              {!isAdding && (
                <button
                  onClick={() => setIsAdding(true)}
                  className="flex items-center gap-2 px-3 py-1.5 bg-blue-600 text-white rounded-lg
                           hover:bg-blue-700 transition-colors text-sm"
                  disabled={loading}
                >
                  <Plus className="w-4 h-4" />
                  Add New Class
                </button>
              )}
            </div>

            {/* Add New Class Form */}
            {isAdding && (
              <div className="mb-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
                <div className="flex items-center gap-3">
                  <input
                    type="text"
                    value={newClassName}
                    onChange={(e) => setNewClassName(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleAddClass()}
                    placeholder="Enter class name (supports Hebrew)"
                    className="flex-1 px-3 py-2 border border-blue-300 rounded-lg focus:ring-2
                             focus:ring-blue-500 focus:border-blue-500"
                    autoFocus
                    disabled={loading}
                  />
                  <button
                    onClick={handleAddClass}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700
                             transition-colors flex items-center gap-2"
                    disabled={loading}
                  >
                    <Save className="w-4 h-4" />
                    Add
                  </button>
                  <button
                    onClick={() => {
                      setIsAdding(false);
                      setNewClassName('');
                    }}
                    className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300
                             transition-colors"
                    disabled={loading}
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}

            {/* Classes List */}
            {loading && classes.length === 0 ? (
              <div className="text-center py-8">
                <Loader2 className="w-8 h-8 animate-spin mx-auto text-blue-600" />
                <div className="text-sm text-gray-500 mt-2">Loading classes...</div>
              </div>
            ) : classes.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                No classes found. Add your first class above.
              </div>
            ) : (
              <div className="space-y-2">
                {classes.map((classItem) => (
                  <div
                    key={classItem.id}
                    className={`p-4 rounded-lg border transition-colors ${
                      classItem.is_complex
                        ? 'bg-orange-50 border-orange-200'
                        : 'bg-white border-gray-200'
                    }`}
                  >
                    {editingId === classItem.id ? (
                      // Edit Mode
                      <div className="flex items-center gap-3">
                        <div className="flex items-center gap-3 flex-1">
                          <div className="w-16 text-sm font-mono text-gray-500">
                            ID: {classItem.id}
                          </div>
                          <input
                            type="text"
                            value={editingName}
                            onChange={(e) => setEditingName(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && handleEditClass(classItem.id)}
                            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2
                                     focus:ring-blue-500 focus:border-blue-500"
                            autoFocus
                            disabled={loading}
                          />
                        </div>
                        <button
                          onClick={() => handleEditClass(classItem.id)}
                          className="p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                          disabled={loading}
                        >
                          <Save className="w-4 h-4" />
                        </button>
                        <button
                          onClick={cancelEdit}
                          className="p-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
                          disabled={loading}
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    ) : (
                      // View Mode
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4 flex-1">
                          <div className="w-16 text-sm font-mono text-gray-500">
                            ID: {classItem.id}
                          </div>
                          <div className="font-medium text-gray-900">{classItem.name}</div>
                          <div className="text-sm text-gray-500">
                            {classItem.count} annotation{classItem.count !== 1 ? 's' : ''}
                          </div>
                          {classItem.is_complex && (
                            <span className="px-2 py-1 bg-orange-100 text-orange-700 text-xs
                                         rounded-full font-medium">
                              Complex
                            </span>
                          )}
                        </div>
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => startEdit(classItem)}
                            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                            disabled={loading}
                          >
                            <Edit2 className="w-4 h-4 text-gray-600" />
                          </button>
                          <button
                            onClick={() => handleDeleteClass(classItem.id, classItem.name)}
                            className="p-2 hover:bg-red-100 rounded-lg transition-colors"
                            disabled={loading || classItem.count > 0}
                            title={classItem.count > 0 ? 'Cannot delete class with annotations' : 'Delete class'}
                          >
                            <Trash2 className={`w-4 h-4 ${classItem.count > 0 ? 'text-gray-300' : 'text-red-600'}`} />
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-gray-200 bg-gray-50">
          <div className="text-sm text-gray-500">
            Changes are saved automatically to <code className="px-2 py-1 bg-gray-200 rounded">classes.txt</code>
          </div>
          <button
            onClick={onClose}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700
                     transition-colors font-medium"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
};
