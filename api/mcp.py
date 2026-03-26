"""Vercel serverless entry point for MCP server (Streamable HTTP transport).

This module creates an ASGI app suitable for Vercel's Python runtime.
Vercel does not send ASGI lifespan events, so we lazily initialize
the MCP session manager on the first incoming HTTP request.
"""

import contextlib
from collections.abc import AsyncIterator

import anyio
from dotenv import load_dotenv

load_dotenv()

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.routing import Mount, Route

from pipedrive.api.features import discover_features
from pipedrive.app import health_check, log_auth_status
from pipedrive.feature_config import FeatureConfig
from pipedrive.mcp_instance import mcp
from pipedrive.middleware.auth import BearerAuthMiddleware
from pipedrive.middleware.cors import CORSMiddleware

# Initialize features
discover_features()
FeatureConfig()
log_auth_status()

# Build the MCP streamable HTTP app (creates the session manager)
_mcp_app = mcp.streamable_http_app()


@contextlib.asynccontextmanager
async def lifespan(app: Starlette) -> AsyncIterator[None]:
    """Initialize the MCP session manager.

    Works both when Vercel sends lifespan events and as explicit init.
    """
    async with mcp.session_manager.run():
        yield


# ASGI wrapper that ensures session manager is initialized even if
# the runtime (Vercel) skips ASGI lifespan events.
class _JsonRpcApp:
    """ASGI app that lazily initializes the session manager per-request."""

    def __init__(self, inner: Starlette) -> None:
        self.inner = inner

    async def __call__(self, scope, receive, send):
        if scope["type"] == "lifespan":
            await self.inner(scope, receive, send)
            return

        # If session manager was not started via lifespan, start it now
        sm = mcp.session_manager
        if sm._task_group is None:
            async with anyio.create_task_group() as tg:
                sm._task_group = tg
                try:
                    await self.inner(scope, receive, send)
                finally:
                    tg.cancel_scope.cancel()
                    sm._task_group = None
        else:
            await self.inner(scope, receive, send)


_starlette_app = Starlette(
    routes=[
        Route("/health", health_check, methods=["GET"]),
        Mount("/", app=_mcp_app),
    ],
    middleware=[
        Middleware(CORSMiddleware),
        Middleware(BearerAuthMiddleware),
    ],
    lifespan=lifespan,
)

app = _JsonRpcApp(_starlette_app)
