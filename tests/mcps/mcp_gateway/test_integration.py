"""
Integration/E2E tests for the MCP Gateway functionality.
These tests interact with a real Pieces OS instance and verify actual behavior.
"""

import urllib.request
import pytest
import asyncio
import mcp.types as types
import requests

from .utils import (
    get_upstream_url,
    ensure_pieces_setup,
    mock_tools_changed_callback,
    TEST_SERVER_NAME,
)
from pieces.mcp.gateway import MCPGateway, PosMcpConnection
from pieces.settings import Settings

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
        Settings.pieces_client.is_pieces_running(3)
        return True
    except (requests.RequestException, ConnectionError, SystemExit):
        return False


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
    connection = PosMcpConnection(upstream_url, mock_tools_changed_callback)

    # Attempt to connect
    session = await connection.connect()
    await asyncio.sleep(1)  # Allow time for connection to establish

    # Verify we got a valid session
    assert session is not None

    # Verify we discovered some tools
    assert len(connection.discovered_tools) > 0

    # Tools should be properly structured Tool objects
    for tool in connection.discovered_tools:
        assert hasattr(tool, "name")
        assert hasattr(tool, "description")
        assert isinstance(tool, types.Tool)


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
    connection = PosMcpConnection(upstream_url, mock_tools_changed_callback)

    try:
        if hasattr(Settings.pieces_client, "version") and hasattr(
            Settings.pieces_client.version, "_mock_name"
        ):
            Settings.pieces_client.version = "3.0.0"

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
        await asyncio.sleep(1)  # Allow time for connection to establish

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
