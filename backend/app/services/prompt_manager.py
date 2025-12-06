"""
Prompt Manager Service

Handles versioned prompts for medical data extraction.
Supports A/B testing, rollback, and experimentation.
"""

import os
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PromptManager:
    """Manages versioned prompts and provides A/B testing capabilities."""

    DEFAULT_VERSION = "v2.0.0"
    PROMPTS_DIR = Path(__file__).parent.parent.parent / "prompts"

    def __init__(self):
        self._cache: Dict[str, str] = {}
        self._load_available_versions()

    def _load_available_versions(self) -> None:
        """Scan prompts directory and cache available versions."""
        if not self.PROMPTS_DIR.exists():
            logger.error(f"Prompts directory not found: {self.PROMPTS_DIR}")
            raise FileNotFoundError(f"Prompts directory not found: {self.PROMPTS_DIR}")

        for file in self.PROMPTS_DIR.glob("v*.txt"):
            version = file.stem
            self._cache[version] = file.read_text(encoding="utf-8")
            logger.info(f"Loaded prompt version: {version}")

        if not self._cache:
            logger.error("No prompt versions found in prompts directory")
            raise ValueError("No prompt versions found")

        logger.info(f"Available prompt versions: {list(self._cache.keys())}")

    def get_prompt(self, version: Optional[str] = None) -> str:
        """
        Get a specific prompt version.

        Args:
            version: Prompt version (e.g., "v1.0.0"). Uses DEFAULT_VERSION if None.

        Returns:
            Prompt template string

        Raises:
            ValueError: If version not found
        """
        version = version or self.DEFAULT_VERSION

        if version not in self._cache:
            available = ", ".join(self._cache.keys())
            raise ValueError(
                f"Prompt version '{version}' not found. " f"Available versions: {available}"
            )

        logger.info(f"Retrieved prompt version: {version}")
        return self._cache[version]

    def list_versions(self) -> List[str]:
        """Get list of available prompt versions."""
        return sorted(self._cache.keys(), reverse=True)

    def get_version_metadata(self, version: str) -> Dict[str, any]:
        """
        Get metadata about a prompt version.

        Args:
            version: Prompt version

        Returns:
            Metadata dictionary with version info
        """
        if version not in self._cache:
            raise ValueError(f"Version '{version}' not found")

        prompt_text = self._cache[version]

        return {
            "version": version,
            "is_default": version == self.DEFAULT_VERSION,
            "length_chars": len(prompt_text),
            "length_tokens_estimate": len(prompt_text) // 4,  # Rough estimate
            "available_since": self._get_file_creation_time(version),
        }

    def _get_file_creation_time(self, version: str) -> str:
        """Get file creation timestamp."""
        file_path = self.PROMPTS_DIR / f"{version}.txt"
        if file_path.exists():
            timestamp = os.path.getctime(file_path)
            return datetime.fromtimestamp(timestamp).isoformat()
        return "unknown"

    def format_prompt(self, document_text: str, version: Optional[str] = None) -> str:
        """
        Format a prompt with document text.

        Args:
            document_text: Medical document content
            version: Prompt version to use

        Returns:
            Formatted prompt ready for model
        """
        template = self.get_prompt(version)

        if "{document_text}" not in template:
            logger.warning(f"Prompt version {version} missing {{document_text}} placeholder")
            return template

        # Use replace() instead of format() to avoid issues with JSON curly braces
        return template.replace("{document_text}", document_text)

    def reload(self) -> None:
        """Reload all prompts from disk (useful for hot-reloading)."""
        self._cache.clear()
        self._load_available_versions()
        logger.info("Prompt cache reloaded")


# Global instance
_prompt_manager: Optional[PromptManager] = None


def get_prompt_manager() -> PromptManager:
    """Get or create global PromptManager instance."""
    global _prompt_manager
    if _prompt_manager is None:
        _prompt_manager = PromptManager()
    return _prompt_manager
