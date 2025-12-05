"""
Shared utilities for Lambda handlers
"""

import json
import logging
import os
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def create_response(
    status_code: int, body: Dict[str, Any], headers: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Create a standardized API Gateway response

    Args:
        status_code: HTTP status code
        body: Response body dictionary
        headers: Optional additional headers

    Returns:
        API Gateway response format
    """
    default_headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type,Authorization",
        "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
    }

    if headers:
        default_headers.update(headers)

    return {
        "statusCode": status_code,
        "headers": default_headers,
        "body": json.dumps(body),
    }


def create_error_response(
    status_code: int, error_message: str, error_type: str = "Error"
) -> Dict[str, Any]:
    """
    Create a standardized error response

    Args:
        status_code: HTTP status code
        error_message: Error message
        error_type: Type of error

    Returns:
        API Gateway error response
    """
    return create_response(
        status_code=status_code, body={"error": error_type, "message": error_message}
    )


def parse_event_body(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse API Gateway event body

    Args:
        event: API Gateway event

    Returns:
        Parsed body dictionary
    """
    body = event.get("body", "{}")

    if isinstance(body, str):
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse body: {body}")
            return {}

    return body


def get_path_parameter(event: Dict[str, Any], param_name: str) -> Optional[str]:
    """
    Extract path parameter from API Gateway event

    Args:
        event: API Gateway event
        param_name: Parameter name

    Returns:
        Parameter value or None
    """
    path_params = event.get("pathParameters") or {}
    return path_params.get(param_name)


def get_query_parameter(
    event: Dict[str, Any], param_name: str, default: Optional[str] = None
) -> Optional[str]:
    """
    Extract query parameter from API Gateway event

    Args:
        event: API Gateway event
        param_name: Parameter name
        default: Default value if not found

    Returns:
        Parameter value or default
    """
    query_params = event.get("queryStringParameters") or {}
    return query_params.get(param_name, default)


def get_env_variable(name: str, default: Optional[str] = None) -> str:
    """
    Get environment variable with optional default

    Args:
        name: Environment variable name
        default: Default value if not found

    Returns:
        Environment variable value

    Raises:
        ValueError: If variable not found and no default provided
    """
    value = os.environ.get(name, default)
    if value is None:
        raise ValueError(f"Required environment variable not set: {name}")
    return value
