import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  FileText,
  BarChart3,
  AlertTriangle,
  CheckCircle,
  Clock,
  ChevronRight,
  TrendingUp
} from 'lucide-react';
import { dashboardApi } from '../api/client';
import RiskChart from '../components/RiskChart';

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const data = await dashboardApi.getStats();
      setStats(data);
    } catch (err) {
      setError('Failed to load dashboard data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">{error}</p>
        <button onClick={fetchDashboardData} className="mt-4 btn btn-primary">
          Retry
        </button>
      </div>
    );
  }

  const statCards = [
    {
      name: 'Total Documents',
      value: stats?.total_documents || 0,
      icon: FileText,
      color: 'bg-blue-500',
      href: '/documents'
    },
    {
      name: 'Total Analyses',
      value: stats?.total_analyses || 0,
      icon: BarChart3,
      color: 'bg-purple-500',
      href: '/analyses'
    },
    {
      name: 'Completed',
      value: stats?.completed_analyses || 0,
      icon: CheckCircle,
      color: 'bg-green-500',
      href: '/analyses'
    },
    {
      name: 'Risks Identified',
      value: stats?.total_risks || 0,
      icon: AlertTriangle,
      color: 'bg-orange-500',
      href: '/analyses'
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">Overview of your legal risk analysis</p>
        </div>
        <Link to="/analyses/new" className="btn btn-primary">
          New Analysis
        </Link>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((stat) => {
          const Icon = stat.icon;
          return (
            <Link
              key={stat.name}
              to={stat.href}
              className="card p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">{stat.name}</p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</p>
                </div>
                <div className={`${stat.color} p-3 rounded-lg`}>
                  <Icon className="h-6 w-6 text-white" />
                </div>
              </div>
            </Link>
          );
        })}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Risk by Severity */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-semibold text-gray-900">Risks by Severity</h3>
          </div>
          <div className="card-body">
            {stats?.risk_summary ? (
              <RiskChart
                type="severity"
                data={stats.risk_summary.by_severity}
              />
            ) : (
              <p className="text-gray-500 text-center py-8">No risk data available</p>
            )}
          </div>
        </div>

        {/* Risk by Category */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-semibold text-gray-900">Risks by Category</h3>
          </div>
          <div className="card-body">
            {stats?.risk_summary ? (
              <RiskChart
                type="category"
                data={stats.risk_summary.by_category}
              />
            ) : (
              <p className="text-gray-500 text-center py-8">No risk data available</p>
            )}
          </div>
        </div>
      </div>

      {/* Recent Analyses */}
      <div className="card">
        <div className="card-header flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">Recent Analyses</h3>
          <Link to="/analyses" className="text-sm text-primary-600 hover:text-primary-700 flex items-center gap-1">
            View all <ChevronRight className="h-4 w-4" />
          </Link>
        </div>
        <div className="divide-y divide-gray-200">
          {stats?.recent_analyses?.length > 0 ? (
            stats.recent_analyses.map((analysis) => (
              <Link
                key={analysis.analysis_id}
                to={`/analyses/${analysis.analysis_id}`}
                className="flex items-center justify-between p-4 hover:bg-gray-50"
              >
                <div className="flex items-center gap-4">
                  <div className={`
                    p-2 rounded-lg
                    ${analysis.status === 'completed' ? 'bg-green-100' :
                      analysis.status === 'running' ? 'bg-blue-100' :
                      analysis.status === 'failed' ? 'bg-red-100' : 'bg-gray-100'}
                  `}>
                    {analysis.status === 'completed' ? (
                      <CheckCircle className="h-5 w-5 text-green-600" />
                    ) : analysis.status === 'running' ? (
                      <Clock className="h-5 w-5 text-blue-600" />
                    ) : analysis.status === 'failed' ? (
                      <AlertTriangle className="h-5 w-5 text-red-600" />
                    ) : (
                      <Clock className="h-5 w-5 text-gray-600" />
                    )}
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">{analysis.name}</p>
                    <p className="text-sm text-gray-500">
                      {analysis.document_count} documents | {analysis.risk_count} risks
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <span className={`
                    badge
                    ${analysis.status === 'completed' ? 'bg-green-100 text-green-800' :
                      analysis.status === 'running' ? 'bg-blue-100 text-blue-800' :
                      analysis.status === 'failed' ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800'}
                  `}>
                    {analysis.status}
                  </span>
                </div>
              </Link>
            ))
          ) : (
            <div className="p-8 text-center text-gray-500">
              <TrendingUp className="h-12 w-12 mx-auto text-gray-300 mb-3" />
              <p>No analyses yet</p>
              <Link to="/analyses/new" className="text-primary-600 hover:text-primary-700 text-sm">
                Start your first analysis
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
