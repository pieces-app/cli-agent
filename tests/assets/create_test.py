from pieces.commands.assets_command import AssetsCommands
from tests.base_test import BaseTestCase,SCRIPT_NAME
from io import StringIO
import sys
import unittest
from unittest.mock import patch, Mock

from pieces.app import main

MODULE_NAME = "pieces.commands.assets_command"


class TestCreateAsset(BaseTestCase):
    def setUp(self):
        self.asset_patcher = patch(f'{MODULE_NAME}.BasicAsset')
        self.mock_basic_asset = self.asset_patcher.start()

    def tearDown(self):
        self.asset_patcher.stop()

    @patch('sys.argv', [SCRIPT_NAME, "create"])
    @patch(f'{MODULE_NAME}.pyperclip.paste')
    @patch('builtins.input') 
    def test_create_asset_save(self, mock_input, mock_paste):
        mock_paste.return_value = 'Mocked clipboard content'
        mock_input.return_value = 'y'
        main()

        # Check if asset was created
        self.mock_basic_asset.create.assert_called_with(raw_content='Mocked clipboard content', metadata=None)
        self.assertIsNotNone(AssetsCommands.current_asset)

    @patch('sys.argv', [SCRIPT_NAME, "create"])
    @patch(f'{MODULE_NAME}.pyperclip.paste')
    @patch('builtins.input')
    def test_create_asset_cancel(self, mock_input, mock_paste):
        mock_paste.return_value = 'Mocked clipboard content'


        mock_input.return_value = 'n'

        main()

        self.assertIsNone(AssetsCommands.current_asset)

    @patch('sys.argv', [SCRIPT_NAME, "create"])
    @patch(f'{MODULE_NAME}.pyperclip.paste')
    @patch('builtins.input')
    def test_create_asset_invalid_input(self, mock_input, mock_paste):
        mock_paste.return_value = 'Mocked clipboard content'

        mock_input.return_value = 'x'

        with patch('builtins.print') as mocked_print:
            main()
            self.assertIsNone(AssetsCommands.current_asset)
            mocked_print.assert_any_call("Invalid input. Please type 'y' to save or 'n' to cancel.")
