import unittest
from unittest.mock import patch, MagicMock
from pieces.commands.commands_functions import ask,startup
import sys
from io import StringIO

class TestAskCommand(unittest.TestCase):
    @patch('pieces.commands.commands_functions.ask')
    def test_ask_command(self, mock_ask_question):
        startup()
        
        stdout = sys.stdout
        sys.stdout = StringIO()

        # Arrange
        mock_query = 'What is the meaning of life?'

        # Act
        result = ask(mock_query)


        # Get the output and restore stdout
        result = sys.stdout.getvalue()
        sys.stdout = stdout

        # Check if the function prints a string
        self.assertIsInstance(result, str)
    

if __name__ == '__main__':
    unittest.main()

    