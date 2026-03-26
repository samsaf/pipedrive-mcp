"""Vercel serverless entry point for MCP server (Streamable HTTP transport).

This module creates an ASGI app suitable for Vercel's Python runtime.
It exposes the MCP server with auth, CORS middleware and health check.
"""

from dotenv import load_dotenv

load_dotenv()

from pipedrive.api.features import discover_features
from pipedrive.feature_config import FeatureConfig
from pipedrive.mcp_instance import mcp
from pipedrive.app import wrap_app_with_middleware, log_auth_status

# Initialize features
discover_features()
FeatureConfig()

# Log auth status
log_auth_status()

# Build the ASGI app: MCP streamable HTTP + middleware
_mcp_app = mcp.streamable_http_app()
app = wrap_app_with_middleware(_mcp_app)
