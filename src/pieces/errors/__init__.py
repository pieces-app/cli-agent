"""
User-friendly error handling for Pieces CLI.

This module provides utilities for transforming technical error messages
into helpful, actionable messages for users.
"""

from .user_friendly import (
    UserFriendlyError,
    ErrorCategory,
    format_error,
    get_user_friendly_message,
)

__all__ = [
    "UserFriendlyError",
    "ErrorCategory",
    "format_error",
    "get_user_friendly_message",
]
