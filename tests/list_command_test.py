import unittest
from unittest.mock import patch, MagicMock,Mock
from pieces.commands.list_command import ListCommand
from pieces.settings import Settings
from io import StringIO
import sys

class TestListCommand(unittest.TestCase):
    def test_list_command(self):
        Settings.startup()
        for i in ["models","assets","apps"]:
            # Redirect stdout to a buffer
            stdout = sys.stdout
            sys.stdout = StringIO()

            # Call the function that prints to stdout
            ListCommand.list_command(type = i)

            # Get the output and restore stdout
            assets = sys.stdout.getvalue()
            sys.stdout = stdout

            # Check if the function prints a string
            self.assertIsInstance(assets, str)

            # Check if the string is not empty
            self.assertTrue(assets)

            assets_list = assets.strip().split('\n')
            
            if i == "models":
                model = assets_list[-1]
                assets_list = assets_list[:-1] # Remove the line which conatin the current model text
                self.assertEqual(model,f"Currently using: {Settings.model_name} with uuid {Settings.model_id}")
            
            # Check if the string represents a numbered list
            self.assertTrue(all(line.strip().startswith(str(i+1)) for i, line in enumerate(assets_list) if line.strip()))

if __name__ == '__main__':
    unittest.main()

