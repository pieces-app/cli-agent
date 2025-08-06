"""
Utilities, fixtures, and helpers for MCP Gateway tests.

This module provides shared components used across validation and integration tests:
- Constants and configuration
- Mock helpers and callbacks
- Test fixtures for dependency injection
- Utility functions for test setup
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

# ===== CONSTANTS =====

TEST_SERVER_NAME = "pieces-test-mcp"
"""Default server name used in MCP Gateway tests."""

DEFAULT_TEST_URL = "http://localhost:39300/model_context_protocol/2024-11-05/sse"
"""Fallback URL when Settings.startup() fails."""


# ===== MOCK HELPERS =====


async def mock_tools_changed_callback():
    """
    Mock callback for tools_changed_callback in tests.

    This is used as a placeholder callback when creating PosMcpConnection
    instances for testing without triggering real tool change notifications.
    """
    pass


def create_mock_tool(name: str, description: str = None) -> Mock:
    """
    Create a mock Tool object for testing.

    Args:
        name: The tool name
        description: Optional tool description

    Returns:
        Mock object configured as a Tool with name and description attributes
    """
    tool = Mock()
    tool.name = name
    tool.description = description
    return tool


def create_mock_tools_list(count: int = 3) -> list:
    """
    Create a list of mock tools for testing.

    Args:
        count: Number of mock tools to create

    Returns:
        List of mock Tool objects
    """
    return [
        create_mock_tool(f"tool_{i}", f"Description for tool {i}") for i in range(count)
    ]


# ===== UTILITY FUNCTIONS =====


def get_upstream_url():
    """
    Get the upstream URL for MCP server, handling potential errors.

    Attempts to get the real URL from Settings, falls back to hardcoded
    URL if Settings initialization fails (common in mocked tests).

    Returns:
        str: The upstream URL for MCP server connections
    """
    try:
        Settings.startup()
        return get_mcp_latest_url()
    except Exception:
        # We are mocking the settings so this will raise an exception most of the time
        # we can hardcode the url instead
        return DEFAULT_TEST_URL


def is_pieces_os_accessible(url: str = None) -> bool:
    """
    Check if PiecesOS MCP server is accessible.

    Args:
        url: Optional URL to check, defaults to get_upstream_url()

    Returns:
        bool: True if server is accessible, False otherwise
    """
    if url is None:
        url = get_upstream_url()

    if url is None:
        return False

    try:
        with urllib.request.urlopen(url, timeout=1) as response:
            response.read(1)
        return True
    except Exception:
        return False


# ===== PYTEST FIXTURES =====


@pytest.fixture(scope="module")
def ensure_pieces_setup():
    """
    Fixture to ensure Pieces OS is installed and accessible for testing.

    This module-scoped fixture checks once per test session whether
    PiecesOS is running and accessible.

    Returns:
        bool: True if Pieces OS is running, False otherwise
    """
    try:
        Settings.startup()
        return True
    except (requests.RequestException, ConnectionError, SystemExit):
        return False


@pytest.fixture
def mock_connection():
    """
    Create a fresh mock PosMcpConnection for testing.

    This function-scoped fixture provides a clean PosMcpConnection
    instance for each test, with any cached results reset.

    Returns:
        PosMcpConnection: Fresh connection instance for testing
    """
    connection = PosMcpConnection("http://test-url", mock_tools_changed_callback)
    # Reset any cached results to ensure clean state
    connection.result = None
    return connection


@pytest.fixture
def mock_gateway():
    """
    Create a mock MCPGateway for testing.

    Returns:
        MCPGateway: Gateway instance configured for testing
    """
    url = get_upstream_url()
    return MCPGateway(server_name=TEST_SERVER_NAME, upstream_url=url)


@pytest.fixture
def sample_tools():
    """
    Provide a sample set of mock tools for testing.

    Returns:
        list: List of mock Tool objects with various configurations
    """
    return [
        create_mock_tool(
            "ask_pieces_ltm", "Ask questions using Pieces Long Term Memory"
        ),
        create_mock_tool("create_pieces_memory", "Create a new memory in Pieces"),
        create_mock_tool("search_pieces", "Search through Pieces assets"),
    ]


# ===== CONTEXT MANAGERS =====


class MockPiecesOSContext:
    """Context manager for mocking PiecesOS state in tests."""

    def __init__(
        self, running: bool = True, ltm_enabled: bool = True, compatible: bool = True
    ):
        """
        Initialize mock context.

        Args:
            running: Whether PiecesOS should appear to be running
            ltm_enabled: Whether LTM should appear enabled
            compatible: Whether version should appear compatible
        """
        self.running = running
        self.ltm_enabled = ltm_enabled
        self.compatible = compatible
        self.patches = []

    def __enter__(self):
        """Enter the context and apply mocks."""
        # This could be expanded to provide common mocking patterns
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context and clean up mocks."""
        for patch_obj in self.patches:
            patch_obj.stop()


# ===== EXPORTS =====

__all__ = [
    # Constants
    "TEST_SERVER_NAME",
    "DEFAULT_TEST_URL",
    # Mock helpers
    "mock_tools_changed_callback",
    "create_mock_tool",
    "create_mock_tools_list",
    # Utilities
    "get_upstream_url",
    "is_pieces_os_accessible",
    # Fixtures
    "ensure_pieces_setup",
    "mock_connection",
    "mock_gateway",
    "sample_tools",
    # Context managers
    "MockPiecesOSContext",
    # Re-exports for convenience
    "UpdateEnum",
    "types",
]
