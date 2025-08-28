"""
Manage commands package for Pieces CLI maintenance operations.

This package provides modular commands for managing the Pieces CLI installation:
- update: Update CLI to latest version
- status: Show CLI status and check for updates
- uninstall: Remove CLI from system

Supports multiple installation methods:
- pip (Python Package Index)
- homebrew (macOS/Linux)
- chocolatey (Windows)
- winget (Windows)
- installer script
"""

from .manage_group import ManageCommandGroup
from .update_command import ManageUpdateCommand
from .status_command import ManageStatusCommand
from .uninstall_command import ManageUninstallCommand

__all__ = [
    "ManageCommandGroup",
    "ManageUpdateCommand",
    "ManageStatusCommand",
    "ManageUninstallCommand",
]

