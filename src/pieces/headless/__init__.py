"""
Headless mode module for Pieces CLI.

This module provides JSON API-like output for commands when running in headless mode.
Supports non-interactive operation with structured JSON responses.
"""

from .exceptions import HeadlessError, HeadlessPromptError, HeadlessConfirmationError
from .output import HeadlessOutput
from .models.base import (
    BaseResponse,
    ErrorResponse,
    SuccessResponse,
    CommandResult,
    ErrorCode,
)

__all__ = [
    "HeadlessError",
    "HeadlessPromptError",
    "HeadlessConfirmationError",
    "HeadlessOutput",
    "BaseResponse",
    "ErrorResponse",
    "SuccessResponse",
    "CommandResult",
    "ErrorCode",
]
