"""
Shared constants for configuration paths.
"""

from pathlib import Path
from platformdirs import user_data_dir

# Base data directory (new location)
PIECES_DATA_DIR = Path(user_data_dir("pieces-cli", "pieces", ensure_exists=True))

# Legacy data directory (old location)
OLD_PIECES_DATA_DIR = Path(user_data_dir("cli-agent", "pieces"))

# Individual configuration file paths
CLI_CONFIG_PATH = PIECES_DATA_DIR / "cli.json"
MODEL_CONFIG_PATH = PIECES_DATA_DIR / "model.json"
MCP_CONFIG_PATH = PIECES_DATA_DIR / "mcp.json"
USER_CONFIG_PATH = PIECES_DATA_DIR / "user.json"

__all__ = [
    "PIECES_DATA_DIR",
    "OLD_PIECES_DATA_DIR",
    "CLI_CONFIG_PATH",
    "MODEL_CONFIG_PATH",
    "MCP_CONFIG_PATH",
    "USER_CONFIG_PATH",
]

