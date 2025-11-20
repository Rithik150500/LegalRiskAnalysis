# test_dashboard.py - Tests for dashboard router
import pytest
import time


class TestDashboardStats:
    """Test dashboard statistics endpoint"""

    def test_get_stats_empty_database(self, client):
        """Test getting stats with empty database"""
        response = client.get("/api/dashboard/stats")
        assert response.status_code == 200

        stats = response.json()
        assert stats["total_documents"] == 0
        assert stats["total_analyses"] == 0
        assert stats["completed_analyses"] == 0
        assert stats["total_risks"] == 0
        assert "risk_summary" in stats
        assert "recent_analyses" in stats

    def test_get_stats_with_documents(self, client, uploaded_document):
        """Test getting stats with documents"""
        response = client.get("/api/dashboard/stats")
        assert response.status_code == 200

        stats = response.json()
        assert stats["total_documents"] == 1

    def test_get_stats_with_analyses(self, client, created_analysis):
        """Test getting stats with analyses"""
        response = client.get("/api/dashboard/stats")
        assert response.status_code == 200

        stats = response.json()
        assert stats["total_analyses"] >= 1

    def test_get_stats_risk_summary_structure(self, client):
        """Test risk summary has correct structure"""
        response = client.get("/api/dashboard/stats")
        assert response.status_code == 200

        risk_summary = response.json()["risk_summary"]
        assert "total" in risk_summary
        assert "by_severity" in risk_summary
        assert "by_category" in risk_summary
        assert "by_likelihood" in risk_summary

    def test_get_stats_by_severity_counts(self, client):
        """Test by_severity contains all severity levels"""
        response = client.get("/api/dashboard/stats")
        assert response.status_code == 200

        by_severity = response.json()["risk_summary"]["by_severity"]
        assert "Critical" in by_severity
        assert "High" in by_severity
        assert "Medium" in by_severity
        assert "Low" in by_severity

    def test_get_stats_by_category_counts(self, client):
        """Test by_category contains all categories"""
        response = client.get("/api/dashboard/stats")
        assert response.status_code == 200

        by_category = response.json()["risk_summary"]["by_category"]
        assert "Contractual" in by_category
        assert "Regulatory" in by_category
        assert "Litigation" in by_category
        assert "IP" in by_category
        assert "Operational" in by_category

    def test_get_stats_by_likelihood_counts(self, client):
        """Test by_likelihood contains all likelihood levels"""
        response = client.get("/api/dashboard/stats")
        assert response.status_code == 200

        by_likelihood = response.json()["risk_summary"]["by_likelihood"]
        assert "Very Likely" in by_likelihood
        assert "Likely" in by_likelihood
        assert "Possible" in by_likelihood
        assert "Unlikely" in by_likelihood

    def test_get_stats_recent_analyses_limit(self, client, uploaded_document):
        """Test recent analyses is limited to 5"""
        # Create more than 5 analyses
        for i in range(7):
            analysis_data = {
                "name": f"Analysis {i}",
                "document_ids": [uploaded_document["doc_id"]]
            }
            client.post("/api/analyses/", json=analysis_data)
            time.sleep(0.05)

        response = client.get("/api/dashboard/stats")
        assert response.status_code == 200

        recent = response.json()["recent_analyses"]
        assert len(recent) <= 5

    def test_get_stats_recent_analyses_structure(self, client, created_analysis):
        """Test recent analyses have correct structure"""
        response = client.get("/api/dashboard/stats")
        assert response.status_code == 200

        recent = response.json()["recent_analyses"]
        if len(recent) > 0:
            analysis = recent[0]
            assert "analysis_id" in analysis
            assert "name" in analysis
            assert "status" in analysis
            assert "document_count" in analysis
            assert "risk_count" in analysis


class TestRiskMatrix:
    """Test risk matrix endpoint"""

    def test_get_risk_matrix_empty(self, client):
        """Test getting risk matrix with no risks"""
        response = client.get("/api/dashboard/risk-matrix")
        assert response.status_code == 200

        data = response.json()
        assert "matrix" in data
        assert "severities" in data
        assert "likelihoods" in data

    def test_get_risk_matrix_severities(self, client):
        """Test risk matrix returns all severities"""
        response = client.get("/api/dashboard/risk-matrix")
        assert response.status_code == 200

        severities = response.json()["severities"]
        assert severities == ["Critical", "High", "Medium", "Low"]

    def test_get_risk_matrix_likelihoods(self, client):
        """Test risk matrix returns all likelihoods"""
        response = client.get("/api/dashboard/risk-matrix")
        assert response.status_code == 200

        likelihoods = response.json()["likelihoods"]
        assert likelihoods == ["Very Likely", "Likely", "Possible", "Unlikely"]

    def test_get_risk_matrix_structure(self, client):
        """Test risk matrix has correct structure"""
        response = client.get("/api/dashboard/risk-matrix")
        assert response.status_code == 200

        matrix = response.json()["matrix"]
        assert isinstance(matrix, list)

        # If there are entries, check structure
        for entry in matrix:
            assert "severity" in entry
            assert "likelihood" in entry
            assert "count" in entry
            assert "risks" in entry


class TestCategoryBreakdown:
    """Test category breakdown endpoint"""

    def test_get_category_breakdown_empty(self, client):
        """Test getting category breakdown with no risks"""
        response = client.get("/api/dashboard/category-breakdown")
        assert response.status_code == 200

        breakdown = response.json()
        assert isinstance(breakdown, list)
        assert len(breakdown) == 5  # Five categories

    def test_get_category_breakdown_all_categories(self, client):
        """Test category breakdown includes all categories"""
        response = client.get("/api/dashboard/category-breakdown")
        assert response.status_code == 200

        breakdown = response.json()
        categories = [item["category"] for item in breakdown]
        assert "Contractual" in categories
        assert "Regulatory" in categories
        assert "Litigation" in categories
        assert "IP" in categories
        assert "Operational" in categories

    def test_get_category_breakdown_structure(self, client):
        """Test category breakdown has correct structure"""
        response = client.get("/api/dashboard/category-breakdown")
        assert response.status_code == 200

        breakdown = response.json()
        for item in breakdown:
            assert "category" in item
            assert "total" in item
            assert "by_severity" in item

            by_severity = item["by_severity"]
            assert "Critical" in by_severity
            assert "High" in by_severity
            assert "Medium" in by_severity
            assert "Low" in by_severity


class TestAnalysisTimeline:
    """Test analysis timeline endpoint"""

    def test_get_timeline_empty(self, client):
        """Test getting timeline with no analyses"""
        response = client.get("/api/dashboard/timeline")
        assert response.status_code == 200

        timeline = response.json()
        assert isinstance(timeline, list)
        assert len(timeline) == 0

    def test_get_timeline_with_analyses(self, client, created_analysis):
        """Test getting timeline with analyses"""
        response = client.get("/api/dashboard/timeline")
        assert response.status_code == 200

        timeline = response.json()
        assert len(timeline) >= 1

    def test_get_timeline_structure(self, client, created_analysis):
        """Test timeline entries have correct structure"""
        response = client.get("/api/dashboard/timeline")
        assert response.status_code == 200

        timeline = response.json()
        if len(timeline) > 0:
            entry = timeline[0]
            assert "analysis_id" in entry
            assert "name" in entry
            assert "date" in entry
            assert "status" in entry
            assert "risk_count" in entry

    def test_get_timeline_ordered_by_date(self, client, uploaded_document):
        """Test timeline is ordered by date ascending"""
        # Create analyses with different timestamps
        for i in range(3):
            analysis_data = {
                "name": f"Timeline Analysis {i}",
                "document_ids": [uploaded_document["doc_id"]]
            }
            client.post("/api/analyses/", json=analysis_data)
            time.sleep(0.1)

        response = client.get("/api/dashboard/timeline")
        timeline = response.json()

        # Should be in ascending order (oldest first)
        for i in range(len(timeline) - 1):
            assert timeline[i]["date"] <= timeline[i + 1]["date"]


class TestDashboardIntegration:
    """Test dashboard integration scenarios"""

    def test_dashboard_reflects_document_upload(self, client, sample_txt_content):
        """Test dashboard reflects new document uploads"""
        # Get initial stats
        response = client.get("/api/dashboard/stats")
        initial_count = response.json()["total_documents"]

        # Upload a document
        files = {"file": ("dashboard_test.txt", sample_txt_content, "text/plain")}
        client.post("/api/documents/upload", files=files)

        # Check stats updated
        response = client.get("/api/dashboard/stats")
        assert response.json()["total_documents"] == initial_count + 1

    def test_dashboard_reflects_analysis_creation(self, client, uploaded_document):
        """Test dashboard reflects new analyses"""
        # Get initial stats
        response = client.get("/api/dashboard/stats")
        initial_count = response.json()["total_analyses"]

        # Create analysis
        analysis_data = {
            "name": "Dashboard Test",
            "document_ids": [uploaded_document["doc_id"]]
        }
        client.post("/api/analyses/", json=analysis_data)

        # Check stats updated
        response = client.get("/api/dashboard/stats")
        assert response.json()["total_analyses"] == initial_count + 1

    def test_dashboard_reflects_deletions(self, client, uploaded_document):
        """Test dashboard reflects deletions"""
        # Create and then delete an analysis
        analysis_data = {
            "name": "Delete Test",
            "document_ids": [uploaded_document["doc_id"]]
        }
        response = client.post("/api/analyses/", json=analysis_data)
        analysis_id = response.json()["analysis_id"]

        # Get count before deletion
        response = client.get("/api/dashboard/stats")
        count_before = response.json()["total_analyses"]

        # Delete analysis
        client.delete(f"/api/analyses/{analysis_id}")

        # Check stats updated
        response = client.get("/api/dashboard/stats")
        assert response.json()["total_analyses"] == count_before - 1
