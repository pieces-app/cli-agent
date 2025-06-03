import pytest
from unittest.mock import patch, Mock

from pieces.core.assets_command import AssetsCommands
from pieces_os_client.models.classification_specific_enum import (
    ClassificationSpecificEnum,
)

from pieces.settings import Settings

SCRIPT_NAME = "src/pieces"


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
    mock_asset = Mock()
    mock_asset.name = "Old Asset Name"
    mock_asset.classification = ClassificationSpecificEnum.JS
    AssetsCommands.current_asset = mock_asset  # noqa: F821
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
    with patch("pieces.settings.Settings") as mock:
        Settings.startup = Mock()
