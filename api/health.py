"""Vercel serverless entry point for health check."""

from dotenv import load_dotenv

load_dotenv()

from pipedrive.api.features import discover_features
from pipedrive.feature_config import FeatureConfig
from pipedrive.mcp_instance import mcp
from pipedrive.app import wrap_app_with_middleware

# Initialize features
discover_features()
FeatureConfig()

# Reuse the same app (health check is included by default)
_mcp_app = mcp.streamable_http_app()
app = wrap_app_with_middleware(_mcp_app)
