import axios from 'axios';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Documents API
export const documentsApi = {
  upload: async (file, summary = '') => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('summary', summary);

    const response = await api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  list: async () => {
    const response = await api.get('/documents/');
    return response.data;
  },

  get: async (docId) => {
    const response = await api.get(`/documents/${docId}`);
    return response.data;
  },

  delete: async (docId) => {
    const response = await api.delete(`/documents/${docId}`);
    return response.data;
  },

  updateSummary: async (docId, summary) => {
    const formData = new FormData();
    formData.append('summary', summary);

    const response = await api.put(`/documents/${docId}/summary`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  getPages: async (docId, pageNums = null) => {
    const params = pageNums ? { page_nums: pageNums.join(',') } : {};
    const response = await api.get(`/documents/${docId}/pages`, { params });
    return response.data;
  },
};

// Analyses API
export const analysesApi = {
  create: async (data) => {
    const response = await api.post('/analyses/', data);
    return response.data;
  },

  list: async (status = null) => {
    const params = status ? { status } : {};
    const response = await api.get('/analyses/', { params });
    return response.data;
  },

  get: async (analysisId) => {
    const response = await api.get(`/analyses/${analysisId}`);
    return response.data;
  },

  getStatus: async (analysisId) => {
    const response = await api.get(`/analyses/${analysisId}/status`);
    return response.data;
  },

  getRisks: async (analysisId, category = null, severity = null) => {
    const params = {};
    if (category) params.category = category;
    if (severity) params.severity = severity;

    const response = await api.get(`/analyses/${analysisId}/risks`, { params });
    return response.data;
  },

  delete: async (analysisId) => {
    const response = await api.delete(`/analyses/${analysisId}`);
    return response.data;
  },
};

// Dashboard API
export const dashboardApi = {
  getStats: async () => {
    const response = await api.get('/dashboard/stats');
    return response.data;
  },

  getRiskMatrix: async () => {
    const response = await api.get('/dashboard/risk-matrix');
    return response.data;
  },

  getCategoryBreakdown: async () => {
    const response = await api.get('/dashboard/category-breakdown');
    return response.data;
  },

  getTimeline: async () => {
    const response = await api.get('/dashboard/timeline');
    return response.data;
  },
};

// Health check
export const healthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};

export default api;
