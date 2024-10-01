from pieces.commands.assets_command import AssetsCommands
from tests.base_test import BaseTestCase,SCRIPT_NAME
from io import StringIO
import sys
import unittest
from unittest.mock import patch, Mock

from pieces.app import main


class TestDeleteAsset(BaseTestCase):
    def setUp(self):
        self._mocked_asset = self.mock_create_assets()
        AssetsCommands.current_asset = self._mocked_asset
        
        

    @patch('sys.argv', [SCRIPT_NAME, "delete"])
    @patch('builtins.input', side_effect=['y']) 
    def test_delete_asset_success(self, mock_input):
        main()
        self._mocked_asset.delete.assert_called_once()
        self.assertIsNone(AssetsCommands.current_asset)

    @patch('sys.argv', [SCRIPT_NAME, "delete"])
    @patch('builtins.input', side_effect=['n']) 
    def test_delete_asset_cancelled(self, mock_input):
        main()
        self._mocked_asset.delete.assert_not_called()
        self.assertIsNotNone(AssetsCommands.current_asset)

    @patch('sys.argv', [SCRIPT_NAME, "delete"])
    @patch('builtins.input', side_effect=['x'])
    def test_delete_asset_invalid_input(self, mock_input):
        main()
        self._mocked_asset.delete.assert_not_called()
        self.assertIsNotNone(AssetsCommands.current_asset)

if __name__ == '__main__':
    unittest.main()
