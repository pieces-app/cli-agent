"""
End-to-end tests for the MCP Gateway functionality.
These tests interact with a real Pieces OS instance and verify actual behavior.
"""

import urllib.request
import pytest
import requests
import mcp.types as types
from unittest.mock import Mock, patch
from pieces.mcp.gateway import MCPGateway, PosMcpConnection
from pieces.mcp.utils import get_mcp_latest_url
from pieces.settings import Settings
from pieces._vendor.pieces_os_client.wrapper.version_compatibility import (
    UpdateEnum,
)

# Constants
TEST_SERVER_NAME = "pieces-test-mcp"


def get_upstream_url():
    """Get the upstream URL, handling potential errors."""
    try:
        Settings.startup()
        return get_mcp_latest_url()
    except Exception:
        # We are mocking the settings so this will raise an exception most of the time we can hardcode the url instead
        return "http://localhost:39300/model_context_protocol/2024-11-05/sse"


@pytest.fixture(scope="module")
def ensure_pieces_setup():
    """
    Fixture to ensure Pieces OS is installed and accessible for testing.
    Returns True if Pieces OS is running, False otherwise.
    """
    try:
        Settings.startup()
        return True
    except (requests.RequestException, ConnectionError, SystemExit):
        return False


# Unit Tests with Mocking
class TestMCPGatewayValidation:
    """Unit tests for MCP Gateway validation flows with mocking"""

    @pytest.fixture
    def mock_connection(self):
        """Create a mock PosMcpConnection for testing"""
        connection = PosMcpConnection("http://test-url")
        # Reset any cached results
        connection.result = None
        return connection

    @pytest.mark.asyncio
    async def test_validate_system_status_pieces_os_not_running(self, mock_connection):
        """Test validation when PiecesOS is not running"""
        with patch.object(
            mock_connection, "_check_pieces_os_status", return_value=False
        ):
            is_valid, error_message = mock_connection._validate_system_status(
                "ask_pieces_ltm"
            )

            assert is_valid is False
            assert "PiecesOS is not running" in error_message
            assert "`pieces open`" in error_message
            assert "ask_pieces_ltm" in error_message

    @pytest.mark.asyncio
    async def test_validate_system_status_version_incompatible_plugin_update(
        self, mock_connection
    ):
        """Test validation when CLI version needs updating"""
        # Mock PiecesOS running
        with patch.object(
            mock_connection, "_check_pieces_os_status", return_value=True
        ):
            # Mock version compatibility check to return plugin update needed
            mock_result = Mock()
            mock_result.compatible = False
            mock_result.update = UpdateEnum.Plugin
            mock_connection.result = mock_result

            is_valid, error_message = mock_connection._validate_system_status(
                "ask_pieces_ltm"
            )

            assert is_valid is False
            assert "Please update the CLI version" in error_message
            assert "pieces manage update" in error_message
            assert "retry your request again after updating" in error_message

    @pytest.mark.asyncio
    async def test_validate_system_status_version_incompatible_pos_update(
        self, mock_connection
    ):
        """Test validation when PiecesOS version needs updating"""
        # Mock PiecesOS running
        with patch.object(
            mock_connection, "_check_pieces_os_status", return_value=True
        ):
            # Mock version compatibility check to return POS update needed
            mock_result = Mock()
            mock_result.compatible = False
            mock_result.update = UpdateEnum.PiecesOS  # Or any value that's not Plugin
            mock_connection.result = mock_result

            is_valid, error_message = mock_connection._validate_system_status(
                "ask_pieces_ltm"
            )

            assert is_valid is False
            assert "Please update PiecesOS" in error_message
            assert "pieces update" in error_message
            assert "retry your request again after updating" in error_message

    @pytest.mark.asyncio
    async def test_validate_system_status_ltm_disabled(self, mock_connection):
        """Test validation when LTM is disabled for LTM tools"""
        # Mock PiecesOS running and version compatible
        with patch.object(
            mock_connection, "_check_pieces_os_status", return_value=True
        ):
            mock_result = Mock()
            mock_result.compatible = True
            mock_connection.result = mock_result

            # Mock LTM disabled
            with patch.object(mock_connection, "_check_ltm_status", return_value=False):
                is_valid, error_message = mock_connection._validate_system_status(
                    "ask_pieces_ltm"
                )

                assert is_valid is False
                assert "Long Term Memory (LTM) is not enabled" in error_message
                assert "`pieces open --ltm`" in error_message
                assert "ask_pieces_ltm" in error_message

    @pytest.mark.asyncio
    async def test_validate_system_status_ltm_disabled_create_memory_tool(
        self, mock_connection
    ):
        """Test validation when LTM is disabled for create_pieces_memory tool"""
        # Mock PiecesOS running and version compatible
        with patch.object(
            mock_connection, "_check_pieces_os_status", return_value=True
        ):
            mock_result = Mock()
            mock_result.compatible = True
            mock_connection.result = mock_result

            # Mock LTM disabled
            with patch.object(mock_connection, "_check_ltm_status", return_value=False):
                is_valid, error_message = mock_connection._validate_system_status(
                    "create_pieces_memory"
                )

                assert is_valid is False
                assert "Long Term Memory (LTM) is not enabled" in error_message
                assert "`pieces open --ltm`" in error_message
                assert "create_pieces_memory" in error_message

    @pytest.mark.asyncio
    async def test_validate_system_status_non_ltm_tool_success(self, mock_connection):
        """Test validation success for non-LTM tools when LTM is disabled"""
        # Mock PiecesOS running and version compatible
        with patch.object(
            mock_connection, "_check_pieces_os_status", return_value=True
        ):
            mock_result = Mock()
            mock_result.compatible = True
            mock_connection.result = mock_result

            # Mock LTM disabled (shouldn't matter for non-LTM tools)
            with patch.object(mock_connection, "_check_ltm_status", return_value=False):
                is_valid, error_message = mock_connection._validate_system_status(
                    "some_other_tool"
                )

                assert is_valid is True
                assert error_message == ""

    @pytest.mark.asyncio
    async def test_validate_system_status_all_checks_pass(self, mock_connection):
        """Test validation when all checks pass"""
        # Mock PiecesOS running
        with patch.object(
            mock_connection, "_check_pieces_os_status", return_value=True
        ):
            # Mock version compatible
            mock_result = Mock()
            mock_result.compatible = True
            mock_connection.result = mock_result

            # Mock LTM enabled
            with patch.object(mock_connection, "_check_ltm_status", return_value=True):
                is_valid, error_message = mock_connection._validate_system_status(
                    "ask_pieces_ltm"
                )

                assert is_valid is True
                assert error_message == ""

    @pytest.mark.asyncio
    async def test_call_tool_with_validation_failure(self, mock_connection):
        """Test call_tool returns error when validation fails"""
        # Mock validation failure
        error_msg = "Test validation error"
        with patch.object(
            mock_connection, "_validate_system_status", return_value=(False, error_msg)
        ):
            result = await mock_connection.call_tool("test_tool", {})

            assert isinstance(result, types.CallToolResult)
            assert len(result.content) == 1
            assert isinstance(result.content[0], types.TextContent)
            assert result.content[0].text == error_msg

    @pytest.mark.asyncio
    async def test_call_tool_with_connection_failure(self, mock_connection):
        """Test call_tool handles connection failures gracefully"""
        # Mock validation success
        with patch.object(
            mock_connection, "_validate_system_status", return_value=(True, "")
        ):
            # Mock connection failure
            with patch.object(
                mock_connection, "connect", side_effect=Exception("Connection failed")
            ):
                result = await mock_connection.call_tool("test_tool", {})

                assert isinstance(result, types.CallToolResult)
                assert len(result.content) == 1
                assert isinstance(result.content[0], types.TextContent)
                assert "`pieces restart`" in result.content[0].text

    @pytest.mark.asyncio
    async def test_get_error_message_for_tool_uses_validation(self, mock_connection):
        """Test that _get_error_message_for_tool uses the validation system"""
        # Mock validation failure
        error_msg = "Validation failed"
        with patch.object(
            mock_connection, "_validate_system_status", return_value=(False, error_msg)
        ):
            result = mock_connection._get_error_message_for_tool("test_tool")

            assert result == error_msg

    @pytest.mark.asyncio
    async def test_get_error_message_for_tool_validation_passes(self, mock_connection):
        """Test _get_error_message_for_tool when validation passes but still has error"""
        # Mock validation success
        with patch.object(
            mock_connection, "_validate_system_status", return_value=(True, "")
        ):
            result = mock_connection._get_error_message_for_tool("test_tool")

            assert "Unable to execute 'test_tool' tool" in result
            assert "`pieces restart`" in result

    def test_check_version_compatibility_caches_result(self, mock_connection):
        """Test that version compatibility check caches the result"""
        # Mock the VersionChecker
        with patch("pieces.mcp.gateway.VersionChecker") as mock_version_checker:
            mock_result = Mock()
            mock_result.compatible = True
            mock_version_checker.return_value.version_check.return_value = mock_result

            # First call
            is_compatible1, msg1 = mock_connection._check_version_compatibility()
            # Second call
            is_compatible2, msg2 = mock_connection._check_version_compatibility()

            # Should have cached the result
            assert mock_connection.result == mock_result
            assert is_compatible1 == is_compatible2 == True
            assert msg1 == msg2 == ""
            # VersionChecker should only be called once due to caching
            mock_version_checker.assert_called_once()

    @patch("pieces.mcp.gateway.HealthWS")
    def test_check_pieces_os_status_health_ws_running(
        self, mock_health_ws, mock_connection
    ):
        """Test _check_pieces_os_status when health WS is already running"""
        # Mock HealthWS.is_running() to return True
        mock_health_ws.is_running.return_value = True

        # Mock Settings.pieces_client.is_pos_stream_running
        with patch("pieces.mcp.gateway.Settings") as mock_settings:
            mock_settings.pieces_client.is_pos_stream_running = True

            result = mock_connection._check_pieces_os_status()

            assert result is True
            mock_health_ws.is_running.assert_called_once()

    @patch("pieces.mcp.gateway.HealthWS")
    @patch("pieces.mcp.gateway.Settings")
    def test_check_pieces_os_status_starts_health_ws(
        self, mock_settings, mock_health_ws, mock_connection
    ):
        """Test _check_pieces_os_status starts health WS when PiecesOS is running"""
        # Mock HealthWS.is_running() to return False initially
        mock_health_ws.is_running.return_value = False

        # Mock pieces_client.is_pieces_running() to return True
        mock_settings.pieces_client.is_pieces_running.return_value = True

        # Mock HealthWS.get_instance() and its start method
        mock_instance = Mock()
        mock_health_ws.get_instance.return_value = mock_instance

        # Mock the workstream API call
        mock_settings.pieces_client.work_stream_pattern_engine_api.workstream_pattern_engine_processors_vision_status.return_value = Mock()

        result = mock_connection._check_pieces_os_status()

        assert result is True
        mock_instance.start.assert_called_once()

    @patch("pieces.mcp.gateway.Settings")
    def test_check_ltm_status(self, mock_settings, mock_connection):
        """Test _check_ltm_status returns LTM enabled status"""
        mock_settings.pieces_client.copilot.context.ltm.is_enabled = True

        result = mock_connection._check_ltm_status()

        assert result is True

    @pytest.mark.asyncio
    async def test_multiple_validation_calls_same_tool(self, mock_connection):
        """Test that multiple validation calls for the same tool work correctly"""
        # Mock all components
        with (
            patch.object(mock_connection, "_check_pieces_os_status", return_value=True),
            patch.object(mock_connection, "_check_ltm_status", return_value=True),
        ):
            mock_result = Mock()
            mock_result.compatible = True
            mock_connection.result = mock_result

            # Call validation multiple times
            is_valid1, msg1 = mock_connection._validate_system_status("ask_pieces_ltm")
            is_valid2, msg2 = mock_connection._validate_system_status("ask_pieces_ltm")

            assert is_valid1 == is_valid2 == True
            assert msg1 == msg2 == ""

    @pytest.mark.asyncio
    async def test_try_get_upstream_url_success(self, mock_connection):
        """Test _try_get_upstream_url when PiecesOS is running"""
        mock_connection.upstream_url = None

        with (
            patch("pieces.mcp.gateway.Settings") as mock_settings,
            patch(
                "pieces.mcp.gateway.get_mcp_latest_url", return_value="http://test-url"
            ),
        ):
            mock_settings.pieces_client.is_pieces_running.return_value = True

            result = mock_connection._try_get_upstream_url()

            assert result is True
            assert mock_connection.upstream_url == "http://test-url"

    @pytest.mark.asyncio
    async def test_try_get_upstream_url_failure(self, mock_connection):
        """Test _try_get_upstream_url when PiecesOS is not running"""
        mock_connection.upstream_url = None

        with patch("pieces.mcp.gateway.Settings") as mock_settings:
            mock_settings.pieces_client.is_pieces_running.return_value = False

            result = mock_connection._try_get_upstream_url()

            assert result is False
            assert mock_connection.upstream_url is None

    @pytest.mark.asyncio
    async def test_try_get_upstream_url_already_set(self, mock_connection):
        """Test _try_get_upstream_url when URL is already set"""
        mock_connection.upstream_url = "http://existing-url"

        result = mock_connection._try_get_upstream_url()

        assert result is True
        assert mock_connection.upstream_url == "http://existing-url"


# Integration/E2E Tests (existing tests)


@pytest.mark.asyncio
async def test_gateway_initialization():
    """Test that the MCPGateway initializes correctly with real components"""
    upstream_url = get_upstream_url()
    if upstream_url is None:
        pytest.skip("MCP server is not accessible. Skipping test.")

    gateway = MCPGateway(server_name=TEST_SERVER_NAME, upstream_url=upstream_url)

    # Check that the gateway was properly initialized
    assert gateway.server.name == TEST_SERVER_NAME
    assert gateway.upstream.upstream_url == upstream_url


@pytest.mark.asyncio
async def test_gateway_connection_with_pos_running(ensure_pieces_setup):
    """Test connecting to the upstream POS server when it's running"""
    if not ensure_pieces_setup:
        pytest.skip("Pieces OS is not running. Skipping test.")

    # Check if we can actually connect to the MCP server
    upstream_url = get_upstream_url()
    if upstream_url is None:
        pytest.skip("MCP server is not accessible. Skipping test.")

    try:
        with urllib.request.urlopen(upstream_url, timeout=1) as response:
            response.read(1)
    except Exception:
        pytest.skip("MCP server is not accessible. Skipping test.")

    # Create the connection
    connection = PosMcpConnection(upstream_url)

    try:
        # Attempt to connect
        session = await connection.connect()

        # Verify we got a valid session
        assert session is not None

        # Verify we discovered some tools
        assert len(connection.discovered_tools) > 0

        # Tools should be properly structured Tool objects
        for tool in connection.discovered_tools:
            assert hasattr(tool, "name")
            assert hasattr(tool, "description")
            assert isinstance(tool, types.Tool)

    finally:
        # Clean up
        await connection.cleanup()


@pytest.mark.asyncio
async def test_call_tool_with_pos_running(ensure_pieces_setup):
    """Test calling a tool on the POS server when it's running"""
    if not ensure_pieces_setup:
        pytest.skip("Pieces OS is not running. Skipping test.")

    # Check if we can actually connect to the MCP server
    upstream_url = get_upstream_url()
    if upstream_url is None:
        pytest.skip("MCP server is not accessible. Skipping test.")

    try:
        import urllib.request

        with urllib.request.urlopen(upstream_url, timeout=1) as response:
            response.read(1)
    except Exception:
        pytest.skip("MCP server is not accessible. Skipping test.")

    # Create the connection
    connection = PosMcpConnection(upstream_url)

    try:
        # Connect to the server
        await connection.connect()

        # Find a tool to call
        if not connection.discovered_tools:
            pytest.skip("No tools discovered from Pieces OS")

        # Get the first tool (it's a Tool object, not a dict)
        tool = connection.discovered_tools[0]
        tool_name = tool.name

        # Call the tool with minimal arguments
        # Note: This might need adjustment based on the actual tools available
        result = await connection.call_tool(
            tool_name, {"question": "test", "chat_llm": "gpt-4o-mini"}
        )

        # Verify we got a result
        assert result is not None
        assert hasattr(result, "content")
        assert len(result.content) > 0

    finally:
        # Clean up
        await connection.cleanup()


@pytest.mark.asyncio
async def test_full_gateway_workflow(ensure_pieces_setup):
    """
    Test a complete workflow with the gateway.

    This test initializes the gateway, connects to POS, lists tools,
    and cleans up.
    """
    if not ensure_pieces_setup:
        pytest.skip("Pieces OS is not running. Skipping test.")

    # Check if we can actually connect to the MCP server
    upstream_url = get_upstream_url()
    if upstream_url is None:
        pytest.skip("MCP server is not accessible. Skipping test.")

    try:
        import urllib.request

        with urllib.request.urlopen(upstream_url, timeout=1) as response:
            response.read(1)
    except Exception:
        pytest.skip("MCP server is not accessible. Skipping test.")

    # Initialize the gateway with real components
    gateway = MCPGateway(server_name=TEST_SERVER_NAME, upstream_url=upstream_url)

    try:
        # Connect to the upstream first
        await gateway.upstream.connect()

        # Verify we can list tools
        tools = gateway.upstream.discovered_tools
        assert len(tools) > 0, "Should discover at least one tool"

        # Verify the tools are properly structured
        for tool in tools:
            assert hasattr(tool, "name")
            assert hasattr(tool, "description")

    finally:
        # Clean up
        await gateway.upstream.cleanup()
