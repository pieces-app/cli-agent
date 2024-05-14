import unittest
from unittest.mock import patch, MagicMock
from pieces.assets import AssetsCommands,AssetsCommandsApi
from pieces.settings import Settings
import sys
from io import StringIO
import random,os
import json
from pieces.utils import sanitize_filename

class TestOpenCommand(unittest.TestCase):
    def test_open_command(self):
        Settings.startup()

        stdout = sys.stdout
        sys.stdout = StringIO()


        assets_length = len(AssetsCommandsApi.get_assets_snapshot())


        sys.stdout = StringIO()
        idx = random.randint(1,assets_length)
        # Act
        AssetsCommands.open_asset(ITEM_INDEX = idx)

        result_open = sys.stdout.getvalue()
        
        sys.stdout = stdout  # Reset sys.stdout to its original state

        result_list = result_open.strip().split('\n')

        name = result_list[-6].removeprefix('Name: ')
        created_readable = result_list[-5].removeprefix('Created: ')
        updated_readable = result_list[-4].removeprefix('Updated: ')
        type = result_list[-3].removeprefix('Type: ')
        language = result_list[-2].removeprefix('Language: ')
        code_snippet_path = result_list[-1].removeprefix('Code: ')


        with open(Settings.extensions_dir) as f:
            language_extension_mapping = json.load(f)
        self.assertTrue(os.path.exists(code_snippet_path))  # assert that the code snippet file exists
        self.assertEqual(os.path.splitext(code_snippet_path)[-1], language_extension_mapping[language])  # assert that the file extension matches the language
        self.assertEqual(os.path.splitext(os.path.basename(code_snippet_path))[0], sanitize_filename(name))


if __name__ == '__main__':
    unittest.main()
        

        