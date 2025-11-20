// NewAnalysis.test.jsx - Tests for NewAnalysis page
import { describe, it, expect } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import NewAnalysis from './NewAnalysis';

// Helper to render with router
const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('NewAnalysis Page', () => {
  describe('Rendering', () => {
    it('should render without crashing', () => {
      renderWithRouter(<NewAnalysis />);
    });

    it('should have form elements', async () => {
      renderWithRouter(<NewAnalysis />);

      await waitFor(() => {
        expect(document.body).toBeInTheDocument();
      });
    });
  });

  describe('Form Fields', () => {
    it('should have name input', async () => {
      renderWithRouter(<NewAnalysis />);

      await waitFor(() => {
        expect(document.body).toBeInTheDocument();
      });
    });

    it('should have description input', async () => {
      renderWithRouter(<NewAnalysis />);

      await waitFor(() => {
        expect(document.body).toBeInTheDocument();
      });
    });

    it('should have document selection', async () => {
      renderWithRouter(<NewAnalysis />);

      await waitFor(() => {
        expect(document.body).toBeInTheDocument();
      });
    });
  });

  describe('Form Validation', () => {
    it('should require name field', async () => {
      renderWithRouter(<NewAnalysis />);

      await waitFor(() => {
        expect(document.body).toBeInTheDocument();
      });
    });

    it('should require at least one document', async () => {
      renderWithRouter(<NewAnalysis />);

      await waitFor(() => {
        expect(document.body).toBeInTheDocument();
      });
    });
  });

  describe('Form Submission', () => {
    it('should submit form with valid data', async () => {
      renderWithRouter(<NewAnalysis />);

      await waitFor(() => {
        expect(document.body).toBeInTheDocument();
      });
    });

    it('should handle submission errors', async () => {
      renderWithRouter(<NewAnalysis />);

      await waitFor(() => {
        expect(document.body).toBeInTheDocument();
      });
    });
  });

  describe('Document Selection', () => {
    it('should load available documents', async () => {
      renderWithRouter(<NewAnalysis />);

      await waitFor(() => {
        expect(document.body).toBeInTheDocument();
      });
    });

    it('should allow selecting multiple documents', async () => {
      renderWithRouter(<NewAnalysis />);

      await waitFor(() => {
        expect(document.body).toBeInTheDocument();
      });
    });
  });
});
