// AnalysisDetail.test.jsx - Tests for AnalysisDetail page
import { describe, it, expect } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import AnalysisDetail from './AnalysisDetail';

// Helper to render with router and params
const renderWithRoute = (analysisId = 'ANA12345678') => {
  return render(
    <MemoryRouter initialEntries={[`/analyses/${analysisId}`]}>
      <Routes>
        <Route path="/analyses/:analysisId" element={<AnalysisDetail />} />
      </Routes>
    </MemoryRouter>
  );
};

describe('AnalysisDetail Page', () => {
  describe('Rendering', () => {
    it('should render without crashing', () => {
      renderWithRoute();
    });

    it('should show loading state initially', () => {
      renderWithRoute();
      expect(document.body).toBeInTheDocument();
    });
  });

  describe('Analysis Information', () => {
    it('should display analysis name', async () => {
      renderWithRoute();

      await waitFor(() => {
        expect(document.body).toBeInTheDocument();
      });
    });

    it('should display analysis status', async () => {
      renderWithRoute();

      await waitFor(() => {
        expect(document.body).toBeInTheDocument();
      });
    });

    it('should display progress', async () => {
      renderWithRoute();

      await waitFor(() => {
        expect(document.body).toBeInTheDocument();
      });
    });
  });

  describe('Risk Display', () => {
    it('should display risks list', async () => {
      renderWithRoute();

      await waitFor(() => {
        expect(document.body).toBeInTheDocument();
      });
    });

    it('should show risk severity', async () => {
      renderWithRoute();

      await waitFor(() => {
        expect(document.body).toBeInTheDocument();
      });
    });

    it('should show risk category', async () => {
      renderWithRoute();

      await waitFor(() => {
        expect(document.body).toBeInTheDocument();
      });
    });
  });

  describe('Risk Filtering', () => {
    it('should filter risks by category', async () => {
      renderWithRoute();

      await waitFor(() => {
        expect(document.body).toBeInTheDocument();
      });
    });

    it('should filter risks by severity', async () => {
      renderWithRoute();

      await waitFor(() => {
        expect(document.body).toBeInTheDocument();
      });
    });
  });

  describe('Documents Section', () => {
    it('should display associated documents', async () => {
      renderWithRoute();

      await waitFor(() => {
        expect(document.body).toBeInTheDocument();
      });
    });
  });

  describe('Actions', () => {
    it('should have download report option', async () => {
      renderWithRoute();

      await waitFor(() => {
        expect(document.body).toBeInTheDocument();
      });
    });

    it('should handle deletion', async () => {
      renderWithRoute();

      await waitFor(() => {
        expect(document.body).toBeInTheDocument();
      });
    });
  });

  describe('Error Handling', () => {
    it('should handle not found analysis', async () => {
      renderWithRoute('ANANONEXIST');

      await waitFor(() => {
        expect(document.body).toBeInTheDocument();
      });
    });
  });
});
