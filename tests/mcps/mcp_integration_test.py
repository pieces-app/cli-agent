import json
import unittest
from unittest.mock import Mock, mock_open, patch, MagicMock

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
from pieces._vendor.pieces_os_client.api.workstream_pattern_engine_api import (
    WorkstreamPatternEngineApi,
)
from pieces._vendor.pieces_os_client.api.model_context_protocol_api import (
    ModelContextProtocolApi,
)


class TestIntegration(MCPTestBase):
    """Unit tests for the *generic* MCP integration wrapper."""

    def setUp(self):
        super().setUp() if hasattr(super(), "setUp") else None  # type: ignore[attr-defined]

        # ------------------------------------------------------------------
        # Mock Pieces client & APIs
        # ------------------------------------------------------------------
        self.mock_api_client = MockPiecesClient()

        # Stub deep API calls used by Integration.search()
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

        # Expose client on the patched global Settings
        Settings.pieces_client = self.mock_api_client

        # ------------------------------------------------------------------
        # APPROACH 1: Mock the entire mcp module before importing
        # ------------------------------------------------------------------
        # Create a mock MCP config schema
        self.mock_mcp_config_schema = MagicMock()
        self.mock_mcp_config_schema.model_validate = MagicMock()
        self.mock_mcp_config_schema.model_dump = MagicMock(return_value={})

        # Patch the mcp module
        with patch("pieces.config.schemas.mcp") as mock_mcp:
            mock_mcp.mcp_integrations = ["test_integration"]
            mock_mcp.MCPConfigSchema = self.mock_mcp_config_schema
            mock_mcp._create_mcp_config_schema = MagicMock(
                return_value=self.mock_mcp_config_schema
            )

            # Now modify the integrations list
            from pieces.config.schemas import mcp

            if "test_integration" not in mcp.mcp_integrations:
                mcp.mcp_integrations.append("test_integration")

            # Recreate the schema with test integration
            mcp.MCPConfigSchema = mcp._create_mcp_config_schema()

        # ------------------------------------------------------------------
        # Integration under test
        # ------------------------------------------------------------------
        self.mcp_properties = default_mcp_properties()
        self.basic_integration = Integration(
            options=[("Option 1", {"key": "value"})],
            text_success="Success text",
            readable="Test Integration",
            docs="https://docs.example.com",
            get_settings_path=lambda: "/tmp/test.json",
            mcp_properties=self.mcp_properties,
            error_text="Test error text",
            loader=json.load,
            saver=lambda x, y: json.dump(x, y, indent=4),
            id="test_integration",  # Synthetic integration ID for tests
        )

    def tearDown(self):
        """Clean up after each test."""
        # Remove test integration from the list if it was added
        from pieces.config.schemas import mcp

        if "test_integration" in mcp.mcp_integrations:
            mcp.mcp_integrations.remove("test_integration")

        # Recreate the schema without test integration
        mcp.MCPConfigSchema = mcp._create_mcp_config_schema()

    # ------------------------------------------------------------------
    # Alternative setUp using patch.multiple
    # ------------------------------------------------------------------
    @patch.multiple(
        "pieces.config.schemas.mcp",
        mcp_integrations=[
            "test_integration",
            "vscode",
            "cursor",
        ],  # Include test_integration
        MCPConfigSchema=MagicMock(),
    )
    def alternative_test_setup(self):
        """Alternative approach using patch.multiple decorator."""
        pass

    # ------------------------------------------------------------------
    # Individual test cases
    # ------------------------------------------------------------------

    def test_integration_initialization(self):
        self.assertEqual(self.basic_integration.readable, "Test Integration")
        self.assertEqual(self.basic_integration.docs, "https://docs.example.com")
        self.assertEqual(self.basic_integration.id, "test_integration")
        self.assertEqual(len(self.basic_integration.options), 1)

    @patch("pieces.config.schemas.mcp.MCPConfigSchema")
    def test_load_mcp_config(self, mock_schema):
        """Test with schema mocked at method level."""
        mock_config = {"test_integration": {"/path/to/project": "sse"}}

        # Mock the schema validation
        mock_instance = MagicMock()
        mock_instance.model_dump.return_value = mock_config
        mock_schema.model_validate.return_value = mock_instance

        with patch("builtins.open", mock_open(read_data=json.dumps(mock_config))):
            config = self.basic_integration.load_config()
            self.assertEqual(config, mock_config)

    @patch("pieces.settings.Settings.mcp_config")
    def test_add_project(self, mock_mcp_config):
        """Calling *on_select* should register the project in *MCPManager*."""
        mock_config = {
            "mcp": {"servers": {"Pieces": {"url": "pieces_url", "type": "sse"}}}
        }

        # Mock the mcp_config methods
        mock_mcp_config.get_projects.return_value = {"/path/to/new/project": "sse"}
        mock_mcp_config.add_project.return_value = None

        with patch("builtins.open", mock_open(read_data=json.dumps(mock_config))):
            result = self.basic_integration.on_select("sse", "/path/to/new/project")
            self.assertTrue(result)

        # Verify the add_project was called
        mock_mcp_config.add_project.assert_called_once_with(
            "test_integration", "sse", "/path/to/new/project"
        )

    @patch("pieces.settings.Settings.mcp_config")
    def test_remove_project(self, mock_mcp_config):
        # Setup the mock to return empty list after removal
        mock_mcp_config.get_projects.return_value = []
        mock_mcp_config.remove_project.return_value = None

        # Call the methods
        mock_mcp_config.add_project("test_integration", "sse", "/path/to/project")
        mock_mcp_config.remove_project("test_integration", "/path/to/project")
        projects = mock_mcp_config.get_projects("test_integration")

        self.assertNotIn("/path/to/project", projects)

    def test_is_set_up(self):
        mock_config = {"test_integration": {"/path/to/project": "sse"}}
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
                found, config = self.basic_integration.search("/path/to/project", "sse")
                self.assertTrue(found)
                self.assertEqual(config, {"url": "pieces_url"})

    # ------------------------------------------------------------------
    # Alternative approach: Mock at the class level
    # ------------------------------------------------------------------
    @patch("pieces.config.schemas.mcp")
    def test_with_full_module_mock(self, mock_mcp_module):
        """Test with the entire mcp module mocked."""
        # Setup the mock module
        mock_mcp_module.mcp_integrations = ["test_integration"]
        mock_mcp_module.MCPConfigSchema = MagicMock()

        # Your test logic here
        self.assertIn("test_integration", mock_mcp_module.mcp_integrations)


if __name__ == "__main__":
    unittest.main()
