from tests.base_test import BaseTestCase,SCRIPT_NAME
from io import StringIO
import sys
import unittest
from unittest.mock import patch, Mock

from pieces.app import main
from pieces.commands.assets_command import AssetsCommands

MODULE_NAME = "pieces.commands.list_command"
OPEN_MODULE_NAME = "pieces.commands.assets_command"

class ListAssetsTest(BaseTestCase):
    @patch('sys.argv', [SCRIPT_NAME, "list", "assets"])
    @patch(f"{MODULE_NAME}.Settings")
    def test_list_assets(self, mock_settings):
        def main_func():
            mock_settings.pieces_client = self.mock_api_client()
            main()
        # Prepare expected arguments for PiecesSelectMenu
        expected_assets = [
            (f"{i}: {asset.name}", {
                "ITEM_INDEX": i,
                "show_warning": False
            })
            for i, asset in enumerate(self.mock_assets(), start=1)
        ]
        self.mock_select_menus(
            main_func,
            MODULE_NAME,
            expected_assets,
            None,AssetsCommands.open_asset
        )


    @patch(f'{OPEN_MODULE_NAME}.Settings.pieces_client.assets')
    @patch(f'{OPEN_MODULE_NAME}.subprocess.run')
    @patch(f'{OPEN_MODULE_NAME}.ConfigCommands.load_config')
    def test_open_asset_success(self, mock_load_config, mock_run, mock_assets):

        mock_assets.return_value = [self.mock_create_assets()]
        mock_load_config.return_value = {'editor': '<editor_command>'}
        result = AssetsCommands.open_asset(ITEM_INDEX=1, editor=True)

        self.assertIsNone(result)  # Assuming the method returns None on success
        mock_run.assert_called_once()  # Check if the editor was called




if __name__ == '__main__':
    unittest.main()