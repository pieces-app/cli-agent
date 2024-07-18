import unittest
from unittest.mock import patch, MagicMock
from pieces.commands.search_command import search
from pieces.settings import Settings
from pieces.gui import print_asset_details, show_error
from io import StringIO
import sys

class TestSearchCommand(unittest.TestCase):

    @patch('pieces.commands.search_command.AssetsApi')
    @patch('pieces.commands.search_command.SearchApi')
    @patch('pieces.commands.search_command.print_asset_details')
    @patch('pieces.commands.search_command.show_error')
    @patch('pieces.commands.search_command.AssetsCommandsApi')
    def test_search_assets(self, MockAssetsCommandsApi, mock_show_error, mock_print_asset_details, MockSearchApi, MockAssetsApi):
        # Mock the settings
        Settings.api_client = MagicMock()

        # Mock the API responses
        mock_assets_api_instance = MockAssetsApi.return_value
        mock_search_api_instance = MockSearchApi.return_value

        mock_result = MagicMock()
        mock_asset1 = MagicMock()
        mock_asset2 = MagicMock()
        mock_asset1.exact = True
        mock_asset1.identifier = 'asset1_id'
        mock_asset2.exact = False
        mock_asset2.identifier = 'asset2_id'
        mock_result.iterable = [mock_asset1, mock_asset2]

        mock_assets_api_instance.assets_search_assets.return_value = mock_result

        # Mock the asset snapshot
        mock_snapshot = MagicMock()
        mock_snapshot.name = 'Asset Name'
        MockAssetsCommandsApi.get_asset_snapshot.return_value = mock_snapshot

        # Redirect stdout to capture print output
        captured_output = StringIO()
        sys.stdout = captured_output

        # Call the search function
        search(['test_query'], search_type='assets')

        # Restore stdout
        sys.stdout = sys.__stdout__

        # Assertions
        mock_assets_api_instance.assets_search_assets.assert_called_with(query='test_query', transferables=False)
        mock_print_asset_details.assert_called_with([('asset1_id', 'Asset Name'), ('asset2_id', 'Asset Name')], "Asset Matches:", 'assets')
        mock_show_error.assert_not_called()

    @patch('pieces.commands.search_command.AssetsApi')
    @patch('pieces.commands.search_command.SearchApi')
    @patch('pieces.commands.search_command.print_asset_details')
    @patch('pieces.commands.search_command.show_error')
    def test_search_no_results(self, mock_show_error, mock_print_asset_details, MockSearchApi, MockAssetsApi):
        # Mock the settings
        Settings.api_client = MagicMock()

        # Mock the API responses
        mock_assets_api_instance = MockAssetsApi.return_value
        mock_search_api_instance = MockSearchApi.return_value

        mock_result = MagicMock()
        mock_result.iterable = []

        mock_assets_api_instance.assets_search_assets.return_value = mock_result

        # Redirect stdout to capture print output
        captured_output = StringIO()
        sys.stdout = captured_output

        # Call the search function
        search(['no_results_query'], search_type='assets')

        # Restore stdout
        sys.stdout = sys.__stdout__

        # Get the captured output
        output = captured_output.getvalue()

        # Assertions
        mock_assets_api_instance.assets_search_assets.assert_called_with(query='no_results_query', transferables=False)
        self.assertIn('No matches found.', output)
        mock_print_asset_details.assert_not_called()
        mock_show_error.assert_not_called()

    @patch('pieces.commands.search_command.AssetsApi')
    @patch('pieces.commands.search_command.SearchApi')
    @patch('pieces.commands.search_command.print_asset_details')
    @patch('pieces.commands.search_command.show_error')
    def test_invalid_search_type(self, mock_show_error, mock_print_asset_details, MockSearchApi, MockAssetsApi):
        # Redirect stdout to capture print output
        captured_output = StringIO()
        sys.stdout = captured_output

        # Call the search function with an invalid search type
        search(['invalid_query'], search_type='invalid_type')

        # Restore stdout
        sys.stdout = sys.__stdout__

        # Assertions
        mock_show_error.assert_called_with("Invalid search type", "Search type 'invalid_type' is not supported.")
        mock_print_asset_details.assert_not_called()

    @patch('pieces.commands.search_command.SearchApi')
    @patch('pieces.commands.search_command.print_asset_details')
    @patch('pieces.commands.search_command.show_error')
    @patch('pieces.commands.search_command.AssetsCommandsApi')
    def test_search_ncs(self, MockAssetsCommandsApi, mock_show_error, mock_print_asset_details, MockSearchApi):
        # Mock the settings
        Settings.api_client = MagicMock()

        # Mock the API responses
        mock_search_api_instance = MockSearchApi.return_value

        mock_result = MagicMock()
        mock_asset1 = MagicMock()
        mock_asset1.exact = True
        mock_asset1.identifier = 'asset1_id'
        mock_result.iterable = [mock_asset1]

        mock_search_api_instance.neural_code_search.return_value = mock_result

        # Mock the asset snapshot
        mock_snapshot = MagicMock()
        mock_snapshot.name = 'NCS Asset'
        MockAssetsCommandsApi.get_asset_snapshot.return_value = mock_snapshot

        # Call the search function
        search(['ncs_query'], search_type='ncs')

        # Assertions
        mock_search_api_instance.neural_code_search.assert_called_with(query='ncs_query')
        mock_print_asset_details.assert_called_with([('asset1_id', 'NCS Asset')], "Asset Matches:", 'ncs')
        mock_show_error.assert_not_called()

    @patch('pieces.commands.search_command.SearchApi')
    @patch('pieces.commands.search_command.print_asset_details')
    @patch('pieces.commands.search_command.show_error')
    @patch('pieces.commands.search_command.AssetsCommandsApi')
    def test_search_fts(self, MockAssetsCommandsApi, mock_show_error, mock_print_asset_details, MockSearchApi):
        # Mock the settings
        Settings.api_client = MagicMock()

        # Mock the API responses
        mock_search_api_instance = MockSearchApi.return_value

        mock_result = MagicMock()
        mock_asset1 = MagicMock()
        mock_asset1.exact = False
        mock_asset1.identifier = 'asset1_id'
        mock_result.iterable = [mock_asset1]

        mock_search_api_instance.full_text_search.return_value = mock_result

        # Mock the asset snapshot
        mock_snapshot = MagicMock()
        mock_snapshot.name = 'FTS Asset'
        MockAssetsCommandsApi.get_asset_snapshot.return_value = mock_snapshot

        # Call the search function
        search(['fts_query'], search_type='fts')

        # Assertions
        mock_search_api_instance.full_text_search.assert_called_with(query='fts_query')
        mock_print_asset_details.assert_called_with([('asset1_id', 'FTS Asset')], "Asset Matches:", 'fts')
        mock_show_error.assert_not_called()

if __name__ == '__main__':
    unittest.main()
