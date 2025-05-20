import pytest
from pieces.app import main
from tests.utils import capture_stderr, restore_stderr, mock_select_menus, SCRIPT_NAME
from unittest.mock import patch, Mock
from pieces.settings import Settings
import sys
from pieces.commands.assets_command import AssetsCommands

MODULE_NAME = "pieces.commands.list_command"
OPEN_MODULE_NAME = "pieces.commands.assets_command"


@pytest.fixture
def mock_sys_argv_drive():
    with patch("sys.argv", [SCRIPT_NAME, "drive"]):
        yield


def test_list_assets(mock_api_client, mock_assets, mock_settings, mock_sys_argv_drive):
    def main_func():
        with (
            patch(f"{MODULE_NAME}.Settings.pieces_client", mock_api_client),
            patch(f"{MODULE_NAME}.BasicAsset") as mock_basic_asset,
        ):
            mock_basic_asset.get_identifiers.return_value = mock_assets
            main()
            Settings.logger.debug(mock_api_client)

    expected_assets = [
        (f"{i}: {asset.name}", {"ITEM_INDEX": i, "show_warning": False})
        for i, asset in enumerate(mock_assets, start=1)
    ]

    # Call the mock select menus
    mock_select_menus(
        main_func, MODULE_NAME, [], None, AssetsCommands.open_asset, expected_assets
    )


@patch("shutil.which")
@patch(f"{OPEN_MODULE_NAME}.BasicAsset")
@patch(f"{OPEN_MODULE_NAME}.Settings.pieces_client.assets")
@patch(f"{OPEN_MODULE_NAME}.subprocess.run")
@patch(f"{OPEN_MODULE_NAME}.ConfigCommands.load_config")
def test_open_asset_success(
    mock_load_config, mock_run, mock_assets, mock_basic_asset, mock_sh
):
    mock_basic_asset.raw_content.return_value = "content"
    mock_sh.return_value = "path_to_editor"
    mock_assets.return_value = [Mock(id="test_id", name="Test Asset")]
    mock_load_config.return_value = {"editor": "<editor_command>"}
    result = AssetsCommands.open_asset(mock_assets.id, ITEM_INDEX=1, editor=True)

    assert result is None
    mock_run.assert_called_once()
