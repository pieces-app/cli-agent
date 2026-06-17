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
    def auto_enable_chat_ltm(self) -> bool:
        """Whether new chats should auto-attach Long-Term Memory."""
        return self.config.auto_enable_chat_ltm

    @auto_enable_chat_ltm.setter
    def auto_enable_chat_ltm(self, value: bool) -> None:
        """Toggle auto-LTM-on-new-chat and persist."""
        self.config.auto_enable_chat_ltm = bool(value)
        self.save()

    @property
    def auto_enable_chat_ltm_lookback_days(self) -> int:
        """How many days back the auto-attached LTM range covers."""
        return self.config.auto_enable_chat_ltm_lookback_days

    @auto_enable_chat_ltm_lookback_days.setter
    def auto_enable_chat_ltm_lookback_days(self, value: int) -> None:
        """Set lookback days (>=0; 0 = SDK 15-min default) and persist."""
        v = int(value)
        if v < 0:
            raise ValueError("auto_enable_chat_ltm_lookback_days must be >= 0")
        self.config.auto_enable_chat_ltm_lookback_days = v
        self.save()

