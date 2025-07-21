"""
Headless output handler for managing JSON responses.

This module provides utilities for outputting structured JSON responses
in headless mode while maintaining compatibility with normal CLI output.
"""

from .models.base import BaseResponse, ErrorResponse, ErrorCode
from .exceptions import HeadlessError


class HeadlessOutput:
    """Manages JSON output for headless mode operations."""

    @staticmethod
    def output_response(response: BaseResponse) -> None:
        """Output a structured response to stdout as JSON."""
        try:
            json_output = response.to_json()
            print(json_output)
        except Exception as e:
            # Fallback error response if JSON serialization fails
            error_response = ErrorResponse(
                command="unknown",
                error_code=ErrorCode.SERIALIZATION_ERROR,
                error_message=f"Failed to serialize response: {str(e)}",
            )
            print(error_response.to_json())

    @staticmethod
    def output_error(
        command: str,
        error_code: ErrorCode = ErrorCode.GENERAL_ERROR,
        error_message: str = "An error occurred",
    ) -> None:
        """Output an error response to stdout as JSON."""
        error_response = ErrorResponse(
            command=command, error_code=error_code, error_message=error_message
        )
        HeadlessOutput.output_response(error_response)

    @staticmethod
    def output_headless_error(error: HeadlessError, command: str = "unknown") -> None:
        """Output a headless-specific error with appropriate context."""

        HeadlessOutput.output_error(
            command=command, error_code=error.error_code, error_message=str(error)
        )

    @staticmethod
    def handle_exception(exception: Exception, command_name: str = "unknown") -> None:
        """Handle and output exceptions in headless mode format."""
        if isinstance(exception, HeadlessError):
            HeadlessOutput.output_headless_error(exception, command_name)
        else:
            HeadlessOutput.output_error(
                command=command_name,
                error_code=ErrorCode.COMMAND_ERROR,
                error_message=f"Command '{command_name}' failed: {str(exception)}",
            )
