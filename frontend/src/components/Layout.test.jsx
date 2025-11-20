// Layout.test.jsx - Tests for Layout component
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Layout from './Layout';

// Helper to render with router
const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('Layout Component', () => {
  describe('Rendering', () => {
    it('should render without crashing', () => {
      renderWithRouter(<Layout />);
    });

    it('should render navigation links', () => {
      renderWithRouter(<Layout />);

      expect(screen.getByText(/dashboard/i)).toBeInTheDocument();
      expect(screen.getByText(/documents/i)).toBeInTheDocument();
      expect(screen.getByText(/analyses/i)).toBeInTheDocument();
    });

    it('should render app title', () => {
      renderWithRouter(<Layout />);

      expect(screen.getByText(/legal risk/i)).toBeInTheDocument();
    });

    it('should render children content', () => {
      renderWithRouter(
        <Layout>
          <div data-testid="child-content">Child Content</div>
        </Layout>
      );

      expect(screen.getByTestId('child-content')).toBeInTheDocument();
    });
  });

  describe('Navigation', () => {
    it('should have correct link to dashboard', () => {
      renderWithRouter(<Layout />);

      const dashboardLink = screen.getByRole('link', { name: /dashboard/i });
      expect(dashboardLink).toHaveAttribute('href', '/');
    });

    it('should have correct link to documents', () => {
      renderWithRouter(<Layout />);

      const documentsLink = screen.getByRole('link', { name: /documents/i });
      expect(documentsLink).toHaveAttribute('href', '/documents');
    });

    it('should have correct link to analyses', () => {
      renderWithRouter(<Layout />);

      const analysesLink = screen.getByRole('link', { name: /analyses/i });
      expect(analysesLink).toHaveAttribute('href', '/analyses');
    });
  });

  describe('Accessibility', () => {
    it('should have main content area', () => {
      renderWithRouter(
        <Layout>
          <main>Content</main>
        </Layout>
      );

      expect(screen.getByRole('main')).toBeInTheDocument();
    });
  });
});
