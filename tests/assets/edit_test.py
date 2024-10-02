from os import name
import unittest
from unittest.mock import patch, MagicMock

from pieces_os_client.models.classification_specific_enum import ClassificationSpecificEnum
from pieces.commands.assets_command import AssetsCommands
from tests.base_test import BaseTestCase, SCRIPT_NAME
from pieces.app import main

class TestEditAsset(BaseTestCase):
    def setUp(self):
        self.new_name = "New Asset Name"
        self.old_name = "Old Asset Name"
        self.new_classification = ClassificationSpecificEnum.BAT
        self.old_classification = ClassificationSpecificEnum.JS
        self._mocked_asset = self.mock_create_assets(name=self.old_name,
            classification=self.old_classification)
        AssetsCommands.current_asset = self._mocked_asset

    @patch('sys.argv', [SCRIPT_NAME, "edit"])
    @patch('builtins.input', side_effect=['New Asset Name', ''])
    def test_edit_asset_with_new_name(self, mock_input):
        main()
        
        self.assertEqual(self._mocked_asset.name, self.new_name)
        self.assertEqual(self._mocked_asset.classification, self.old_classification)

    @patch('sys.argv', [SCRIPT_NAME, "edit"])
    @patch('builtins.input', side_effect=['', 'bat'])
    def test_edit_asset_with_new_classification(self, mock_input):
        main()

        self.assertEqual(self._mocked_asset.name, self.old_name)
        self.assertEqual(self._mocked_asset.classification, self.new_classification)

    @patch('sys.argv', [SCRIPT_NAME, "edit"])
    @patch('builtins.input', side_effect=['New Asset Name', 'bat'])
    def test_edit_asset_with_both_new_values(self, mock_input):
        main()

        self.assertEqual(self._mocked_asset.name, self.new_name)
        self.assertEqual(self._mocked_asset.classification, self.new_classification)

    @patch('sys.argv', [SCRIPT_NAME, "edit"])
    @patch('builtins.input', side_effect=['', ''])
    def test_edit_asset_with_no_changes(self, mock_input):
        main()
        self.assertEqual(self._mocked_asset.name, self.old_name)
        self.assertEqual(self._mocked_asset.classification, self.old_classification)

if __name__ == '__main__':
    unittest.main()
