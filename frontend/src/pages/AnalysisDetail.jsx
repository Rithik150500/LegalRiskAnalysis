import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  ArrowLeft,
  CheckCircle,
  Clock,
  XCircle,
  AlertTriangle,
  FileText,
  Download,
  ExternalLink,
  Filter,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { analysesApi } from '../api/client';
import RiskChart from '../components/RiskChart';

function AnalysisDetail() {
  const { analysisId } = useParams();
  const navigate = useNavigate();
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedSeverity, setSelectedSeverity] = useState('');
  const [expandedRisks, setExpandedRisks] = useState({});

  useEffect(() => {
    fetchAnalysis();
    const interval = setInterval(() => {
      if (analysis?.status === 'running' || analysis?.status === 'pending') {
        fetchAnalysis();
      }
    }, 2000);
    return () => clearInterval(interval);
  }, [analysisId]);

  const fetchAnalysis = async () => {
    try {
      const data = await analysesApi.get(analysisId);
      setAnalysis(data);
      setLoading(false);
    } catch (err) {
      setError('Failed to load analysis');
      console.error(err);
      setLoading(false);
    }
  };

  const toggleRisk = (riskId) => {
    setExpandedRisks(prev => ({
      ...prev,
      [riskId]: !prev[riskId]
    }));
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
        return <CheckCircle className="h-6 w-6 text-green-600" />;
      case 'running':
        return <Clock className="h-6 w-6 text-blue-600" />;
      case 'failed':
        return <XCircle className="h-6 w-6 text-red-600" />;
      default:
        return <Clock className="h-6 w-6 text-gray-600" />;
    }
  };

  const getSeverityClass = (severity) => {
    switch (severity) {
      case 'Critical':
        return 'risk-critical';
      case 'High':
        return 'risk-high';
      case 'Medium':
        return 'risk-medium';
      case 'Low':
        return 'risk-low';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error || !analysis) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">{error || 'Analysis not found'}</p>
        <button onClick={() => navigate('/analyses')} className="mt-4 btn btn-primary">
          Back to Analyses
        </button>
      </div>
    );
  }

  const filteredRisks = (analysis.risks || []).filter(risk => {
    if (selectedCategory && risk.category !== selectedCategory) return false;
    if (selectedSeverity && risk.severity !== selectedSeverity) return false;
    return true;
  });

  const riskSummary = {
    by_severity: {
      Critical: analysis.risks?.filter(r => r.severity === 'Critical').length || 0,
      High: analysis.risks?.filter(r => r.severity === 'High').length || 0,
      Medium: analysis.risks?.filter(r => r.severity === 'Medium').length || 0,
      Low: analysis.risks?.filter(r => r.severity === 'Low').length || 0,
    },
    by_category: {
      Contractual: analysis.risks?.filter(r => r.category === 'Contractual').length || 0,
      Regulatory: analysis.risks?.filter(r => r.category === 'Regulatory').length || 0,
      Litigation: analysis.risks?.filter(r => r.category === 'Litigation').length || 0,
      IP: analysis.risks?.filter(r => r.category === 'IP').length || 0,
      Operational: analysis.risks?.filter(r => r.category === 'Operational').length || 0,
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <button
          onClick={() => navigate('/analyses')}
          className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Analyses
        </button>

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
              <h1 className="text-2xl font-bold text-gray-900">{analysis.name}</h1>
              <p className="text-gray-500 mt-1">{analysis.analysis_id}</p>
              {analysis.description && (
                <p className="text-gray-600 mt-2">{analysis.description}</p>
              )}
            </div>
          </div>
          {analysis.status === 'completed' && (
            <div className="flex items-center gap-2">
              {analysis.report_path && (
                <a
                  href={analysis.report_path}
                  download
                  className="btn btn-secondary flex items-center gap-2"
                  title="Download Word Report"
                >
                  <Download className="h-4 w-4" />
                  Download Report
                </a>
              )}
              {analysis.dashboard_path && (
                <a
                  href={analysis.dashboard_path}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn btn-primary flex items-center gap-2"
                  title="Open Interactive Dashboard"
                >
                  <ExternalLink className="h-4 w-4" />
                  View Dashboard
                </a>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Progress for running analysis */}
      {(analysis.status === 'running' || analysis.status === 'pending') && (
        <div className="card">
          <div className="card-body">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm font-medium text-gray-700">
                {analysis.current_step || 'Waiting to start...'}
              </p>
              <span className="text-sm text-gray-500">{analysis.progress}%</span>
            </div>
            <div className="progress-bar">
              <div
                className="progress-bar-fill"
                style={{ width: `${analysis.progress}%` }}
              />
            </div>
          </div>
        </div>
      )}

      {/* Error message */}
      {analysis.status === 'failed' && analysis.error_message && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          <p className="font-medium">Analysis Failed</p>
          <p className="text-sm mt-1">{analysis.error_message}</p>
        </div>
      )}

      {/* Info Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card p-4">
          <p className="text-sm text-gray-500">Documents</p>
          <p className="text-2xl font-bold text-gray-900">{analysis.document_count}</p>
        </div>
        <div className="card p-4">
          <p className="text-sm text-gray-500">Risks Found</p>
          <p className="text-2xl font-bold text-gray-900">{analysis.risk_count}</p>
        </div>
        <div className="card p-4">
          <p className="text-sm text-gray-500">Created</p>
          <p className="text-sm font-medium text-gray-900">{formatDate(analysis.created_at)}</p>
        </div>
        <div className="card p-4">
          <p className="text-sm text-gray-500">Completed</p>
          <p className="text-sm font-medium text-gray-900">{formatDate(analysis.completed_at)}</p>
        </div>
      </div>

      {/* Charts */}
      {analysis.status === 'completed' && analysis.risks?.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold text-gray-900">Risks by Severity</h3>
            </div>
            <div className="card-body">
              <RiskChart type="severity" data={riskSummary.by_severity} />
            </div>
          </div>
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold text-gray-900">Risks by Category</h3>
            </div>
            <div className="card-body">
              <RiskChart type="category" data={riskSummary.by_category} />
            </div>
          </div>
        </div>
      )}

      {/* Documents */}
      {analysis.documents?.length > 0 && (
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-semibold text-gray-900">Analyzed Documents</h3>
          </div>
          <div className="divide-y divide-gray-200">
            {analysis.documents.map((doc) => (
              <div key={doc.doc_id} className="flex items-center gap-3 p-4">
                <FileText className="h-5 w-5 text-gray-400" />
                <div>
                  <p className="font-medium text-gray-900">{doc.original_filename}</p>
                  <p className="text-sm text-gray-500">{doc.doc_id} | {doc.page_count} pages</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Risks */}
      {analysis.status === 'completed' && (
        <div className="card">
          <div className="card-header flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900">
              Identified Risks ({filteredRisks.length})
            </h3>
            <div className="flex items-center gap-2">
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="input text-sm py-1.5"
              >
                <option value="">All Categories</option>
                <option value="Contractual">Contractual</option>
                <option value="Regulatory">Regulatory</option>
                <option value="Litigation">Litigation</option>
                <option value="IP">IP</option>
                <option value="Operational">Operational</option>
              </select>
              <select
                value={selectedSeverity}
                onChange={(e) => setSelectedSeverity(e.target.value)}
                className="input text-sm py-1.5"
              >
                <option value="">All Severities</option>
                <option value="Critical">Critical</option>
                <option value="High">High</option>
                <option value="Medium">Medium</option>
                <option value="Low">Low</option>
              </select>
            </div>
          </div>

          {filteredRisks.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              <AlertTriangle className="h-12 w-12 mx-auto text-gray-300 mb-3" />
              <p>No risks found matching your filters</p>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {filteredRisks.map((risk) => (
                <div key={risk.risk_id} className="p-4">
                  <button
                    onClick={() => toggleRisk(risk.risk_id)}
                    className="w-full text-left"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-3">
                        <span className={`badge ${getSeverityClass(risk.severity)}`}>
                          {risk.severity}
                        </span>
                        <div>
                          <p className="font-medium text-gray-900">{risk.title}</p>
                          <p className="text-sm text-gray-500 mt-1">
                            {risk.risk_id} | {risk.category}
                          </p>
                        </div>
                      </div>
                      {expandedRisks[risk.risk_id] ? (
                        <ChevronUp className="h-5 w-5 text-gray-400" />
                      ) : (
                        <ChevronDown className="h-5 w-5 text-gray-400" />
                      )}
                    </div>
                  </button>

                  {expandedRisks[risk.risk_id] && (
                    <div className="mt-4 pl-16 space-y-4">
                      <div>
                        <p className="text-sm font-medium text-gray-700">Description</p>
                        <p className="text-sm text-gray-600 mt-1">{risk.description}</p>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-700">Likelihood</p>
                        <p className="text-sm text-gray-600 mt-1">{risk.likelihood}</p>
                      </div>
                      {risk.evidence?.length > 0 && (
                        <div>
                          <p className="text-sm font-medium text-gray-700">Evidence</p>
                          {risk.evidence.map((ev, idx) => (
                            <div key={idx} className="mt-2 bg-gray-50 p-3 rounded-lg">
                              <p className="text-xs text-gray-500">
                                {ev.doc_id} - Page {ev.page_num}
                              </p>
                              <p className="text-sm text-gray-700 mt-1 italic">
                                "{ev.citation}"
                              </p>
                            </div>
                          ))}
                        </div>
                      )}
                      <div>
                        <p className="text-sm font-medium text-gray-700">Legal Basis</p>
                        <p className="text-sm text-gray-600 mt-1">{risk.legal_basis}</p>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-700">Recommended Mitigation</p>
                        <p className="text-sm text-gray-600 mt-1">{risk.recommended_mitigation}</p>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default AnalysisDetail;
