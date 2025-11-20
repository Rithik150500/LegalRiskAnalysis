import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  FileText,
  CheckSquare,
  Square,
  Play,
  AlertCircle
} from 'lucide-react';
import { documentsApi, analysesApi } from '../api/client';

function NewAnalysis() {
  const navigate = useNavigate();
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    selectedDocs: []
  });

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      const data = await documentsApi.list();
      setDocuments(data);
    } catch (err) {
      setError('Failed to load documents');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const toggleDocument = (docId) => {
    setFormData(prev => ({
      ...prev,
      selectedDocs: prev.selectedDocs.includes(docId)
        ? prev.selectedDocs.filter(id => id !== docId)
        : [...prev.selectedDocs, docId]
    }));
  };

  const selectAll = () => {
    setFormData(prev => ({
      ...prev,
      selectedDocs: documents.map(d => d.doc_id)
    }));
  };

  const deselectAll = () => {
    setFormData(prev => ({
      ...prev,
      selectedDocs: []
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!formData.name.trim()) {
      setError('Please enter an analysis name');
      return;
    }

    if (formData.selectedDocs.length === 0) {
      setError('Please select at least one document');
      return;
    }

    try {
      setSubmitting(true);
      setError(null);

      const analysis = await analysesApi.create({
        name: formData.name.trim(),
        description: formData.description.trim(),
        document_ids: formData.selectedDocs
      });

      navigate(`/analyses/${analysis.analysis_id}`);
    } catch (err) {
      setError('Failed to create analysis');
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate('/analyses')}
          className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Analyses
        </button>
        <h1 className="text-2xl font-bold text-gray-900">New Analysis</h1>
        <p className="text-gray-600 mt-1">Create a new legal risk analysis</p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6 flex items-center gap-2">
          <AlertCircle className="h-5 w-5 flex-shrink-0" />
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Analysis Details */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-semibold text-gray-900">Analysis Details</h3>
          </div>
          <div className="card-body space-y-4">
            <div>
              <label htmlFor="name" className="label">
                Analysis Name <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g., Q4 2023 Contract Review"
                className="input"
                required
              />
            </div>
            <div>
              <label htmlFor="description" className="label">Description</label>
              <textarea
                id="description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Optional description of this analysis..."
                rows={3}
                className="input"
              />
            </div>
          </div>
        </div>

        {/* Document Selection */}
        <div className="card">
          <div className="card-header flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900">
              Select Documents <span className="text-red-500">*</span>
            </h3>
            <div className="flex items-center gap-2 text-sm">
              <button
                type="button"
                onClick={selectAll}
                className="text-primary-600 hover:text-primary-700"
              >
                Select All
              </button>
              <span className="text-gray-300">|</span>
              <button
                type="button"
                onClick={deselectAll}
                className="text-gray-600 hover:text-gray-700"
              >
                Deselect All
              </button>
            </div>
          </div>
          <div className="card-body">
            {loading ? (
              <div className="flex items-center justify-center h-32">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
              </div>
            ) : documents.length === 0 ? (
              <div className="text-center py-8">
                <FileText className="h-12 w-12 mx-auto text-gray-300 mb-3" />
                <p className="text-gray-500">No documents available</p>
                <button
                  type="button"
                  onClick={() => navigate('/documents')}
                  className="mt-2 text-primary-600 hover:text-primary-700"
                >
                  Upload documents first
                </button>
              </div>
            ) : (
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {documents.map((doc) => (
                  <label
                    key={doc.doc_id}
                    className={`
                      flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-colors
                      ${formData.selectedDocs.includes(doc.doc_id)
                        ? 'bg-primary-50 border border-primary-200'
                        : 'bg-gray-50 border border-transparent hover:bg-gray-100'}
                    `}
                  >
                    <button
                      type="button"
                      onClick={() => toggleDocument(doc.doc_id)}
                      className="flex-shrink-0"
                    >
                      {formData.selectedDocs.includes(doc.doc_id) ? (
                        <CheckSquare className="h-5 w-5 text-primary-600" />
                      ) : (
                        <Square className="h-5 w-5 text-gray-400" />
                      )}
                    </button>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-gray-900 truncate">
                        {doc.original_filename}
                      </p>
                      <p className="text-sm text-gray-500">
                        {doc.doc_id} | {doc.page_count} pages
                      </p>
                    </div>
                  </label>
                ))}
              </div>
            )}
            {formData.selectedDocs.length > 0 && (
              <p className="mt-4 text-sm text-gray-600">
                {formData.selectedDocs.length} document(s) selected
              </p>
            )}
          </div>
        </div>

        {/* Submit */}
        <div className="flex items-center justify-end gap-4">
          <button
            type="button"
            onClick={() => navigate('/analyses')}
            className="btn btn-secondary"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={submitting || documents.length === 0}
            className="btn btn-primary flex items-center gap-2"
          >
            <Play className="h-4 w-4" />
            {submitting ? 'Starting...' : 'Start Analysis'}
          </button>
        </div>
      </form>
    </div>
  );
}

export default NewAnalysis;
