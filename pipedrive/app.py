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


def _mask(value: str) -> str:
    """Mask a secret, showing only first 4 and last 4 chars + length."""
    if not value:
        return "<empty>"
    if len(value) <= 8:
        return f"<too short: {len(value)} chars>"
    return f"{value[:4]}...{value[-4:]} (len={len(value)})"


async def debug_env(request: Request) -> JSONResponse:
    """TEMPORARY debug endpoint to inspect what env vars the server actually sees.

    Reveals only first/last 4 chars of secrets to avoid full leak. Remove this
    endpoint after debugging is complete.
    """
    api_token = os.getenv("PIPEDRIVE_API_TOKEN", "")
    domain = os.getenv("PIPEDRIVE_COMPANY_DOMAIN", "")
    auth_token = os.getenv("MCP_AUTH_TOKEN", "")

    return JSONResponse({
        "PIPEDRIVE_API_TOKEN": _mask(api_token),
        "PIPEDRIVE_COMPANY_DOMAIN": domain,  # not a secret
        "MCP_AUTH_TOKEN": _mask(auth_token),
        "api_token_has_whitespace": api_token != api_token.strip() if api_token else False,
        "domain_has_whitespace": domain != domain.strip() if domain else False,
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
        # TEMPORARY debug endpoint - remove after debugging
        routes.append(Route("/debug-env", debug_env, methods=["GET"]))

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
