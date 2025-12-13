"""
Tests for root application endpoints.
"""

import pytest
from fastapi import status


class TestMainRoutes:
    """Test cases for main application routes."""
    
    def test_root_endpoint(self, client):
        """Test the root endpoint returns correct response."""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["name"] == "PULSE API"
        assert data["version"] == "2.0.0"
        assert data["status"] == "running"
    
    def test_health_check(self, client):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "healthy"}
    
    def test_application_startup(self, client):
        """Test that the application starts up correctly."""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
