"""
Base response models for headless mode JSON output.

These models provide a consistent structure for all headless mode responses.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import sys
from enum import IntEnum
import json


class ErrorCode(IntEnum):
    """Error codes for headless mode failures."""

    # General errors (1-99)
    GENERAL_ERROR = 1
    SERIALIZATION_ERROR = 2
    COMMAND_ERROR = 3
    INVALID_ARGUMENT = 4
    TIMEOUT_ERROR = 5
    INVALID_PATH = 6

    # User interaction errors (100-199)
    PROMPT_REQUIRED = 100
    CONFIRMATION_REQUIRED = 101
    USER_INPUT_REQUIRED = 102
    USER_INTERRUPTED = 102
    INTERACTIVE_OPERATION = 103

    # System errors (200-299)
    PIECES_OS_UPDATE_REQUIRED = 202
    CLI_UPDATE_REQUIRED = 203
    AUTHENTICATION_FAILED = 204
    LTM_NOT_ENABLED = 205

    # MCP errors (400-499)
    MCP_SETUP_FAILED = 400
    MCP_START_FAILED = 401
    MCP_REPAIR_FAILED = 402
    MCP_SERVER_NOT_RUNNING = 403


class BaseResponse(ABC):
    """Abstract base class for all headless responses."""

    def __init__(self, success: bool, command: str):
        """
        Initialize base response.

        Args:
            success: True for success, False for failure
            command: The command that was executed
        """
        self.success = success
        self.command = command

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary format."""
        pass

    def to_json(self, indent: Optional[int] = None) -> str:
        """Convert response to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


class SuccessResponse(BaseResponse):
    """Success response for headless mode."""

    def __init__(self, command: str, data: Any = None):
        """
        Initialize success response.

        Args:
            command: The command that was executed
            data: The response data (depends on command)
        """
        super().__init__(success=True, command=command)
        self.data = data

    def to_dict(self) -> Dict[str, Any]:
        response = {"success": self.success, "command": self.command, "data": self.data}
        return response


class ErrorResponse(BaseResponse):
    """Error response for headless mode."""

    def __init__(self, command: str, error_code: ErrorCode, error_message: str):
        """
        Initialize error response.

        Args:
            command: The command that was executed
            error_code: The error code (integer enum)
            error_message: The error message
        """
        super().__init__(success=False, command=command)
        self.data = {"error_type": error_code.value, "error_message": error_message}

    def to_dict(self) -> Dict[str, Any]:
        response = {"success": self.success, "command": self.command, "data": self.data}
        return response


class CommandResult:
    """Result of command execution that can be either an exit code or a headless response."""

    def __init__(self, exit_code: int, headless_response: BaseResponse):
        self.exit_code = exit_code
        self.headless_response = headless_response

    def exit(self, is_headless: bool = False):
        if is_headless:
            print(self.headless_response.to_json())
        else:
            sys.exit(self.exit_code)
