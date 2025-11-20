# test_documents.py - Tests for documents router
import pytest
import os


class TestDocumentUpload:
    """Test document upload endpoint"""

    def test_upload_text_document(self, client, sample_txt_content):
        """Test uploading a text document"""
        files = {"file": ("test.txt", sample_txt_content, "text/plain")}
        data = {"summary": "Test document"}

        response = client.post("/api/documents/upload", files=files, data=data)
        assert response.status_code == 200

        doc = response.json()
        assert "doc_id" in doc
        assert doc["doc_id"].startswith("DOC")
        assert doc["original_filename"] == "test.txt"
        assert doc["file_type"] == "TXT"
        assert doc["summary"] == "Test document"
        assert doc["page_count"] == 1

    def test_upload_pdf_document(self, client, sample_pdf_content):
        """Test uploading a PDF document"""
        files = {"file": ("contract.pdf", sample_pdf_content, "application/pdf")}
        data = {"summary": "PDF contract"}

        response = client.post("/api/documents/upload", files=files, data=data)
        assert response.status_code == 200

        doc = response.json()
        assert doc["file_type"] == "PDF"
        assert doc["page_count"] >= 1

    def test_upload_without_summary_auto_generates(self, client, sample_txt_content):
        """Test upload without summary auto-generates one"""
        files = {"file": ("auto_summary.txt", sample_txt_content, "text/plain")}

        response = client.post("/api/documents/upload", files=files)
        assert response.status_code == 200

        doc = response.json()
        assert doc["summary"] is not None
        assert "auto_summary.txt" in doc["summary"]

    def test_upload_stores_file_size(self, client, sample_txt_content):
        """Test upload correctly stores file size"""
        files = {"file": ("sized.txt", sample_txt_content, "text/plain")}

        response = client.post("/api/documents/upload", files=files)
        assert response.status_code == 200

        doc = response.json()
        assert doc["file_size"] == len(sample_txt_content)

    def test_upload_multiple_documents(self, client, sample_txt_content):
        """Test uploading multiple documents"""
        doc_ids = []
        for i in range(3):
            files = {"file": (f"doc_{i}.txt", sample_txt_content, "text/plain")}
            response = client.post("/api/documents/upload", files=files)
            assert response.status_code == 200
            doc_ids.append(response.json()["doc_id"])

        # All doc_ids should be unique
        assert len(set(doc_ids)) == 3


class TestDocumentList:
    """Test document list endpoint"""

    def test_list_empty_documents(self, client):
        """Test listing documents when none exist"""
        response = client.get("/api/documents/")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_documents_returns_uploaded(self, client, uploaded_document):
        """Test listing documents returns uploaded documents"""
        response = client.get("/api/documents/")
        assert response.status_code == 200

        docs = response.json()
        assert len(docs) == 1
        assert docs[0]["doc_id"] == uploaded_document["doc_id"]

    def test_list_documents_with_pagination(self, client, multiple_documents):
        """Test listing documents with pagination"""
        # Test skip
        response = client.get("/api/documents/?skip=1")
        assert response.status_code == 200
        docs = response.json()
        assert len(docs) == 2

        # Test limit
        response = client.get("/api/documents/?limit=1")
        assert response.status_code == 200
        docs = response.json()
        assert len(docs) == 1

    def test_list_documents_skip_and_limit(self, client, multiple_documents):
        """Test listing documents with both skip and limit"""
        response = client.get("/api/documents/?skip=1&limit=1")
        assert response.status_code == 200
        docs = response.json()
        assert len(docs) == 1


class TestGetDocument:
    """Test get document by ID endpoint"""

    def test_get_document_by_id(self, client, uploaded_document):
        """Test getting a document by ID"""
        doc_id = uploaded_document["doc_id"]
        response = client.get(f"/api/documents/{doc_id}")
        assert response.status_code == 200

        doc = response.json()
        assert doc["doc_id"] == doc_id
        assert "file_path" in doc
        assert "pages_data" in doc

    def test_get_nonexistent_document(self, client):
        """Test getting a nonexistent document returns 404"""
        response = client.get("/api/documents/DOCNONEXIST")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_document_includes_pages_data(self, client, uploaded_document):
        """Test get document includes pages data"""
        doc_id = uploaded_document["doc_id"]
        response = client.get(f"/api/documents/{doc_id}")
        assert response.status_code == 200

        doc = response.json()
        assert doc["pages_data"] is not None
        assert isinstance(doc["pages_data"], list)


class TestDeleteDocument:
    """Test delete document endpoint"""

    def test_delete_document(self, client, uploaded_document):
        """Test deleting a document"""
        doc_id = uploaded_document["doc_id"]
        response = client.delete(f"/api/documents/{doc_id}")
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]

        # Verify document is gone
        response = client.get(f"/api/documents/{doc_id}")
        assert response.status_code == 404

    def test_delete_nonexistent_document(self, client):
        """Test deleting a nonexistent document returns 404"""
        response = client.delete("/api/documents/DOCNONEXIST")
        assert response.status_code == 404

    def test_delete_removes_from_list(self, client, uploaded_document):
        """Test delete removes document from list"""
        doc_id = uploaded_document["doc_id"]

        # Verify it exists in list
        response = client.get("/api/documents/")
        assert len(response.json()) == 1

        # Delete it
        client.delete(f"/api/documents/{doc_id}")

        # Verify it's gone from list
        response = client.get("/api/documents/")
        assert len(response.json()) == 0


class TestUpdateDocumentSummary:
    """Test update document summary endpoint"""

    def test_update_summary(self, client, uploaded_document):
        """Test updating document summary"""
        doc_id = uploaded_document["doc_id"]
        new_summary = "Updated summary text"

        response = client.put(
            f"/api/documents/{doc_id}/summary",
            data={"summary": new_summary}
        )
        assert response.status_code == 200

        doc = response.json()
        assert doc["summary"] == new_summary

    def test_update_summary_nonexistent_document(self, client):
        """Test updating summary of nonexistent document returns 404"""
        response = client.put(
            "/api/documents/DOCNONEXIST/summary",
            data={"summary": "New summary"}
        )
        assert response.status_code == 404

    def test_update_summary_persists(self, client, uploaded_document):
        """Test updated summary persists when retrieved"""
        doc_id = uploaded_document["doc_id"]
        new_summary = "Persistent summary"

        client.put(
            f"/api/documents/{doc_id}/summary",
            data={"summary": new_summary}
        )

        # Retrieve and verify
        response = client.get(f"/api/documents/{doc_id}")
        assert response.json()["summary"] == new_summary


class TestGetDocumentPages:
    """Test get document pages endpoint"""

    def test_get_all_pages(self, client, uploaded_document):
        """Test getting all document pages"""
        doc_id = uploaded_document["doc_id"]
        response = client.get(f"/api/documents/{doc_id}/pages")
        assert response.status_code == 200

        data = response.json()
        assert data["doc_id"] == doc_id
        assert "total_pages" in data
        assert "pages" in data
        assert isinstance(data["pages"], list)

    def test_get_specific_pages(self, client, uploaded_document):
        """Test getting specific pages by number"""
        doc_id = uploaded_document["doc_id"]
        response = client.get(f"/api/documents/{doc_id}/pages?page_nums=1")
        assert response.status_code == 200

        data = response.json()
        assert len(data["pages"]) <= 1

    def test_get_pages_nonexistent_document(self, client):
        """Test getting pages of nonexistent document returns 404"""
        response = client.get("/api/documents/DOCNONEXIST/pages")
        assert response.status_code == 404

    def test_get_pages_invalid_format(self, client, uploaded_document):
        """Test getting pages with invalid format returns 400"""
        doc_id = uploaded_document["doc_id"]
        response = client.get(f"/api/documents/{doc_id}/pages?page_nums=invalid")
        assert response.status_code == 400
        assert "Invalid page numbers" in response.json()["detail"]


class TestDocumentFileTypes:
    """Test various file types"""

    def test_upload_docx_file(self, client):
        """Test uploading a DOCX file"""
        content = b"PK\x03\x04"  # Minimal DOCX/ZIP signature
        files = {"file": ("document.docx", content, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}

        response = client.post("/api/documents/upload", files=files)
        assert response.status_code == 200

        doc = response.json()
        assert doc["file_type"] == "DOCX"

    def test_upload_unknown_extension(self, client):
        """Test uploading a file with unknown extension"""
        content = b"Some content"
        files = {"file": ("document.xyz", content, "application/octet-stream")}

        response = client.post("/api/documents/upload", files=files)
        assert response.status_code == 200

        doc = response.json()
        assert doc["file_type"] == "XYZ"
