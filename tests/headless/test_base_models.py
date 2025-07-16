"""
Test suite for headless base models.

Tests for BaseResponse, SuccessResponse, ErrorResponse, CommandResult, and ErrorCode.
"""

import json
import pytest
from unittest.mock import patch, Mock
import sys

from pieces.headless.models.base import (
    BaseResponse,
    SuccessResponse,
    ErrorResponse,
    CommandResult,
    ErrorCode,
)


class TestErrorCode:
    """Test ErrorCode enum values."""

    def test_error_code_values(self):
        """Test that error codes have correct integer values."""
        assert ErrorCode.GENERAL_ERROR == 1
        assert ErrorCode.SERIALIZATION_ERROR == 2
        assert ErrorCode.COMMAND_ERROR == 3
        assert ErrorCode.INVALID_ARGUMENT == 4
        assert ErrorCode.TIMEOUT_ERROR == 5

        assert ErrorCode.PROMPT_REQUIRED == 100
        assert ErrorCode.CONFIRMATION_REQUIRED == 101
        assert ErrorCode.USER_INPUT_REQUIRED == 102
        assert ErrorCode.INTERACTIVE_OPERATION == 103

        assert ErrorCode.PIECES_OS_UPDATE_REQUIRED == 202
        assert ErrorCode.CLI_UPDATE_REQUIRED == 203
        assert ErrorCode.AUTHENTICATION_FAILED == 204
        assert ErrorCode.LTM_NOT_ENABLED == 205

        assert ErrorCode.MCP_SETUP_FAILED == 400
        assert ErrorCode.MCP_START_FAILED == 401
        assert ErrorCode.MCP_REPAIR_FAILED == 402
        assert ErrorCode.MCP_SERVER_NOT_RUNNING == 403

    def test_error_code_type(self):
        """Test that error codes are proper IntEnum instances."""
        assert isinstance(ErrorCode.GENERAL_ERROR, int)
        assert isinstance(ErrorCode.GENERAL_ERROR.value, int)


class TestSuccessResponse:
    """Test SuccessResponse class."""

    def test_success_response_basic(self):
        """Test basic success response creation."""
        response = SuccessResponse(command="test", data={"key": "value"})

        assert response.success is True
        assert response.command == "test"
        assert response.data == {"key": "value"}

    def test_success_response_none_data(self):
        """Test success response with None data."""
        response = SuccessResponse(command="test", data=None)

        assert response.success is True
        assert response.command == "test"
        assert response.data is None

    def test_success_response_to_dict(self):
        """Test success response conversion to dict."""
        response = SuccessResponse(command="test", data={"key": "value"})
        expected = {"success": True, "command": "test", "data": {"key": "value"}}

        assert response.to_dict() == expected

    def test_success_response_to_json(self):
        """Test success response conversion to JSON."""
        response = SuccessResponse(command="test", data={"key": "value"})
        json_str = response.to_json()

        # Parse back to verify it's valid JSON
        parsed = json.loads(json_str)
        expected = {"success": True, "command": "test", "data": {"key": "value"}}

        assert parsed == expected

    def test_success_response_to_json_with_indent(self):
        """Test success response JSON with indentation."""
        response = SuccessResponse(command="test", data={"key": "value"})
        json_str = response.to_json(indent=2)

        # Should contain newlines and spaces when indented
        assert "\n" in json_str
        assert "  " in json_str

        # Should still be valid JSON
        parsed = json.loads(json_str)
        expected = {"success": True, "command": "test", "data": {"key": "value"}}

        assert parsed == expected

    def test_success_response_complex_data(self):
        """Test success response with complex data structures."""
        complex_data = {
            "list": [1, 2, 3],
            "nested": {"inner": "value"},
            "boolean": True,
            "null": None,
        }
        response = SuccessResponse(command="complex", data=complex_data)

        assert response.data == complex_data

        # Verify JSON serialization works
        json_str = response.to_json()
        parsed = json.loads(json_str)
        assert parsed["data"] == complex_data


class TestErrorResponse:
    """Test ErrorResponse class."""

    def test_error_response_basic(self):
        """Test basic error response creation."""
        response = ErrorResponse(
            command="test",
            error_code=ErrorCode.GENERAL_ERROR,
            error_message="Test error",
        )

        assert response.success is False
        assert response.command == "test"
        assert response.data == {"error_type": 1, "error_message": "Test error"}

    def test_error_response_to_dict(self):
        """Test error response conversion to dict."""
        response = ErrorResponse(
            command="test",
            error_code=ErrorCode.PROMPT_REQUIRED,
            error_message="Prompt required",
        )
        expected = {
            "success": False,
            "command": "test",
            "data": {"error_type": 100, "error_message": "Prompt required"},
        }

        assert response.to_dict() == expected

    def test_error_response_to_json(self):
        """Test error response conversion to JSON."""
        response = ErrorResponse(
            command="test",
            error_code=ErrorCode.MCP_SETUP_FAILED,
            error_message="MCP setup failed",
        )
        json_str = response.to_json()

        # Parse back to verify it's valid JSON
        parsed = json.loads(json_str)
        expected = {
            "success": False,
            "command": "test",
            "data": {"error_type": 400, "error_message": "MCP setup failed"},
        }

        assert parsed == expected

    def test_error_response_different_error_codes(self):
        """Test error response with different error codes."""
        test_cases = [
            (ErrorCode.GENERAL_ERROR, 1),
            (ErrorCode.CONFIRMATION_REQUIRED, 101),
            (ErrorCode.CLI_UPDATE_REQUIRED, 203),
            (ErrorCode.MCP_SERVER_NOT_RUNNING, 403),
        ]

        for error_code, expected_value in test_cases:
            response = ErrorResponse(
                command="test", error_code=error_code, error_message="Test message"
            )

            assert response.data["error_type"] == expected_value


class TestCommandResult:
    """Test CommandResult class."""

    def test_command_result_creation(self):
        """Test CommandResult creation."""
        success_response = SuccessResponse(command="test", data={"result": "ok"})
        result = CommandResult(exit_code=0, headless_response=success_response)

        assert result.exit_code == 0
        assert result.headless_response == success_response

    def test_command_result_exit_non_headless(self):
        """Test CommandResult.exit() in non-headless mode."""
        success_response = SuccessResponse(command="test", data={"result": "ok"})
        result = CommandResult(exit_code=0, headless_response=success_response)

        with patch("sys.exit") as mock_exit:
            result.exit(is_headless=False)
            mock_exit.assert_called_once_with(0)

    def test_command_result_exit_headless(self):
        """Test CommandResult.exit() in headless mode."""
        success_response = SuccessResponse(command="test", data={"result": "ok"})
        result = CommandResult(exit_code=0, headless_response=success_response)

        with patch("builtins.print") as mock_print:
            result.exit(is_headless=True)

            # Should print JSON response
            mock_print.assert_called_once()
            printed_output = mock_print.call_args[0][0]

            # Verify it's valid JSON
            parsed = json.loads(printed_output)
            expected = {"success": True, "command": "test", "data": {"result": "ok"}}
            assert parsed == expected

    def test_command_result_exit_headless_error(self):
        """Test CommandResult.exit() with error response in headless mode."""
        error_response = ErrorResponse(
            command="test",
            error_code=ErrorCode.GENERAL_ERROR,
            error_message="Test error",
        )
        result = CommandResult(exit_code=1, headless_response=error_response)

        with patch("builtins.print") as mock_print:
            result.exit(is_headless=True)

            # Should print JSON error response
            mock_print.assert_called_once()
            printed_output = mock_print.call_args[0][0]

            # Verify it's valid JSON
            parsed = json.loads(printed_output)
            expected = {
                "success": False,
                "command": "test",
                "data": {"error_type": 1, "error_message": "Test error"},
            }
            assert parsed == expected


class TestBaseResponse:
    """Test BaseResponse abstract class behavior."""

    def test_base_response_cannot_be_instantiated(self):
        """Test that BaseResponse cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseResponse(success=True, command="test")

    def test_base_response_subclass_must_implement_to_dict(self):
        """Test that BaseResponse subclasses must implement to_dict."""

        class IncompleteResponse(BaseResponse):
            pass

        with pytest.raises(TypeError):
            IncompleteResponse(success=True, command="test")

    def test_base_response_to_json_method(self):
        """Test BaseResponse.to_json() method using a concrete subclass."""
        response = SuccessResponse(command="test", data={"key": "value"})

        # Test default (no indent)
        json_str = response.to_json()
        parsed = json.loads(json_str)
        assert parsed["success"] is True
        assert parsed["command"] == "test"
        assert parsed["data"] == {"key": "value"}

        # Test with indent
        json_str_indented = response.to_json(indent=4)
        parsed_indented = json.loads(json_str_indented)
        assert parsed_indented == parsed
        assert "\n" in json_str_indented

