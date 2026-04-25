from typing import Optional

from mcp.server.fastmcp import Context

from log_config import logger
from pipedrive.api.features.shared.conversion.id_conversion import convert_id_string
from pipedrive.api.features.shared.utils import format_tool_response
from pipedrive.api.pipedrive_api_error import PipedriveAPIError
from pipedrive.api.pipedrive_context import PipedriveMCPContext
from pipedrive.mcp_instance import mcp


@mcp.tool("list_stages_from_pipedrive")
async def list_stages_from_pipedrive(
    ctx: Context,
    pipeline_id_str: Optional[str] = None,
) -> str:
    """Lists all stages from the Pipedrive CRM, optionally filtered by pipeline.

    This tool retrieves every stage configured in the Pipedrive account. Stages
    represent the different steps deals move through within a pipeline. Use this
    tool to discover available stage IDs before creating or updating deals, or
    to inspect the configuration of a specific pipeline.

    Format requirements:
        - pipeline_id_str: Optional numeric pipeline ID as a string (e.g. "1").
          When provided, only stages belonging to this pipeline are returned.
          When omitted, all stages across all pipelines are returned.

    Example:
        # List all stages across all pipelines
        list_stages_from_pipedrive()

        # List stages of a specific pipeline
        list_stages_from_pipedrive(pipeline_id_str="1")

    Args:
        ctx: Context object containing the Pipedrive client
        pipeline_id_str: Optional pipeline ID (as string) to filter stages by

    Returns:
        JSON string containing the list of stages. Each stage includes its id,
        order_nr, name, active flag, deal_probability, pipeline_id, rotten_flag,
        rotten_days, add_time, and update_time.
    """
    logger.debug(
        f"Tool 'list_stages_from_pipedrive' ENTERED with pipeline_id_str='{pipeline_id_str}'"
    )

    # Sanitize empty string to None
    pipeline_id_str = None if pipeline_id_str == "" else pipeline_id_str

    pd_mcp_ctx: PipedriveMCPContext = ctx.request_context.lifespan_context

    try:
        pipeline_id, pipeline_id_error = convert_id_string(
            pipeline_id_str, "pipeline_id"
        )
        if pipeline_id_error:
            logger.error(pipeline_id_error)
            return format_tool_response(False, error_message=pipeline_id_error)

        stages = await pd_mcp_ctx.pipedrive_client.deals.list_stages(
            pipeline_id=pipeline_id
        )

        logger.info(f"Successfully retrieved {len(stages)} stages")
        return format_tool_response(True, data={"items": stages})

    except PipedriveAPIError as e:
        logger.error(
            f"PipedriveAPIError in tool 'list_stages_from_pipedrive': {str(e)}"
        )
        return format_tool_response(False, error_message=str(e), data=e.response_data)
    except Exception as e:
        logger.exception(
            f"Unexpected error in tool 'list_stages_from_pipedrive': {str(e)}"
        )
        return format_tool_response(
            False, error_message=f"An unexpected error occurred: {str(e)}"
        )
