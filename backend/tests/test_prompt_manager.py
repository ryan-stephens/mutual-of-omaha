"""
Unit tests for PromptManager service
"""

import pytest
from pathlib import Path
from app.services.prompt_manager import PromptManager


class TestPromptManager:
    """Test suite for PromptManager"""
    
    def test_get_default_prompt(self):
        """Test retrieving default prompt version"""
        pm = PromptManager()
        prompt = pm.get_prompt()
        
        assert prompt is not None
        assert isinstance(prompt, str)
        assert len(prompt) > 0
    
    def test_get_specific_version(self):
        """Test retrieving specific prompt version"""
        pm = PromptManager()
        prompt = pm.get_prompt("v1.0.0")
        
        assert prompt is not None
        assert "medical data extraction" in prompt.lower()
    
    def test_list_versions(self):
        """Test listing available prompt versions"""
        pm = PromptManager()
        versions = pm.list_versions()
        
        assert isinstance(versions, list)
        assert len(versions) >= 3  # We have v1.0.0, v1.1.0, v2.0.0
        assert "v1.0.0" in versions
        assert "v2.0.0" in versions
    
    def test_get_version_metadata(self):
        """Test retrieving prompt metadata"""
        pm = PromptManager()
        metadata = pm.get_version_metadata("v2.0.0")
        
        assert metadata["version"] == "v2.0.0"
        assert metadata["is_default"] == True
        assert metadata["length_chars"] > 0
        assert metadata["length_tokens_estimate"] > 0
    
    def test_format_prompt(self):
        """Test prompt formatting with document text"""
        pm = PromptManager()
        document_text = "Patient: John Doe\nDOB: 1980-01-01"
        
        formatted = pm.format_prompt(document_text, "v1.0.0")
        
        assert document_text in formatted
        assert len(formatted) > len(document_text)
    
    def test_invalid_version_raises_error(self):
        """Test that invalid version raises ValueError"""
        pm = PromptManager()
        
        with pytest.raises(ValueError) as exc_info:
            pm.get_prompt("v999.0.0")
        
        assert "not found" in str(exc_info.value).lower()
    
    def test_prompt_contains_placeholder(self):
        """Test that prompts contain required placeholder"""
        pm = PromptManager()
        
        for version in pm.list_versions():
            prompt = pm.get_prompt(version)
            # Check if prompt can be formatted (has placeholder)
            try:
                formatted = pm.format_prompt("test", version)
                assert "test" in formatted
            except KeyError:
                pytest.fail(f"Prompt {version} missing {{document_text}} placeholder")
