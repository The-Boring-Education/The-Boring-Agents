"""
Tests for the health check endpoint.

Simple API tests to verify the server is running correctly.
"""

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Tests for /api/v1/health endpoint."""
    
    def test_health_check_returns_ok(self, client: TestClient):
        """Test that health check returns ok status."""
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
    
    def test_health_check_returns_service_info(self, client: TestClient):
        """Test that health check returns service information."""
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "version" in data
        assert data["service"] == "The Boring Agents API"
    
    def test_health_check_returns_environment(self, client: TestClient):
        """Test that health check returns environment info."""
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "environment" in data

