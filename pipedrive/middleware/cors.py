"""CORS middleware for MCP server."""

import os
import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


def get_allowed_origins() -> list[str]:
    """Get allowed origins from environment variable."""
    origins = os.getenv("ALLOWED_ORIGINS", "*").strip()
    if origins == "*":
        return ["*"]
    return [o.strip() for o in origins.split(",") if o.strip()]


class CORSMiddleware(BaseHTTPMiddleware):
    """Simple CORS middleware for MCP server.

    Handles preflight OPTIONS requests and adds CORS headers to all responses.
    Configured via ALLOWED_ORIGINS environment variable (default: *).
    """

    async def dispatch(self, request: Request, call_next):
        allowed_origins = get_allowed_origins()
        origin = request.headers.get("origin", "")

        # Determine the origin to allow
        if "*" in allowed_origins:
            allow_origin = "*"
        elif origin in allowed_origins:
            allow_origin = origin
        else:
            allow_origin = ""

        # Handle preflight OPTIONS request
        if request.method == "OPTIONS":
            response = Response(status_code=204)
            if allow_origin:
                response.headers["Access-Control-Allow-Origin"] = allow_origin
                response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
                response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
                response.headers["Access-Control-Max-Age"] = "86400"
            return response

        # Process the request
        response = await call_next(request)

        # Add CORS headers to response
        if allow_origin:
            response.headers["Access-Control-Allow-Origin"] = allow_origin
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"

        return response
