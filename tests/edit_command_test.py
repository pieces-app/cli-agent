import unittest
from unittest.mock import patch
from pieces.assets import AssetsCommands,AssetsCommandsApi
from pieces.settings import Settings

class TestEditCommand(unittest.TestCase):
    @patch('builtins.input', side_effect='y')
    @patch('pyperclip.paste', return_value='print("Hello, World!")')
    def test_edit_command(self,mock_paste,mock_buildins):
        Settings.startup()

        NAME = "TEST"
        CLASSIFICATION = "java"

        AssetsCommands.create_asset() # create new asset to test on

        AssetsCommands.edit_asset(name = NAME, classification=CLASSIFICATION) # change some asset meta data


        asset = AssetsCommandsApi.update_asset_snapshot(AssetsCommands.current_asset)

        self.assertEqual(asset.name,NAME)
        self.assertEqual(asset.formats.iterable[0].classification.specific.value.lower(),CLASSIFICATION.lower())

        AssetsCommands.delete_asset() # Delete the created asset


if __name__ == '__main__':
    unittest.main()

