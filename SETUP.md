# Legal Risk Analysis - Setup Guide

A full-stack application for analyzing legal documents and identifying risks using AI-powered multi-agent system.

## Architecture

```
legal-risk-analysis/
├── backend/                 # FastAPI backend
│   ├── main.py             # Application entry point
│   ├── models.py           # Pydantic & SQLAlchemy models
│   ├── database.py         # Database configuration
│   └── routers/            # API endpoints
│       ├── documents.py    # Document management
│       ├── analyses.py     # Analysis operations
│       └── dashboard.py    # Statistics & charts
├── frontend/               # React frontend
│   ├── src/
│   │   ├── pages/         # Page components
│   │   ├── components/    # Reusable components
│   │   └── api/           # API client
│   └── package.json
└── legal-risk-agent/       # AI agent system
```

## Prerequisites

- Python 3.9+
- Node.js 18+
- npm or yarn

## Quick Start

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (optional)
cp ../.env.example .env
# Edit .env with your API keys if using real AI analysis

# Start backend server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at http://localhost:5173

## API Endpoints

### Documents
- `POST /api/documents/upload` - Upload a document
- `GET /api/documents/` - List all documents
- `GET /api/documents/{doc_id}` - Get document details
- `DELETE /api/documents/{doc_id}` - Delete a document

### Analyses
- `POST /api/analyses/` - Create new analysis
- `GET /api/analyses/` - List all analyses
- `GET /api/analyses/{analysis_id}` - Get analysis details
- `GET /api/analyses/{analysis_id}/status` - Get analysis progress
- `GET /api/analyses/{analysis_id}/risks` - Get risks with filtering
- `DELETE /api/analyses/{analysis_id}` - Delete analysis

### Dashboard
- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /api/dashboard/risk-matrix` - Get risk matrix data
- `GET /api/dashboard/category-breakdown` - Get category breakdown

## Features

### Document Management
- Upload PDF, DOC, DOCX, TXT files
- Automatic page extraction for PDFs
- Document summaries and metadata
- Search and filter documents

### Risk Analysis
- Create analyses from selected documents
- Real-time progress tracking
- AI-powered risk identification
- Risk categorization (Contractual, Regulatory, Litigation, IP, Operational)
- Severity and likelihood assessment

### Dashboard & Visualization
- Overview statistics
- Risk distribution charts (by severity and category)
- Risk matrix visualization
- Recent analyses timeline

### Risk Details
- Detailed risk descriptions
- Evidence with citations
- Legal basis references
- Mitigation recommendations
- Filtering by category and severity

## Development

### Build Frontend for Production

```bash
cd frontend
npm run build
```

### Run Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm run test
```

## Environment Variables

Create a `.env` file in the backend directory:

```env
# Required for AI-powered analysis
ANTHROPIC_API_KEY=your_anthropic_key
TAVILY_API_KEY=your_tavily_key

# Database (optional, defaults to SQLite)
DATABASE_URL=sqlite:///./legal_risk_analysis.db
```

## Technology Stack

### Backend
- FastAPI - High-performance Python web framework
- SQLAlchemy - Database ORM
- Pydantic - Data validation
- SQLite - Database (default)
- PyPDF2 - PDF processing

### Frontend
- React 18 - UI framework
- Vite - Build tool
- Tailwind CSS - Styling
- Chart.js - Visualizations
- React Router - Navigation
- Axios - HTTP client
- Lucide React - Icons

## License

MIT License
