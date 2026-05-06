import json
from typing import Any, Dict, List, Optional
from datetime import date, datetime


# MCP tool annotation presets — see https://modelcontextprotocol.io/specification
# These hint to the client (Claude Desktop, claude.ai, etc.) about tool behavior.
# All Pipedrive tools talk to an external API, so openWorldHint is always True.

#: Read-only tools: get_*, list_*, search_*. Safe to call repeatedly, no side effects.
TOOL_ANNOTATIONS_READ: Dict[str, bool] = {
    "readOnlyHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": True,
}

#: Create tools: create_*, add_*. Each call produces a new resource (not idempotent).
TOOL_ANNOTATIONS_CREATE: Dict[str, bool] = {
    "readOnlyHint": False,
    "destructiveHint": False,
    "idempotentHint": False,
    "openWorldHint": True,
}

#: Update tools: update_*. Overwrites existing fields, but rejouer la même update donne le même état.
TOOL_ANNOTATIONS_UPDATE: Dict[str, bool] = {
    "readOnlyHint": False,
    "destructiveHint": True,
    "idempotentHint": True,
    "openWorldHint": True,
}

#: Delete tools: delete_*, remove_*. Destructive, but supprimer ce qui est déjà supprimé est un no-op.
TOOL_ANNOTATIONS_DELETE: Dict[str, bool] = {
    "readOnlyHint": False,
    "destructiveHint": True,
    "idempotentHint": True,
    "openWorldHint": True,
}


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder that can handle dates and datetimes."""
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)


def format_tool_response(
    success: bool, data: Optional[Any] = None, error_message: Optional[str] = None
) -> str:
    """
    Format a consistent JSON response for tool results.
    
    Args:
        success: Whether the operation was successful
        data: The data to return on success
        error_message: The error message to return on failure
        
    Returns:
        JSON formatted string with success status and data or error
    """
    return json.dumps(
        {"success": success, "data": data, "error": error_message}, 
        indent=2,
        cls=DateTimeEncoder
    )


def safe_split_to_list(comma_separated_string: Optional[str]) -> Optional[List[str]]:
    """
    Safely convert a comma-separated string to a list of strings.
    
    Args:
        comma_separated_string: A comma-separated string, or None
        
    Returns:
        A list of strings, or None if the input is None or empty
    """
    if not comma_separated_string:
        return None
        
    # Split by comma and strip whitespace
    result = [item.strip() for item in comma_separated_string.split(",") if item.strip()]
    
    # Return None if the result is an empty list
    return result if result else None


def format_validation_error(
    field_name: str, value: str, expected_format: str, example: str
) -> str:
    """
    Create a consistent validation error message with example.
    
    Args:
        field_name: Name of the field that failed validation
        value: The invalid value provided
        expected_format: Description of the expected format
        example: Example of valid value
        
    Returns:
        Formatted error message
    """
    return f"Invalid {field_name} format: '{value}'. {expected_format} Example: '{example}'"


def sanitize_inputs(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize input strings by converting empty strings to None.

    Args:
        inputs: Dictionary of input parameters

    Returns:
        Dictionary with sanitized inputs
    """
    sanitized = {}
    for key, value in inputs.items():
        if isinstance(value, str) and value.strip() == "":
            sanitized[key] = None
        else:
            sanitized[key] = value
    return sanitized


def empty_to_none(*values: Optional[str]) -> tuple:
    """
    Convert empty/whitespace-only string args to None, preserve everything else.

    Positional helper for tools that have many Optional[str] parameters and want
    to collapse `x = None if x == "" else x` into a single tuple unpack.

    Returns:
        Tuple of sanitized values, in the same order as input.

    Example:
        cursor, owner_id_str, pipeline_id_str = empty_to_none(
            cursor, owner_id_str, pipeline_id_str
        )
    """
    return tuple(
        None if isinstance(v, str) and v.strip() == "" else v
        for v in values
    )


def clean_optional_strs(**kwargs: Optional[str]) -> Dict[str, Optional[str]]:
    """
    Convert empty-string and whitespace-only inputs to None for kwargs.

    Replaces the boilerplate `x = None if x == "" else x` repeated across tools.
    Returns a dict where each empty/whitespace string becomes None, and non-string
    values are passed through unchanged.

    Args:
        **kwargs: Named string parameters (typically from a tool signature).

    Returns:
        Dict mapping each kwarg name to its sanitized value.

    Example:
        cleaned = clean_optional_strs(cursor=cursor, owner_id_str=owner_id_str)
        cursor = cleaned["cursor"]
        owner_id_str = cleaned["owner_id_str"]
    """
    return {
        key: (None if isinstance(value, str) and value.strip() == "" else value)
        for key, value in kwargs.items()
    }


def build_paginated_response(
    items: List[Any],
    next_cursor: Optional[str] = None,
    total: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Build a standardized pagination response payload.

    Includes count and has_more so consumers can paginate without inspecting
    next_cursor manually.

    Args:
        items: The list of items returned for this page.
        next_cursor: Opaque cursor for fetching the next page, or None if last page.
        total: Optional total count if the upstream API provides it.

    Returns:
        Dict with keys: items, count, has_more, next_cursor (and total if provided).
    """
    payload: Dict[str, Any] = {
        "items": items,
        "count": len(items),
        "has_more": next_cursor is not None,
        "next_cursor": next_cursor,
    }
    if total is not None:
        payload["total"] = total
    return payload


def bool_to_lowercase_str(value: Optional[bool]) -> Optional[str]:
    """
    Convert a boolean value to a lowercase string 'true' or 'false'.
    
    Args:
        value: Boolean value to convert
        
    Returns:
        String 'true' or 'false', or None if input is None
    """
    if value is None:
        return None
    return str(value).lower()
