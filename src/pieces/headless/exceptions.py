"""
Headless mode specific exceptions.

These exceptions are raised when operations that require user interaction
are attempted in headless mode without appropriate defaults.
"""

from typing import Optional
from .models.base import ErrorCode
from .._vendor.pieces_os_client.wrapper.version_compatibility import (
    VersionCheckResult,
    UpdateEnum,
)


class HeadlessError(Exception):
    """Base exception for headless mode errors."""

    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        default_value: Optional[str] = None,
    ):
        super().__init__(message)
        self.error_code = error_code
        self.default_value = default_value


class HeadlessMissingInputError(HeadlessError):
    """Raised when a prompt is required in headless mode without a default."""

    def __init__(self):
        super().__init__(
            "Prompt required in headless mode",
            ErrorCode.USER_INPUT_REQUIRED,
        )


class HeadlessPromptError(HeadlessError):
    """Raised when a prompt is required in headless mode without a default."""

    def __init__(self, details: Optional[str] = None):
        if not details:
            details = ""
        else:
            details = f"\ndetails: {details}"
        super().__init__(
            f"Prompt required in headless mode{details}",
            ErrorCode.PROMPT_REQUIRED,
        )


class HeadlessConfirmationError(HeadlessError):
    """Raised when confirmation is required in headless mode without a default."""

    def __init__(self):
        super().__init__(
            "Confirmation required in headless mode",
            ErrorCode.CONFIRMATION_REQUIRED,
        )


class HeadlessInteractiveOperationError(HeadlessError):
    """Raised when an interactive operation is attempted in headless mode."""

    def __init__(self, operation_name: str = ""):
        message = f"Interactive operation{' ' + operation_name if operation_name else ''} cannot be performed in headless mode"
        super().__init__(
            message,
            ErrorCode.INTERACTIVE_OPERATION,
        )


class HeadlessCompatibilityError(HeadlessError):
    """Raised when the CLI is not compatible with PiecesOS."""

    def __init__(self, version_check_result: VersionCheckResult):
        if version_check_result.update == UpdateEnum.PiecesOS:
            message = "PiecesOS version is too old and needs to be updated"
            error_code = ErrorCode.PIECES_OS_UPDATE_REQUIRED
        elif version_check_result.update == UpdateEnum.Plugin:
            message = "CLI version is too old and needs to be updated"
            error_code = ErrorCode.CLI_UPDATE_REQUIRED
        else:
            message = "Version compatibility issue"
            error_code = ErrorCode.PIECES_OS_UPDATE_REQUIRED
        super().__init__(
            message,
            error_code,
        )


class HeadlessLTMNotEnabledError(HeadlessError):
    """Raised when LTM is not enabled."""

    def __init__(self):
        super().__init__(
            "LTM is not enabled",
            ErrorCode.LTM_NOT_ENABLED,
        )
