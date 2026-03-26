"""Tests for health check endpoint."""

import pytest
from unittest.mock import patch, MagicMock
from starlette.testclient import TestClient

from pipedrive.app import health_check, wrap_app_with_middleware


class TestHealthCheck:
    """Tests for the health check endpoint."""

    def test_health_check_returns_ok(self):
        """Health check should return status ok with version and features."""
        from starlette.applications import Starlette
        from starlette.routing import Route

        app = Starlette(routes=[Route("/health", health_check, methods=["GET"])])
        client = TestClient(app)
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data
        assert "features" in data
        assert isinstance(data["features"], list)

    @patch.dict("os.environ", {"MCP_AUTH_TOKEN": "secret"})
    def test_health_check_no_auth_required(self):
        """Health check should work without auth even when auth is enabled."""
        from starlette.applications import Starlette
        from starlette.routing import Route
        from starlette.middleware import Middleware
        from starlette.requests import Request
        from starlette.responses import JSONResponse
        from pipedrive.middleware.auth import BearerAuthMiddleware

        app = Starlette(
            routes=[Route("/health", health_check, methods=["GET"])],
            middleware=[Middleware(BearerAuthMiddleware)],
        )
        client = TestClient(app)

        # No auth header - should still work
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
