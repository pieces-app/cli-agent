"""
Configuration Management Package for Pieces CLI

This package provides:
- JSON schema definitions and validation
- Configuration file management
- Migration utilities from legacy formats
- Type-safe configuration access
"""

from .schemas import (
    CLIConfigSchema,
    ModelConfigSchema,
    ModelInfo,
    MCPConfigSchema,
    UserDataSchema,
)
from .managers import (
    BaseConfigManager,
    CLIManager,
    ModelManager,
    MCPManager,
    UserManager,
)

__all__ = [
    # Main interfaces
    "BaseConfigManager",
    "CLIManager",
    "ModelManager",
    "MCPManager",
    "UserManager",
    # Schema classes (for validation and type hints)
    "CLIConfigSchema",
    "ModelConfigSchema",
    "ModelInfo",
    "MCPConfigSchema",
    "UserDataSchema",
]

