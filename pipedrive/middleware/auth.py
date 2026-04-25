"""Bearer token authentication middleware for MCP server."""

import os
import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


def get_auth_token() -> str | None:
    """Get the expected auth token from environment. Returns None if auth is disabled."""
    return os.getenv("MCP_AUTH_TOKEN", "").strip() or None


class BearerAuthMiddleware(BaseHTTPMiddleware):
    """Middleware that verifies Bearer token authentication on incoming requests.

    If MCP_AUTH_TOKEN is not set, authentication is disabled (dev mode).
    Health check endpoint is always accessible without authentication.
    """

    EXCLUDED_PATHS = {"/health", "/api/health"}
    # Prefixes always allowed without auth so OAuth-discovery clients (e.g. claude.ai
    # Custom Connector) get a clean 404 from the underlying app instead of a misleading 401.
    EXCLUDED_PREFIXES = ("/.well-known/", "/register")

    async def dispatch(self, request: Request, call_next):
        # Always allow preflight OPTIONS requests
        if request.method == "OPTIONS":
            return await call_next(request)

        # Skip auth for health check and OAuth discovery endpoints
        path = request.url.path
        if path in self.EXCLUDED_PATHS or path.startswith(self.EXCLUDED_PREFIXES):
            return await call_next(request)

        expected_token = get_auth_token()

        # If no token configured, auth is disabled
        if expected_token is None:
            return await call_next(request)

        # Extract Bearer token from Authorization header
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"error": "Missing or invalid Authorization header. Expected: Bearer <token>"},
            )

        provided_token = auth_header[7:]  # Strip "Bearer " prefix
        if provided_token != expected_token:
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid authentication token"},
            )

        return await call_next(request)
