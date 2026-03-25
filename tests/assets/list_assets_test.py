import pytest
from unittest.mock import patch, Mock
from pieces.settings import Settings
from pieces.core.assets_command import AssetsCommands
from pieces.core.list_command import ListCommand

MODULE_NAME = "pieces.core.list_command"
OPEN_MODULE_NAME = "pieces.core.assets_command"


@patch("pieces.utils.PiecesSelectMenu")
@patch(f"{MODULE_NAME}.BasicAsset")
@patch(f"{OPEN_MODULE_NAME}.Settings.pieces_client.assets")
def test_list_assets_builds_menu_entries_from_default_asset_lookup(
    mock_assets_api, mock_basic_asset, mock_menu_cls, mock_assets
):
    mock_assets_api.return_value = mock_assets
    mock_basic_asset.get_identifiers.return_value = [
        Mock(id=asset.id) for asset in mock_assets
    ]
    mock_basic_asset.side_effect = lambda asset_id: next(
        asset for asset in mock_assets if asset.id == asset_id
    )

    ListCommand.list_assets()

    mock_menu_cls.assert_called_once()
    menu_entries, on_enter, footer = mock_menu_cls.call_args.args

    assert footer is None
    assert on_enter == AssetsCommands.open_asset
    assert [label for label, _ in menu_entries] == [
        f"{index}: {asset.name}" for index, asset in enumerate(mock_assets, start=1)
    ]
    assert [payload["asset_id"] for _, payload in menu_entries] == [
        asset.id for asset in mock_assets
    ]
    mock_menu_cls.return_value.run.assert_called_once()


@patch("shutil.which")
@patch(f"{OPEN_MODULE_NAME}.BasicAsset")
@patch(f"{OPEN_MODULE_NAME}.Settings.pieces_client.assets")
@patch(f"{OPEN_MODULE_NAME}.subprocess.run")
def test_open_asset_success(mock_run, mock_assets, mock_basic_asset, mock_sh, tmp_path):
    """Ensure open_asset opens the asset in the configured editor using the new
    Settings.cli_config approach.

    The legacy ConfigCommands.load_config helper has been removed, so the test now
    patches Settings.cli_config.editor directly. A temporary directory is used
    for `Settings.open_snippet_dir` to avoid filesystem side-effects."""

    # Configure the fake editor and BasicAsset mocks
    mock_sh.return_value = "path_to_editor"
    mock_assets.return_value = [Mock(id="test_id", name="Test Asset")]

    mock_asset_instance = Mock()
    mock_asset_instance.raw_content = "content"
    mock_asset_instance.classification = "python"
    mock_basic_asset.return_value = mock_asset_instance

    # Point the snippet directory to a temporary path and set the editor
    Settings.open_snippet_dir = str(tmp_path)
    Settings.cli_config.editor = "dummy_editor"

    result = AssetsCommands.open_asset("test_id", ITEM_INDEX=1, editor=True)

    assert result is None
    mock_run.assert_called_once()


@patch("pieces.utils.PiecesSelectMenu")
@patch(f"{OPEN_MODULE_NAME}.Settings.pieces_client.assets")
def test_list_assets_builds_menu_entries_with_asset_ids(
    mock_assets_api, mock_menu_cls, mock_assets
):
    mock_assets_api.return_value = mock_assets

    ListCommand.list_assets(assets=mock_assets, footer="Search results")

    mock_menu_cls.assert_called_once()
    menu_entries, on_enter, footer = mock_menu_cls.call_args.args

    assert footer == "Search results"
    assert on_enter == AssetsCommands.open_asset
    assert len(menu_entries) == len(mock_assets)
    assert [label for label, _ in menu_entries] == [
        f"{index}: {asset.name}" for index, asset in enumerate(mock_assets, start=1)
    ]
    assert [payload["asset_id"] for _, payload in menu_entries] == [
        asset.id for asset in mock_assets
    ]
    mock_menu_cls.return_value.run.assert_called_once()
    mock_menu_cls.return_value.add_entry.assert_not_called()


@patch.object(Settings, "logger")
@patch("pieces.utils.PiecesSelectMenu")
@patch(f"{OPEN_MODULE_NAME}.Settings.pieces_client.assets")
def test_list_assets_skips_menu_when_no_entries_can_be_built(
    mock_assets_api, mock_menu_cls, mock_logger
):
    mock_assets_api.return_value = [object()]

    ListCommand.list_assets(assets=[object()])

    mock_menu_cls.assert_not_called()
    mock_logger.print.assert_called_once_with("No materials available to select.")
