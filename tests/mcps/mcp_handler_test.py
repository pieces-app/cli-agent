import json
import unittest
from unittest.mock import Mock, mock_open, patch

from tests.mcps.utils import (
    MCPTestBase,
    MockPiecesClient,
    default_mcp_properties,
)

from pieces.mcp.integration import Integration
from pieces.settings import Settings
from pieces._vendor.pieces_os_client.models.workstream_pattern_engine_status import (
    WorkstreamPatternEngineStatus,
)


class TestMCPHandler(MCPTestBase):
    """Tests focusing on high-level MCP handler behaviours."""

    def setUp(self):
        super().setUp() if hasattr(super(), "setUp") else None  # type: ignore[attr-defined]

        # ------------------------------------------------------------------
        # Mock Pieces client & sub-API
        # ------------------------------------------------------------------
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
        Settings.pieces_client = self.mock_api_client

        # Integration instance under test
        self.mcp_properties = default_mcp_properties()
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
            id="test_integration",
        )

    # ------------------------------------------------------------------
    # Individual tests
    # ------------------------------------------------------------------

    def test_handle_mcp_server_status(self):
        mock_config = {
            "mcp": {"servers": {"Pieces": {"url": "pieces_url", "type": "sse"}}}
        }
        with patch("builtins.open", mock_open(read_data=json.dumps(mock_config))):
            with patch.object(
                self.integration, "search", return_value=(True, {"type": "sse"})
            ):
                status = self.integration.is_set_up()
                self.assertTrue(status)

    def test_handle_mcp_docs(self):
        self.assertEqual(self.integration.docs, "https://docs.example.com")

    def test_handle_mcp_repair(self):
        with patch.object(self.integration, "need_repair", return_value={}):
            self.integration.need_repair()
            self.integration.need_repair.assert_called_once()  # type: ignore[attr-defined]

    def test_handle_mcp_error(self):
        self.assertEqual(self.integration.error_text, "Test error text")


if __name__ == "__main__":
    unittest.main()
