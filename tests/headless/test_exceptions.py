"""
Test suite for headless exceptions.

Tests for all HeadlessError subclasses and their error handling behavior.
"""

import pytest
from unittest.mock import Mock

from pieces.headless.exceptions import (
    HeadlessError,
    HeadlessMissingInputError,
    HeadlessPromptError,
    HeadlessConfirmationError,
    HeadlessInteractiveOperationError,
    HeadlessCompatibilityError,
    HeadlessLTMNotEnabledError,
)
from pieces.headless.models.base import ErrorCode
from pieces._vendor.pieces_os_client.wrapper.version_compatibility import (
    VersionCheckResult,
    UpdateEnum,
)


class TestHeadlessError:
    """Test HeadlessError base class."""

    def test_headless_error_basic(self):
        """Test basic HeadlessError creation."""
        error = HeadlessError(
            message="Test error",
            error_code=ErrorCode.GENERAL_ERROR,
            default_value=None
        )
        
        assert str(error) == "Test error"
        assert error.error_code == ErrorCode.GENERAL_ERROR
        assert error.default_value is None

    def test_headless_error_with_default_value(self):
        """Test HeadlessError with default value."""
        error = HeadlessError(
            message="Test error with default",
            error_code=ErrorCode.PROMPT_REQUIRED,
            default_value="default_value"
        )
        
        assert str(error) == "Test error with default"
        assert error.error_code == ErrorCode.PROMPT_REQUIRED
        assert error.default_value == "default_value"

    def test_headless_error_inheritance(self):
        """Test that HeadlessError inherits from Exception."""
        error = HeadlessError(
            message="Test error",
            error_code=ErrorCode.GENERAL_ERROR
        )
        
        assert isinstance(error, Exception)
        assert isinstance(error, HeadlessError)

    def test_headless_error_different_error_codes(self):
        """Test HeadlessError with different error codes."""
        test_cases = [
            ErrorCode.GENERAL_ERROR,
            ErrorCode.PROMPT_REQUIRED,
            ErrorCode.CONFIRMATION_REQUIRED,
            ErrorCode.MCP_SETUP_FAILED,
            ErrorCode.LTM_NOT_ENABLED,
        ]
        
        for error_code in test_cases:
            error = HeadlessError(
                message=f"Test error for {error_code}",
                error_code=error_code
            )
            
            assert error.error_code == error_code


class TestHeadlessMissingInputError:
    """Test HeadlessMissingInputError class."""

    def test_missing_input_error_creation(self):
        """Test HeadlessMissingInputError creation."""
        error = HeadlessMissingInputError()
        
        assert str(error) == "Prompt required in headless mode"
        assert error.error_code == ErrorCode.USER_INPUT_REQUIRED
        assert error.default_value is None

    def test_missing_input_error_inheritance(self):
        """Test HeadlessMissingInputError inheritance."""
        error = HeadlessMissingInputError()
        
        assert isinstance(error, HeadlessError)
        assert isinstance(error, Exception)

    def test_missing_input_error_no_parameters(self):
        """Test that HeadlessMissingInputError takes no parameters."""
        error = HeadlessMissingInputError()
        
        # Should have predetermined message and error code
        assert str(error) == "Prompt required in headless mode"
        assert error.error_code == ErrorCode.USER_INPUT_REQUIRED


class TestHeadlessPromptError:
    """Test HeadlessPromptError class."""

    def test_prompt_error_creation(self):
        """Test HeadlessPromptError creation."""
        error = HeadlessPromptError()
        
        assert str(error) == "Prompt required in headless mode"
        assert error.error_code == ErrorCode.PROMPT_REQUIRED
        assert error.default_value is None

    def test_prompt_error_inheritance(self):
        """Test HeadlessPromptError inheritance."""
        error = HeadlessPromptError()
        
        assert isinstance(error, HeadlessError)
        assert isinstance(error, Exception)

    def test_prompt_error_no_parameters(self):
        """Test that HeadlessPromptError takes no parameters."""
        error = HeadlessPromptError()
        
        # Should have predetermined message and error code
        assert str(error) == "Prompt required in headless mode"
        assert error.error_code == ErrorCode.PROMPT_REQUIRED


class TestHeadlessConfirmationError:
    """Test HeadlessConfirmationError class."""

    def test_confirmation_error_creation(self):
        """Test HeadlessConfirmationError creation."""
        error = HeadlessConfirmationError()
        
        assert str(error) == "Confirmation required in headless mode"
        assert error.error_code == ErrorCode.CONFIRMATION_REQUIRED
        assert error.default_value is None

    def test_confirmation_error_inheritance(self):
        """Test HeadlessConfirmationError inheritance."""
        error = HeadlessConfirmationError()
        
        assert isinstance(error, HeadlessError)
        assert isinstance(error, Exception)

    def test_confirmation_error_no_parameters(self):
        """Test that HeadlessConfirmationError takes no parameters."""
        error = HeadlessConfirmationError()
        
        # Should have predetermined message and error code
        assert str(error) == "Confirmation required in headless mode"
        assert error.error_code == ErrorCode.CONFIRMATION_REQUIRED


class TestHeadlessInteractiveOperationError:
    """Test HeadlessInteractiveOperationError class."""

    def test_interactive_operation_error_no_operation_name(self):
        """Test HeadlessInteractiveOperationError without operation name."""
        error = HeadlessInteractiveOperationError()
        
        assert str(error) == "Interactive operation cannot be performed in headless mode"
        assert error.error_code == ErrorCode.INTERACTIVE_OPERATION
        assert error.default_value is None

    def test_interactive_operation_error_with_operation_name(self):
        """Test HeadlessInteractiveOperationError with operation name."""
        error = HeadlessInteractiveOperationError("menu selection")
        
        assert str(error) == "Interactive operation menu selection cannot be performed in headless mode"
        assert error.error_code == ErrorCode.INTERACTIVE_OPERATION
        assert error.default_value is None

    def test_interactive_operation_error_empty_operation_name(self):
        """Test HeadlessInteractiveOperationError with empty operation name."""
        error = HeadlessInteractiveOperationError("")
        
        assert str(error) == "Interactive operation cannot be performed in headless mode"
        assert error.error_code == ErrorCode.INTERACTIVE_OPERATION

    def test_interactive_operation_error_inheritance(self):
        """Test HeadlessInteractiveOperationError inheritance."""
        error = HeadlessInteractiveOperationError("test")
        
        assert isinstance(error, HeadlessError)
        assert isinstance(error, Exception)

    def test_interactive_operation_error_various_operation_names(self):
        """Test HeadlessInteractiveOperationError with various operation names."""
        test_cases = [
            ("menu", "Interactive operation menu cannot be performed in headless mode"),
            ("input", "Interactive operation input cannot be performed in headless mode"),
            ("confirmation", "Interactive operation confirmation cannot be performed in headless mode"),
            ("selection", "Interactive operation selection cannot be performed in headless mode"),
        ]
        
        for operation_name, expected_message in test_cases:
            error = HeadlessInteractiveOperationError(operation_name)
            assert str(error) == expected_message


class TestHeadlessCompatibilityError:
    """Test HeadlessCompatibilityError class."""

    def test_compatibility_error_pieces_os_update_required(self):
        """Test HeadlessCompatibilityError when PiecesOS needs update."""
        version_check_result = Mock(spec=VersionCheckResult)
        version_check_result.update = UpdateEnum.PiecesOS
        
        error = HeadlessCompatibilityError(version_check_result)
        
        assert str(error) == "PiecesOS version is too old and needs to be updated"
        assert error.error_code == ErrorCode.PIECES_OS_UPDATE_REQUIRED
        assert error.default_value is None

    def test_compatibility_error_cli_update_required(self):
        """Test HeadlessCompatibilityError when CLI needs update."""
        version_check_result = Mock(spec=VersionCheckResult)
        version_check_result.update = UpdateEnum.Plugin
        
        error = HeadlessCompatibilityError(version_check_result)
        
        assert str(error) == "CLI version is too old and needs to be updated"
        assert error.error_code == ErrorCode.CLI_UPDATE_REQUIRED
        assert error.default_value is None

    def test_compatibility_error_unknown_update_type(self):
        """Test HeadlessCompatibilityError with unknown update type."""
        version_check_result = Mock(spec=VersionCheckResult)
        version_check_result.update = "unknown"  # Not a valid UpdateEnum
        
        error = HeadlessCompatibilityError(version_check_result)
        
        assert str(error) == "Version compatibility issue"
        assert error.error_code == ErrorCode.PIECES_OS_UPDATE_REQUIRED  # fallback
        assert error.default_value is None

    def test_compatibility_error_inheritance(self):
        """Test HeadlessCompatibilityError inheritance."""
        version_check_result = Mock(spec=VersionCheckResult)
        version_check_result.update = UpdateEnum.PiecesOS
        
        error = HeadlessCompatibilityError(version_check_result)
        
        assert isinstance(error, HeadlessError)
        assert isinstance(error, Exception)

    def test_compatibility_error_with_version_check_result(self):
        """Test HeadlessCompatibilityError preserves version check result."""
        version_check_result = Mock(spec=VersionCheckResult)
        version_check_result.update = UpdateEnum.PiecesOS
        
        error = HeadlessCompatibilityError(version_check_result)
        
        # The error should be created based on the version check result
        assert str(error) == "PiecesOS version is too old and needs to be updated"


class TestHeadlessLTMNotEnabledError:
    """Test HeadlessLTMNotEnabledError class."""

    def test_ltm_not_enabled_error_creation(self):
        """Test HeadlessLTMNotEnabledError creation."""
        error = HeadlessLTMNotEnabledError()
        
        assert str(error) == "LTM is not enabled"
        assert error.error_code == ErrorCode.LTM_NOT_ENABLED
        assert error.default_value is None

    def test_ltm_not_enabled_error_inheritance(self):
        """Test HeadlessLTMNotEnabledError inheritance."""
        error = HeadlessLTMNotEnabledError()
        
        assert isinstance(error, HeadlessError)
        assert isinstance(error, Exception)

    def test_ltm_not_enabled_error_no_parameters(self):
        """Test that HeadlessLTMNotEnabledError takes no parameters."""
        error = HeadlessLTMNotEnabledError()
        
        # Should have predetermined message and error code
        assert str(error) == "LTM is not enabled"
        assert error.error_code == ErrorCode.LTM_NOT_ENABLED


class TestExceptionRaising:
    """Test that exceptions can be raised and caught properly."""

    def test_raise_headless_error(self):
        """Test raising and catching HeadlessError."""
        with pytest.raises(HeadlessError) as exc_info:
            raise HeadlessError(
                message="Test error",
                error_code=ErrorCode.GENERAL_ERROR
            )
        
        assert str(exc_info.value) == "Test error"
        assert exc_info.value.error_code == ErrorCode.GENERAL_ERROR

    def test_raise_specific_headless_errors(self):
        """Test raising and catching specific headless errors."""
        # Test each specific error type
        error_classes = [
            HeadlessMissingInputError,
            HeadlessPromptError,
            HeadlessConfirmationError,
            HeadlessLTMNotEnabledError,
        ]
        
        for error_class in error_classes:
            with pytest.raises(error_class) as exc_info:
                raise error_class()
            
            assert isinstance(exc_info.value, HeadlessError)
            assert isinstance(exc_info.value, error_class)

    def test_raise_interactive_operation_error(self):
        """Test raising and catching HeadlessInteractiveOperationError."""
        with pytest.raises(HeadlessInteractiveOperationError) as exc_info:
            raise HeadlessInteractiveOperationError("test operation")
        
        assert "test operation" in str(exc_info.value)
        assert isinstance(exc_info.value, HeadlessError)

    def test_raise_compatibility_error(self):
        """Test raising and catching HeadlessCompatibilityError."""
        version_check_result = Mock(spec=VersionCheckResult)
        version_check_result.update = UpdateEnum.PiecesOS
        
        with pytest.raises(HeadlessCompatibilityError) as exc_info:
            raise HeadlessCompatibilityError(version_check_result)
        
        assert "PiecesOS version is too old" in str(exc_info.value)
        assert isinstance(exc_info.value, HeadlessError)

    def test_catch_all_as_headless_error(self):
        """Test that all headless errors can be caught as HeadlessError."""
        specific_errors = [
            HeadlessMissingInputError(),
            HeadlessPromptError(),
            HeadlessConfirmationError(),
            HeadlessInteractiveOperationError("test"),
            HeadlessLTMNotEnabledError(),
        ]
        
        for error in specific_errors:
            with pytest.raises(HeadlessError):
                raise error

    def test_exception_attributes_preserved(self):
        """Test that exception attributes are preserved when raised."""
        error = HeadlessError(
            message="Test message",
            error_code=ErrorCode.TIMEOUT_ERROR,
            default_value="default"
        )
        
        with pytest.raises(HeadlessError) as exc_info:
            raise error
        
        caught_error = exc_info.value
        assert str(caught_error) == "Test message"
        assert caught_error.error_code == ErrorCode.TIMEOUT_ERROR
        assert caught_error.default_value == "default" 