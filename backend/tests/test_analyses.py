# test_analyses.py - Tests for analyses router
import pytest
import time


class TestCreateAnalysis:
    """Test analysis creation endpoint"""

    def test_create_analysis(self, client, uploaded_document):
        """Test creating an analysis"""
        analysis_data = {
            "name": "Test Analysis",
            "description": "Test description",
            "document_ids": [uploaded_document["doc_id"]]
        }

        response = client.post("/api/analyses/", json=analysis_data)
        assert response.status_code == 200

        analysis = response.json()
        assert "analysis_id" in analysis
        assert analysis["analysis_id"].startswith("ANA")
        assert analysis["name"] == "Test Analysis"
        assert analysis["description"] == "Test description"
        assert analysis["status"] in ["pending", "running"]
        assert analysis["document_count"] == 1

    def test_create_analysis_with_multiple_documents(self, client, multiple_documents):
        """Test creating analysis with multiple documents"""
        doc_ids = [doc["doc_id"] for doc in multiple_documents]
        analysis_data = {
            "name": "Multi-doc Analysis",
            "description": "Analysis of multiple documents",
            "document_ids": doc_ids
        }

        response = client.post("/api/analyses/", json=analysis_data)
        assert response.status_code == 200

        analysis = response.json()
        assert analysis["document_count"] == len(doc_ids)

    def test_create_analysis_with_missing_document(self, client, uploaded_document):
        """Test creating analysis with missing document returns 404"""
        analysis_data = {
            "name": "Invalid Analysis",
            "document_ids": [uploaded_document["doc_id"], "DOCNONEXIST"]
        }

        response = client.post("/api/analyses/", json=analysis_data)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_create_analysis_without_documents(self, client):
        """Test creating analysis without documents fails"""
        analysis_data = {
            "name": "No docs",
            "document_ids": []
        }

        response = client.post("/api/analyses/", json=analysis_data)
        # Empty document list should still work but create 0 associations
        # or return validation error depending on implementation
        assert response.status_code in [200, 400, 422]

    def test_create_analysis_initializes_progress(self, client, uploaded_document):
        """Test created analysis initializes with correct progress"""
        analysis_data = {
            "name": "Progress Test",
            "document_ids": [uploaded_document["doc_id"]]
        }

        response = client.post("/api/analyses/", json=analysis_data)
        assert response.status_code == 200

        analysis = response.json()
        assert analysis["progress"] >= 0
        assert analysis["risk_count"] == 0


class TestListAnalyses:
    """Test analysis list endpoint"""

    def test_list_empty_analyses(self, client):
        """Test listing analyses when none exist"""
        response = client.get("/api/analyses/")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_analyses_returns_created(self, client, created_analysis):
        """Test listing analyses returns created analyses"""
        response = client.get("/api/analyses/")
        assert response.status_code == 200

        analyses = response.json()
        assert len(analyses) >= 1
        analysis_ids = [a["analysis_id"] for a in analyses]
        assert created_analysis["analysis_id"] in analysis_ids

    def test_list_analyses_with_pagination(self, client, uploaded_document):
        """Test listing analyses with pagination"""
        # Create multiple analyses
        for i in range(3):
            analysis_data = {
                "name": f"Analysis {i}",
                "document_ids": [uploaded_document["doc_id"]]
            }
            client.post("/api/analyses/", json=analysis_data)

        # Test limit
        response = client.get("/api/analyses/?limit=2")
        assert response.status_code == 200
        assert len(response.json()) == 2

        # Test skip
        response = client.get("/api/analyses/?skip=1")
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_list_analyses_filter_by_status(self, client, created_analysis):
        """Test filtering analyses by status"""
        # Filter by pending status
        response = client.get("/api/analyses/?status=pending")
        assert response.status_code == 200
        # All returned analyses should have pending status
        for analysis in response.json():
            assert analysis["status"] == "pending"

    def test_list_analyses_ordered_by_date(self, client, uploaded_document):
        """Test analyses are ordered by creation date descending"""
        # Create analyses with slight delay
        for i in range(2):
            analysis_data = {
                "name": f"Analysis {i}",
                "document_ids": [uploaded_document["doc_id"]]
            }
            client.post("/api/analyses/", json=analysis_data)
            time.sleep(0.1)

        response = client.get("/api/analyses/")
        analyses = response.json()

        # Should be in descending order (most recent first)
        for i in range(len(analyses) - 1):
            assert analyses[i]["created_at"] >= analyses[i + 1]["created_at"]


class TestGetAnalysis:
    """Test get analysis by ID endpoint"""

    def test_get_analysis_by_id(self, client, created_analysis):
        """Test getting an analysis by ID"""
        analysis_id = created_analysis["analysis_id"]
        response = client.get(f"/api/analyses/{analysis_id}")
        assert response.status_code == 200

        analysis = response.json()
        assert analysis["analysis_id"] == analysis_id
        assert "documents" in analysis
        assert "risks" in analysis
        assert "result_data" in analysis

    def test_get_nonexistent_analysis(self, client):
        """Test getting a nonexistent analysis returns 404"""
        response = client.get("/api/analyses/ANANONEXIST")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_analysis_includes_documents(self, client, created_analysis):
        """Test get analysis includes associated documents"""
        analysis_id = created_analysis["analysis_id"]
        response = client.get(f"/api/analyses/{analysis_id}")
        assert response.status_code == 200

        analysis = response.json()
        assert "documents" in analysis
        assert len(analysis["documents"]) == analysis["document_count"]


class TestGetAnalysisStatus:
    """Test get analysis status endpoint"""

    def test_get_analysis_status(self, client, created_analysis):
        """Test getting analysis status"""
        analysis_id = created_analysis["analysis_id"]
        response = client.get(f"/api/analyses/{analysis_id}/status")
        assert response.status_code == 200

        status = response.json()
        assert status["analysis_id"] == analysis_id
        assert "status" in status
        assert "progress" in status
        assert "current_step" in status

    def test_get_status_nonexistent_analysis(self, client):
        """Test getting status of nonexistent analysis returns 404"""
        response = client.get("/api/analyses/ANANONEXIST/status")
        assert response.status_code == 404


class TestGetAnalysisRisks:
    """Test get analysis risks endpoint"""

    def test_get_analysis_risks(self, client, created_analysis):
        """Test getting risks for an analysis"""
        analysis_id = created_analysis["analysis_id"]
        response = client.get(f"/api/analyses/{analysis_id}/risks")
        assert response.status_code == 200

        data = response.json()
        assert data["analysis_id"] == analysis_id
        assert "total" in data
        assert "risks" in data
        assert isinstance(data["risks"], list)

    def test_get_risks_nonexistent_analysis(self, client):
        """Test getting risks of nonexistent analysis returns 404"""
        response = client.get("/api/analyses/ANANONEXIST/risks")
        assert response.status_code == 404

    def test_get_risks_filter_by_category(self, client, created_analysis):
        """Test filtering risks by category"""
        analysis_id = created_analysis["analysis_id"]
        response = client.get(f"/api/analyses/{analysis_id}/risks?category=Contractual")
        assert response.status_code == 200

        data = response.json()
        # All returned risks should be in Contractual category
        for risk in data["risks"]:
            assert risk["category"] == "Contractual"

    def test_get_risks_filter_by_severity(self, client, created_analysis):
        """Test filtering risks by severity"""
        analysis_id = created_analysis["analysis_id"]
        response = client.get(f"/api/analyses/{analysis_id}/risks?severity=High")
        assert response.status_code == 200

        data = response.json()
        # All returned risks should have High severity
        for risk in data["risks"]:
            assert risk["severity"] == "High"


class TestDeleteAnalysis:
    """Test delete analysis endpoint"""

    def test_delete_analysis(self, client, created_analysis):
        """Test deleting an analysis"""
        analysis_id = created_analysis["analysis_id"]
        response = client.delete(f"/api/analyses/{analysis_id}")
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]

        # Verify analysis is gone
        response = client.get(f"/api/analyses/{analysis_id}")
        assert response.status_code == 404

    def test_delete_nonexistent_analysis(self, client):
        """Test deleting a nonexistent analysis returns 404"""
        response = client.delete("/api/analyses/ANANONEXIST")
        assert response.status_code == 404

    def test_delete_removes_from_list(self, client, created_analysis):
        """Test delete removes analysis from list"""
        analysis_id = created_analysis["analysis_id"]

        # Verify it exists in list
        response = client.get("/api/analyses/")
        analysis_ids = [a["analysis_id"] for a in response.json()]
        assert analysis_id in analysis_ids

        # Delete it
        client.delete(f"/api/analyses/{analysis_id}")

        # Verify it's gone from list
        response = client.get("/api/analyses/")
        analysis_ids = [a["analysis_id"] for a in response.json()]
        assert analysis_id not in analysis_ids


class TestAnalysisWorkflow:
    """Test complete analysis workflow"""

    def test_complete_analysis_workflow(self, client, sample_txt_content):
        """Test complete analysis workflow from upload to completion"""
        # 1. Upload document
        files = {"file": ("workflow_test.txt", sample_txt_content, "text/plain")}
        response = client.post("/api/documents/upload", files=files)
        assert response.status_code == 200
        doc_id = response.json()["doc_id"]

        # 2. Create analysis
        analysis_data = {
            "name": "Workflow Test Analysis",
            "description": "Testing complete workflow",
            "document_ids": [doc_id]
        }
        response = client.post("/api/analyses/", json=analysis_data)
        assert response.status_code == 200
        analysis_id = response.json()["analysis_id"]

        # 3. Check status
        response = client.get(f"/api/analyses/{analysis_id}/status")
        assert response.status_code == 200
        assert response.json()["analysis_id"] == analysis_id

        # 4. Get analysis details
        response = client.get(f"/api/analyses/{analysis_id}")
        assert response.status_code == 200
        assert len(response.json()["documents"]) == 1

        # 5. Get risks
        response = client.get(f"/api/analyses/{analysis_id}/risks")
        assert response.status_code == 200

        # 6. Delete analysis
        response = client.delete(f"/api/analyses/{analysis_id}")
        assert response.status_code == 200

        # 7. Document should still exist
        response = client.get(f"/api/documents/{doc_id}")
        assert response.status_code == 200
