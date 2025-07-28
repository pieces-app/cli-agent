import pytest
from unittest.mock import patch, Mock
import sys
import os
from pathlib import Path

SCRIPT_NAME = "src/pieces"
ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from pieces._vendor.pieces_os_client.models.classification_specific_enum import (
    ClassificationSpecificEnum,
)
from pieces.config.constants import PIECES_DATA_DIR
from pieces.logger import Logger


@pytest.fixture(autouse=True)
def mock_sys_exit():
    """Mock sys.exit globally to prevent tests from actually exiting."""
    with patch("sys.exit") as mock_exit:
        yield mock_exit


@pytest.fixture(autouse=True)
def mock_settings_startup():
    """Mock Settings.startup to prevent PiecesOS connection during tests."""
    from pieces.settings import Settings

    with patch.object(Settings, "startup"):
        yield


@pytest.fixture(autouse=True)
def mock_pieces_client():
    """Mock the pieces client to prevent actual API calls during tests."""
    from pieces.settings import Settings

    mock_client = Mock()
    mock_client.is_pieces_running.return_value = True
    with patch.object(Settings, "pieces_client", mock_client):
        yield mock_client


@pytest.fixture(autouse=True)
def mock_headless_mode():
    """Set headless_mode to False by default for all tests."""
    from pieces.settings import Settings

    with patch.object(Settings, "headless_mode", False):
        yield


@pytest.fixture
def mock_input():
    with patch("builtins.input") as mock:
        yield mock


@pytest.fixture
def mock_basic_asset():
    with patch("pieces.core.assets_command.BasicAsset") as mock:
        yield mock


@pytest.fixture
def mock_pyperclip_paste():
    with patch("pieces.core.assets_command.pyperclip.paste") as mock:
        yield mock


@pytest.fixture
def mocked_asset():
    # Import lazily to avoid heavy module import at collection time
    from pieces.core.assets_command import AssetsCommands  # noqa: E402

    mock_asset = Mock()
    mock_asset.name = "Old Asset Name"
    mock_asset.classification = ClassificationSpecificEnum.JS
    AssetsCommands.current_asset = mock_asset
    yield mock_asset
    AssetsCommands.current_asset = None


@pytest.fixture
def mock_assets():
    """Fixture to create a list of mock assets."""
    return [
        Mock(id=f"{i}_id", name=f"Asset {i}", raw_content=f"Content {i}")
        for i in range(5)
    ]


@pytest.fixture
def mock_api_client(mock_assets):
    mock_client = Mock()
    mock_client.assets.return_value = mock_assets
    return mock_client


@pytest.fixture()
def mock_settings():
    from pieces.settings import Settings

    with patch("pieces.settings.Settings") as mock:
        Settings.startup = Mock()


@pytest.fixture(autouse=True)
def test_logger():
    """
    Ensure all tests use a real logger that logs to test_logs directory
    instead of the production logger. This provides real logging for better
    test output while keeping logs separate from production.
    """
    # Create a real logger instance for tests with debug mode enabled
    real_logger = Logger(True, os.path.join(PIECES_DATA_DIR, "test_logs"))

    # Patch Logger.get_instance() to return our test logger
    with patch.object(Logger, "get_instance", return_value=real_logger):
        # Also patch Settings.logger to use our test logger
        with patch("pieces.settings.Settings.logger", real_logger):
            yield real_logger

    # Cleanup: Close file handler if it exists to prevent file handle leaks
    if hasattr(real_logger, "file_handler") and real_logger.file_handler:
        real_logger.file_handler.close()
        real_logger.logger.removeHandler(real_logger.file_handler)
