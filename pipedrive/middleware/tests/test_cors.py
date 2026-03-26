"""Tests for CORS middleware."""

import pytest
from unittest.mock import patch
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from pipedrive.middleware.cors import CORSMiddleware


async def _ok_endpoint(request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok"})


def _create_app() -> Starlette:
    return Starlette(
        routes=[Route("/test", _ok_endpoint, methods=["GET", "POST"])],
        middleware=[Middleware(CORSMiddleware)],
    )


class TestCORSMiddleware:
    """Tests for CORSMiddleware."""

    @patch.dict("os.environ", {"ALLOWED_ORIGINS": "*"})
    def test_wildcard_origin_adds_cors_headers(self):
        app = _create_app()
        client = TestClient(app)
        response = client.get("/test", headers={"Origin": "https://example.com"})
        assert response.status_code == 200
        assert response.headers["Access-Control-Allow-Origin"] == "*"
        assert "GET" in response.headers["Access-Control-Allow-Methods"]
        assert "POST" in response.headers["Access-Control-Allow-Methods"]

    @patch.dict("os.environ", {"ALLOWED_ORIGINS": "https://claude.ai,https://app.example.com"})
    def test_specific_origin_allowed(self):
        app = _create_app()
        client = TestClient(app)
        response = client.get("/test", headers={"Origin": "https://claude.ai"})
        assert response.status_code == 200
        assert response.headers["Access-Control-Allow-Origin"] == "https://claude.ai"

    @patch.dict("os.environ", {"ALLOWED_ORIGINS": "https://claude.ai"})
    def test_disallowed_origin_no_cors_header(self):
        app = _create_app()
        client = TestClient(app)
        response = client.get("/test", headers={"Origin": "https://evil.com"})
        assert response.status_code == 200
        assert response.headers.get("Access-Control-Allow-Origin", "") == ""

    @patch.dict("os.environ", {"ALLOWED_ORIGINS": "*"})
    def test_preflight_options_returns_204(self):
        app = _create_app()
        client = TestClient(app)
        response = client.options("/test", headers={"Origin": "https://example.com"})
        assert response.status_code == 204
        assert response.headers["Access-Control-Allow-Origin"] == "*"
        assert "Authorization" in response.headers["Access-Control-Allow-Headers"]
        assert response.headers.get("Access-Control-Max-Age") == "86400"

    @patch.dict("os.environ", {"ALLOWED_ORIGINS": "*"})
    def test_cors_headers_on_post(self):
        app = _create_app()
        client = TestClient(app)
        response = client.post("/test", headers={"Origin": "https://example.com"})
        assert response.headers["Access-Control-Allow-Origin"] == "*"
