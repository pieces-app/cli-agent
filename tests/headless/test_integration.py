"""
Test suite for headless mode integration.

Integration tests for headless mode flag handling, command execution, and 
interaction between different headless components.
"""

import json
import pytest
from unittest.mock import patch, Mock, MagicMock
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
)
from pieces.headless.output import HeadlessOutput
from pieces.settings import Settings


class TestHeadlessIntegration:
    """Test integration between headless components."""

    def test_headless_error_to_output_integration(self):
        """Test integration between headless errors and output."""
        error = HeadlessPromptError()
        
        with patch("builtins.print") as mock_print:
            HeadlessOutput.output_headless_error(error, command="test")
            
            mock_print.assert_called_once()
            printed_output = mock_print.call_args[0][0]
            
            # Should produce valid JSON error response
            parsed = json.loads(printed_output)
            assert parsed["success"] is False
            assert parsed["command"] == "test"
            assert parsed["data"]["error_type"] == ErrorCode.PROMPT_REQUIRED

    def test_command_result_integration(self):
        """Test CommandResult integration with headless responses."""
        success_response = SuccessResponse(command="test", data={"result": "success"})
        command_result = CommandResult(exit_code=0, headless_response=success_response)
        
        with patch("builtins.print") as mock_print:
            command_result.exit(is_headless=True)
            
            mock_print.assert_called_once()
            printed_output = mock_print.call_args[0][0]
            
            # Should output the headless response
            parsed = json.loads(printed_output)
            assert parsed["success"] is True
            assert parsed["command"] == "test"
            assert parsed["data"]["result"] == "success"

    def test_error_response_to_command_result_integration(self):
        """Test ErrorResponse to CommandResult integration."""
        error_response = ErrorResponse(
            command="test",
            error_code=ErrorCode.GENERAL_ERROR,
            error_message="Test error"
        )
        command_result = CommandResult(exit_code=1, headless_response=error_response)
        
        with patch("builtins.print") as mock_print:
            command_result.exit(is_headless=True)
            
            mock_print.assert_called_once()
            printed_output = mock_print.call_args[0][0]
            
            # Should output the error response
            parsed = json.loads(printed_output)
            assert parsed["success"] is False
            assert parsed["command"] == "test"
            assert parsed["data"]["error_type"] == ErrorCode.GENERAL_ERROR

    def test_exception_handling_integration(self):
        """Test exception handling integration with HeadlessOutput."""
        # Test with HeadlessError
        headless_error = HeadlessConfirmationError()
        
        with patch("builtins.print") as mock_print:
            HeadlessOutput.handle_exception(headless_error, command_name="test")
            
            mock_print.assert_called_once()
            printed_output = mock_print.call_args[0][0]
            
            parsed = json.loads(printed_output)
            assert parsed["success"] is False
            assert parsed["command"] == "test"
            assert parsed["data"]["error_type"] == ErrorCode.CONFIRMATION_REQUIRED

        # Test with general exception
        general_error = ValueError("Test general error")
        
        with patch("builtins.print") as mock_print:
            HeadlessOutput.handle_exception(general_error, command_name="test")
            
            mock_print.assert_called_once()
            printed_output = mock_print.call_args[0][0]
            
            parsed = json.loads(printed_output)
            assert parsed["success"] is False
            assert parsed["command"] == "test"
            assert parsed["data"]["error_type"] == ErrorCode.COMMAND_ERROR

    def test_headless_mode_setting_integration(self):
        """Test headless mode setting integration."""
        # Test that headless mode can be set and accessed
        original_headless_mode = Settings.headless_mode
        
        try:
            Settings.headless_mode = True
            assert Settings.headless_mode is True
            
            Settings.headless_mode = False
            assert Settings.headless_mode is False
            
        finally:
            Settings.headless_mode = original_headless_mode

    def test_headless_output_with_different_response_types(self):
        """Test HeadlessOutput with different response types."""
        # Test with SuccessResponse
        success_response = SuccessResponse(command="test", data={"key": "value"})
        
        with patch("builtins.print") as mock_print:
            HeadlessOutput.output_response(success_response)
            
            mock_print.assert_called_once()
            printed_output = mock_print.call_args[0][0]
            
            parsed = json.loads(printed_output)
            assert parsed["success"] is True
            assert parsed["command"] == "test"
            assert parsed["data"]["key"] == "value"

        # Test with ErrorResponse
        error_response = ErrorResponse(
            command="test",
            error_code=ErrorCode.INVALID_ARGUMENT,
            error_message="Invalid argument"
        )
        
        with patch("builtins.print") as mock_print:
            HeadlessOutput.output_response(error_response)
            
            mock_print.assert_called_once()
            printed_output = mock_print.call_args[0][0]
            
            parsed = json.loads(printed_output)
            assert parsed["success"] is False
            assert parsed["command"] == "test"
            assert parsed["data"]["error_type"] == ErrorCode.INVALID_ARGUMENT

    def test_headless_error_with_all_error_codes(self):
        """Test headless errors with all error codes."""
        error_code_test_cases = [
            ErrorCode.GENERAL_ERROR,
            ErrorCode.PROMPT_REQUIRED,
            ErrorCode.CONFIRMATION_REQUIRED,
            ErrorCode.INTERACTIVE_OPERATION,
            ErrorCode.MCP_SETUP_FAILED,
            ErrorCode.LTM_NOT_ENABLED,
        ]
        
        for error_code in error_code_test_cases:
            error = HeadlessError(
                message=f"Test error for {error_code}",
                error_code=error_code
            )
            
            with patch("builtins.print") as mock_print:
                HeadlessOutput.output_headless_error(error, command="test")
                
                mock_print.assert_called_once()
                printed_output = mock_print.call_args[0][0]
                
                parsed = json.loads(printed_output)
                assert parsed["success"] is False
                assert parsed["command"] == "test"
                assert parsed["data"]["error_type"] == error_code

    def test_json_serialization_consistency(self):
        """Test JSON serialization consistency across components."""
        # Test SuccessResponse
        success_response = SuccessResponse(command="test", data={"key": "value"})
        
        # Direct JSON serialization
        direct_json = success_response.to_json()
        
        # Via HeadlessOutput
        with patch("builtins.print") as mock_print:
            HeadlessOutput.output_response(success_response)
            output_json = mock_print.call_args[0][0]
        
        # Both should produce identical JSON
        assert json.loads(direct_json) == json.loads(output_json)

    def test_error_response_consistency(self):
        """Test error response consistency across different error types."""
        # Test different ways to create error responses
        error_response_1 = ErrorResponse(
            command="test",
            error_code=ErrorCode.GENERAL_ERROR,
            error_message="Test error"
        )
        
        # Via HeadlessOutput.output_error
        with patch("builtins.print") as mock_print:
            HeadlessOutput.output_error(
                command="test",
                error_code=ErrorCode.GENERAL_ERROR,
                error_message="Test error"
            )
            output_json = mock_print.call_args[0][0]
        
        # Both should produce the same structure
        direct_json = error_response_1.to_json()
        assert json.loads(direct_json) == json.loads(output_json)

    def test_command_result_exit_modes(self):
        """Test CommandResult exit behavior in different modes."""
        success_response = SuccessResponse(command="test", data={"result": "success"})
        error_response = ErrorResponse(
            command="test",
            error_code=ErrorCode.GENERAL_ERROR,
            error_message="Test error"
        )
        
        # Test success in headless mode
        success_result = CommandResult(exit_code=0, headless_response=success_response)
        
        with patch("builtins.print") as mock_print:
            success_result.exit(is_headless=True)
            
            mock_print.assert_called_once()
            printed_output = mock_print.call_args[0][0]
            parsed = json.loads(printed_output)
            assert parsed["success"] is True

        # Test error in headless mode
        error_result = CommandResult(exit_code=1, headless_response=error_response)
        
        with patch("builtins.print") as mock_print:
            error_result.exit(is_headless=True)
            
            mock_print.assert_called_once()
            printed_output = mock_print.call_args[0][0]
            parsed = json.loads(printed_output)
            assert parsed["success"] is False

        # Test non-headless mode
        with patch("sys.exit") as mock_exit:
            success_result.exit(is_headless=False)
            mock_exit.assert_called_once_with(0)

    def test_complex_data_structures_integration(self):
        """Test complex data structures through the entire pipeline."""
        complex_data = {
            "nested": {
                "array": [1, 2, {"inner": "value"}],
                "null_value": None,
                "boolean": True,
                "unicode": "Hello 世界",
            },
            "list": [
                {"id": 1, "name": "first"},
                {"id": 2, "name": "second"},
            ]
        }
        
        response = SuccessResponse(command="complex_test", data=complex_data)
        
        # Test direct serialization
        direct_json = response.to_json()
        direct_parsed = json.loads(direct_json)
        
        # Test through HeadlessOutput
        with patch("builtins.print") as mock_print:
            HeadlessOutput.output_response(response)
            output_json = mock_print.call_args[0][0]
        
        output_parsed = json.loads(output_json)
        
        # Both should handle complex data identically
        assert direct_parsed == output_parsed
        assert direct_parsed["data"] == complex_data

    def test_unicode_handling_integration(self):
        """Test unicode handling across all components."""
        unicode_data = {
            "message": "Hello 世界",
            "emoji": "🎉",
            "special": "Café",
        }
        
        response = SuccessResponse(command="unicode_test", data=unicode_data)
        
        # Test through HeadlessOutput
        with patch("builtins.print") as mock_print:
            HeadlessOutput.output_response(response)
            output_json = mock_print.call_args[0][0]
        
        parsed = json.loads(output_json)
        assert parsed["data"] == unicode_data

    def test_error_handling_chain_integration(self):
        """Test error handling chain from exception to output."""
        # Test the complete chain: Exception -> HeadlessError -> HeadlessOutput
        
        # 1. Create a HeadlessError
        original_error = HeadlessPromptError()
        
        # 2. Handle through HeadlessOutput
        with patch("builtins.print") as mock_print:
            HeadlessOutput.handle_exception(original_error, command_name="test")
            
            mock_print.assert_called_once()
            printed_output = mock_print.call_args[0][0]
            
            # 3. Verify the complete chain worked
            parsed = json.loads(printed_output)
            assert parsed["success"] is False
            assert parsed["command"] == "test"
            assert parsed["data"]["error_type"] == ErrorCode.PROMPT_REQUIRED
            assert "Prompt required in headless mode" in parsed["data"]["error_message"]

    def test_headless_output_fallback_behavior(self):
        """Test HeadlessOutput fallback behavior when serialization fails."""
        # Create a mock response that fails to serialize
        mock_response = Mock()
        mock_response.to_json.side_effect = Exception("Serialization failed")
        
        with patch("builtins.print") as mock_print:
            HeadlessOutput.output_response(mock_response)
            
            mock_print.assert_called_once()
            printed_output = mock_print.call_args[0][0]
            
            # Should output fallback error response
            parsed = json.loads(printed_output)
            assert parsed["success"] is False
            assert parsed["command"] == "unknown"
            assert parsed["data"]["error_type"] == ErrorCode.SERIALIZATION_ERROR
            assert "Failed to serialize response" in parsed["data"]["error_message"]

    def test_output_indentation_consistency(self):
        """Test that output indentation is consistent across components."""
        response = SuccessResponse(command="test", data={"key": "value"})
        
        # Test default indentation (2 spaces)
        with patch("builtins.print") as mock_print:
            HeadlessOutput.output_response(response)
            default_output = mock_print.call_args[0][0]
        
        # Test custom indentation
        with patch("builtins.print") as mock_print:
            HeadlessOutput.output_response(response, indent=4)
            custom_output = mock_print.call_args[0][0]
        
        # Test no indentation
        with patch("builtins.print") as mock_print:
            HeadlessOutput.output_response(response, indent=None)
            no_indent_output = mock_print.call_args[0][0]
        
        # All should parse to the same data
        default_parsed = json.loads(default_output)
        custom_parsed = json.loads(custom_output)
        no_indent_parsed = json.loads(no_indent_output)
        
        assert default_parsed == custom_parsed == no_indent_parsed
        
        # But formatting should be different
        assert "\n" in default_output
        assert "\n" in custom_output
        assert "\n" not in no_indent_output

    def test_headless_mode_command_flow(self):
        """Test the complete command flow in headless mode."""
        # Simulate a command that succeeds in headless mode
        response = SuccessResponse(command="test_command", data={"result": "success"})
        result = CommandResult(exit_code=0, headless_response=response)
        
        # Mock headless mode enabled
        with patch.object(Settings, 'headless_mode', True):
            with patch("builtins.print") as mock_print:
                result.exit(is_headless=True)
                
                mock_print.assert_called_once()
                printed_output = mock_print.call_args[0][0]
                
                # Should output JSON response
                parsed = json.loads(printed_output)
                assert parsed["success"] is True
                assert parsed["command"] == "test_command"
                assert parsed["data"]["result"] == "success" 