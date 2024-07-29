import unittest
from unittest.mock import patch, MagicMock,Mock
from pieces.commands.list_command import ListCommand , PiecesSelectMenu
from pieces.settings import Settings
import io
import sys

class TestListCommand(unittest.TestCase):

    @patch('builtins.print')
    def test_list_assets(self, mock_print):
        with patch.object(ListCommand, 'list_assets') as mock_list_assets:
            ListCommand.list_command(type='assets', max_assets=5)
            mock_list_assets.assert_called_once_with(5)
        @patch('builtins.print')
        
    def test_list_models(self, mock_print):
        with patch.object(ListCommand, 'list_models') as mock_list_models:
            ListCommand.list_command(type='models')
            mock_list_models.assert_called_once()

if __name__ == '__main__':
    unittest.main()

