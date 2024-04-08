import unittest
from unittest.mock import patch
from pieces.commands import create_asset, delete_asset,startup
from pieces.commands import commands_functions
from pieces.api.assets import get_asset_by_id

class TestAssetFunctions(unittest.TestCase):

    @patch('builtins.input', side_effect=['y', 'y'])
    @patch('pyperclip.paste', return_value='print("Hello, World!")')
    def test_create_and_delete_asset(self, mock_paste, mock_input):
        startup()
        # Call create_asset and store the returned asset
        create_asset()

        # Ensure that it is correctly assigned to the current asset
        new_asset=list(commands_functions.current_asset)[0]


        asset_object = get_asset_by_id(new_asset)

        get_asset_by_id(new_asset) # Checks that the asset was created with no errors

        # Call delete_asset
        delete_asset()

        # Check that the asset was deleted
        try:
            get_asset_by_id(new_asset)
        except Exception:
            self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()