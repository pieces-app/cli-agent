"""
MCP configuration manager.
"""

from pathlib import Path
from typing import Dict
from .base import BaseConfigManager
from ..schemas.mcp import (
    MCPConfigSchema,
    mcp_integrations,
    mcp_types,
)


class MCPManager(BaseConfigManager[MCPConfigSchema]):
    """Manager for MCP configuration - matches existing mcp/integration.py functionality."""

    def __init__(self, config_path: Path):
        """
        Initialize MCP manager.

        Args:
            config_path: Full path to the MCP configuration file
        """
        super().__init__(config_path, MCPConfigSchema)

    # Project management - matches existing MCPLocalConfig methods
    def add_project(self, integration: str, mcp_type: mcp_types, path: str) -> None:
        """
        Add project to integration.

        Args:
            integration: Integration name (vscode, cursor, etc.)
            mcp_type: MCP communication type ('stdio' or 'sse')
            path: Project path
        """
        projects = self.get_projects(integration)
        projects[path] = mcp_type
        setattr(self.config, integration, projects)
        self.save()

    def remove_project(self, integration: str, path: str) -> None:
        """
        Remove project from integration.

        Args:
            integration: Integration name
            path: Project path
        """
        projects = self.get_projects(integration)
        projects.pop(path, None)
        setattr(self.config, integration, projects)
        self.save()

    def get_projects(self, integration: str) -> Dict[str, mcp_types]:
        """
        Get projects for integration.

        Args:
            integration: Integration name

        Returns:
            Dictionary mapping project paths to MCP types
        """
        return getattr(self.config, integration, {}).copy()

    def has_projects(self, integration: str) -> bool:
        """Check if integration has any projects."""
        return len(self.get_projects(integration)) > 0

    def get_all_projects(self) -> Dict[str, Dict[str, mcp_types]]:
        """Get all projects for all integrations."""
        return {
            integration: self.get_projects(integration)
            for integration in mcp_integrations
        }

    def clear_integration(self, integration: str) -> None:
        """Clear all projects for an integration."""
        setattr(self.config, integration, {})
        self.save()

    # Migration compatibility
    def migrate_json(self) -> None:
        """Migrate from old format if needed - matches existing migration logic."""
        if self.config.schema_version == "0.0.1":
            return

        # Convert list format to dict format
        for integration in mcp_integrations:
            value = getattr(self.config, integration, {})
            if isinstance(value, list):
                # Convert list to dict with stdio as default
                setattr(self.config, integration, dict.fromkeys(value, "stdio"))

        self.config.schema_version = "0.0.1"
        self.save()

    # Convenience properties for common integrations
    def get_vscode_projects(self) -> Dict[str, mcp_types]:
        """Get VS Code projects."""
        return self.get_projects("vscode")

    def get_cursor_projects(self) -> Dict[str, mcp_types]:
        """Get Cursor projects."""
        return self.get_projects("cursor")

    def add_vscode_project(self, path: str, mcp_type: mcp_types = "stdio") -> None:
        """Add VS Code project."""
        self.add_project("vscode", mcp_type, path)

    def add_cursor_project(self, path: str, mcp_type: mcp_types = "stdio") -> None:
        """Add Cursor project."""
        self.add_project("cursor", mcp_type, path)
