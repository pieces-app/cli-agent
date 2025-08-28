"""
Headless response models for structured JSON output.
"""

from .base import BaseResponse, ErrorResponse, SuccessResponse, ErrorCode
from .version import create_version_success
from .mcp import (
    create_mcp_list_success,
    create_mcp_setup_success,
)

__all__ = [
    # Base classes
    "BaseResponse",
    "ErrorResponse",
    "SuccessResponse",
    "ErrorCode",
    # Factory functions
    "create_version_success",
    "create_mcp_list_success",
    "create_mcp_setup_success",
]
