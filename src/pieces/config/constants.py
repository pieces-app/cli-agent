"""
Shared constants for configuration paths.
"""

import platform
from pathlib import Path
from platformdirs import user_data_dir

# Base data directory (new location)
PIECES_DATA_DIR = Path(user_data_dir("pieces-cli", "pieces", ensure_exists=True))

# Legacy data directory (old location)
OLD_PIECES_DATA_DIR = Path(user_data_dir("cli-agent", "pieces"))


def get_pieces_os_data_dir() -> Path:
    """Return the Pieces OS database directory for the current platform.

    Per docs.pieces.app:
    - macOS: ~/Library/com.pieces.os/
    - Windows: ~/Documents/com.pieces.os/
    - Linux: ~/.local/share/com.pieces.os/
    """
    home = Path.home()
    system = platform.system()
    if system == "Darwin":
        return home / "Library" / "com.pieces.os"
    if system == "Windows":
        return home / "Documents" / "com.pieces.os"
    if system == "Linux":
        return home / ".local" / "share" / "com.pieces.os"
    # Fallback for unknown platforms
    return home / ".local" / "share" / "com.pieces.os"


# Individual configuration file paths
CLI_CONFIG_PATH = PIECES_DATA_DIR / "cli.json"
MODEL_CONFIG_PATH = PIECES_DATA_DIR / "model.json"
MCP_CONFIG_PATH = PIECES_DATA_DIR / "mcp.json"
USER_CONFIG_PATH = PIECES_DATA_DIR / "user.json"

__all__ = [
    "PIECES_DATA_DIR",
    "OLD_PIECES_DATA_DIR",
    "get_pieces_os_data_dir",
    "CLI_CONFIG_PATH",
    "MODEL_CONFIG_PATH",
    "MCP_CONFIG_PATH",
    "USER_CONFIG_PATH",
]

