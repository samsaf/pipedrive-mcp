from mcp.server.fastmcp import Context

from log_config import logger
from pipedrive.api.features.shared.utils import format_tool_response
from pipedrive.api.pipedrive_api_error import PipedriveAPIError
from pipedrive.api.pipedrive_context import PipedriveMCPContext
from pipedrive.mcp_instance import mcp


@mcp.tool("list_pipelines_from_pipedrive")
async def list_pipelines_from_pipedrive(ctx: Context) -> str:
    """Lists all pipelines from the Pipedrive CRM.

    This tool retrieves every pipeline configured in the Pipedrive account.
    Pipelines represent the different sales processes in the CRM, each containing
    a set of stages that deals move through. Use this tool to discover the
    available pipeline IDs before creating or filtering deals.

    Format requirements:
        - No parameters required.

    Example:
        list_pipelines_from_pipedrive()

    Args:
        ctx: Context object containing the Pipedrive client

    Returns:
        JSON string containing the list of pipelines. Each pipeline includes
        its id, name, url_title, order_nr, active flag, deal_probability flag,
        add_time, update_time, and is_deal_probability_enabled flag.
    """
    logger.debug("Tool 'list_pipelines_from_pipedrive' ENTERED")

    pd_mcp_ctx: PipedriveMCPContext = ctx.request_context.lifespan_context

    try:
        pipelines = await pd_mcp_ctx.pipedrive_client.deals.list_pipelines()

        logger.info(f"Successfully retrieved {len(pipelines)} pipelines")
        return format_tool_response(True, data={"items": pipelines})

    except PipedriveAPIError as e:
        logger.error(
            f"PipedriveAPIError in tool 'list_pipelines_from_pipedrive': {str(e)}"
        )
        return format_tool_response(False, error_message=str(e), data=e.response_data)
    except Exception as e:
        logger.exception(
            f"Unexpected error in tool 'list_pipelines_from_pipedrive': {str(e)}"
        )
        return format_tool_response(
            False, error_message=f"An unexpected error occurred: {str(e)}"
        )
