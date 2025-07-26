import pytest
from unittest.mock import patch, Mock
import sys
from pathlib import Path

SCRIPT_NAME = "src/pieces"
ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from pieces._vendor.pieces_os_client.models.classification_specific_enum import (
    ClassificationSpecificEnum,
)


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
