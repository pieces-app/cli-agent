import unittest
from unittest.mock import patch, Mock, mock_open
import json
from pieces.mcp_core.integration import Integration, MCPProperties


class TestMCPHandler(unittest.TestCase):
    def setUp(self):
        self.mock_settings = Mock()
        self.mock_settings.mcp_config = "/tmp/mcp_config.json"
        self.mock_settings.logger = Mock()
        self.mock_settings.logger.console = Mock()
        self.mock_settings.logger.confirm = Mock(return_value=True)

        self.mcp_properties = MCPProperties(
            stdio_property={"type": "stdio"},
            stdio_path=["mcp", "servers", "Pieces"],
            sse_property={"type": "sse"},
            sse_path=["mcp", "servers", "Pieces"],
            url_property_name="url",
            command_property_name="command",
            args_property_name="args"
        )

        self.integration = Integration(
            options=[("Option 1", {"key": "value"})],
            text_success="Success text",
            readable="Test Integration",
            docs="https://docs.example.com",
            get_settings_path=lambda: "/tmp/test.json",
            mcp_properties=self.mcp_properties,
            error_text="Test error text",
            loader=json.load,
            saver=lambda x, y: json.dump(x, y, indent=4),
            id="test_integration"
        )

    def test_handle_mcp_server_status(self):
        mock_config = {"mcp": {"servers": {"Pieces": {"url": "pieces_url", "type": "sse"}}}}
        with patch("builtins.open", mock_open(read_data=json.dumps(mock_config))):
            with patch.object(self.integration, 'search', return_value=(True, {"type": "sse"})):
                status = self.integration.is_set_up()
                self.assertTrue(status)

    def test_handle_mcp_docs(self):
        docs = self.integration.docs
        self.assertEqual(docs, "https://docs.example.com")

    def test_handle_mcp_repair(self):
        with patch.object(self.integration, 'need_repair') as mock_repair:
            mock_repair.return_value = {}
            self.integration.need_repair()
            mock_repair.assert_called_once()

    def test_handle_mcp_error(self):
        error = self.integration.error_text
        self.assertEqual(error, "Test error text")


if __name__ == "__main__":
    unittest.main()
