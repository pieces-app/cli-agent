"""
Migration utilities for moving from old JSON configs to new config system.

Usage:
    from pieces.config import run_migration
    from pathlib import Path

    success = run_migration()
"""

import json
import shutil
from pathlib import Path
from typing import Dict
from ..settings import Settings
from .constants import (
    MCP_CONFIG_PATH,
    OLD_PIECES_DATA_DIR,
    PIECES_DATA_DIR,
)


class ConfigMigrator:
    """Handles migration from old JSON configs to new config system."""

    def __init__(
        self,
        pieces_data_dir: Path = PIECES_DATA_DIR,
        old_data_dir: Path = OLD_PIECES_DATA_DIR,
    ):
        """
        Initialize migrator.

        Args:
            pieces_data_dir: Path to existing pieces data directory
        """
        self.pieces_data_dir = Path(pieces_data_dir)
        self.old_data_dir = Path(old_data_dir)
        self.logger = Settings.logger

    def migrate_all(self) -> bool:
        """
        Migrate all configurations to new system.

        Args:
            new_config_dir: Directory for new configuration files

        Returns:
            True if migration successful
        """
        success = True

        if not self.get_migration_status()["cli_config"]:
            if not self._migrate_cli_config():
                success = False

        if not self.get_migration_status()["mcp_config"]:
            if not self._copy_mcp_config():
                success = False

        return success

    def _migrate_cli_config(self) -> bool:
        """Migrate pieces_config.json to new CLIConfigSchema if needed."""
        old_config_path = self.pieces_data_dir / "pieces_config.json"

        if not old_config_path.exists():
            self.logger.info("No pieces_config.json found, creating default CLI config")
            return True

        try:
            # Load old config
            with open(old_config_path, "r", encoding="utf-8") as f:
                old_data = json.load(f)

            self.logger.info(f"Migrating CLI config from {old_config_path}")

            Settings.cli_config.config.editor = old_data.get("editor", None)
            Settings.user_config.skip_onboarding = old_data.get(
                "skip_onboarding", False
            )

            return Settings.cli_config.save()

        except Exception as e:
            self.logger.error(f"Failed to migrate CLI config: {e}")
            return False

    def _copy_mcp_config(self) -> bool:
        """Copy MCP config (no migration needed - same format)."""
        old_mcp_path = self.pieces_data_dir / "mcp_config.json"

        if not old_mcp_path.exists():
            self.logger.info("No mcp_config.json found, creating default MCP config")

        try:
            self.logger.info(f"Copying MCP config from {old_mcp_path}")

            # Simply copy the file since format is the same
            import shutil

            shutil.copy2(old_mcp_path, MCP_CONFIG_PATH)
            return True

        except Exception as e:
            self.logger.error(f"Failed to copy MCP config: {e}")
            return False

    def needs_migration(self) -> bool:
        """Check if migration is needed."""
        old_files = [
            self.old_data_dir / "pieces_config.json",
            self.old_data_dir / "mcp_config.json",
        ]
        return any(f.exists() for f in old_files)

    def get_migration_status(self) -> Dict[str, bool]:
        """Get status of what needs migration."""
        return {
            "cli_config": not (self.pieces_data_dir / "pieces_config.json").exists(),
            "mcp_config": not (self.pieces_data_dir / "mcp_config.json").exists(),
        }


def run_migration() -> bool:
    """
    Convenience function to run full migration.

    Args:
        old_data_dir: Path to existing pieces data directory
        new_config_dir: Directory for new configuration files

    Returns:
        True if migration successful
    """
    migrator = ConfigMigrator(OLD_PIECES_DATA_DIR)

    if not migrator.needs_migration():
        Settings.logger.info("No migration needed, all configurations are up to date.")
        return True

    backup_successful = False
    try:
        if OLD_PIECES_DATA_DIR.exists() and OLD_PIECES_DATA_DIR.is_dir():
            backup_base = PIECES_DATA_DIR / "legacy_backup"
            backup_path = shutil.make_archive(
                str(backup_base), "zip", root_dir=OLD_PIECES_DATA_DIR
            )
            Settings.logger.info(f"Legacy data directory backed up at {backup_path}")
            backup_successful = True
    except Exception as e:
        Settings.logger.error(f"Failed to backup legacy directory: {e}")

    success = migrator.migrate_all()

    if success:
        Settings.logger.info("Configuration migration completed successfully!")
        if backup_successful:
            try:
                shutil.rmtree(OLD_PIECES_DATA_DIR)
                Settings.logger.info(
                    "Legacy data directory removed after successful migration."
                )
            except Exception as e:
                Settings.logger.print(
                    f"[red]Could not remove legacy directory, Please remove it manually.[/red]"
                )
                Settings.logger.print(
                    f"[yellow]Legacy directory: {OLD_PIECES_DATA_DIR}[/yellow]"
                )
                Settings.logger.info(f"Could not remove legacy directory: {e}")
    else:
        Settings.logger.error("Configuration migration failed!")

    return success
