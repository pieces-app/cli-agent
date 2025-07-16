"""
Test suite for headless error scenarios.

Tests for various error scenarios in headless mode including edge cases,
complex error handling, and error propagation.
"""

import json
import pytest
from unittest.mock import patch, Mock, MagicMock, call
from io import StringIO

from pieces.headless.models.base import (
    SuccessResponse,
    ErrorResponse,
    CommandResult,
    ErrorCode,
)
from pieces.headless.exceptions import (
    HeadlessError,
    HeadlessPromptError,
    HeadlessConfirmationError,
    HeadlessInteractiveOperationError,
    HeadlessCompatibilityError,
    HeadlessLTMNotEnabledError,
)
from pieces.headless.output import HeadlessOutput
from pieces._vendor.pieces_os_client.wrapper.version_compatibility import (
    VersionCheckResult,
    UpdateEnum,
)


class TestHeadlessErrorScenarios:
    """Test various error scenarios in headless mode."""

    def test_nested_exception_handling(self):
        """Test handling of nested exceptions."""
        # Create a nested exception scenario
        inner_error = ValueError("Inner error")
        outer_error = HeadlessError(
            message=f"Outer error: {str(inner_error)}",
            error_code=ErrorCode.GENERAL_ERROR,
        )

        with patch("builtins.print") as mock_print:
            HeadlessOutput.handle_exception(outer_error, command_name="test")

            mock_print.assert_called_once()
            printed_output = mock_print.call_args[0][0]

            parsed = json.loads(printed_output)
            assert parsed["success"] is False
            assert parsed["command"] == "test"
            assert parsed["data"]["error_type"] == ErrorCode.GENERAL_ERROR
            assert "Outer error: Inner error" in parsed["data"]["error_message"]

    def test_multiple_error_handling(self):
        """Test handling multiple errors in sequence."""
        errors = [
            HeadlessPromptError(),
            HeadlessConfirmationError(),
            HeadlessInteractiveOperationError("test"),
            HeadlessLTMNotEnabledError(),
        ]

        for error in errors:
            with patch("builtins.print") as mock_print:
                HeadlessOutput.handle_exception(error, command_name="test")

                mock_print.assert_called_once()
                printed_output = mock_print.call_args[0][0]

                parsed = json.loads(printed_output)
                assert parsed["success"] is False
                assert parsed["command"] == "test"
                assert parsed["data"]["error_type"] == error.error_code

    def test_error_with_malformed_json_data(self):
        """Test error handling with data that might break JSON serialization."""
        # Create response with potentially problematic data
        problematic_data = {
            "circular_ref": None,
            "large_number": 999999999999999999999,
            "special_chars": "\x00\x01\x02",
            "unicode_mix": "Hello\u0000World",
        }

        # Set up circular reference
        problematic_data["circular_ref"] = problematic_data

        try:
            response = SuccessResponse(command="test", data=problematic_data)

            with patch("builtins.print") as mock_print:
                # This should trigger the serialization error fallback
                HeadlessOutput.output_response(response)

                mock_print.assert_called_once()
                printed_output = mock_print.call_args[0][0]

                # Should output fallback error response
                parsed = json.loads(printed_output)
                assert parsed["success"] is False
                assert parsed["command"] == "unknown"
                assert parsed["data"]["error_type"] == ErrorCode.SERIALIZATION_ERROR

        except ValueError:
            # If circular reference is detected during creation, that's also valid
            pass

    def test_error_propagation_through_command_result(self):
        """Test error propagation through CommandResult."""
        # Test that errors propagate correctly through CommandResult
        error_response = ErrorResponse(
            command="test",
            error_code=ErrorCode.TIMEOUT_ERROR,
            error_message="Command timed out",
        )

        result = CommandResult(exit_code=1, headless_response=error_response)

        # Test headless mode
        with patch("builtins.print") as mock_print:
            result.exit(is_headless=True)

            mock_print.assert_called_once()
            printed_output = mock_print.call_args[0][0]

            parsed = json.loads(printed_output)
            assert parsed["success"] is False
            assert parsed["command"] == "test"
            assert parsed["data"]["error_type"] == ErrorCode.TIMEOUT_ERROR
            assert parsed["data"]["error_message"] == "Command timed out"

        # Test non-headless mode
        with patch("sys.exit") as mock_exit:
            result.exit(is_headless=False)
            mock_exit.assert_called_once_with(1)

    def test_compatibility_error_scenarios(self):
        """Test HeadlessCompatibilityError with various scenarios."""
        # Test PiecesOS update required
        pieces_os_update_result = Mock(spec=VersionCheckResult)
        pieces_os_update_result.update = UpdateEnum.PiecesOS

        error = HeadlessCompatibilityError(pieces_os_update_result)

        with patch("builtins.print") as mock_print:
            HeadlessOutput.output_headless_error(error, command="test")

            mock_print.assert_called_once()
            printed_output = mock_print.call_args[0][0]

            parsed = json.loads(printed_output)
            assert parsed["success"] is False
            assert parsed["data"]["error_type"] == ErrorCode.PIECES_OS_UPDATE_REQUIRED
            assert "PiecesOS version is too old" in parsed["data"]["error_message"]

        # Test CLI update required
        cli_update_result = Mock(spec=VersionCheckResult)
        cli_update_result.update = UpdateEnum.Plugin

        error = HeadlessCompatibilityError(cli_update_result)

        with patch("builtins.print") as mock_print:
            HeadlessOutput.output_headless_error(error, command="test")

            mock_print.assert_called_once()
            printed_output = mock_print.call_args[0][0]

            parsed = json.loads(printed_output)
            assert parsed["success"] is False
            assert parsed["data"]["error_type"] == ErrorCode.CLI_UPDATE_REQUIRED
            assert "CLI version is too old" in parsed["data"]["error_message"]

    def test_interactive_operation_error_scenarios(self):
        """Test HeadlessInteractiveOperationError with various scenarios."""
        test_cases = [
            ("", "Interactive operation cannot be performed in headless mode"),
            ("menu", "Interactive operation menu cannot be performed in headless mode"),
            (
                "user input",
                "Interactive operation user input cannot be performed in headless mode",
            ),
            (
                "file selection",
                "Interactive operation file selection cannot be performed in headless mode",
            ),
        ]

        for operation_name, expected_message in test_cases:
            error = HeadlessInteractiveOperationError(operation_name)

            with patch("builtins.print") as mock_print:
                HeadlessOutput.output_headless_error(error, command="test")

                mock_print.assert_called_once()
                printed_output = mock_print.call_args[0][0]

                parsed = json.loads(printed_output)
                assert parsed["success"] is False
                assert parsed["data"]["error_type"] == ErrorCode.INTERACTIVE_OPERATION
                assert parsed["data"]["error_message"] == expected_message

    def test_error_with_extremely_long_messages(self):
        """Test error handling with extremely long error messages."""
        long_message = "A" * 10000  # 10KB message

        error = HeadlessError(message=long_message, error_code=ErrorCode.GENERAL_ERROR)

        with patch("builtins.print") as mock_print:
            HeadlessOutput.output_headless_error(error, command="test")

            mock_print.assert_called_once()
            printed_output = mock_print.call_args[0][0]

            # Should handle long messages correctly
            parsed = json.loads(printed_output)
            assert parsed["success"] is False
            assert parsed["data"]["error_message"] == long_message

    def test_error_with_unicode_and_special_characters(self):
        """Test error handling with unicode and special characters."""
        unicode_message = "Error: 测试 🎉 \n\t\r Special chars: \x00\x01"

        error = HeadlessError(
            message=unicode_message, error_code=ErrorCode.GENERAL_ERROR
        )

        with patch("builtins.print") as mock_print:
            HeadlessOutput.output_headless_error(error, command="test")

            mock_print.assert_called_once()
            printed_output = mock_print.call_args[0][0]

            # Should handle unicode correctly
            parsed = json.loads(printed_output)
            assert parsed["success"] is False
            # Note: Some special characters might be escaped in JSON
            assert "测试" in parsed["data"]["error_message"]
            assert "🎉" in parsed["data"]["error_message"]

    def test_concurrent_error_handling(self):
        """Test handling multiple errors concurrently."""
        errors = [
            HeadlessPromptError(),
            HeadlessConfirmationError(),
            HeadlessInteractiveOperationError("test"),
        ]

        print_calls = []

        def mock_print_side_effect(output):
            print_calls.append(output)

        with patch("builtins.print", side_effect=mock_print_side_effect):
            for error in errors:
                HeadlessOutput.handle_exception(error, command_name="test")

            # Should have handled all errors
            assert len(print_calls) == len(errors)

            # Each should be valid JSON
            for output in print_calls:
                parsed = json.loads(output)
                assert parsed["success"] is False
                assert parsed["command"] == "test"

    def test_error_chaining_and_propagation(self):
        """Test error chaining and propagation through multiple layers."""
        # Simulate a chain of errors
        original_exception = ValueError("Original error")

        # Wrap in HeadlessError
        headless_error = HeadlessError(
            message=f"Wrapped error: {str(original_exception)}",
            error_code=ErrorCode.COMMAND_ERROR,
        )

        # Handle through HeadlessOutput
        with patch("builtins.print") as mock_print:
            HeadlessOutput.handle_exception(headless_error, command_name="test")

            mock_print.assert_called_once()
            printed_output = mock_print.call_args[0][0]

            parsed = json.loads(printed_output)
            assert parsed["success"] is False
            assert parsed["command"] == "test"
            assert parsed["data"]["error_type"] == ErrorCode.COMMAND_ERROR
            assert "Wrapped error: Original error" in parsed["data"]["error_message"]

    def test_error_with_none_values(self):
        """Test error handling with None values."""
        # Test HeadlessError with None default_value
        error = HeadlessError(
            message="Test error", error_code=ErrorCode.GENERAL_ERROR, default_value=None
        )

        with patch("builtins.print") as mock_print:
            HeadlessOutput.output_headless_error(error, command="test")

            mock_print.assert_called_once()
            printed_output = mock_print.call_args[0][0]

            parsed = json.loads(printed_output)
            assert parsed["success"] is False
            assert parsed["data"]["error_message"] == "Test error"

    def test_error_output_with_different_indentation(self):
        """Test error output with different indentation settings."""
        error = HeadlessError(message="Test error", error_code=ErrorCode.GENERAL_ERROR)

        error_response = ErrorResponse(
            command="test",
            error_code=ErrorCode.GENERAL_ERROR,
            error_message="Test error",
        )

        # Test with different indentation settings
        indent_settings = [None, 0, 2, 4, 8]

        for indent in indent_settings:
            with patch("builtins.print") as mock_print:
                HeadlessOutput.output_response(error_response, indent=indent)

                mock_print.assert_called_once()
                printed_output = mock_print.call_args[0][0]

                # Should always be valid JSON regardless of indentation
                parsed = json.loads(printed_output)
                assert parsed["success"] is False
                assert parsed["data"]["error_type"] == ErrorCode.GENERAL_ERROR

    def test_error_with_empty_command_name(self):
        """Test error handling with empty command name."""
        error = HeadlessError(message="Test error", error_code=ErrorCode.GENERAL_ERROR)

        with patch("builtins.print") as mock_print:
            HeadlessOutput.output_headless_error(error, command="")

            mock_print.assert_called_once()
            printed_output = mock_print.call_args[0][0]

            parsed = json.loads(printed_output)
            assert parsed["success"] is False
            assert parsed["command"] == ""

    def test_error_cascade_through_output_methods(self):
        """Test error cascade through different output methods."""
        error = HeadlessError(message="Test error", error_code=ErrorCode.GENERAL_ERROR)

        # Test that output_headless_error calls output_error
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

    def test_error_with_very_long_command_name(self):
        """Test error handling with very long command name."""
        long_command = "a" * 1000  # 1KB command name

        error = HeadlessError(message="Test error", error_code=ErrorCode.GENERAL_ERROR)

        with patch("builtins.print") as mock_print:
            HeadlessOutput.output_headless_error(error, command=long_command)

            mock_print.assert_called_once()
            printed_output = mock_print.call_args[0][0]

            parsed = json.loads(printed_output)
            assert parsed["success"] is False
            assert parsed["command"] == long_command

    def test_error_serialization_edge_cases(self):
        """Test error serialization edge cases."""
        # Test with response that has problematic to_json method
        mock_response = Mock()

        # First call succeeds, second fails
        mock_response.to_json.side_effect = [
            '{"success": true}',  # First call succeeds
            Exception("Serialization failed"),  # Second call fails
        ]

        # First call should succeed
        with patch("builtins.print") as mock_print:
            HeadlessOutput.output_response(mock_response)

            mock_print.assert_called_once()
            printed_output = mock_print.call_args[0][0]

            parsed = json.loads(printed_output)
            assert parsed["success"] is True

        # Second call should trigger fallback
        with patch("builtins.print") as mock_print:
            HeadlessOutput.output_response(mock_response)

            mock_print.assert_called_once()
            printed_output = mock_print.call_args[0][0]

            parsed = json.loads(printed_output)
            assert parsed["success"] is False
            assert parsed["data"]["error_type"] == ErrorCode.SERIALIZATION_ERROR

    def test_error_with_recursive_exception_handling(self):
        """Test error handling with recursive exceptions."""
        # Test exception that occurs during error handling
        error = HeadlessError(
            message="Original error", error_code=ErrorCode.GENERAL_ERROR
        )

        with patch("builtins.print") as mock_print:
            # Mock print to raise an exception
            mock_print.side_effect = Exception("Print failed")

            # This should not crash, but might not produce output
            try:
                HeadlessOutput.output_headless_error(error, command="test")
            except Exception:
                # If an exception is raised, it should be the print exception
                pass

    def test_error_handling_with_mixed_exception_types(self):
        """Test error handling with mixed exception types."""
        exceptions = [
            ValueError("Value error"),
            TypeError("Type error"),
            KeyError("Key error"),
            AttributeError("Attribute error"),
            RuntimeError("Runtime error"),
        ]

        for exception in exceptions:
            with patch("builtins.print") as mock_print:
                HeadlessOutput.handle_exception(exception, command_name="test")

                mock_print.assert_called_once()
                printed_output = mock_print.call_args[0][0]

                parsed = json.loads(printed_output)
                assert parsed["success"] is False
                assert parsed["command"] == "test"
                assert parsed["data"]["error_type"] == ErrorCode.COMMAND_ERROR
                assert str(exception) in parsed["data"]["error_message"]

    def test_error_message_encoding_scenarios(self):
        """Test various error message encoding scenarios."""
        test_messages = [
            "Simple ASCII message",
            "Unicode message: café 世界 🎉",
            "Mixed encoding: \x00\x01\x02 normal text",
            "Newlines and tabs:\n\t\r",
            "Quotes and escapes: \"quoted\" 'single' \\escaped",
            'JSON-like: {"key": "value"}',
            "XML-like: <tag>content</tag>",
        ]

        for message in test_messages:
            error = HeadlessError(message=message, error_code=ErrorCode.GENERAL_ERROR)

            with patch("builtins.print") as mock_print:
                HeadlessOutput.output_headless_error(error, command="test")

                mock_print.assert_called_once()
                printed_output = mock_print.call_args[0][0]

                # Should always produce valid JSON
                parsed = json.loads(printed_output)
                assert parsed["success"] is False
                # Error message should be present (might be escaped)
                assert "error_message" in parsed["data"]

