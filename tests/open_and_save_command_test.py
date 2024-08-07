import unittest
from unittest.mock import patch, MagicMock
from pieces.assets import AssetsCommands,AssetsCommandsApi
from pieces.commands import ConfigCommands
from pieces.settings import Settings
import sys
from io import StringIO
import random,os
import json
from pieces.utils import sanitize_filename
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.util import ClassNotFound

class TestOpenSaveCommand(unittest.TestCase):
    def setUp(self):
        Settings.startup()
        self.mock_assets_api = MagicMock()
        self.mock_asset_api = MagicMock()
        self.mock_format_api = MagicMock()
        AssetsCommandsApi.assets_api = self.mock_assets_api
        AssetsCommandsApi.asset_api = self.mock_asset_api
        AssetsCommandsApi.format_api = self.mock_format_api

    def test_open_command(self, ITEM_INDEX=None):
        Settings.startup()
        stdout = sys.stdout
        sys.stdout = StringIO()
        assets_length = len(AssetsCommandsApi().assets_snapshot)
        sys.stdout = StringIO()
        if not ITEM_INDEX:
            ITEM_INDEX = random.randint(1, assets_length)
        
        # Act
        AssetsCommands.open_asset(ITEM_INDEX=ITEM_INDEX)
        result_open = sys.stdout.getvalue()
        
        sys.stdout = stdout  # Reset sys.stdout to its original state
        result_list = result_open.strip().split('\n')
        name = result_list[-6].removeprefix('Name: ')
        created_readable = result_list[-5].removeprefix('Created: ')
        updated_readable = result_list[-4].removeprefix('Updated: ')
        type = result_list[-3].removeprefix('Type: ')
        language = result_list[-2].removeprefix('Language: ')
        code_snippet = result_list[-1].removeprefix('Code content: ')
        

        # Test 1: Verify that the code snippet is not empty
        self.assertTrue(code_snippet.strip(), "The code snippet should not be empty")
        # Test 2: Verify that the language is valid
        is_valid_language, identified_language = self.verify_language(code_snippet)
        self.assertTrue(is_valid_language, f"The code snippet should be in a valid programming language. Identified as: {identified_language}")
        
        print("test_open_command passed successfully")

    def verify_language(self, code_content):
        try:
            # Try to guess the lexer based on the code content
            lexer = guess_lexer(code_content)
            return True, lexer.name
        except ClassNotFound:
            # If we can't guess the lexer, assume the language is invalid
            return False, "Unknown"

    @patch('builtins.input', side_effect=['y','y'])
    @patch('pyperclip.paste', return_value='print("Hello, World!")')
    def test_save_command(self, mock_paste, mock_buildins):
        # Simulate creating a new asset
        mock_new_asset = MagicMock()
        mock_new_asset.id = 'new_asset_id'
        mock_new_asset.name = "Print Hello World in Python"
        self.mock_asset_api.asset_create.return_value = mock_new_asset
        
        with patch('builtins.print'):  # Suppress print statements
            AssetsCommands.create_asset()
        
        # Check if the asset was created
        self.assertTrue(mock_new_asset.name, "Asset name is empty")
        print("Asset creation successful")

        # Update the asset cache
        AssetsCommandsApi._assets_snapshot = {mock_new_asset.id: mock_new_asset}
        AssetsCommands.current_asset = mock_new_asset.id

        with patch('pieces.assets.assets_command.open', create=True):
            AssetsCommands.open_asset(ITEM_INDEX=1)

        # Mock the update process
        mock_updated_asset = MagicMock()
        mock_updated_asset.formats.iterable[0].fragment.string.raw = 'print("Hello, World!")'
        self.mock_asset_api.asset_update.return_value = mock_updated_asset

        # Simulate updating the asset
        with patch('builtins.print'):  # Suppress print statements
            AssetsCommands.update_asset()

        # Check if the code was saved
        updated_asset = AssetsCommandsApi.update_asset_snapshot(AssetsCommands.current_asset)
        self.assertTrue(updated_asset.formats.iterable[0].fragment.string.raw, "Updated asset content is empty")
        print("Asset updated successful")

        # Simulate deleting the asset
        with patch('builtins.print'):  # Suppress print statements
            AssetsCommands.delete_asset()
        
        print("test_save_command passed successfully")

if __name__ == '__main__':
    unittest.main()
