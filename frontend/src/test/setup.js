// Test setup file
import '@testing-library/jest-dom';
import { afterEach, beforeAll, afterAll } from 'vitest';
import { cleanup } from '@testing-library/react';
import { setupServer } from 'msw/node';
import { http, HttpResponse } from 'msw';

// Clean up after each test
afterEach(() => {
  cleanup();
});

// Mock handlers for API testing
export const handlers = [
  // Health check
  http.get('/api/health', () => {
    return HttpResponse.json({ status: 'healthy', version: '1.0.0' });
  }),

  // Documents
  http.get('/api/documents/', () => {
    return HttpResponse.json([
      {
        id: 1,
        doc_id: 'DOC12345678',
        filename: 'test.pdf',
        original_filename: 'contract.pdf',
        file_type: 'PDF',
        file_size: 1024,
        summary: 'Test document',
        page_count: 5,
        uploaded_at: '2024-01-01T00:00:00Z',
      },
    ]);
  }),

  http.get('/api/documents/:docId', ({ params }) => {
    return HttpResponse.json({
      id: 1,
      doc_id: params.docId,
      filename: 'test.pdf',
      original_filename: 'contract.pdf',
      file_type: 'PDF',
      file_size: 1024,
      summary: 'Test document',
      page_count: 5,
      uploaded_at: '2024-01-01T00:00:00Z',
      pages_data: [{ page_num: 1, summdesc: 'Page 1' }],
      file_path: '/uploads/test.pdf',
    });
  }),

  http.post('/api/documents/upload', () => {
    return HttpResponse.json({
      id: 1,
      doc_id: 'DOCNEWUUID1',
      filename: 'uploaded.pdf',
      original_filename: 'uploaded.pdf',
      file_type: 'PDF',
      file_size: 2048,
      summary: 'Uploaded document',
      page_count: 3,
      uploaded_at: '2024-01-01T00:00:00Z',
    });
  }),

  http.delete('/api/documents/:docId', ({ params }) => {
    return HttpResponse.json({ message: `Document ${params.docId} deleted successfully` });
  }),

  http.put('/api/documents/:docId/summary', ({ params }) => {
    return HttpResponse.json({
      id: 1,
      doc_id: params.docId,
      filename: 'test.pdf',
      original_filename: 'contract.pdf',
      file_type: 'PDF',
      file_size: 1024,
      summary: 'Updated summary',
      page_count: 5,
      uploaded_at: '2024-01-01T00:00:00Z',
    });
  }),

  http.get('/api/documents/:docId/pages', ({ params }) => {
    return HttpResponse.json({
      doc_id: params.docId,
      total_pages: 5,
      pages: [{ page_num: 1, summdesc: 'Page 1' }],
    });
  }),

  // Analyses
  http.get('/api/analyses/', () => {
    return HttpResponse.json([
      {
        id: 1,
        analysis_id: 'ANA12345678',
        name: 'Test Analysis',
        description: 'Test description',
        status: 'completed',
        progress: 100,
        current_step: 'Complete',
        created_at: '2024-01-01T00:00:00Z',
        started_at: '2024-01-01T00:00:00Z',
        completed_at: '2024-01-01T00:01:00Z',
        error_message: null,
        document_count: 2,
        risk_count: 5,
      },
    ]);
  }),

  http.get('/api/analyses/:analysisId', ({ params }) => {
    return HttpResponse.json({
      id: 1,
      analysis_id: params.analysisId,
      name: 'Test Analysis',
      description: 'Test description',
      status: 'completed',
      progress: 100,
      current_step: 'Complete',
      created_at: '2024-01-01T00:00:00Z',
      started_at: '2024-01-01T00:00:00Z',
      completed_at: '2024-01-01T00:01:00Z',
      error_message: null,
      document_count: 2,
      risk_count: 5,
      result_data: { summary: 'Analysis complete' },
      report_path: '/outputs/report.docx',
      dashboard_path: '/outputs/dashboard.html',
      documents: [],
      risks: [],
    });
  }),

  http.post('/api/analyses/', () => {
    return HttpResponse.json({
      id: 1,
      analysis_id: 'ANANEWUUID1',
      name: 'New Analysis',
      description: 'New analysis description',
      status: 'pending',
      progress: 0,
      current_step: null,
      created_at: '2024-01-01T00:00:00Z',
      started_at: null,
      completed_at: null,
      error_message: null,
      document_count: 1,
      risk_count: 0,
    });
  }),

  http.get('/api/analyses/:analysisId/status', ({ params }) => {
    return HttpResponse.json({
      analysis_id: params.analysisId,
      status: 'completed',
      progress: 100,
      current_step: 'Complete',
      error_message: null,
    });
  }),

  http.get('/api/analyses/:analysisId/risks', ({ params }) => {
    return HttpResponse.json({
      analysis_id: params.analysisId,
      total: 2,
      risks: [
        {
          id: 1,
          risk_id: 'RISK_001',
          category: 'Contractual',
          title: 'Test Risk',
          description: 'Test description',
          severity: 'High',
          likelihood: 'Likely',
          evidence: [],
          legal_basis: 'Contract Law',
          recommended_mitigation: 'Review contract',
        },
      ],
    });
  }),

  http.delete('/api/analyses/:analysisId', ({ params }) => {
    return HttpResponse.json({ message: `Analysis ${params.analysisId} deleted successfully` });
  }),

  // Dashboard
  http.get('/api/dashboard/stats', () => {
    return HttpResponse.json({
      total_documents: 10,
      total_analyses: 5,
      completed_analyses: 3,
      total_risks: 15,
      risk_summary: {
        total: 15,
        by_severity: { Critical: 2, High: 5, Medium: 5, Low: 3 },
        by_category: { Contractual: 5, Regulatory: 4, Litigation: 2, IP: 2, Operational: 2 },
        by_likelihood: { 'Very Likely': 3, Likely: 5, Possible: 4, Unlikely: 3 },
      },
      recent_analyses: [],
    });
  }),

  http.get('/api/dashboard/risk-matrix', () => {
    return HttpResponse.json({
      matrix: [],
      severities: ['Critical', 'High', 'Medium', 'Low'],
      likelihoods: ['Very Likely', 'Likely', 'Possible', 'Unlikely'],
    });
  }),

  http.get('/api/dashboard/category-breakdown', () => {
    return HttpResponse.json([
      { category: 'Contractual', total: 5, by_severity: { Critical: 1, High: 2, Medium: 1, Low: 1 } },
      { category: 'Regulatory', total: 4, by_severity: { Critical: 0, High: 2, Medium: 1, Low: 1 } },
      { category: 'Litigation', total: 2, by_severity: { Critical: 0, High: 1, Medium: 1, Low: 0 } },
      { category: 'IP', total: 2, by_severity: { Critical: 1, High: 0, Medium: 1, Low: 0 } },
      { category: 'Operational', total: 2, by_severity: { Critical: 0, High: 0, Medium: 1, Low: 1 } },
    ]);
  }),

  http.get('/api/dashboard/timeline', () => {
    return HttpResponse.json([
      {
        analysis_id: 'ANA12345678',
        name: 'Test Analysis',
        date: '2024-01-01T00:00:00Z',
        status: 'completed',
        risk_count: 5,
      },
    ]);
  }),
];

// Create MSW server
export const server = setupServer(...handlers);

// Start server before all tests
beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));

// Reset handlers after each test
afterEach(() => server.resetHandlers());

// Close server after all tests
afterAll(() => server.close());
