import unittest
from unittest.mock import patch, MagicMock
from pieces.copilot import ask
from pieces.settings import Settings
import sys
from io import StringIO
from pieces.copilot.conversations import conversation_handler

class TestAskCommand(unittest.TestCase):
    @patch('pieces.copilot.ask')
    @patch('builtins.input', return_value='y')
    def test_ask_command(self, mock_input,mock_ask_question):
        Settings.startup()
        
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

        # delete the conversation created
        conversation_handler(delete=True)
    

if __name__ == '__main__':
    unittest.main()

    