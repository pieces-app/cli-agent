import unittest
from unittest.mock import patch, MagicMock,Mock
from pieces.commands.list_command import ListCommand , PiecesSelectMenu
from pieces.settings import Settings
import io
import sys
import platform

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

    def test_list_apps(self):
        # Determine the local OS
        local_os = platform.system().upper()
        if local_os in ["WINDOWS", "LINUX", "DARWIN"]:
            local_os = "MACOS" if local_os == "DARWIN" else local_os
        else:
            local_os = "WEB"

        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            with patch.object(ListCommand, 'list_apps') as mock_list_apps:
                mock_list_apps.side_effect = lambda: print(f"1: VS_CODE, 1.17.0, {local_os}\n2: PIECES_FOR_DEVELOPERS, 3.0.2, {local_os}")
                ListCommand.list_command(type='apps')
                
            output = fake_out.getvalue().strip()
            self.assertIn(f'1: VS_CODE, 1.17.0, {local_os}', output)
            self.assertIn(f'2: PIECES_FOR_DEVELOPERS, 3.0.2, {local_os}', output)


    def test_list_command_invalid_type(self):
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            with patch.object(ListCommand, 'list_assets') as mock_list_assets:
                with patch.object(ListCommand, 'list_apps') as mock_list_apps:
                    with patch.object(ListCommand, 'list_models') as mock_list_models:
                        ListCommand.list_command(type='invalid_type')
                        
                        # Check that none of the methods were called
                        self.assertFalse(mock_list_assets.called)
                        self.assertFalse(mock_list_apps.called)
                        self.assertFalse(mock_list_models.called)
                        
                        # Check that nothing was printed
                        self.assertEqual(fake_out.getvalue(), '')

if __name__ == '__main__':
    unittest.main()


