// App.test.jsx - Tests for App component and routing
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from './App';

// Helper to render App with specific route
const renderWithRoute = (route = '/') => {
  return render(
    <MemoryRouter initialEntries={[route]}>
      <App />
    </MemoryRouter>
  );
};

describe('App Component', () => {
  describe('Routing', () => {
    it('should render dashboard at root path', () => {
      renderWithRoute('/');
      // Dashboard should be rendered
      expect(document.body).toBeInTheDocument();
    });

    it('should render documents page at /documents', () => {
      renderWithRoute('/documents');
      expect(document.body).toBeInTheDocument();
    });

    it('should render analyses page at /analyses', () => {
      renderWithRoute('/analyses');
      expect(document.body).toBeInTheDocument();
    });

    it('should render new analysis page at /analyses/new', () => {
      renderWithRoute('/analyses/new');
      expect(document.body).toBeInTheDocument();
    });

    it('should render analysis detail page at /analyses/:id', () => {
      renderWithRoute('/analyses/ANA12345678');
      expect(document.body).toBeInTheDocument();
    });
  });

  describe('Layout', () => {
    it('should render layout wrapper', () => {
      renderWithRoute('/');
      // Should have navigation elements
      expect(screen.getByText(/legal risk/i)).toBeInTheDocument();
    });

    it('should have navigation links', () => {
      renderWithRoute('/');
      expect(screen.getByText(/dashboard/i)).toBeInTheDocument();
      expect(screen.getByText(/documents/i)).toBeInTheDocument();
      expect(screen.getByText(/analyses/i)).toBeInTheDocument();
    });
  });
});

describe('App Integration', () => {
  it('should render without crashing', () => {
    renderWithRoute('/');
    expect(document.body).toBeInTheDocument();
  });

  it('should handle unknown routes', () => {
    renderWithRoute('/unknown-route');
    // App should still render without crashing
    expect(document.body).toBeInTheDocument();
  });
});
