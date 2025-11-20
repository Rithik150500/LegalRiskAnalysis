// client.test.js - Tests for API client
import { describe, it, expect, beforeEach } from 'vitest';
import { documentsApi, analysesApi, dashboardApi, healthCheck } from './client';

describe('Health Check API', () => {
  it('should return healthy status', async () => {
    const result = await healthCheck();
    expect(result.status).toBe('healthy');
    expect(result.version).toBe('1.0.0');
  });
});

describe('Documents API', () => {
  describe('list', () => {
    it('should return list of documents', async () => {
      const result = await documentsApi.list();
      expect(Array.isArray(result)).toBe(true);
      expect(result.length).toBeGreaterThan(0);
      expect(result[0]).toHaveProperty('doc_id');
      expect(result[0]).toHaveProperty('filename');
    });
  });

  describe('get', () => {
    it('should return document by ID', async () => {
      const result = await documentsApi.get('DOC12345678');
      expect(result.doc_id).toBe('DOC12345678');
      expect(result).toHaveProperty('pages_data');
      expect(result).toHaveProperty('file_path');
    });
  });

  describe('upload', () => {
    it('should upload a document', async () => {
      const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
      const result = await documentsApi.upload(file, 'Test summary');
      expect(result).toHaveProperty('doc_id');
      expect(result.doc_id).toMatch(/^DOC/);
    });

    it('should upload without summary', async () => {
      const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
      const result = await documentsApi.upload(file);
      expect(result).toHaveProperty('doc_id');
    });
  });

  describe('delete', () => {
    it('should delete a document', async () => {
      const result = await documentsApi.delete('DOC12345678');
      expect(result.message).toContain('deleted successfully');
    });
  });

  describe('updateSummary', () => {
    it('should update document summary', async () => {
      const result = await documentsApi.updateSummary('DOC12345678', 'New summary');
      expect(result).toHaveProperty('doc_id');
      expect(result.summary).toBe('Updated summary');
    });
  });

  describe('getPages', () => {
    it('should get all pages', async () => {
      const result = await documentsApi.getPages('DOC12345678');
      expect(result).toHaveProperty('doc_id');
      expect(result).toHaveProperty('total_pages');
      expect(result).toHaveProperty('pages');
      expect(Array.isArray(result.pages)).toBe(true);
    });

    it('should get specific pages', async () => {
      const result = await documentsApi.getPages('DOC12345678', [1, 2]);
      expect(result).toHaveProperty('pages');
    });
  });
});

describe('Analyses API', () => {
  describe('list', () => {
    it('should return list of analyses', async () => {
      const result = await analysesApi.list();
      expect(Array.isArray(result)).toBe(true);
      expect(result.length).toBeGreaterThan(0);
      expect(result[0]).toHaveProperty('analysis_id');
      expect(result[0]).toHaveProperty('name');
      expect(result[0]).toHaveProperty('status');
    });

    it('should filter by status', async () => {
      const result = await analysesApi.list('completed');
      expect(Array.isArray(result)).toBe(true);
    });
  });

  describe('get', () => {
    it('should return analysis by ID', async () => {
      const result = await analysesApi.get('ANA12345678');
      expect(result.analysis_id).toBe('ANA12345678');
      expect(result).toHaveProperty('documents');
      expect(result).toHaveProperty('risks');
      expect(result).toHaveProperty('result_data');
    });
  });

  describe('create', () => {
    it('should create a new analysis', async () => {
      const data = {
        name: 'Test Analysis',
        description: 'Test description',
        document_ids: ['DOC12345678'],
      };
      const result = await analysesApi.create(data);
      expect(result).toHaveProperty('analysis_id');
      expect(result.analysis_id).toMatch(/^ANA/);
      expect(result.status).toBe('pending');
    });
  });

  describe('getStatus', () => {
    it('should return analysis status', async () => {
      const result = await analysesApi.getStatus('ANA12345678');
      expect(result.analysis_id).toBe('ANA12345678');
      expect(result).toHaveProperty('status');
      expect(result).toHaveProperty('progress');
      expect(result).toHaveProperty('current_step');
    });
  });

  describe('getRisks', () => {
    it('should return risks for analysis', async () => {
      const result = await analysesApi.getRisks('ANA12345678');
      expect(result.analysis_id).toBe('ANA12345678');
      expect(result).toHaveProperty('total');
      expect(result).toHaveProperty('risks');
      expect(Array.isArray(result.risks)).toBe(true);
    });

    it('should filter by category', async () => {
      const result = await analysesApi.getRisks('ANA12345678', 'Contractual');
      expect(result).toHaveProperty('risks');
    });

    it('should filter by severity', async () => {
      const result = await analysesApi.getRisks('ANA12345678', null, 'High');
      expect(result).toHaveProperty('risks');
    });

    it('should filter by both category and severity', async () => {
      const result = await analysesApi.getRisks('ANA12345678', 'Contractual', 'High');
      expect(result).toHaveProperty('risks');
    });
  });

  describe('delete', () => {
    it('should delete an analysis', async () => {
      const result = await analysesApi.delete('ANA12345678');
      expect(result.message).toContain('deleted successfully');
    });
  });
});

describe('Dashboard API', () => {
  describe('getStats', () => {
    it('should return dashboard statistics', async () => {
      const result = await dashboardApi.getStats();
      expect(result).toHaveProperty('total_documents');
      expect(result).toHaveProperty('total_analyses');
      expect(result).toHaveProperty('completed_analyses');
      expect(result).toHaveProperty('total_risks');
      expect(result).toHaveProperty('risk_summary');
      expect(result).toHaveProperty('recent_analyses');
    });

    it('should return risk summary with correct structure', async () => {
      const result = await dashboardApi.getStats();
      const { risk_summary } = result;
      expect(risk_summary).toHaveProperty('total');
      expect(risk_summary).toHaveProperty('by_severity');
      expect(risk_summary).toHaveProperty('by_category');
      expect(risk_summary).toHaveProperty('by_likelihood');
    });
  });

  describe('getRiskMatrix', () => {
    it('should return risk matrix data', async () => {
      const result = await dashboardApi.getRiskMatrix();
      expect(result).toHaveProperty('matrix');
      expect(result).toHaveProperty('severities');
      expect(result).toHaveProperty('likelihoods');
      expect(Array.isArray(result.severities)).toBe(true);
      expect(Array.isArray(result.likelihoods)).toBe(true);
    });

    it('should return correct severity levels', async () => {
      const result = await dashboardApi.getRiskMatrix();
      expect(result.severities).toEqual(['Critical', 'High', 'Medium', 'Low']);
    });

    it('should return correct likelihood levels', async () => {
      const result = await dashboardApi.getRiskMatrix();
      expect(result.likelihoods).toEqual(['Very Likely', 'Likely', 'Possible', 'Unlikely']);
    });
  });

  describe('getCategoryBreakdown', () => {
    it('should return category breakdown', async () => {
      const result = await dashboardApi.getCategoryBreakdown();
      expect(Array.isArray(result)).toBe(true);
      expect(result.length).toBe(5);
    });

    it('should include all categories', async () => {
      const result = await dashboardApi.getCategoryBreakdown();
      const categories = result.map((item) => item.category);
      expect(categories).toContain('Contractual');
      expect(categories).toContain('Regulatory');
      expect(categories).toContain('Litigation');
      expect(categories).toContain('IP');
      expect(categories).toContain('Operational');
    });

    it('should have correct structure per category', async () => {
      const result = await dashboardApi.getCategoryBreakdown();
      result.forEach((item) => {
        expect(item).toHaveProperty('category');
        expect(item).toHaveProperty('total');
        expect(item).toHaveProperty('by_severity');
      });
    });
  });

  describe('getTimeline', () => {
    it('should return analysis timeline', async () => {
      const result = await dashboardApi.getTimeline();
      expect(Array.isArray(result)).toBe(true);
    });

    it('should have correct structure', async () => {
      const result = await dashboardApi.getTimeline();
      if (result.length > 0) {
        const entry = result[0];
        expect(entry).toHaveProperty('analysis_id');
        expect(entry).toHaveProperty('name');
        expect(entry).toHaveProperty('date');
        expect(entry).toHaveProperty('status');
        expect(entry).toHaveProperty('risk_count');
      }
    });
  });
});
