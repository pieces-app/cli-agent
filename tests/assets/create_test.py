import pytest
from io import StringIO
from pieces.app import main
from tests.utils import run_main_with_args
from unittest.mock import patch, Mock


def assert_asset_created(mock_basic_asset, content):
    mock_basic_asset.create.assert_called_with(raw_content=content, metadata=None)
    mock_basic_asset.create.assert_called_once()


def test_create_asset_save(mock_basic_asset, mock_pyperclip_paste, mock_input):
    mock_pyperclip_paste.return_value = "Mocked clipboard content"
    mock_input.return_value = "y"
    run_main_with_args(["create"], main)

    assert_asset_created(mock_basic_asset, "Mocked clipboard content")


def test_create_asset_cancel(mock_basic_asset, mock_pyperclip_paste, mock_input):
    mock_pyperclip_paste.return_value = "Mocked clipboard content"
    mock_input.return_value = "n"
    run_main_with_args(["create"], main)

    mock_basic_asset.create.assert_not_called()


def test_create_asset_invalid_input(mock_basic_asset, mock_pyperclip_paste, mock_input):
    mock_pyperclip_paste.return_value = "Mocked clipboard content"
    mock_input.side_effect = ["x", "x", "x", "x", "n"]

    with patch("pieces.logger.Logger.confirm") as mocked_print:
        run_main_with_args(["create"], main)
        mocked_print.assert_any_call("Do you want to save this content?")


def test_create_asset_with_c_flag(mock_basic_asset):
    input_text = "Content from stdin"
    with patch("sys.stdin", new=StringIO(input_text)):
        run_main_with_args(["create", "-c"], main)

    assert_asset_created(mock_basic_asset, input_text)


def test_create_asset_with_existing_assets(
    mock_basic_asset, mock_assets, mock_pyperclip_paste, mock_input
):
    mock_pyperclip_paste.return_value = "New Asset Content"
    mock_input.return_value = "y"
    run_main_with_args(["create"], main)

    # Verify that a new asset is created
    assert_asset_created(mock_basic_asset, "New Asset Content")

    # Verify that existing assets are not affected
    for asset in mock_assets:
        asset.create.assert_not_called()
