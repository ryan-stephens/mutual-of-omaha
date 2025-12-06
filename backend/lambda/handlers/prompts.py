"""
Lambda handler for prompt version management
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, Any

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_query_parameter(event: Dict[str, Any], param_name: str, default: str = None) -> str:
    """Extract query parameter from API Gateway event"""
    query_params = event.get("queryStringParameters") or {}
    return query_params.get(param_name, default)


def create_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """Create API Gateway response with CORS headers"""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        },
        "body": json.dumps(body),
    }


def create_error_response(status_code: int, message: str) -> Dict[str, Any]:
    """Create error response"""
    return create_response(status_code, {"error": "Error", "message": message})


def list_prompt_versions() -> list:
    """
    Scan the prompts directory and return available versions

    Returns:
        List of version strings (e.g., ['v1.0.0', 'v1.1.0', 'v2.0.0'])
    """
    # Get the prompts directory relative to this file
    handler_dir = Path(__file__).parent
    prompts_dir = handler_dir.parent.parent / "prompts"

    logger.info(f"Scanning prompts directory: {prompts_dir}")

    if not prompts_dir.exists():
        logger.error(f"Prompts directory not found: {prompts_dir}")
        return []

    versions = []

    # Scan for .txt files in prompts directory
    for file_path in prompts_dir.glob("*.txt"):
        # Extract version from filename (e.g., "v1.0.0.txt" -> "v1.0.0")
        version = file_path.stem
        versions.append(version)
        logger.info(f"Found prompt version: {version}")

    # Sort versions (v1.0.0, v1.1.0, v2.0.0, etc.)
    versions.sort()

    return versions


def get_default_version(versions: list) -> str:
    """
    Determine the default version (latest version)

    Args:
        versions: List of version strings

    Returns:
        Default version string
    """
    if not versions:
        return "v2.0.0"  # Fallback

    # Return the last version (highest version number)
    return versions[-1]


def handler(event, context):
    """
    Process prompt version requests

    Supports:
    - GET /api/prompts/versions - List all available prompt versions
    """
    try:
        logger.info(f"Prompts request received: {event.get('httpMethod')} {event.get('path')}")

        # Handle GET /api/prompts/versions
        if event.get("httpMethod") == "GET":
            versions = list_prompt_versions()
            default_version = get_default_version(versions)

            logger.info(f"Returning {len(versions)} prompt versions, default: {default_version}")

            return create_response(
                200,
                {
                    "versions": versions,
                    "default_version": default_version,
                    "total_count": len(versions),
                },
            )

        # Unsupported method
        return create_error_response(405, "Method not allowed")

    except Exception as e:
        logger.error(f"Error processing prompts request: {str(e)}", exc_info=True)
        return create_error_response(500, f"Internal server error: {str(e)}")
