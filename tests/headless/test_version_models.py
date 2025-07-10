"""
Test suite for headless version models.

Tests for version-specific response models and factory functions.
"""

import json
import pytest
from unittest.mock import Mock

from pieces.headless.models.version import create_version_success
from pieces.headless.models.base import SuccessResponse


class TestVersionSuccess:
    """Test create_version_success function."""

    def test_create_version_success_basic(self):
        """Test basic version success response creation."""
        response = create_version_success(
            cli_version="1.0.0",
            pieces_os_version="2.0.0"
        )
        
        assert isinstance(response, SuccessResponse)
        assert response.success is True
        assert response.command == "version"
        
        expected_data = {
            "cli_version": "1.0.0",
            "pieces_os_version": "2.0.0"
        }
        assert response.data == expected_data

    def test_create_version_success_different_versions(self):
        """Test version success response with different version strings."""
        test_cases = [
            ("1.0.0", "2.0.0"),
            ("1.2.3", "2.4.6"),
            ("0.1.0-alpha", "1.0.0-beta"),
            ("1.0.0-rc.1", "2.0.0-rc.2"),
            ("dev", "dev"),
        ]
        
        for cli_version, pieces_os_version in test_cases:
            response = create_version_success(
                cli_version=cli_version,
                pieces_os_version=pieces_os_version
            )
            
            assert response.data["cli_version"] == cli_version
            assert response.data["pieces_os_version"] == pieces_os_version

    def test_create_version_success_semantic_versions(self):
        """Test version success response with semantic version strings."""
        response = create_version_success(
            cli_version="1.2.3",
            pieces_os_version="2.4.6"
        )
        
        assert response.data["cli_version"] == "1.2.3"
        assert response.data["pieces_os_version"] == "2.4.6"

    def test_create_version_success_prerelease_versions(self):
        """Test version success response with pre-release versions."""
        response = create_version_success(
            cli_version="1.0.0-alpha.1",
            pieces_os_version="2.0.0-beta.2"
        )
        
        assert response.data["cli_version"] == "1.0.0-alpha.1"
        assert response.data["pieces_os_version"] == "2.0.0-beta.2"

    def test_create_version_success_build_metadata(self):
        """Test version success response with build metadata."""
        response = create_version_success(
            cli_version="1.0.0+build.123",
            pieces_os_version="2.0.0+build.456"
        )
        
        assert response.data["cli_version"] == "1.0.0+build.123"
        assert response.data["pieces_os_version"] == "2.0.0+build.456"

    def test_create_version_success_development_versions(self):
        """Test version success response with development versions."""
        response = create_version_success(
            cli_version="dev",
            pieces_os_version="nightly"
        )
        
        assert response.data["cli_version"] == "dev"
        assert response.data["pieces_os_version"] == "nightly"

    def test_create_version_success_empty_versions(self):
        """Test version success response with empty version strings."""
        response = create_version_success(
            cli_version="",
            pieces_os_version=""
        )
        
        assert response.data["cli_version"] == ""
        assert response.data["pieces_os_version"] == ""

    def test_create_version_success_mixed_versions(self):
        """Test version success response with mixed version formats."""
        response = create_version_success(
            cli_version="1.2.3",
            pieces_os_version="dev"
        )
        
        assert response.data["cli_version"] == "1.2.3"
        assert response.data["pieces_os_version"] == "dev"

    def test_create_version_success_json_serialization(self):
        """Test that version success response can be serialized to JSON."""
        response = create_version_success(
            cli_version="1.2.3",
            pieces_os_version="2.4.6"
        )
        
        json_str = response.to_json()
        parsed = json.loads(json_str)
        
        assert parsed["success"] is True
        assert parsed["command"] == "version"
        assert parsed["data"]["cli_version"] == "1.2.3"
        assert parsed["data"]["pieces_os_version"] == "2.4.6"

    def test_create_version_success_json_with_indent(self):
        """Test that version success response can be serialized with indentation."""
        response = create_version_success(
            cli_version="1.2.3",
            pieces_os_version="2.4.6"
        )
        
        json_str = response.to_json(indent=2)
        parsed = json.loads(json_str)
        
        # Should contain newlines and indentation
        assert "\n" in json_str
        assert "  " in json_str
        
        # Should still be valid JSON with correct data
        assert parsed["success"] is True
        assert parsed["command"] == "version"
        assert parsed["data"]["cli_version"] == "1.2.3"
        assert parsed["data"]["pieces_os_version"] == "2.4.6"

    def test_create_version_success_to_dict(self):
        """Test that version success response can be converted to dict."""
        response = create_version_success(
            cli_version="1.2.3",
            pieces_os_version="2.4.6"
        )
        
        result_dict = response.to_dict()
        expected = {
            "success": True,
            "command": "version",
            "data": {
                "cli_version": "1.2.3",
                "pieces_os_version": "2.4.6"
            }
        }
        
        assert result_dict == expected

    def test_create_version_success_unicode_versions(self):
        """Test version success response with unicode characters."""
        response = create_version_success(
            cli_version="1.0.0-测试",
            pieces_os_version="2.0.0-β"
        )
        
        assert response.data["cli_version"] == "1.0.0-测试"
        assert response.data["pieces_os_version"] == "2.0.0-β"
        
        # Should serialize to JSON properly
        json_str = response.to_json()
        parsed = json.loads(json_str)
        assert parsed["data"]["cli_version"] == "1.0.0-测试"
        assert parsed["data"]["pieces_os_version"] == "2.0.0-β"

    def test_create_version_success_special_characters(self):
        """Test version success response with special characters."""
        response = create_version_success(
            cli_version="1.0.0-alpha+build.123",
            pieces_os_version="2.0.0-beta.2+exp.sha.5114f85"
        )
        
        assert response.data["cli_version"] == "1.0.0-alpha+build.123"
        assert response.data["pieces_os_version"] == "2.0.0-beta.2+exp.sha.5114f85"

    def test_create_version_success_long_versions(self):
        """Test version success response with long version strings."""
        long_cli_version = "1.2.3-alpha.1+build.123.abcdef1234567890"
        long_pieces_os_version = "2.4.6-beta.2+build.456.fedcba0987654321"
        
        response = create_version_success(
            cli_version=long_cli_version,
            pieces_os_version=long_pieces_os_version
        )
        
        assert response.data["cli_version"] == long_cli_version
        assert response.data["pieces_os_version"] == long_pieces_os_version

    def test_create_version_success_none_versions(self):
        """Test version success response with None values."""
        response = create_version_success(
            cli_version=None,
            pieces_os_version=None
        )
        
        assert response.data["cli_version"] is None
        assert response.data["pieces_os_version"] is None
        
        # Should serialize to JSON properly
        json_str = response.to_json()
        parsed = json.loads(json_str)
        assert parsed["data"]["cli_version"] is None
        assert parsed["data"]["pieces_os_version"] is None

    def test_create_version_success_mixed_none_values(self):
        """Test version success response with mixed None values."""
        response = create_version_success(
            cli_version="1.2.3",
            pieces_os_version=None
        )
        
        assert response.data["cli_version"] == "1.2.3"
        assert response.data["pieces_os_version"] is None

    def test_create_version_success_inheritance(self):
        """Test that version success response inherits from SuccessResponse."""
        response = create_version_success(
            cli_version="1.2.3",
            pieces_os_version="2.4.6"
        )
        
        assert isinstance(response, SuccessResponse)
        assert response.success is True
        assert response.command == "version"

    def test_create_version_success_data_structure(self):
        """Test that version success response has correct data structure."""
        response = create_version_success(
            cli_version="1.2.3",
            pieces_os_version="2.4.6"
        )
        
        # Should have exactly two keys in data
        assert len(response.data) == 2
        assert "cli_version" in response.data
        assert "pieces_os_version" in response.data

    def test_create_version_success_immutability(self):
        """Test that version success response data is not accidentally mutable."""
        response = create_version_success(
            cli_version="1.2.3",
            pieces_os_version="2.4.6"
        )
        
        original_data = response.data.copy()
        
        # Modifying response.data should not affect the original
        response.data["cli_version"] = "modified"
        
        # Create a new response to verify the factory still works correctly
        new_response = create_version_success(
            cli_version="1.2.3",
            pieces_os_version="2.4.6"
        )
        
        assert new_response.data["cli_version"] == "1.2.3"
        assert new_response.data["pieces_os_version"] == "2.4.6"

    def test_create_version_success_consistent_output(self):
        """Test that version success response produces consistent output."""
        # Create multiple responses with same data
        response1 = create_version_success(
            cli_version="1.2.3",
            pieces_os_version="2.4.6"
        )
        
        response2 = create_version_success(
            cli_version="1.2.3",
            pieces_os_version="2.4.6"
        )
        
        # Should produce identical output
        assert response1.to_json() == response2.to_json()
        assert response1.to_dict() == response2.to_dict()
        assert response1.data == response2.data

    def test_create_version_success_parameter_types(self):
        """Test version success response with different parameter types."""
        # Test with string representations of numbers
        response = create_version_success(
            cli_version=str(1.23),
            pieces_os_version=str(2.46)
        )
        
        assert response.data["cli_version"] == "1.23"
        assert response.data["pieces_os_version"] == "2.46" 