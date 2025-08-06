import json
import os
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


class TestIntegrationPaths(MCPTestBase):
    """Cross-platform path handling for MCP integrations."""

    def setUp(self):
        super().setUp() if hasattr(super(), "setUp") else None  # type: ignore[attr-defined]

        # Common mocks -------------------------------------------------------
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

        self.mcp_properties = default_mcp_properties()

    # ------------------------------------------------------------------
    # Helper to construct integration with variable path function
    # ------------------------------------------------------------------

    def _create_integration(self, path_fn):
        return Integration(
            options=[("Option 1", {"key": "value"})],
            text_success="Success text",
            readable="Test Integration",
            docs="https://docs.example.com",
            get_settings_path=path_fn,
            mcp_properties=self.mcp_properties,
            error_text="Test error text",
            loader=json.load,
            saver=lambda x, y: json.dump(x, y, indent=4),
            id="test_integration",
        )

    # ------------------------------------------------------------------
    # Individual test cases
    # ------------------------------------------------------------------

    def _generic_path_test(self, fake_os_name, path_value):
        with patch("os.name", fake_os_name):
            integration = self._create_integration(lambda: path_value)

            mock_config = {
                "mcp": {"servers": {"Pieces": {"url": "pieces_url", "type": "sse"}}}
            }
            with patch("builtins.open", mock_open(read_data=json.dumps(mock_config))):
                found, config = integration.search(path_value, "sse")
                self.assertTrue(found)
                self.assertEqual(config["type"], "sse")

    def test_windows_paths(self):
        self._generic_path_test("nt", "C:\\Users\\Test\\AppData\\Roaming\\test.json")

    def test_unix_paths(self):
        self._generic_path_test("posix", "/home/test/.config/test.json")

    def test_macos_paths(self):
        self._generic_path_test(
            "posix", "/Users/test/Library/Application Support/test.json"
        )

    def test_path_handling_with_spaces(self):
        integration = self._create_integration(lambda: "/path/with spaces/test.json")
        mock_config = {
            "mcp": {"servers": {"Pieces": {"url": "pieces_url", "type": "sse"}}}
        }
        with patch("builtins.open", mock_open(read_data=json.dumps(mock_config))):
            found, config = integration.search("/path/with spaces/test.json", "sse")
            self.assertTrue(found)
            self.assertEqual(config["type"], "sse")

    def test_path_handling_with_special_characters(self):
        integration = self._create_integration(
            lambda: "/path/with@special#chars/test.json"
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
        integration = self._create_integration(lambda: "/path/with/unicode/测试.json")
        mock_config = {
            "mcp": {"servers": {"Pieces": {"url": "pieces_url", "type": "sse"}}}
        }
        with patch("builtins.open", mock_open(read_data=json.dumps(mock_config))):
            found, config = integration.search("/path/with/unicode/测试.json", "sse")
            self.assertTrue(found)
            self.assertEqual(config["type"], "sse")


if __name__ == "__main__":
    unittest.main()
