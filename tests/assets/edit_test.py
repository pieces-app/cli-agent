import pytest
from tests.utils import SCRIPT_NAME
from unittest.mock import patch
from pieces.app import main
from pieces._vendor.pieces_os_client.models.classification_specific_enum import (
    ClassificationSpecificEnum,
)


@pytest.fixture
def mock_sys_argv_edit():
    with patch("sys.argv", [SCRIPT_NAME, "edit"]):
        yield


def test_edit_asset_with_new_name(mocked_asset, mock_sys_argv_edit, mock_input):
    mock_input.side_effect = ["New Asset Name", ""]
    main()

    assert mocked_asset.name == "New Asset Name"
    assert mocked_asset.classification == ClassificationSpecificEnum.JS


def test_edit_asset_with_new_classification(
    mocked_asset, mock_sys_argv_edit, mock_input
):
    mock_input.side_effect = ["", "bat"]
    main()

    assert mocked_asset.name == "Old Asset Name"
    assert mocked_asset.classification == ClassificationSpecificEnum.BAT


def test_edit_asset_with_both_new_values(mocked_asset, mock_sys_argv_edit, mock_input):
    mock_input.side_effect = ["New Asset Name", "bat"]
    main()

    assert mocked_asset.name == "New Asset Name"
    assert mocked_asset.classification == ClassificationSpecificEnum.BAT


def test_edit_asset_with_no_changes(mocked_asset, mock_sys_argv_edit, mock_input):
    mock_input.side_effect = ["", ""]
    main()

    assert mocked_asset.name == "Old Asset Name"
    assert mocked_asset.classification == ClassificationSpecificEnum.JS
