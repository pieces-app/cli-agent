"""
CLI configuration manager.
"""

from pathlib import Path
from typing import Optional
from ..schemas.cli import CLIConfigSchema
from .base import BaseConfigManager


class CLIManager(BaseConfigManager[CLIConfigSchema]):
    """Manager for CLI configuration."""

    def __init__(self, config_path: Path):
        """
        Initialize CLI manager.

        Args:
            config_path: Full path to the CLI configuration file
        """
        super().__init__(config_path, CLIConfigSchema)

    # Convenience properties for common settings
    @property
    def editor(self) -> Optional[str]:
        """Get configured editor."""
        return self.config.editor

    @editor.setter
    def editor(self, value: Optional[str]) -> None:
        """Set editor and save."""
        self.config.editor = value
        self.save()

    @property
    def theme(self) -> str:
        """Get configured theme."""
        return self.config.theme

    @theme.setter
    def theme(self, value: str) -> None:
        """Set theme and save."""
        self.config.theme = value
        self.save()

    @property
    def auto_launch_pieces_os(self) -> bool:
        """Get whether the CLI should auto-launch PiecesOS."""
        return self.config.auto_launch_pieces_os

    @auto_launch_pieces_os.setter
    def auto_launch_pieces_os(self, value: bool) -> None:
        """Set whether the CLI should auto-launch PiecesOS."""
        self.config.auto_launch_pieces_os = value
        self.save()

