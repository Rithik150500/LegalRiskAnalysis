# conftest.py - Pytest fixtures for backend tests
import os
import sys
import tempfile
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from models import Base
from database import get_db


@pytest.fixture(scope="function")
def test_db():
    """Create a fresh test database for each test"""
    # Create a temporary database file
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    database_url = f"sqlite:///{db_path}"

    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False}
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    yield TestingSessionLocal, database_url

    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture(scope="function")
def db_session(test_db):
    """Get a database session for testing"""
    TestingSessionLocal, _ = test_db
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(test_db):
    """Create a test client with test database"""
    TestingSessionLocal, _ = test_db

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_pdf_content():
    """Generate minimal PDF content for testing"""
    # Minimal valid PDF file content
    return (
        b"%PDF-1.4\n"
        b"1 0 obj\n"
        b"<< /Type /Catalog /Pages 2 0 R >>\n"
        b"endobj\n"
        b"2 0 obj\n"
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>\n"
        b"endobj\n"
        b"3 0 obj\n"
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Contents 4 0 R /Resources << >> >>\n"
        b"endobj\n"
        b"4 0 obj\n"
        b"<< /Length 44 >>\n"
        b"stream\n"
        b"BT\n"
        b"/F1 12 Tf\n"
        b"100 700 Td\n"
        b"(Test) Tj\n"
        b"ET\n"
        b"endstream\n"
        b"endobj\n"
        b"xref\n"
        b"0 5\n"
        b"0000000000 65535 f \n"
        b"0000000009 00000 n \n"
        b"0000000058 00000 n \n"
        b"0000000115 00000 n \n"
        b"0000000214 00000 n \n"
        b"trailer\n"
        b"<< /Size 5 /Root 1 0 R >>\n"
        b"startxref\n"
        b"307\n"
        b"%%EOF"
    )


@pytest.fixture
def sample_txt_content():
    """Generate sample text content for testing"""
    return b"This is a sample legal document for testing purposes."


@pytest.fixture
def uploaded_document(client, sample_txt_content):
    """Create an uploaded document for testing"""
    files = {"file": ("test_document.txt", sample_txt_content, "text/plain")}
    data = {"summary": "Test document summary"}
    response = client.post("/api/documents/upload", files=files, data=data)
    return response.json()


@pytest.fixture
def uploaded_pdf_document(client, sample_pdf_content):
    """Create an uploaded PDF document for testing"""
    files = {"file": ("test_contract.pdf", sample_pdf_content, "application/pdf")}
    data = {"summary": "Test PDF document"}
    response = client.post("/api/documents/upload", files=files, data=data)
    return response.json()


@pytest.fixture
def multiple_documents(client, sample_txt_content):
    """Create multiple documents for testing analyses"""
    documents = []
    for i in range(3):
        files = {"file": (f"document_{i}.txt", sample_txt_content, "text/plain")}
        data = {"summary": f"Document {i} summary"}
        response = client.post("/api/documents/upload", files=files, data=data)
        documents.append(response.json())
    return documents


@pytest.fixture
def created_analysis(client, uploaded_document):
    """Create an analysis for testing"""
    analysis_data = {
        "name": "Test Analysis",
        "description": "Test analysis description",
        "document_ids": [uploaded_document["doc_id"]]
    }
    response = client.post("/api/analyses/", json=analysis_data)
    return response.json()
