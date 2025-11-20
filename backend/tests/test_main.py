# test_main.py - Tests for main application endpoints
import pytest


class TestHealthEndpoint:
    """Test health check endpoint"""

    def test_health_check_returns_healthy(self, client):
        """Test health check returns healthy status"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert data["version"] == "1.0.0"


class TestRootEndpoint:
    """Test root endpoint"""

    def test_root_returns_api_info(self, client):
        """Test root returns API information"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Legal Risk Analysis API" in data["message"]
        assert "docs" in data
        assert "health" in data


class TestCORSConfiguration:
    """Test CORS middleware configuration"""

    def test_cors_headers_present(self, client):
        """Test CORS headers are present in response"""
        response = client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET"
            }
        )
        # CORS should allow the origin
        assert response.status_code in [200, 204]


class TestAPIDocumentation:
    """Test API documentation endpoints"""

    def test_openapi_json_accessible(self, client):
        """Test OpenAPI JSON is accessible"""
        response = client.get("/api/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert data["info"]["title"] == "Legal Risk Analysis API"

    def test_swagger_docs_accessible(self, client):
        """Test Swagger docs are accessible"""
        response = client.get("/api/docs")
        assert response.status_code == 200

    def test_redoc_accessible(self, client):
        """Test ReDoc is accessible"""
        response = client.get("/api/redoc")
        assert response.status_code == 200


class TestErrorHandling:
    """Test error handling"""

    def test_404_for_unknown_route(self, client):
        """Test 404 returned for unknown routes"""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404

    def test_405_for_wrong_method(self, client):
        """Test 405 returned for wrong HTTP method"""
        response = client.post("/api/health")
        assert response.status_code == 405
