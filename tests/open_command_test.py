import unittest
from unittest.mock import patch, MagicMock
from pieces.commands.commands_functions import startup,open_asset,list_assets
import sys
from io import StringIO
import random,os
import json
from pieces.commands.commands_functions import sanitize_filename

class TestAskCommand(unittest.TestCase):
    @patch('pieces.commands.commands_functions.open_asset')
    def test_open_command(self, mock_open_question):
        # get all the list assets 
        startup()

        stdout = sys.stdout
        sys.stdout = StringIO()

        list_assets()

        # Get the output and restore stdout
        result_list = sys.stdout.getvalue()

        assets_length = len(result_list.strip().split('\n'))


        sys.stdout = StringIO()
        # Act
        open_asset(ITEM_INDEX =random.randint(1,assets_length))

        result_open = sys.stdout.getvalue()
        sys.stdout = stdout  # Reset sys.stdout to its original state

        result_list = result_open.strip().split('\n')

        name = result_list[-6].removeprefix('Name: ')
        created_readable = result_list[-5].removeprefix('Created: ')
        updated_readable = result_list[-4].removeprefix('Updated: ')
        type = result_list[-3].removeprefix('Type: ')
        language = result_list[-2].removeprefix('Language: ')
        code_snippet_path = result_list[-1].removeprefix('Code: ')


        with open("src/pieces/commands/extensions.json") as f:
            language_extension_mapping = json.load(f)
        self.assertTrue(os.path.exists(code_snippet_path))  # assert that the code snippet file exists
        self.assertEqual(os.path.splitext(code_snippet_path)[-1], language_extension_mapping[language])  # assert that the file extension matches the language
        self.assertEqual(os.path.splitext(os.path.basename(code_snippet_path))[0], sanitize_filename(name))

        

        