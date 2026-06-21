"""
MCP URL resolution and schema version selection.

Resolves PiecesOS MCP endpoint URLs from the schema versions API and caches
them to avoid repeated API calls. The cache is invalidated when PiecesOS
restarts or the connection is cleaned up.

The gateway prefers the ``2025-03-26`` streamable HTTP schema for upstream
connections (more robust than SSE), while IDE integration configs continue
to use the ``2024-11-05`` SSE schema for direct IDE-to-PiecesOS connections.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..settings import Settings

if TYPE_CHECKING:
    from pieces._vendor.pieces_os_client.models.model_context_protocol_schema_version import (
        ModelContextProtocolSchemaVersion,
    )

PREFERRED_SCHEMA_VERSION = "2025-03-26"
"""Streamable HTTP schema -- preferred for gateway upstream connections."""

SSE_SCHEMA_VERSION = "2024-11-05"
"""SSE schema -- used for IDE integration configs that connect directly to PiecesOS."""

_latest_urls: list[ModelContextProtocolSchemaVersion] = []


def get_mcp_model_urls() -> list[ModelContextProtocolSchemaVersion]:
    """Fetch and cache the list of MCP schema versions from PiecesOS.

    Returns:
        List of ``ModelContextProtocolSchemaVersion`` objects, each containing
        ``entry_endpoint`` and ``version`` fields.

    Raises:
        Exception: If the PiecesOS API call fails.
    """
    global _latest_urls
    if not _latest_urls:
        res = Settings.pieces_client.model_context_protocol_api.model_context_protocol_schema_versions()
        _latest_urls = res.iterable
    return _latest_urls


def invalidate_mcp_url_cache() -> None:
    """Clear the cached schema version URLs.

    Call this when PiecesOS restarts, the connection is cleaned up, or the
    upstream URL needs to be re-resolved (e.g. PiecesOS changed ports).
    """
    global _latest_urls
    _latest_urls = []


def get_mcp_latest_url() -> str:
    """Get the preferred MCP endpoint URL for gateway upstream connections.

    Prefers the ``2025-03-26`` streamable HTTP schema. Falls back to the
    first available schema if the preferred version is not found.

    Returns:
        The entry endpoint URL string.

    Raises:
        ValueError: If no MCP schema versions are available from PiecesOS.
    """
    urls = get_mcp_model_urls()
    if not urls:
        raise ValueError("No MCP schema versions available from PiecesOS")
    for schema in urls:
        if schema.version == PREFERRED_SCHEMA_VERSION:
            return schema.entry_endpoint
    return urls[0].entry_endpoint


def get_mcp_sse_url() -> str | None:
    """Get the SSE endpoint URL specifically for IDE integration configs.

    IDE integrations (Claude, Cursor, VS Code, etc.) connect directly to
    PiecesOS using SSE, so they need the ``2024-11-05`` schema URL.

    Returns:
        The SSE entry endpoint URL, or ``None`` if no schemas are available.
    """
    urls = get_mcp_model_urls()
    if not urls:
        return None
    for schema in urls:
        if schema.version == SSE_SCHEMA_VERSION:
            return schema.entry_endpoint
    return urls[0].entry_endpoint


def get_mcp_urls() -> list[str]:
    """Get all known MCP endpoint URLs (all schema versions).

    Returns:
        List of endpoint URL strings.
    """
    return [mcp.entry_endpoint for mcp in get_mcp_model_urls()]
