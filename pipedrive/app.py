"""Application builder that composes the MCP server with middleware and health check."""

import json
import logging
import os

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from pipedrive.middleware.auth import BearerAuthMiddleware, get_auth_token
from pipedrive.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)

VERSION = "1.0.0"


async def health_check(request: Request) -> JSONResponse:
    """Health check endpoint returning server status and enabled features."""
    from pipedrive.api.features.tool_registry import registry

    enabled_features = list(registry.get_enabled_features().keys())

    return JSONResponse({
        "status": "ok",
        "version": VERSION,
        "features": enabled_features,
    })


def wrap_app_with_middleware(app: Starlette, include_health: bool = True) -> Starlette:
    """Wrap an existing Starlette app with auth, CORS middleware and health route.

    This takes the Starlette app produced by FastMCP (sse_app or streamable_http_app)
    and wraps it with our middleware stack. We rebuild a new Starlette app that mounts
    the original app as a catch-all, adds our custom routes, and applies middleware.

    Args:
        app: The Starlette app from FastMCP
        include_health: Whether to add the /health route
    """
    from starlette.routing import Mount

    routes = []

    if include_health:
        routes.append(Route("/health", health_check, methods=["GET"]))

    # Mount the original MCP app to handle all other routes
    routes.append(Mount("/", app=app))

    middleware = [
        Middleware(CORSMiddleware),
        Middleware(BearerAuthMiddleware),
    ]

    wrapped = Starlette(
        routes=routes,
        middleware=middleware,
    )

    return wrapped


def log_auth_status() -> None:
    """Log whether authentication is enabled or disabled."""
    token = get_auth_token()
    if token is None:
        logger.warning(
            "MCP_AUTH_TOKEN is not set - authentication is DISABLED. "
            "Set MCP_AUTH_TOKEN environment variable to secure the server."
        )
    else:
        logger.info("Authentication is enabled (Bearer token)")
