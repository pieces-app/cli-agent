import unittest
import json
from unittest.mock import patch, Mock, mock_open, PropertyMock
from pieces.mcp.integration import Integration, MCPProperties
from pieces.settings import Settings
from pieces._vendor.pieces_os_client.models.workstream_pattern_engine_status import (
    WorkstreamPatternEngineStatus,
)
from pieces._vendor.pieces_os_client.api.workstream_pattern_engine_api import (
    WorkstreamPatternEngineApi,
)
from pieces._vendor.pieces_os_client.api.model_context_protocol_api import (
    ModelContextProtocolApi,
)


class MockPiecesClient(Mock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_client = Mock()
        self._work_stream_pattern_engine_api = WorkstreamPatternEngineApi(
            self.api_client
        )
        self._model_context_protocol_api = ModelContextProtocolApi(self.api_client)
        self.copilot = Mock()
        self.copilot.context = Mock()
        self.copilot.context.ltm = Mock()
        self.copilot.context.ltm.is_enabled = False
        self.copilot.context.ltm.check_perms = Mock(return_value=[])
        self.copilot.context.ltm.enable = Mock()
        self.copilot.context.ltm.ltm_status = None
        self._port = "39300"
        self.host = "http://127.0.0.1:39300"
        self.is_pieces_running = Mock(return_value=True)
        self.init_host = Mock()

    @property
    def work_stream_pattern_engine_api(self):
        return self._work_stream_pattern_engine_api

    @property
    def model_context_protocol_api(self):
        return self._model_context_protocol_api


class TestIntegrationPaths(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.settings_patcher = patch("pieces.settings.Settings")
        cls.mock_settings = cls.settings_patcher.start()
        cls.mock_settings.mcp_config = "/tmp/mcp_config.json"
        cls.mock_settings.logger = Mock()
        cls.mock_settings.logger.console = Mock()
        cls.mock_settings.logger.confirm = Mock(return_value=True)

        # Mock the MCP URL functions
        cls.mcp_urls_patcher = patch("pieces.mcp.integration.get_mcp_urls")
        cls.mock_mcp_urls = cls.mcp_urls_patcher.start()
        cls.mock_mcp_urls.return_value = ["pieces_url"]

        cls.mcp_latest_url_patcher = patch("pieces.mcp.integration.get_mcp_latest_url")
        cls.mock_mcp_latest_url = cls.mcp_latest_url_patcher.start()
        cls.mock_mcp_latest_url.return_value = "pieces_url"

    @classmethod
    def tearDownClass(cls):
        cls.settings_patcher.stop()
        cls.mcp_urls_patcher.stop()
        cls.mcp_latest_url_patcher.stop()

    def setUp(self):
        self.mock_api_client = MockPiecesClient()
        self.mock_workstream_api = Mock()
        self.mock_workstream_api.workstream_pattern_engine_processors_vision_status = (
            Mock(
                return_value=WorkstreamPatternEngineStatus.from_dict(
                    {
                        "vision": {
                            "deactivation": {
                                "from": {"value": "2025-05-20T12:41:46.211Z"},
                                "to": {"value": "2025-05-20T18:42:02.407636Z"},
                                "continuous": True,
                            },
                            "degraded": False,
                        }
                    }
                )
            )
        )
        self.mock_api_client._work_stream_pattern_engine_api = self.mock_workstream_api
        self.mock_settings.pieces_client = self.mock_api_client

        self.mcp_properties = MCPProperties(
            stdio_property={"type": "stdio"},
            stdio_path=["mcp", "servers", "Pieces"],
            sse_property={"type": "sse"},
            sse_path=["mcp", "servers", "Pieces"],
            url_property_name="url",
            command_property_name="command",
            args_property_name="args",
        )

    def tearDown(self):
        self.mock_api_client.reset_mock()
        self.mock_workstream_api.reset_mock()
        self.mock_settings.logger.reset_mock()

    def test_windows_paths(self):
        with patch("os.name", "nt"):
            integration = Integration(
                options=[("Option 1", {"key": "value"})],
                text_success="Success text",
                readable="Test Integration",
                docs="https://docs.example.com",
                get_settings_path=lambda: "C:\\Users\\Test\\AppData\\Roaming\\test.json",
                mcp_properties=self.mcp_properties,
                error_text="Test error text",
                loader=json.load,
                saver=lambda x, y: json.dump(x, y, indent=4),
                id="test_integration",
            )

            mock_config = {
                "mcp": {"servers": {"Pieces": {"url": "pieces_url", "type": "sse"}}}
            }

            with patch("builtins.open", mock_open(read_data=json.dumps(mock_config))):
                found, config = integration.search(
                    "C:\\Users\\Test\\AppData\\Roaming\\test.json", "sse"
                )
                self.assertTrue(found)
                self.assertEqual(config["type"], "sse")

    def test_unix_paths(self):
        with patch("os.name", "posix"):
            integration = Integration(
                options=[("Option 1", {"key": "value"})],
                text_success="Success text",
                readable="Test Integration",
                docs="https://docs.example.com",
                get_settings_path=lambda: "/home/test/.config/test.json",
                mcp_properties=self.mcp_properties,
                error_text="Test error text",
                loader=json.load,
                saver=lambda x, y: json.dump(x, y, indent=4),
                id="test_integration",
            )

            mock_config = {
                "mcp": {"servers": {"Pieces": {"url": "pieces_url", "type": "sse"}}}
            }

            with patch("builtins.open", mock_open(read_data=json.dumps(mock_config))):
                found, config = integration.search(
                    "/home/test/.config/test.json", "sse"
                )
                self.assertTrue(found)
                self.assertEqual(config["type"], "sse")

    def test_macos_paths(self):
        with patch("os.name", "posix"):
            integration = Integration(
                options=[("Option 1", {"key": "value"})],
                text_success="Success text",
                readable="Test Integration",
                docs="https://docs.example.com",
                get_settings_path=lambda: "/Users/test/Library/Application Support/test.json",
                mcp_properties=self.mcp_properties,
                error_text="Test error text",
                loader=json.load,
                saver=lambda x, y: json.dump(x, y, indent=4),
                id="test_integration",
            )

            mock_config = {
                "mcp": {"servers": {"Pieces": {"url": "pieces_url", "type": "sse"}}}
            }

            with patch("builtins.open", mock_open(read_data=json.dumps(mock_config))):
                found, config = integration.search(
                    "/Users/test/Library/Application Support/test.json", "sse"
                )
                self.assertTrue(found)
                self.assertEqual(config["type"], "sse")

    def test_path_handling_with_spaces(self):
        integration = Integration(
            options=[("Option 1", {"key": "value"})],
            text_success="Success text",
            readable="Test Integration",
            docs="https://docs.example.com",
            get_settings_path=lambda: "/path/with spaces/test.json",
            mcp_properties=self.mcp_properties,
            error_text="Test error text",
            loader=json.load,
            saver=lambda x, y: json.dump(x, y, indent=4),
            id="test_integration",
        )

        mock_config = {
            "mcp": {"servers": {"Pieces": {"url": "pieces_url", "type": "sse"}}}
        }

        with patch("builtins.open", mock_open(read_data=json.dumps(mock_config))):
            found, config = integration.search("/path/with spaces/test.json", "sse")
            self.assertTrue(found)
            self.assertEqual(config["type"], "sse")

    def test_path_handling_with_special_characters(self):
        integration = Integration(
            options=[("Option 1", {"key": "value"})],
            text_success="Success text",
            readable="Test Integration",
            docs="https://docs.example.com",
            get_settings_path=lambda: "/path/with@special#chars/test.json",
            mcp_properties=self.mcp_properties,
            error_text="Test error text",
            loader=json.load,
            saver=lambda x, y: json.dump(x, y, indent=4),
            id="test_integration",
        )

        mock_config = {
            "mcp": {"servers": {"Pieces": {"url": "pieces_url", "type": "sse"}}}
        }

        with patch("builtins.open", mock_open(read_data=json.dumps(mock_config))):
            found, config = integration.search(
                "/path/with@special#chars/test.json", "sse"
            )
            self.assertTrue(found)
            self.assertEqual(config["type"], "sse")

    def test_path_handling_with_unicode(self):
        integration = Integration(
            options=[("Option 1", {"key": "value"})],
            text_success="Success text",
            readable="Test Integration",
            docs="https://docs.example.com",
            get_settings_path=lambda: "/path/with/unicode/测试.json",
            mcp_properties=self.mcp_properties,
            error_text="Test error text",
            loader=json.load,
            saver=lambda x, y: json.dump(x, y, indent=4),
            id="test_integration",
        )

        mock_config = {
            "mcp": {"servers": {"Pieces": {"url": "pieces_url", "type": "sse"}}}
        }

        with patch("builtins.open", mock_open(read_data=json.dumps(mock_config))):
            found, config = integration.search("/path/with/unicode/测试.json", "sse")
            self.assertTrue(found)
            self.assertEqual(config["type"], "sse")


if __name__ == "__main__":
    unittest.main()
