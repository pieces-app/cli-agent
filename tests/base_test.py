"""
This is a base class which will be used to mock the api client
"""
import sys
import unittest
from unittest.mock import Mock,patch

from pieces_os_client.models.classification_specific_enum import ClassificationSpecificEnum

# Import all the API classes
from pieces.wrapper.basic_identifier.asset import BasicAsset
from pieces.settings import Settings


SCRIPT_NAME = "src/pieces"

class BaseTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._out = sys.stdout

        # Create class-level patches
        cls.settings_patcher = patch('pieces.app.Settings')

        # Start the patches
        cls.mock_settings = cls.settings_patcher.start()
        cls.mock_settings.startup = Mock() # Remove the startup
        
        # Assign the mock_api_client to the mock_settings instance
        cls.mock_settings.pieces_client = cls.mock_api_client()

    def mock_select_menus(self,
        main_func,
        module,
        expected_select_options,
        expected_footer,
        expected_on_enter):
        with patch(f"{module}.PiecesSelectMenu") as mock_menu:
            main_func()
            # Check that PiecesSelectMenu was called with the expected arguments
            mock_menu.assert_called_once()

            # Get the actual call arguments
            
            actual_select_options,actual_on_enter,actual_footer = mock_menu.call_args.args
            self.assertEqual(actual_footer, expected_footer)
            self.assertEqual(actual_on_enter, expected_on_enter)

            actual_list_items, actual_args_used = zip(*actual_select_options) 
            expected_list_items, expected_args_used = zip(*expected_select_options)
            self.assertEqual(actual_list_items,expected_list_items)

            for idx in range(len(expected_args_used)): 
                for key,val in expected_args_used[idx].items():
                    self.assertEqual(actual_args_used[idx][key],val)

    @classmethod
    def mock_assets(cls):
        return [cls.mock_create_assets(
            id=f"{i}_id",
            name=f"{i}_name",
            raw_content=f"{i} Content",
            classification=ClassificationSpecificEnum.PY) 
        for i in range(4)]

    @classmethod
    def mock_api_client(cls):
        mock = Mock()
        mock.assets.return_value = cls.mock_assets()
        return mock

    @classmethod
    def tearDownClass(cls):
        # Stop the patches
        cls.settings_patcher.stop()

    @classmethod
    def print(cls,*args):
        cls._out.write(f"{'\n'.join(args)}")


    @classmethod
    def mock_create_assets(
        cls,
        id ="test_id",
        name = "Test Asset",
        raw_content = "Test content",
        classification=ClassificationSpecificEnum.PY):
        """
            Generates a mock asset
        """

        mock_asset = Mock(spec=BasicAsset)
        mock_asset.id = id
        mock_asset.name = name
        mock_asset.raw_content = raw_content
        mock_asset.classification = classification
        return mock_asset

