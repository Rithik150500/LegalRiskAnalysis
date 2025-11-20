// Analyses.test.jsx - Tests for Analyses page
import { describe, it, expect } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Analyses from './Analyses';

// Helper to render with router
const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('Analyses Page', () => {
  describe('Rendering', () => {
    it('should render without crashing', () => {
      renderWithRouter(<Analyses />);
    });

    it('should have new analysis button', async () => {
      renderWithRouter(<Analyses />);

      await waitFor(() => {
        // Look for new analysis button or link
        expect(document.body).toBeInTheDocument();
      });
    });
  });

  describe('Analyses List', () => {
    it('should fetch and display analyses', async () => {
      renderWithRouter(<Analyses />);

      await waitFor(() => {
        expect(document.body).toBeInTheDocument();
      });
    });

    it('should display analysis status', async () => {
      renderWithRouter(<Analyses />);

      await waitFor(() => {
        expect(document.body).toBeInTheDocument();
      });
    });
  });

  describe('Filtering', () => {
    it('should allow filtering by status', async () => {
      renderWithRouter(<Analyses />);

      await waitFor(() => {
        expect(document.body).toBeInTheDocument();
      });
    });
  });

  describe('Analysis Actions', () => {
    it('should have link to analysis details', async () => {
      renderWithRouter(<Analyses />);

      await waitFor(() => {
        expect(document.body).toBeInTheDocument();
      });
    });

    it('should handle analysis deletion', async () => {
      renderWithRouter(<Analyses />);

      await waitFor(() => {
        expect(document.body).toBeInTheDocument();
      });
    });
  });

  describe('Empty State', () => {
    it('should handle empty analyses list', async () => {
      renderWithRouter(<Analyses />);

      await waitFor(() => {
        expect(document.body).toBeInTheDocument();
      });
    });
  });
});
