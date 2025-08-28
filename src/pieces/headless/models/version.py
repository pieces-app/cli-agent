"""
Version command response models for headless mode.
"""

from .base import SuccessResponse


def create_version_success(
    cli_version: str,
    pieces_os_version: str,
) -> SuccessResponse:
    """Create a successful version response."""
    version_data = {
        "cli_version": cli_version,
        "pieces_os_version": pieces_os_version,
    }

    return SuccessResponse(command="version", data=version_data)
