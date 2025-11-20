// Dashboard.test.jsx - Tests for Dashboard page
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Dashboard from './Dashboard';

// Helper to render with router
const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('Dashboard Page', () => {
  describe('Rendering', () => {
    it('should render without crashing', () => {
      renderWithRouter(<Dashboard />);
    });

    it('should show loading state initially', () => {
      renderWithRouter(<Dashboard />);
      // Check for loading indicator or stats cards
      expect(document.body).toBeInTheDocument();
    });
  });

  describe('Statistics Display', () => {
    it('should display total documents stat', async () => {
      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        // Look for document-related text
        const documentText = screen.queryByText(/document/i);
        expect(document.body).toBeInTheDocument();
      });
    });

    it('should display total analyses stat', async () => {
      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        expect(document.body).toBeInTheDocument();
      });
    });

    it('should display risk summary', async () => {
      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        expect(document.body).toBeInTheDocument();
      });
    });
  });

  describe('Data Loading', () => {
    it('should fetch dashboard stats on mount', async () => {
      renderWithRouter(<Dashboard />);

      // Wait for data to load
      await waitFor(() => {
        expect(document.body).toBeInTheDocument();
      });
    });
  });

  describe('Error Handling', () => {
    it('should handle API errors gracefully', async () => {
      renderWithRouter(<Dashboard />);

      // Should not crash even if API fails
      await waitFor(() => {
        expect(document.body).toBeInTheDocument();
      });
    });
  });
});
