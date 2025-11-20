import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Plus,
  Search,
  X,
  CheckCircle,
  Clock,
  AlertTriangle,
  XCircle,
  Trash2,
  Eye,
  Filter
} from 'lucide-react';
import { analysesApi } from '../api/client';

function Analyses() {
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  useEffect(() => {
    fetchAnalyses();
  }, [statusFilter]);

  const fetchAnalyses = async () => {
    try {
      setLoading(true);
      const data = await analysesApi.list(statusFilter || null);
      setAnalyses(data);
    } catch (err) {
      setError('Failed to load analyses');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (analysisId) => {
    if (!confirm('Are you sure you want to delete this analysis?')) return;

    try {
      await analysesApi.delete(analysisId);
      await fetchAnalyses();
    } catch (err) {
      setError('Failed to delete analysis');
      console.error(err);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case 'running':
        return <Clock className="h-5 w-5 text-blue-600 animate-spin" />;
      case 'failed':
        return <XCircle className="h-5 w-5 text-red-600" />;
      default:
        return <Clock className="h-5 w-5 text-gray-600" />;
    }
  };

  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'running':
        return 'bg-blue-100 text-blue-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const filteredAnalyses = analyses.filter(analysis =>
    analysis.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    analysis.analysis_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    analysis.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Analyses</h1>
          <p className="text-gray-600 mt-1">View and manage risk analyses</p>
        </div>
        <Link to="/analyses/new" className="btn btn-primary flex items-center gap-2">
          <Plus className="h-4 w-4" />
          New Analysis
        </Link>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search analyses..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="input pl-10"
          />
          {searchTerm && (
            <button
              onClick={() => setSearchTerm('')}
              className="absolute right-3 top-1/2 -translate-y-1/2"
            >
              <X className="h-5 w-5 text-gray-400 hover:text-gray-600" />
            </button>
          )}
        </div>
        <div className="relative">
          <Filter className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="input pl-10 pr-8 appearance-none"
          >
            <option value="">All Status</option>
            <option value="pending">Pending</option>
            <option value="running">Running</option>
            <option value="completed">Completed</option>
            <option value="failed">Failed</option>
          </select>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Analyses List */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>
      ) : filteredAnalyses.length === 0 ? (
        <div className="card p-12 text-center">
          <AlertTriangle className="h-12 w-12 mx-auto text-gray-300 mb-3" />
          <p className="text-gray-500">
            {searchTerm || statusFilter ? 'No analyses match your filters' : 'No analyses yet'}
          </p>
          {!searchTerm && !statusFilter && (
            <Link to="/analyses/new" className="mt-4 inline-block text-primary-600 hover:text-primary-700">
              Create your first analysis
            </Link>
          )}
        </div>
      ) : (
        <div className="grid gap-4">
          {filteredAnalyses.map((analysis) => (
            <div key={analysis.analysis_id} className="card hover:shadow-md transition-shadow">
              <div className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-4">
                    <div className={`
                      p-3 rounded-lg
                      ${analysis.status === 'completed' ? 'bg-green-100' :
                        analysis.status === 'running' ? 'bg-blue-100' :
                        analysis.status === 'failed' ? 'bg-red-100' : 'bg-gray-100'}
                    `}>
                      {getStatusIcon(analysis.status)}
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">{analysis.name}</h3>
                      <p className="text-sm text-gray-500 mt-1">{analysis.analysis_id}</p>
                      {analysis.description && (
                        <p className="text-sm text-gray-600 mt-2">{analysis.description}</p>
                      )}
                      <div className="flex items-center gap-4 mt-3 text-sm text-gray-500">
                        <span>{analysis.document_count} documents</span>
                        <span>{analysis.risk_count} risks</span>
                        <span>Created {formatDate(analysis.created_at)}</span>
                      </div>
                      {analysis.status === 'running' && analysis.current_step && (
                        <div className="mt-3">
                          <p className="text-sm text-blue-600">{analysis.current_step}</p>
                          <div className="mt-2 progress-bar">
                            <div
                              className="progress-bar-fill"
                              style={{ width: `${analysis.progress}%` }}
                            />
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`badge ${getStatusBadgeClass(analysis.status)}`}>
                      {analysis.status}
                    </span>
                    <Link
                      to={`/analyses/${analysis.analysis_id}`}
                      className="p-2 hover:bg-gray-100 rounded-lg"
                      title="View details"
                    >
                      <Eye className="h-4 w-4 text-gray-600" />
                    </Link>
                    <button
                      onClick={() => handleDelete(analysis.analysis_id)}
                      className="p-2 hover:bg-red-50 rounded-lg"
                      title="Delete"
                    >
                      <Trash2 className="h-4 w-4 text-red-600" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Analyses;
