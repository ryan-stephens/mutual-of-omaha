"""
Prompts management endpoints for versioning and experimentation
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from app.services.prompt_manager import get_prompt_manager
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


class PromptVersionInfo(BaseModel):
    """Prompt version metadata"""

    version: str
    is_default: bool
    length_chars: int
    length_tokens_estimate: int
    available_since: str


class PromptVersionsResponse(BaseModel):
    """List of available prompt versions"""

    versions: List[str]
    default_version: str
    total_count: int


@router.get("/prompts/versions", response_model=PromptVersionsResponse)
async def list_prompt_versions():
    """
    List all available prompt versions

    Returns:
        List of prompt versions with metadata
    """
    try:
        prompt_manager = get_prompt_manager()
        versions = prompt_manager.list_versions()

        return PromptVersionsResponse(
            versions=versions,
            default_version=prompt_manager.DEFAULT_VERSION,
            total_count=len(versions),
        )

    except Exception as e:
        logger.error(f"Failed to list prompt versions: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve prompt versions: {str(e)}"
        )


@router.get("/prompts/versions/{version}", response_model=PromptVersionInfo)
async def get_prompt_version_info(version: str):
    """
    Get detailed information about a specific prompt version

    Args:
        version: Prompt version (e.g., "v1.0.0")

    Returns:
        Prompt version metadata
    """
    try:
        prompt_manager = get_prompt_manager()
        metadata = prompt_manager.get_version_metadata(version)

        return PromptVersionInfo(**metadata)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get prompt version info: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve prompt version info: {str(e)}"
        )


@router.get("/prompts/versions/{version}/content")
async def get_prompt_content(version: str):
    """
    Get the actual prompt content for a version

    Args:
        version: Prompt version

    Returns:
        Raw prompt text
    """
    try:
        prompt_manager = get_prompt_manager()
        content = prompt_manager.get_prompt(version)

        return {"version": version, "content": content}

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get prompt content: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve prompt content: {str(e)}"
        )


@router.post("/prompts/reload")
async def reload_prompts():
    """
    Reload all prompts from disk (hot-reload for development)

    Returns:
        Success message with loaded versions
    """
    try:
        prompt_manager = get_prompt_manager()
        prompt_manager.reload()
        versions = prompt_manager.list_versions()

        return {
            "message": "Prompts reloaded successfully",
            "versions": versions,
            "count": len(versions),
        }

    except Exception as e:
        logger.error(f"Failed to reload prompts: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to reload prompts: {str(e)}"
        )
