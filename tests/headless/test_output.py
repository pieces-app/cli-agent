"""
Test suite for headless output functionality.

Tests for HeadlessOutput class including JSON formatting, error output, and exception handling.
"""

import json
import pytest
from unittest.mock import patch, Mock
from io import StringIO

from pieces.headless.output import HeadlessOutput
from pieces.headless.models.base import (
    SuccessResponse,
    ErrorResponse,
    ErrorCode,
)
from pieces.headless.exceptions import (
    HeadlessError,
    HeadlessPromptError,
    HeadlessConfirmationError,
    HeadlessInteractiveOperationError,
)


class TestHeadlessOutput:
    """Test HeadlessOutput class methods."""

    def test_output_response_success(self):
        """Test outputting a success response."""
        response = SuccessResponse(command="test", data={"result": "success"})

        with patch("builtins.print") as mock_print:
            HeadlessOutput.output_response(response)

            mock_print.assert_called_once()
            printed_output = mock_print.call_args[0][0]

            # Verify it's valid JSON
            parsed = json.loads(printed_output)
            expected = {
                "success": True,
                "command": "test",
                "data": {"result": "success"},
            }
            assert parsed == expected

    def test_output_response_error(self):
        """Test outputting an error response."""
        response = ErrorResponse(
            command="test",
            error_code=ErrorCode.GENERAL_ERROR,
            error_message="Test error",
        )

        with patch("builtins.print") as mock_print:
            HeadlessOutput.output_response(response)

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

    def test_output_response_with_indent(self):
        """Test outputting response with custom indentation."""
        response = SuccessResponse(command="test", data={"key": "value"})

        with patch("builtins.print") as mock_print:
            HeadlessOutput.output_response(response, indent=4)

            mock_print.assert_called_once()
            printed_output = mock_print.call_args[0][0]

            # Should contain newlines and 4-space indentation
            assert "\n" in printed_output
            assert "    " in printed_output

            # Should still be valid JSON
            parsed = json.loads(printed_output)
            expected = {"success": True, "command": "test", "data": {"key": "value"}}
            assert parsed == expected

    def test_output_response_no_indent(self):
        """Test outputting response without indentation."""
        response = SuccessResponse(command="test", data={"key": "value"})

        with patch("builtins.print") as mock_print:
            HeadlessOutput.output_response(response, indent=None)

            mock_print.assert_called_once()
            printed_output = mock_print.call_args[0][0]

            # Should not contain newlines when no indent
            assert "\n" not in printed_output

            # Should still be valid JSON
            parsed = json.loads(printed_output)
            expected = {"success": True, "command": "test", "data": {"key": "value"}}
            assert parsed == expected

    def test_output_response_serialization_error(self):
        """Test handling serialization errors in output_response."""
        # Create a mock response that fails to serialize
        mock_response = Mock()
        mock_response.to_json.side_effect = Exception("Serialization failed")

        with patch("builtins.print") as mock_print:
            HeadlessOutput.output_response(mock_response)

            mock_print.assert_called_once()
            printed_output = mock_print.call_args[0][0]

            # Should output a fallback error response
            parsed = json.loads(printed_output)
            assert parsed["success"] is False
            assert parsed["command"] == "unknown"
            assert parsed["data"]["error_type"] == ErrorCode.SERIALIZATION_ERROR
            assert "Failed to serialize response" in parsed["data"]["error_message"]

    def test_output_error_basic(self):
        """Test basic error output."""
        with patch("builtins.print") as mock_print:
            HeadlessOutput.output_error(
                command="test_command",
                error_code=ErrorCode.GENERAL_ERROR,
                error_message="Test error message",
            )

            mock_print.assert_called_once()
            printed_output = mock_print.call_args[0][0]

            # Verify it's valid JSON
            parsed = json.loads(printed_output)
            expected = {
                "success": False,
                "command": "test_command",
                "data": {"error_type": 1, "error_message": "Test error message"},
            }
            assert parsed == expected

    def test_output_error_with_defaults(self):
        """Test error output with default values."""
        with patch("builtins.print") as mock_print:
            HeadlessOutput.output_error(command="test_command")

            mock_print.assert_called_once()
            printed_output = mock_print.call_args[0][0]

            # Verify it's valid JSON with defaults
            parsed = json.loads(printed_output)
            expected = {
                "success": False,
                "command": "test_command",
                "data": {
                    "error_type": ErrorCode.GENERAL_ERROR,
                    "error_message": "An error occurred",
                },
            }
            assert parsed == expected

    def test_output_error_different_error_codes(self):
        """Test error output with different error codes."""
        test_cases = [
            (ErrorCode.PROMPT_REQUIRED, "Prompt required"),
            (ErrorCode.CONFIRMATION_REQUIRED, "Confirmation required"),
            (ErrorCode.MCP_SETUP_FAILED, "MCP setup failed"),
            (ErrorCode.LTM_NOT_ENABLED, "LTM not enabled"),
        ]

        for error_code, error_message in test_cases:
            with patch("builtins.print") as mock_print:
                HeadlessOutput.output_error(
                    command="test", error_code=error_code, error_message=error_message
                )

                mock_print.assert_called_once()
                printed_output = mock_print.call_args[0][0]

                # Verify correct error code is used
                parsed = json.loads(printed_output)
                assert parsed["data"]["error_type"] == error_code
                assert parsed["data"]["error_message"] == error_message

    def test_output_headless_error_basic(self):
        """Test outputting a headless error."""
        error = HeadlessError(
            message="Test headless error", error_code=ErrorCode.PROMPT_REQUIRED
        )

        with patch("builtins.print") as mock_print:
            HeadlessOutput.output_headless_error(error, command="test_command")

            mock_print.assert_called_once()
            printed_output = mock_print.call_args[0][0]

            # Verify it's valid JSON
            parsed = json.loads(printed_output)
            expected = {
                "success": False,
                "command": "test_command",
                "data": {
                    "error_type": ErrorCode.PROMPT_REQUIRED,
                    "error_message": "Test headless error",
                },
            }
            assert parsed == expected

    def test_output_headless_error_with_default_command(self):
        """Test outputting a headless error with default command."""
        error = HeadlessError(message="Test error", error_code=ErrorCode.GENERAL_ERROR)

        with patch("builtins.print") as mock_print:
            HeadlessOutput.output_headless_error(error)

            mock_print.assert_called_once()
            printed_output = mock_print.call_args[0][0]

            # Should use "unknown" as default command
            parsed = json.loads(printed_output)
            assert parsed["command"] == "unknown"

    def test_output_headless_error_specific_types(self):
        """Test outputting specific types of headless errors."""
        test_cases = [
            (HeadlessPromptError(), ErrorCode.PROMPT_REQUIRED),
            (HeadlessConfirmationError(), ErrorCode.CONFIRMATION_REQUIRED),
            (
                HeadlessInteractiveOperationError("test"),
                ErrorCode.INTERACTIVE_OPERATION,
            ),
        ]

        for error, expected_code in test_cases:
            with patch("builtins.print") as mock_print:
                HeadlessOutput.output_headless_error(error, command="test")

                mock_print.assert_called_once()
                printed_output = mock_print.call_args[0][0]

                # Verify correct error code is used
                parsed = json.loads(printed_output)
                assert parsed["data"]["error_type"] == expected_code

    def test_handle_exception_headless_error(self):
        """Test handling HeadlessError exceptions."""
        error = HeadlessError(
            message="Test headless error", error_code=ErrorCode.CONFIRMATION_REQUIRED
        )

        with patch("builtins.print") as mock_print:
            HeadlessOutput.handle_exception(error, command_name="test_command")

            mock_print.assert_called_once()
            printed_output = mock_print.call_args[0][0]

            # Should output as headless error
            parsed = json.loads(printed_output)
            expected = {
                "success": False,
                "command": "test_command",
                "data": {
                    "error_type": ErrorCode.CONFIRMATION_REQUIRED,
                    "error_message": "Test headless error",
                },
            }
            assert parsed == expected

    def test_handle_exception_general_exception(self):
        """Test handling general exceptions."""
        error = ValueError("Test general error")

        with patch("builtins.print") as mock_print:
            HeadlessOutput.handle_exception(error, command_name="test_command")

            mock_print.assert_called_once()
            printed_output = mock_print.call_args[0][0]

            # Should output as command error
            parsed = json.loads(printed_output)
            expected = {
                "success": False,
                "command": "test_command",
                "data": {
                    "error_type": ErrorCode.COMMAND_ERROR,
                    "error_message": "Command 'test_command' failed: Test general error",
                },
            }
            assert parsed == expected

    def test_handle_exception_with_default_command(self):
        """Test handling exceptions with default command name."""
        error = RuntimeError("Test runtime error")

        with patch("builtins.print") as mock_print:
            HeadlessOutput.handle_exception(error)

            mock_print.assert_called_once()
            printed_output = mock_print.call_args[0][0]

            # Should use "unknown" as default command
            parsed = json.loads(printed_output)
            assert parsed["command"] == "unknown"
            assert (
                "Command 'unknown' failed: Test runtime error"
                in parsed["data"]["error_message"]
            )

    def test_handle_exception_different_exception_types(self):
        """Test handling different types of exceptions."""
        test_cases = [
            (ValueError("Value error"), "Value error"),
            (RuntimeError("Runtime error"), "Runtime error"),
            (TypeError("Type error"), "Type error"),
            (KeyError("Key error"), "Key error"),
        ]

        for exception, expected_message in test_cases:
            with patch("builtins.print") as mock_print:
                HeadlessOutput.handle_exception(exception, command_name="test")

                mock_print.assert_called_once()
                printed_output = mock_print.call_args[0][0]

                # Verify error message contains exception message
                parsed = json.loads(printed_output)
                assert expected_message in parsed["data"]["error_message"]
                assert parsed["data"]["error_type"] == ErrorCode.COMMAND_ERROR

    def test_handle_exception_specific_headless_errors(self):
        """Test handling specific headless error types."""
        test_cases = [
            HeadlessPromptError(),
            HeadlessConfirmationError(),
            HeadlessInteractiveOperationError("menu"),
        ]

        for error in test_cases:
            with patch("builtins.print") as mock_print:
                HeadlessOutput.handle_exception(error, command_name="test")

                mock_print.assert_called_once()
                printed_output = mock_print.call_args[0][0]

                # Should be handled as headless error
                parsed = json.loads(printed_output)
                assert parsed["success"] is False
                assert parsed["command"] == "test"
                assert parsed["data"]["error_type"] == error.error_code

    def test_output_response_complex_data(self):
        """Test outputting response with complex data structures."""
        complex_data = {
            "list": [1, 2, 3, {"nested": "value"}],
            "dict": {"a": 1, "b": 2},
            "boolean": True,
            "null": None,
            "string": "test",
            "unicode": "Hello 世界",
        }

        response = SuccessResponse(command="complex_test", data=complex_data)

        with patch("builtins.print") as mock_print:
            HeadlessOutput.output_response(response)

            mock_print.assert_called_once()
            printed_output = mock_print.call_args[0][0]

            # Should handle complex data correctly
            parsed = json.loads(printed_output)
            assert parsed["data"] == complex_data

    def test_output_response_empty_data(self):
        """Test outputting response with empty data."""
        response = SuccessResponse(command="empty_test", data={})

        with patch("builtins.print") as mock_print:
            HeadlessOutput.output_response(response)

            mock_print.assert_called_once()
            printed_output = mock_print.call_args[0][0]

            # Should handle empty data correctly
            parsed = json.loads(printed_output)
            assert parsed["data"] == {}

    def test_output_response_none_data(self):
        """Test outputting response with None data."""
        response = SuccessResponse(command="none_test", data=None)

        with patch("builtins.print") as mock_print:
            HeadlessOutput.output_response(response)

            mock_print.assert_called_once()
            printed_output = mock_print.call_args[0][0]

            # Should handle None data correctly
            parsed = json.loads(printed_output)
            assert parsed["data"] is None

    def test_output_methods_call_each_other_correctly(self):
        """Test that output methods call each other correctly."""
        # Test that output_headless_error calls output_error
        error = HeadlessError(message="Test error", error_code=ErrorCode.GENERAL_ERROR)

        with patch.object(HeadlessOutput, "output_error") as mock_output_error:
            HeadlessOutput.output_headless_error(error, command="test")

            mock_output_error.assert_called_once_with(
                command="test",
                error_code=ErrorCode.GENERAL_ERROR,
                error_message="Test error",
            )

        # Test that output_error calls output_response
        with patch.object(HeadlessOutput, "output_response") as mock_output_response:
            HeadlessOutput.output_error(
                command="test",
                error_code=ErrorCode.GENERAL_ERROR,
                error_message="Test error",
            )

            mock_output_response.assert_called_once()
            # Verify it's called with an ErrorResponse
            call_args = mock_output_response.call_args[0][0]
            assert isinstance(call_args, ErrorResponse)
            assert call_args.command == "test"

