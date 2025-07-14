"""
Test suite for headless MCP models.

Tests for MCP-specific response models, factory functions, and data structures.
"""

import json
import pytest
from unittest.mock import Mock

from pieces.headless.models.mcp import (
    create_mcp_setup_success,
    MCPListResponse,
    create_mcp_list_success,
    MCPRepairResult,
    create_mcp_repair_success,
)
from pieces.headless.models.base import SuccessResponse


class TestMCPSetupSuccess:
    """Test create_mcp_setup_success function."""

    def test_create_mcp_setup_success_basic(self):
        """Test basic MCP setup success response creation."""
        response = create_mcp_setup_success(
            integration_name="vscode",
            configuration_path="/path/to/config.json",
            instructions="Follow these steps to complete setup",
            setup_type="stdio",
        )

        assert isinstance(response, SuccessResponse)
        assert response.success is True
        assert response.command == "mcp setup"

        expected_data = {
            "integration_name": "vscode",
            "setup_type": "stdio",
            "instructions": "Follow these steps to complete setup",
            "configuration_path": "/path/to/config.json",
            "location_type": "global",
        }
        assert response.data == expected_data

    def test_create_mcp_setup_success_with_sse(self):
        """Test MCP setup success response with SSE setup type."""
        response = create_mcp_setup_success(
            integration_name="cursor",
            configuration_path="/path/to/cursor/config.json",
            instructions="SSE setup instructions",
            setup_type="sse",
        )

        assert response.data["setup_type"] == "sse"
        assert response.data["integration_name"] == "cursor"
        assert response.data["instructions"] == "SSE setup instructions"
        assert response.data["configuration_path"] == "/path/to/cursor/config.json"

    def test_create_mcp_setup_success_none_config_path(self):
        """Test MCP setup success response with None configuration path."""
        response = create_mcp_setup_success(
            integration_name="raycast",
            configuration_path=None,
            instructions="Raycast setup instructions",
            setup_type="stdio",
        )

        assert response.data["configuration_path"] is None
        assert response.data["integration_name"] == "raycast"

    def test_create_mcp_setup_success_default_setup_type(self):
        """Test MCP setup success response with default setup type."""
        response = create_mcp_setup_success(
            integration_name="vscode",
            configuration_path="/path/to/config.json",
            instructions="Default setup instructions",
        )

        # Should default to "stdio"
        assert response.data["setup_type"] == "stdio"

    def test_create_mcp_setup_success_json_serialization(self):
        """Test that MCP setup success response can be serialized to JSON."""
        response = create_mcp_setup_success(
            integration_name="vscode",
            configuration_path="/path/to/config.json",
            instructions="Test instructions",
            setup_type="stdio",
        )

        json_str = response.to_json()
        parsed = json.loads(json_str)

        assert parsed["success"] is True
        assert parsed["command"] == "mcp setup"
        assert parsed["data"]["integration_name"] == "vscode"
        assert parsed["data"]["setup_type"] == "stdio"

    def test_create_mcp_setup_success_different_integrations(self):
        """Test MCP setup success response with different integration names."""
        test_cases = [
            ("vscode", "VSCode setup"),
            ("cursor", "Cursor setup"),
            ("raycast", "Raycast setup"),
            ("warp", "Warp setup"),
        ]

        for integration_name, instructions in test_cases:
            response = create_mcp_setup_success(
                integration_name=integration_name,
                configuration_path=f"/path/to/{integration_name}/config.json",
                instructions=instructions,
                setup_type="stdio",
            )

            assert response.data["integration_name"] == integration_name
            assert response.data["instructions"] == instructions


class TestMCPListResponse:
    """Test MCPListResponse class."""

    def test_mcp_list_response_creation(self):
        """Test MCPListResponse creation."""
        response = MCPListResponse(integration_name="vscode", status="healthy")

        assert response.integration_name == "vscode"
        assert response.status == "healthy"

    def test_mcp_list_response_to_dict(self):
        """Test MCPListResponse to_dict method."""
        response = MCPListResponse(integration_name="cursor", status="needs_repair")

        expected = {"integration_name": "cursor", "status": "needs_repair"}

        assert response.to_dict() == expected

    def test_mcp_list_response_different_statuses(self):
        """Test MCPListResponse with different status values."""
        test_cases = [
            ("vscode", "healthy"),
            ("cursor", "available_to_setup"),
            ("raycast", "needs_repair"),
        ]

        for integration_name, status in test_cases:
            response = MCPListResponse(integration_name=integration_name, status=status)

            assert response.integration_name == integration_name
            assert response.status == status

            # Verify to_dict works correctly
            result_dict = response.to_dict()
            assert result_dict["integration_name"] == integration_name
            assert result_dict["status"] == status

    def test_mcp_list_response_json_serialization(self):
        """Test that MCPListResponse can be serialized via to_dict."""
        response = MCPListResponse(integration_name="vscode", status="healthy")

        dict_result = response.to_dict()

        # Should be JSON serializable
        json_str = json.dumps(dict_result)
        parsed = json.loads(json_str)

        assert parsed["integration_name"] == "vscode"
        assert parsed["status"] == "healthy"


class TestMCPListSuccess:
    """Test create_mcp_list_success function."""

    def test_create_mcp_list_success_basic(self):
        """Test basic MCP list success response creation."""
        integrations = [
            MCPListResponse("vscode", "healthy"),
            MCPListResponse("cursor", "needs_repair"),
        ]

        response = create_mcp_list_success(integrations)

        assert isinstance(response, SuccessResponse)
        assert response.success is True
        assert response.command == "mcp list"

        expected_data = {
            "integrations": [
                {"integration_name": "vscode", "status": "healthy"},
                {"integration_name": "cursor", "status": "needs_repair"},
            ]
        }
        assert response.data == expected_data

    def test_create_mcp_list_success_empty_list(self):
        """Test MCP list success response with empty integration list."""
        response = create_mcp_list_success([])

        assert response.data == {"integrations": []}

    def test_create_mcp_list_success_single_integration(self):
        """Test MCP list success response with single integration."""
        integrations = [MCPListResponse("vscode", "healthy")]

        response = create_mcp_list_success(integrations)

        expected_data = {
            "integrations": [{"integration_name": "vscode", "status": "healthy"}]
        }
        assert response.data == expected_data

    def test_create_mcp_list_success_multiple_integrations(self):
        """Test MCP list success response with multiple integrations."""
        integrations = [
            MCPListResponse("vscode", "healthy"),
            MCPListResponse("cursor", "needs_repair"),
            MCPListResponse("raycast", "available_to_setup"),
        ]

        response = create_mcp_list_success(integrations)

        expected_data = {
            "integrations": [
                {"integration_name": "vscode", "status": "healthy"},
                {"integration_name": "cursor", "status": "needs_repair"},
                {"integration_name": "raycast", "status": "available_to_setup"},
            ]
        }
        assert response.data == expected_data

    def test_create_mcp_list_success_json_serialization(self):
        """Test that MCP list success response can be serialized to JSON."""
        integrations = [
            MCPListResponse("vscode", "healthy"),
            MCPListResponse("cursor", "needs_repair"),
        ]

        response = create_mcp_list_success(integrations)
        json_str = response.to_json()
        parsed = json.loads(json_str)

        assert parsed["success"] is True
        assert parsed["command"] == "mcp list"
        assert len(parsed["data"]["integrations"]) == 2
        assert parsed["data"]["integrations"][0]["integration_name"] == "vscode"
        assert parsed["data"]["integrations"][1]["integration_name"] == "cursor"


class TestMCPRepairResult:
    """Test MCPRepairResult class."""

    def test_mcp_repair_result_creation_basic(self):
        """Test basic MCPRepairResult creation."""
        result = MCPRepairResult(
            integration_name="vscode",
            status="repaired",
            configuration_path="/path/to/config.json",
        )

        assert result.integration_name == "vscode"
        assert result.status == "repaired"
        assert result.configuration_path == "/path/to/config.json"

    def test_mcp_repair_result_creation_without_config_path(self):
        """Test MCPRepairResult creation without configuration path."""
        result = MCPRepairResult(integration_name="cursor", status="failed")

        assert result.integration_name == "cursor"
        assert result.status == "failed"
        assert result.configuration_path is None

    def test_mcp_repair_result_to_dict_with_config_path(self):
        """Test MCPRepairResult to_dict with configuration path."""
        result = MCPRepairResult(
            integration_name="vscode",
            status="repaired",
            configuration_path="/path/to/config.json",
        )

        expected = {
            "integration_name": "vscode",
            "status": "repaired",
            "configuration_path": "/path/to/config.json",
        }

        assert result.to_dict() == expected

    def test_mcp_repair_result_to_dict_without_config_path(self):
        """Test MCPRepairResult to_dict without configuration path."""
        result = MCPRepairResult(integration_name="cursor", status="failed")

        expected = {"integration_name": "cursor", "status": "failed"}

        assert result.to_dict() == expected

    def test_mcp_repair_result_different_statuses(self):
        """Test MCPRepairResult with different status values."""
        test_cases = [
            ("vscode", "repaired", "/path/to/vscode/config.json"),
            ("cursor", "healthy", "/path/to/cursor/config.json"),
            ("raycast", "failed", None),
        ]

        for integration_name, status, config_path in test_cases:
            result = MCPRepairResult(
                integration_name=integration_name,
                status=status,
                configuration_path=config_path,
            )

            assert result.integration_name == integration_name
            assert result.status == status
            assert result.configuration_path == config_path

    def test_mcp_repair_result_json_serialization(self):
        """Test that MCPRepairResult can be serialized via to_dict."""
        result = MCPRepairResult(
            integration_name="vscode",
            status="repaired",
            configuration_path="/path/to/config.json",
        )

        dict_result = result.to_dict()

        # Should be JSON serializable
        json_str = json.dumps(dict_result)
        parsed = json.loads(json_str)

        assert parsed["integration_name"] == "vscode"
        assert parsed["status"] == "repaired"
        assert parsed["configuration_path"] == "/path/to/config.json"


class TestMCPRepairSuccess:
    """Test create_mcp_repair_success function."""

    def test_create_mcp_repair_success_basic(self):
        """Test basic MCP repair success response creation."""
        repair_results = [
            MCPRepairResult("vscode", "repaired", "/path/to/vscode/config.json"),
            MCPRepairResult("cursor", "healthy", "/path/to/cursor/config.json"),
            MCPRepairResult("raycast", "failed", None),
        ]

        response = create_mcp_repair_success(repair_results)

        assert isinstance(response, SuccessResponse)
        assert response.success is True
        assert response.command == "mcp repair"

        expected_data = {
            "repairs": [
                {
                    "integration_name": "vscode",
                    "status": "repaired",
                    "configuration_path": "/path/to/vscode/config.json",
                },
                {
                    "integration_name": "cursor",
                    "status": "healthy",
                    "configuration_path": "/path/to/cursor/config.json",
                },
                {"integration_name": "raycast", "status": "failed"},
            ],
            "summary": {"total": 3, "repaired": 1, "healthy": 1, "failed": 1},
        }
        assert response.data == expected_data

    def test_create_mcp_repair_success_empty_results(self):
        """Test MCP repair success response with empty results."""
        response = create_mcp_repair_success([])

        expected_data = {
            "repairs": [],
            "summary": {"total": 0, "repaired": 0, "healthy": 0, "failed": 0},
        }
        assert response.data == expected_data

    def test_create_mcp_repair_success_single_result(self):
        """Test MCP repair success response with single result."""
        repair_results = [MCPRepairResult("vscode", "repaired", "/path/to/config.json")]

        response = create_mcp_repair_success(repair_results)

        expected_data = {
            "repairs": [
                {
                    "integration_name": "vscode",
                    "status": "repaired",
                    "configuration_path": "/path/to/config.json",
                }
            ],
            "summary": {"total": 1, "repaired": 1, "healthy": 0, "failed": 0},
        }
        assert response.data == expected_data

    def test_create_mcp_repair_success_all_statuses(self):
        """Test MCP repair success response with all possible statuses."""
        repair_results = [
            MCPRepairResult("vscode", "repaired", "/path/to/vscode/config.json"),
            MCPRepairResult("cursor", "repaired", "/path/to/cursor/config.json"),
            MCPRepairResult("raycast", "healthy", None),
            MCPRepairResult("warp", "healthy", "/path/to/warp/config.json"),
            MCPRepairResult("other", "failed", None),
        ]

        response = create_mcp_repair_success(repair_results)

        expected_summary = {"total": 5, "repaired": 2, "healthy": 2, "failed": 1}

        assert response.data["summary"] == expected_summary

    def test_create_mcp_repair_success_summary_calculation(self):
        """Test that summary counts are calculated correctly."""
        repair_results = [
            MCPRepairResult("integration1", "repaired", "/path1"),
            MCPRepairResult("integration2", "repaired", "/path2"),
            MCPRepairResult("integration3", "repaired", "/path3"),
            MCPRepairResult("integration4", "healthy", "/path4"),
            MCPRepairResult("integration5", "healthy", "/path5"),
            MCPRepairResult("integration6", "failed", None),
        ]

        response = create_mcp_repair_success(repair_results)

        assert response.data["summary"]["total"] == 6
        assert response.data["summary"]["repaired"] == 3
        assert response.data["summary"]["healthy"] == 2
        assert response.data["summary"]["failed"] == 1

    def test_create_mcp_repair_success_json_serialization(self):
        """Test that MCP repair success response can be serialized to JSON."""
        repair_results = [
            MCPRepairResult("vscode", "repaired", "/path/to/config.json"),
            MCPRepairResult("cursor", "failed", None),
        ]

        response = create_mcp_repair_success(repair_results)
        json_str = response.to_json()
        parsed = json.loads(json_str)

        assert parsed["success"] is True
        assert parsed["command"] == "mcp repair"
        assert len(parsed["data"]["repairs"]) == 2
        assert parsed["data"]["summary"]["total"] == 2
        assert parsed["data"]["summary"]["repaired"] == 1
        assert parsed["data"]["summary"]["failed"] == 1

    def test_create_mcp_repair_success_all_repaired(self):
        """Test MCP repair success response when all integrations are repaired."""
        repair_results = [
            MCPRepairResult("vscode", "repaired", "/path/to/vscode/config.json"),
            MCPRepairResult("cursor", "repaired", "/path/to/cursor/config.json"),
        ]

        response = create_mcp_repair_success(repair_results)

        expected_summary = {"total": 2, "repaired": 2, "healthy": 0, "failed": 0}

        assert response.data["summary"] == expected_summary

    def test_create_mcp_repair_success_all_healthy(self):
        """Test MCP repair success response when all integrations are healthy."""
        repair_results = [
            MCPRepairResult("vscode", "healthy", "/path/to/vscode/config.json"),
            MCPRepairResult("cursor", "healthy", "/path/to/cursor/config.json"),
        ]

        response = create_mcp_repair_success(repair_results)

        expected_summary = {"total": 2, "repaired": 0, "healthy": 2, "failed": 0}

        assert response.data["summary"] == expected_summary

    def test_create_mcp_repair_success_all_failed(self):
        """Test MCP repair success response when all integrations failed."""
        repair_results = [
            MCPRepairResult("vscode", "failed", None),
            MCPRepairResult("cursor", "failed", None),
        ]

        response = create_mcp_repair_success(repair_results)

        expected_summary = {"total": 2, "repaired": 0, "healthy": 0, "failed": 2}

        assert response.data["summary"] == expected_summary


class TestMCPModelsIntegration:
    """Test integration between MCP models and base response classes."""

    def test_mcp_models_return_success_responses(self):
        """Test that all MCP factory functions return SuccessResponse instances."""
        # Test setup success
        setup_response = create_mcp_setup_success(
            integration_name="vscode",
            configuration_path="/path/to/config.json",
            instructions="Instructions",
            setup_type="stdio",
        )
        assert isinstance(setup_response, SuccessResponse)

        # Test list success
        list_response = create_mcp_list_success([MCPListResponse("vscode", "healthy")])
        assert isinstance(list_response, SuccessResponse)

        # Test repair success
        repair_response = create_mcp_repair_success(
            [MCPRepairResult("vscode", "repaired", "/path/to/config.json")]
        )
        assert isinstance(repair_response, SuccessResponse)

    def test_mcp_models_have_correct_command_names(self):
        """Test that MCP models have correct command names."""
        # Test setup command
        setup_response = create_mcp_setup_success(
            integration_name="vscode",
            configuration_path="/path/to/config.json",
            instructions="Instructions",
        )
        assert setup_response.command == "mcp setup"

        # Test list command
        list_response = create_mcp_list_success([])
        assert list_response.command == "mcp list"

        # Test repair command
        repair_response = create_mcp_repair_success([])
        assert repair_response.command == "mcp repair"

    def test_mcp_models_json_output_format(self):
        """Test that MCP models produce consistently formatted JSON."""
        # Test that all responses follow the same JSON structure
        responses = [
            create_mcp_setup_success("vscode", "/path", "instructions"),
            create_mcp_list_success([MCPListResponse("vscode", "healthy")]),
            create_mcp_repair_success([MCPRepairResult("vscode", "repaired", "/path")]),
        ]

        for response in responses:
            json_str = response.to_json()
            parsed = json.loads(json_str)

            # All should have the same top-level structure
            assert "success" in parsed
            assert "command" in parsed
            assert "data" in parsed

            assert parsed["success"] is True
            assert parsed["command"].startswith("mcp ")
            assert isinstance(parsed["data"], dict)
