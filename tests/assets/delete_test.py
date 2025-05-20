import pytest
from pieces.app import main
from tests.utils import run_main_with_args
from pieces.commands.assets_command import AssetsCommands


def assert_asset_deleted(mocked_asset):
    mocked_asset.delete.assert_called_once()


def test_delete_asset_success(mocked_asset, mock_input):
    mock_input.side_effect = ["y"]
    AssetsCommands.current_asset = mocked_asset
    run_main_with_args(["delete"], main)

    assert_asset_deleted(mocked_asset)
    assert AssetsCommands.current_asset is None


def test_delete_asset_cancelled(mocked_asset, mock_input):
    mock_input.side_effect = ["n"]
    AssetsCommands.current_asset = mocked_asset
    run_main_with_args(["delete"], main)

    mocked_asset.delete.assert_not_called()
    assert AssetsCommands.current_asset is not None


def test_delete_specific_asset(mocked_asset, mock_assets, mock_input):
    asset_to_delete = mock_assets[0]
    AssetsCommands.current_asset = asset_to_delete

    mock_input.side_effect = ["y"]
    run_main_with_args(["delete"], main)

    asset_to_delete.delete.assert_called_once()

    for asset in mock_assets[1:]:
        asset.delete.assert_not_called()
