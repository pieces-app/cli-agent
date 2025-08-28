"""
Utility helpers for configuration validation.
"""

import re
from typing import Any

SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")
UUID_PATTERN = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)


def validate_semver(value: Any) -> str:
    """Validate semantic version string (e.g., '1.0.0')."""
    if isinstance(value, str) and SEMVER_PATTERN.match(value):
        return value
    raise ValueError("Invalid semantic version format")


def validate_uuid(value: Any) -> str:
    """Validate UUID string."""
    if isinstance(value, str) and UUID_PATTERN.match(value):
        return value
    raise ValueError("Invalid UUID format")


__all__ = [
    "validate_semver",
    "validate_uuid",
]

