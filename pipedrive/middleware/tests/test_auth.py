"""Tests for Bearer token authentication middleware."""

import pytest
from unittest.mock import patch
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from pipedrive.middleware.auth import BearerAuthMiddleware


async def _ok_endpoint(request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok"})


async def _health_endpoint(request: Request) -> JSONResponse:
    return JSONResponse({"status": "healthy"})


def _create_app() -> Starlette:
    return Starlette(
        routes=[
            Route("/test", _ok_endpoint, methods=["GET", "POST"]),
            Route("/health", _health_endpoint, methods=["GET"]),
        ],
        middleware=[Middleware(BearerAuthMiddleware)],
    )


class TestBearerAuthMiddleware:
    """Tests for BearerAuthMiddleware."""

    @patch.dict("os.environ", {"MCP_AUTH_TOKEN": "secret-token-123"})
    def test_valid_token_allows_request(self):
        app = _create_app()
        client = TestClient(app)
        response = client.get("/test", headers={"Authorization": "Bearer secret-token-123"})
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    @patch.dict("os.environ", {"MCP_AUTH_TOKEN": "secret-token-123"})
    def test_invalid_token_returns_401(self):
        app = _create_app()
        client = TestClient(app)
        response = client.get("/test", headers={"Authorization": "Bearer wrong-token"})
        assert response.status_code == 401
        assert "Invalid" in response.json()["error"]

    @patch.dict("os.environ", {"MCP_AUTH_TOKEN": "secret-token-123"})
    def test_missing_auth_header_returns_401(self):
        app = _create_app()
        client = TestClient(app)
        response = client.get("/test")
        assert response.status_code == 401
        assert "Missing" in response.json()["error"]

    @patch.dict("os.environ", {"MCP_AUTH_TOKEN": "secret-token-123"})
    def test_malformed_auth_header_returns_401(self):
        app = _create_app()
        client = TestClient(app)
        response = client.get("/test", headers={"Authorization": "Basic dXNlcjpwYXNz"})
        assert response.status_code == 401

    @patch.dict("os.environ", {"MCP_AUTH_TOKEN": ""})
    def test_empty_token_disables_auth(self):
        app = _create_app()
        client = TestClient(app)
        response = client.get("/test")
        assert response.status_code == 200

    @patch.dict("os.environ", {}, clear=False)
    def test_no_token_env_disables_auth(self):
        """When MCP_AUTH_TOKEN is not set at all, auth is disabled."""
        import os
        env = os.environ.copy()
        env.pop("MCP_AUTH_TOKEN", None)
        with patch.dict("os.environ", env, clear=True):
            app = _create_app()
            client = TestClient(app)
            response = client.get("/test")
            assert response.status_code == 200

    @patch.dict("os.environ", {"MCP_AUTH_TOKEN": "secret-token-123"})
    def test_health_endpoint_bypasses_auth(self):
        app = _create_app()
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    @patch.dict("os.environ", {"MCP_AUTH_TOKEN": "secret-token-123"})
    def test_options_request_bypasses_auth(self):
        app = _create_app()
        client = TestClient(app)
        response = client.options("/test")
        assert response.status_code != 401
