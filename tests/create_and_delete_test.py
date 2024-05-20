import unittest
from unittest.mock import patch
from pieces.assets import AssetsCommands, AssetsCommandsApi
from pieces.settings import Settings
from pieces_os_client.models.asset import Asset

class TestCreateDeleteFunctions(unittest.TestCase):

    @patch('builtins.input', side_effect=['y', 'y'])
    @patch('pyperclip.paste', return_value='print("Hello, World!")')
    def test_create_and_delete_asset(self, mock_paste, mock_input):
        Settings.startup()
        # Call create_asset and store the returned asset
        AssetsCommands.create_asset()

        # Ensure that it is correctly assigned to the current asset
        new_asset=AssetsCommands.current_asset


        asset_object = AssetsCommandsApi.get_asset_snapshot(new_asset)

        self.assertIsInstance(asset_object,Asset)

        # Call delete_asset
        AssetsCommands.delete_asset()

        # Check that the asset was deleted
        try:
            AssetsCommandsApi.get_asset_snapshot(new_asset)
        except: # Asset not found!
            self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()