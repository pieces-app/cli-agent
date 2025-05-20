import unittest
import json
from unittest.mock import patch, Mock, mock_open, PropertyMock
from pieces.mcp.integration import Integration
from pieces.settings import Settings
from pieces_os_client.models.workstream_pattern_engine_status import (
    WorkstreamPatternEngineStatus,
)
from pieces_os_client.api.workstream_pattern_engine_api import WorkstreamPatternEngineApi
from pieces_os_client.api.model_context_protocol_api import ModelContextProtocolApi


class MockPiecesClient(Mock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_client = Mock()
        self._work_stream_pattern_engine_api = WorkstreamPatternEngineApi(self.api_client)
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


class TestIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.settings_patcher = patch("pieces.settings.Settings")
        cls.mock_settings = cls.settings_patcher.start()
        cls.mock_settings.mcp_config = "/tmp/mcp_config.json"
        cls.mock_settings.logger = Mock()
        cls.mock_settings.logger.console = Mock()
        cls.mock_settings.logger.confirm = Mock(return_value=True)

    @classmethod
    def tearDownClass(cls):
        cls.settings_patcher.stop()

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

        self.mock_model_context_protocol_api = Mock()
        self.mock_model_context_protocol_api.model_context_protocol_schema_versions = (
            Mock(return_value=[Mock(entry_endpoint="mock_url")])
        )
        self.mock_api_client._model_context_protocol_api = (
            self.mock_model_context_protocol_api
        )

        self.mock_settings.pieces_client = self.mock_api_client

        self.basic_integration = Integration(
            options=[("Option 1", {"key": "value"})],
            text_success="Success text",
            readable="Test Integration",
            docs="https://docs.example.com",
            get_settings_path=lambda: "/tmp/test.json",
            path_to_mcp_settings=["mcp", "servers", "Pieces"],
            mcp_settings={"type": "sse"},
        )

    def tearDown(self):
        self.mock_api_client.reset_mock()
        self.mock_workstream_api.reset_mock()
        self.mock_model_context_protocol_api.reset_mock()
        self.mock_settings.logger.reset_mock()

    def test_integration_initialization(self):
        self.assertEqual(self.basic_integration.readable, "Test Integration")
        self.assertEqual(self.basic_integration.docs, "https://docs.example.com")
        self.assertEqual(self.basic_integration.id, "test_integration")
        self.assertEqual(len(self.basic_integration.options), 1)

    def test_load_mcp_config(self):
        mock_config = {"test_integration": ["/path/to/project"]}
        with patch("builtins.open", mock_open(read_data=json.dumps(mock_config))):
            config = self.basic_integration.load_mcp_config()
            self.assertEqual(config, mock_config)

    def test_add_project(self):
        mock_config = {"test_integration": ["/path/to/project"]}
        with patch("builtins.open", mock_open(read_data=json.dumps(mock_config))):
            self.basic_integration.add_project(
                "test_integration", "/path/to/new/project"
            )
            open.assert_called_with(Settings.mcp_config, "w")

    def test_remove_project(self):
        mock_config = {"test_integration": ["/path/to/project"]}
        with patch("builtins.open", mock_open(read_data=json.dumps(mock_config))):
            self.basic_integration.remove_project("/path/to/project")
            open.assert_called_with(Settings.mcp_config, "w")

    def test_is_set_up(self):
        mock_config = {"test_integration": ["/path/to/project"]}
        with patch("builtins.open", mock_open(read_data=json.dumps(mock_config))):
            with patch.object(
                self.basic_integration, "search", return_value=(True, {})
            ):
                self.assertTrue(self.basic_integration.is_set_up())

    def test_search(self):
        mock_config = {"mcp": {"servers": {"Pieces": {"url": "pieces_url"}}}}
        with patch("builtins.open", mock_open(read_data=json.dumps(mock_config))):
            with patch(
                "pieces.mcp.integration.get_mcp_urls", return_value=["pieces_url"]
            ):
                found, config = self.basic_integration.search("/path/to/project")
                self.assertTrue(found)
                self.assertEqual(config, {"url": "pieces_url"})


if __name__ == "__main__":
    unittest.main()
